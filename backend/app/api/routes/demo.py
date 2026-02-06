"""
PartnerScout AI - Demo Routes

API endpoints for demo mode functionality.
Supports the "Watch Demo" feature.

Endpoints:
- POST /api/demo/start - Create a demo job with pre-seeded profiles
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.constants import HttpStatus
from app.guards.auth import UserContext, get_optional_user
from app.services.demo_service import DemoService, get_demo_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================

class DemoStartResponse(BaseModel):
    """Response model for starting a demo."""
    
    job_id: UUID
    status: str
    message: str
    profiles_count: int
    redirect_url: str
    is_demo: bool = True


# =============================================================================
# Demo Endpoints
# =============================================================================

@router.post(
    "/demo/start",
    response_model=DemoStartResponse,
    status_code=HttpStatus.CREATED,
    summary="Start a demo session",
    description="Create a demo job with pre-seeded profiles for exploration.",
    responses={
        201: {"description": "Demo job created successfully"},
        500: {"description": "Failed to create demo job"},
    }
)
async def start_demo(
    user: Optional[UserContext] = Depends(get_optional_user),
    demo_service: DemoService = Depends(get_demo_service),
) -> DemoStartResponse:
    """
    Create a demo job with pre-seeded profiles.
    
    Works for both authenticated and anonymous users.
    The demo job is immediately in 'completed' status with
    sample profiles pre-scored for exploration.
    
    **Note:** Demo jobs are marked with [DEMO] prefix in the name.
    """
    try:
        user_id = user.user_id if user else None
        result = demo_service.create_demo_job(user_id=user_id)
        
        logger.info(f"Created demo job {result['job_id']} for user {user_id or 'anonymous'}")
        
        return DemoStartResponse(
            job_id=UUID(result["job_id"]),
            status=result["status"],
            message=result["message"],
            profiles_count=result["profiles_count"],
            redirect_url=result["redirect_url"],
            is_demo=result["is_demo"],
        )
        
    except Exception as e:
        logger.error(f"Failed to create demo job: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "DEMO_CREATION_FAILED",
                    "message": f"Failed to create demo job: {str(e)}"
                }
            }
        )
