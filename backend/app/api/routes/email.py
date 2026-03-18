"""
PartnerScout AI - Email Routes

API endpoints for email generation and sending.
Implements STORY-2.4.3: Implement Email Endpoints.

Endpoints:
- POST /api/email/generate    - Generate an outreach email for a profile
- POST /api/email/send        - Send an email to a profile
- GET  /api/email/tones       - Get available email tones
"""

import logging
import time
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.constants import HttpStatus
from app.core.exceptions import (
    BusinessError,
    ForbiddenError,
    JobNotFoundError,
    PartnerScoutError,
    ProfileNotFoundError,
)
from app.guards.auth import UserContext, get_current_user
from app.guards.ownership import (
    ProfileOwnerGuard,
    _get_profile_owner_guard,
)
from app.models.email import (
    EmailTone,
    GenerateEmailRequest,
    GenerateEmailResponse,
    SendEmailRequest,
    SendEmailResponse,
)
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository
from app.services.email_service import EmailService, get_email_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Dependency Functions
# =============================================================================

def get_profile_repository() -> ProfileRepository:
    """Get a ProfileRepository instance."""
    return ProfileRepository()


def get_job_repository() -> JobRepository:
    """Get a JobRepository instance."""
    return JobRepository()


# =============================================================================
# Email Generation Endpoint
# =============================================================================

@router.post(
    "/email/generate",
    response_model=GenerateEmailResponse,
    summary="Generate an outreach email",
    description="Generate a personalized outreach email for a discovered profile.",
    responses={
        200: {"description": "Email generated successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner of the job/profile"},
        404: {"description": "Profile or job not found"},
        422: {"description": "Validation error"},
    }
)
async def generate_email(
    request: GenerateEmailRequest,
    user: UserContext = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    job_repo: JobRepository = Depends(get_job_repository),
) -> GenerateEmailResponse:
    """
    Generate a personalized outreach email for a profile.
    
    Creates an AI-generated email tailored to the profile and brand context.
    Supports multiple tones (professional, friendly, casual) and custom context.
    
    **Required:**
    - profile_id: The target profile UUID
    - job_id: The discovery job UUID
    
    **Optional:**
    - tone: Email tone (professional, friendly, casual) - defaults to friendly
    - include_profile_compliment: Include a specific compliment - defaults to true
    - custom_context: Additional context to include in the email
    - sender_name: Name for the email signature
    - sender_company: Company name for the signature
    """
    start_time = time.time()
    
    try:
        # Verify profile exists
        profile = profile_repo.get_by_id(str(request.profile_id))
        
        # Verify job exists and user owns it
        job = job_repo.get_by_id(str(request.job_id))
        
        if job.get("user_id") != user.user_id:
            raise ForbiddenError(
                message="You do not have access to this job",
                resource_type="job",
                resource_id=str(request.job_id),
            )
        
        # Verify profile belongs to job
        if profile.get("job_id") != str(request.job_id):
            raise ForbiddenError(
                message="Profile does not belong to the specified job",
                resource_type="profile",
                resource_id=str(request.profile_id),
                details={
                    "expected_job_id": str(request.job_id),
                    "actual_job_id": profile.get("job_id"),
                },
            )
        
        # Generate the email
        generated_email = email_service.generate_email(
            profile_id=str(request.profile_id),
            job_id=str(request.job_id),
            tone=request.tone,
            include_profile_compliment=request.include_profile_compliment,
            custom_context=request.custom_context,
            sender_name=request.sender_name,
            sender_company=request.sender_company,
        )
        
        generation_duration = time.time() - start_time
        
        logger.info(
            f"Generated email for profile {request.profile_id} "
            f"(tone: {request.tone.value}, duration: {generation_duration:.2f}s)"
        )
        
        return GenerateEmailResponse(
            email=generated_email,
            profile_name=profile.get("full_name"),
            profile_username=profile.get("username", "unknown"),
            generation_duration_seconds=round(generation_duration, 3),
        )
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


# =============================================================================
# Email Send Endpoint
# =============================================================================

@router.post(
    "/email/send",
    response_model=SendEmailResponse,
    summary="Send an outreach email",
    description="Send an outreach email to a discovered profile (mock implementation).",
    responses={
        200: {"description": "Email sent successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner of the job/profile"},
        404: {"description": "Profile or job not found"},
        422: {"description": "Validation error"},
    }
)
async def send_email(
    request: SendEmailRequest,
    user: UserContext = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    job_repo: JobRepository = Depends(get_job_repository),
) -> SendEmailResponse:
    """
    Send an outreach email to a profile.
    
    This is currently a mock implementation that simulates sending.
    In production, this would integrate with an email service provider.
    
    **Required:**
    - profile_id: The target profile UUID
    - job_id: The discovery job UUID
    - recipient_email: Email address to send to
    - subject: Email subject line
    - body: Email body content
    
    **Optional:**
    - html_body: HTML formatted body
    - from_name: Sender name
    - from_email: Sender email address
    - reply_to: Reply-to email address
    - track_opens: Enable open tracking - defaults to true
    - track_clicks: Enable click tracking - defaults to true
    - schedule_for: Schedule for later delivery
    """
    try:
        # Verify profile exists
        profile = profile_repo.get_by_id(str(request.profile_id))
        
        # Verify job exists and user owns it
        job = job_repo.get_by_id(str(request.job_id))
        
        if job.get("user_id") != user.user_id:
            raise ForbiddenError(
                message="You do not have access to this job",
                resource_type="job",
                resource_id=str(request.job_id),
            )
        
        # Verify profile belongs to job
        if profile.get("job_id") != str(request.job_id):
            raise ForbiddenError(
                message="Profile does not belong to the specified job",
                resource_type="profile",
                resource_id=str(request.profile_id),
            )
        
        # Send the email (mock)
        result = email_service.send_email_mock(
            profile_id=str(request.profile_id),
            job_id=str(request.job_id),
            recipient_email=request.recipient_email,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
            from_name=request.from_name,
            from_email=str(request.from_email) if request.from_email else None,
        )
        
        if result.success:
            logger.info(
                f"Sent email to {request.recipient_email} for profile {request.profile_id}"
            )
        else:
            logger.warning(
                f"Failed to send email to {request.recipient_email}: {result.error}"
            )
        
        return result
        
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


# =============================================================================
# Email Tones Endpoint
# =============================================================================

@router.get(
    "/email/tones",
    summary="Get available email tones",
    description="Get a list of available email tones for generation.",
    responses={
        200: {"description": "List of available tones"},
    }
)
async def get_available_tones(
    email_service: EmailService = Depends(get_email_service),
) -> dict:
    """
    Get available email tones.
    
    Returns a list of tone options with their labels and descriptions.
    Useful for populating UI dropdowns.
    """
    tones = email_service.get_available_tones()
    return {"tones": tones}
