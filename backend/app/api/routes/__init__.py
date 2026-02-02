# Routes module - API route handlers
"""
API Routes Package

Contains all API endpoint handlers:
- health: Health check endpoints
- jobs: Job/session management endpoints (STORY-2.4.1)
- status: Status update endpoints (STORY-2.4.2)
- email: Email generation and sending endpoints (STORY-2.4.3)
- agents: AI agent endpoints (STORY-3.3.6)
"""

from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.status import router as status_router
from app.api.routes.email import router as email_router
from app.api.routes.agents import router as agents_router

__all__ = [
    "health_router",
    "jobs_router",
    "status_router",
    "email_router",
    "agents_router",
]
