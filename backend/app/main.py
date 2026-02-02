"""
PartnerScout AI - FastAPI Application Entry Point

This module initializes the FastAPI application with all routes,
middleware, and exception handlers.

STORY-2.4.1: Implement Health & Job Endpoints
STORY-2.4.4: Register All Routes in Main App

Subtasks completed:
- SUB-2.4.4.1.1: All routers registered (health, jobs, status, email)
- SUB-2.4.4.1.2: CORS configured with dynamic origins from settings
- SUB-2.4.4.1.3: Exception handlers for PartnerScoutError, ValidationError, and generic errors
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import logging
from typing import List

from app.api.routes import health
from app.api.routes import jobs
from app.api.routes import status
from app.api.routes import email
from app.api.routes import agents
from app.core.config import settings
from app.core.exceptions import PartnerScoutError
from app.core.constants import HttpStatus


# Configure logging based on settings
logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("PartnerScout AI Backend starting...")
    log_registered_routes()
    yield
    # Shutdown
    logger.info("PartnerScout AI Backend shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="PartnerScout AI",
    description="AI-powered Instagram partner discovery platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(PartnerScoutError)
async def partner_scout_exception_handler(
    request: Request, 
    exc: PartnerScoutError
) -> JSONResponse:
    """
    Handle all PartnerScout custom exceptions.
    
    Converts exceptions to standardized JSON error responses.
    Response format: {"detail": {"error": {...}}}
    """
    logger.warning(
        f"PartnerScoutError: {exc.code} - {exc.message}",
        extra={"details": exc.details}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.to_dict()}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Formats validation errors in a consistent structure.
    Response format: {"detail": {"error": {...}}}
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=HttpStatus.UNPROCESSABLE_ENTITY,
        content={
            "detail": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"errors": errors},
                }
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle HTTPException from FastAPI and Starlette.
    
    Ensures consistent error response format for HTTP exceptions.
    Response format: {"detail": {"error": {...}}}
    """
    # If detail is already a dict with the expected structure, wrap it
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Otherwise, wrap in standard error format with detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "error": {
                    "code": _status_code_to_error_code(exc.status_code),
                    "message": str(exc.detail) if exc.detail else "HTTP error occurred",
                }
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle all unhandled exceptions.
    
    Logs the error and returns a generic error response.
    In production, sensitive error details are not exposed.
    Response format: {"detail": {"error": {...}}}
    """
    logger.exception(f"Unhandled exception: {exc}")
    
    # In development, include more details
    if settings.is_development and settings.debug:
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            content={
                "detail": {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": str(exc),
                        "details": {"type": type(exc).__name__},
                    }
                }
            }
        )
    
    return JSONResponse(
        status_code=HttpStatus.INTERNAL_SERVER_ERROR,
        content={
            "detail": {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            }
        }
    )


def _status_code_to_error_code(status_code: int) -> str:
    """
    Map HTTP status codes to error codes.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Appropriate error code string
    """
    mapping = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    return mapping.get(status_code, "HTTP_ERROR")


# =============================================================================
# Middleware Configuration
# =============================================================================

def get_cors_origins() -> List[str]:
    """
    Get CORS origins from settings.
    
    Returns:
        List of allowed origins for CORS.
    """
    # Start with configured origins from settings
    origins = settings.cors_origins_list.copy()
    
    # Always include localhost variants in development
    if settings.is_development:
        dev_origins = [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev server
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
        for origin in dev_origins:
            if origin not in origins:
                origins.append(origin)
    
    return origins


# Configure CORS with dynamic origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Service-Key",
        "X-Requested-With",
        "Accept",
        "Origin",
    ],
    expose_headers=[
        "X-Request-Id",
        "X-Total-Count",
    ],
)


# =============================================================================
# Route Registration
# =============================================================================

# Health routes
app.include_router(
    health.router, 
    prefix="/api", 
    tags=["Health"]
)

# Job routes (STORY-2.4.1)
app.include_router(
    jobs.router,
    prefix="/api",
    tags=["Jobs"]
)

# Status routes (STORY-2.4.2)
app.include_router(
    status.router,
    prefix="/api",
    tags=["Status"]
)

# Email routes (STORY-2.4.3)
app.include_router(
    email.router,
    prefix="/api",
    tags=["Email"]
)

# Agent routes (STORY-3.3.6)
app.include_router(
    agents.router,
    prefix="/api",
    tags=["Agents"]
)


# =============================================================================
# Root Endpoint
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information and available routes.
    
    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": "PartnerScout AI",
        "version": "1.0.0",
        "description": "AI-powered Instagram partner discovery platform",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": {
                "basic": "GET /api/health",
                "detailed": "GET /api/health/detailed",
            },
            "jobs": {
                "create": "POST /api/jobs",
                "list": "GET /api/jobs",
                "get": "GET /api/jobs/{job_id}",
                "update": "PATCH /api/jobs/{job_id}",
                "delete": "DELETE /api/jobs/{job_id}",
                "start": "POST /api/jobs/{job_id}/start",
                "retry": "POST /api/jobs/{job_id}/retry",
                "analytics": "GET /api/jobs/{job_id}/analytics",
                "quota": "GET /api/jobs/quota",
            },
            "status": {
                "update_job": "PATCH /api/jobs/{job_id}/status",
                "update_profile": "PATCH /api/profiles/{profile_id}/status",
                "batch_update": "PATCH /api/jobs/{job_id}/profiles/status",
            },
            "email": {
                "generate": "POST /api/email/generate",
                "send": "POST /api/email/send",
                "tones": "GET /api/email/tones",
            },
            "agents": {
                "analyze_brand": "POST /api/agent/analyze-brand",
                "discover": "POST /api/agent/discover",
                "score": "POST /api/agent/score",
                "status": "GET /api/agent/status",
            },
        },
        "environment": settings.environment,
    }


# =============================================================================
# Route Registration Summary (Logged in lifespan)
# =============================================================================

def log_registered_routes():
    """Log all registered routes."""
    logger.info("=" * 60)
    logger.info("PartnerScout AI - Registered Routes:")
    logger.info("=" * 60)
    
    route_groups = {
        "Health": ["/api/health", "/api/health/detailed"],
        "Jobs": [
            "/api/jobs", "/api/jobs/{job_id}", "/api/jobs/{job_id}/start",
            "/api/jobs/{job_id}/retry", "/api/jobs/{job_id}/analytics",
            "/api/jobs/quota"
        ],
        "Status": [
            "/api/jobs/{job_id}/status", "/api/profiles/{profile_id}/status",
            "/api/jobs/{job_id}/profiles/status"
        ],
        "Email": ["/api/email/generate", "/api/email/send", "/api/email/tones"],
        "Agents": [
            "/api/agent/analyze-brand", "/api/agent/discover",
            "/api/agent/score", "/api/agent/status"
        ],
    }
    
    for group, routes in route_groups.items():
        logger.info(f"  [{group}]: {len(routes)} endpoints")
        for route in routes:
            logger.info(f"    - {route}")
    
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"CORS Origins: {len(get_cors_origins())} configured")
    logger.info("=" * 60)
