"""
FastAPI application entry point.

This is the main entry point for the PartnerScout AI backend.
It creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- Logging initialization
- Router registration
- Lifespan management for startup/shutdown
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

# Initialize logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.
    
    This context manager handles application startup and shutdown.
    
    On startup:
    - Configures logging based on environment
    - Logs application start
    
    On shutdown:
    - Logs application shutdown
    - Cleans up resources (database connections, etc.)
    
    Args:
        app: The FastAPI application instance
        
    Yields:
        Control back to the application during its runtime
    """
    settings = get_settings()
    
    # Setup logging based on environment
    # Development: colorful console output
    # Production: JSON logs for log aggregators
    setup_logging(
        log_level="DEBUG" if settings.debug else "INFO",
        json_logs=settings.is_production
    )
    
    # Log startup
    logger.info(
        "Starting PartnerScout AI",
        environment=settings.environment,
        debug=settings.debug,
        database_type="sqlite" if settings.use_sqlite_fallback else "supabase"
    )
    
    # Yield control to the application
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down PartnerScout AI")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    This factory function creates a new FastAPI instance with
    all middleware, routers, and configuration applied.
    
    Using a factory function allows for:
    - Easy testing with custom configurations
    - Multiple app instances if needed
    - Clear separation of concerns
    
    Returns:
        Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Create FastAPI app with metadata
    app = FastAPI(
        title="PartnerScout AI",
        description="Instagram Partner Discovery Platform for D2C Brands",
        version="0.1.0",
        # Only show docs in development mode for security
        docs_url="/docs" if settings.is_development or settings.is_testing else None,
        redoc_url="/redoc" if settings.is_development or settings.is_testing else None,
        # Use lifespan for startup/shutdown
        lifespan=lifespan,
    )
    
    # Configure CORS middleware
    # This allows the frontend to communicate with the backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    # Health check endpoints
    app.include_router(health.router, prefix="/api")
    
    # Future routers will be added here:
    # app.include_router(auth.router, prefix="/api")
    # app.include_router(discovery.router, prefix="/api")
    # app.include_router(profiles.router, prefix="/api")
    # app.include_router(agent.router, prefix="/api")
    
    return app


# Create the application instance
# This is what uvicorn will import and run
app = create_application()
