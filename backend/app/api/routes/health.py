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
            username = user_data.get("data", {}).get("username", "?")
            services["apify"] = f"healthy (plan={plan}, user={username})"

            # Check recent actor runs
            runs_url = f"https://api.apify.com/v2/actor-runs?token={apify_key}&limit=5&desc=true"
            runs_resp = urllib.request.urlopen(
                urllib.request.Request(runs_url), timeout=10
            )
            runs_data = _json.loads(runs_resp.read())
            runs = runs_data.get("data", {}).get("items", [])
            services["apify_recent_runs"] = len(runs)
            if runs:
                latest = runs[0]
                services["apify_last_run"] = (
                    f"{latest.get('status')} at {latest.get('startedAt', '?')}"
                )
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


@router.get("/health/apify-test")
async def apify_scrape_test():
    """
    Run a minimal Apify actor call to verify end-to-end scraping works.

    Returns diagnostics about the apify_client library, API key, and actor run.
    """
    import os
    import traceback

    result: dict = {"steps": []}

    def log(msg: str):
        result["steps"].append(msg)

    # Step 1: Check env var
    apify_key = os.environ.get("APIFY_API_KEY", "")
    log(f"APIFY_API_KEY set: {bool(apify_key)}, prefix: {apify_key[:12]}...")

    # Step 2: Try importing apify_client
    try:
        from apify_client import ApifyClient
        import apify_client as _ac
        log(f"apify_client imported OK, version={getattr(_ac, '__version__', '?')}")
    except Exception as e:
        log(f"apify_client import FAILED: {e}")
        result["error"] = str(e)
        return result

    # Step 3: Create client and try to run actor
    try:
        client = ApifyClient(apify_key)
        log("ApifyClient created")

        # Run the profile scraper with a single well-known username
        run_input = {
            "usernames": ["instagram"],
            "resultsLimit": 1,
        }
        log("Starting actor run: apify/instagram-profile-scraper")
        run = client.actor("apify/instagram-profile-scraper").call(
            run_input=run_input,
            timeout_secs=120,
        )
        log(f"Actor run completed: status={run.get('status')}, id={run.get('id', '?')[:12]}")

        dataset_id = run.get("defaultDatasetId")
        if dataset_id:
            items = list(client.dataset(dataset_id).iterate_items())
            log(f"Dataset items: {len(items)}")
            if items:
                item = items[0]
                log(
                    f"Profile: @{item.get('username')}, "
                    f"followers={item.get('followersCount')}"
                )
                result["success"] = True
            else:
                log("No items in dataset")
                result["success"] = False
        else:
            log("No dataset ID in run result")
            result["success"] = False

    except Exception as e:
        tb = traceback.format_exc()
        log(f"Actor run FAILED: {e}")
        log(f"Traceback: {tb[-300:]}")
        result["error"] = str(e)
        result["success"] = False

    return result
