"""
Health check API endpoints.

Provides endpoints for monitoring the health of the application
and its dependencies. Used by load balancers, monitoring systems,
and orchestration tools.
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

# Create router with tags for OpenAPI documentation
router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Basic health check",
    description="Returns basic health status. Use for load balancer health checks.",
    response_model=Dict[str, Any]
)
async def health_check(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns the application's health status along with
    version and environment information.
    
    This endpoint is suitable for:
    - Load balancer health checks
    - Basic uptime monitoring
    - Quick connectivity tests
    
    Returns:
        Dict containing status, version, and environment
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get(
    "/detailed",
    summary="Detailed health check",
    description="Returns detailed health status including database connectivity.",
    response_model=Dict[str, Any]
)
async def health_check_detailed(
    settings: Settings = Depends(get_settings)
) -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    
    Returns comprehensive health status including:
    - Database connectivity status
    - External service status (when implemented)
    - Current timestamp
    
    This endpoint is suitable for:
    - Detailed status pages
    - Debugging connectivity issues
    - Monitoring dashboards
    
    Returns:
        Dict containing detailed health information
    """
    # Initialize response
    response = {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "connected": False,
            "type": "sqlite" if settings.use_sqlite_fallback else "supabase"
        },
        "services": {}
    }
    
    # Check database connectivity
    # For now, just report the configured type
    # Full connectivity tests will be added in EPIC-2
    if settings.use_sqlite_fallback:
        response["database"]["connected"] = True
        response["database"]["path"] = settings.sqlite_database_path
    else:
        # Will implement actual Supabase connectivity check in EPIC-2
        response["database"]["connected"] = bool(
            settings.supabase_url and settings.supabase_key
        )
    
    # Determine overall health status
    if not response["database"]["connected"]:
        response["status"] = "degraded"
    
    return response
