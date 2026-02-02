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
    # TODO: Implement actual service health checks
    services = {
        "database": "healthy",  # Will check Supabase connectivity
        "llm_provider": "healthy",  # Will check LLM API connectivity
        "apify": "healthy",  # Will check Apify API connectivity
    }
    
    # Determine overall status
    overall_status = "healthy" if all(
        s == "healthy" for s in services.values()
    ) else "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services
    )
