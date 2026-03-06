"""
Health Check Routes

Provides health check endpoints for monitoring and load balancer probes.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    timestamp: str
    version: str
    services: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        HealthResponse: Current health status of the API.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check endpoint.

    Checks connectivity to all dependent services.

    Returns:
        DetailedHealthResponse: Detailed health status including service connectivity.
    """
    import os

    services: dict = {}

    # --- Apify ---
    apify_key = os.environ.get("APIFY_API_KEY", "")
    if not apify_key or apify_key == "your-apify-api-key":
        services["apify"] = "not_configured"
    else:
        services["apify_key_prefix"] = apify_key[:12] + "..."
        try:
            from app.services.apify_service import get_apify_service
            svc = get_apify_service()
            services["apify_configured"] = svc.is_configured()
            # Quick connectivity check via REST
            import urllib.request, json as _json
            test_url = f"https://api.apify.com/v2/users/me?token={apify_key}"
            resp = urllib.request.urlopen(
                urllib.request.Request(test_url), timeout=10
            )
            user_data = _json.loads(resp.read())
            plan = user_data.get("data", {}).get("plan", {}).get("id", "?")
            services["apify"] = f"healthy (plan={plan})"
        except Exception as e:
            services["apify"] = f"error: {str(e)[:120]}"

    # --- LLM ---
    llm_provider = os.environ.get("LLM_PROVIDER", "?")
    services["llm_provider"] = llm_provider
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    services["gemini_key_set"] = bool(gemini_key and len(gemini_key) > 5)

    # --- Database ---
    try:
        from app.core.config import settings as _settings
        services["supabase_url"] = _settings.supabase.url[:40] + "..."
        services["database"] = "configured"
    except Exception as e:
        services["database"] = f"error: {str(e)[:80]}"

    overall_status = "healthy" if "error" not in str(services.get("apify", "")) else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services
    )
