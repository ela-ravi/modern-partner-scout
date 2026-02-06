"""
PartnerScout AI - Job Routes

API endpoints for managing discovery jobs (sessions).
Implements STORY-2.4.1: Health & Job Endpoints.

Endpoints:
- POST   /api/jobs              - Create a new discovery job
- GET    /api/jobs              - List all jobs for the current user
- GET    /api/jobs/{job_id}     - Get job details with profiles
- POST   /api/jobs/{job_id}/start   - Start discovery workflow
- DELETE /api/jobs/{job_id}     - Delete a job
- POST   /api/jobs/{job_id}/retry   - Retry a failed job
- PATCH  /api/jobs/{job_id}     - Update job metadata
- GET    /api/jobs/{job_id}/analytics - Get job analytics
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.core.constants import HttpStatus, Defaults
from app.core.exceptions import (
    BusinessError,
    DailyLimitExceededError,
    ForbiddenError,
    InvalidStatusTransitionError,
    JobAlreadyCompletedError,
    JobNotFoundError,
    JobNotStartableError,
    N8NError,
    PartnerScoutError,
)
from app.guards.auth import UserContext, get_current_user
from app.guards.ownership import verify_job_owner_user_only
from app.models.job import (
    CreateJobRequest,
    Job,
    JobAnalytics,
    JobCancelResponse,
    JobDeleteResponse,
    JobListResponse,
    JobStartResponse,
    JobSummary,
    JobWithProfiles,
    UpdateJobRequest,
)
from app.services.job_service import JobService, get_job_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Helper Functions
# =============================================================================

def _handle_exception(e: Exception) -> None:
    """
    Convert PartnerScout exceptions to HTTPExceptions.
    
    Args:
        e: The exception to handle
        
    Raises:
        HTTPException: With appropriate status code and error details
    """
    if isinstance(e, PartnerScoutError):
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    # Re-raise unknown exceptions
    raise


# =============================================================================
# Job CRUD Endpoints
# =============================================================================

@router.post(
    "/jobs",
    response_model=Job,
    status_code=HttpStatus.CREATED,
    summary="Create a new discovery job",
    description="Create a new discovery job/session for finding Instagram partners.",
    responses={
        201: {"description": "Job created successfully"},
        401: {"description": "Authentication required"},
        422: {"description": "Validation error"},
        429: {"description": "Daily job limit exceeded"},
    }
)
async def create_job(
    request: CreateJobRequest,
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> Job:
    """
    Create a new discovery job.
    
    Creates a new discovery session with the provided brand description
    and reference Instagram profiles. The job starts in 'pending' status.
    
    **Daily Limit:** Users are limited to 10 jobs per 24-hour period.
    
    **Reference Profiles:** Must provide between 2-10 valid Instagram URLs.
    """
    try:
        job_data = job_service.create_job(
            user_id=user.user_id,
            brand_description=request.brand_description,
            reference_profiles=request.reference_profiles,
            name=request.name,
            follower_range_min=request.follower_range_min,
            follower_range_max=request.follower_range_max,
            discovery_limit=request.discovery_limit,
            # Enhancement fields (Item 5)
            keywords=request.keywords,
            hashtags=request.hashtags,
            min_score_threshold=request.min_score_threshold,
        )
        
        logger.info(f"Created job {job_data['id']} for user {user.user_id}")
        return Job(**job_data)
        
    except DailyLimitExceededError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.get(
    "/jobs",
    response_model=JobListResponse,
    summary="List all jobs for current user",
    description="Retrieve a paginated list of discovery jobs for the authenticated user.",
    responses={
        200: {"description": "List of jobs"},
        401: {"description": "Authentication required"},
    }
)
async def list_jobs(
    status: Optional[str] = Query(
        None,
        description="Filter by job status (pending, analyzing, discovering, scoring, completed, failed, cancelled)"
    ),
    limit: int = Query(
        Defaults.PAGE_SIZE,
        ge=1,
        le=Defaults.MAX_PAGE_SIZE,
        description="Maximum number of jobs to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of jobs to skip for pagination"
    ),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> JobListResponse:
    """
    List discovery jobs for the current user.
    
    Returns a paginated list of jobs, sorted by creation date (newest first).
    Optionally filter by status.
    """
    result = job_service.list_user_jobs(
        user_id=user.user_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    
    # Convert to response model
    jobs = [JobSummary(**job) for job in result["jobs"]]
    
    return JobListResponse(
        jobs=jobs,
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )


# =============================================================================
# User Quota Endpoint (must be defined before {job_id} routes)
# =============================================================================

@router.get(
    "/jobs/quota",
    summary="Get remaining daily quota",
    description="Check how many jobs the user can still create today.",
    responses={
        200: {"description": "Quota information"},
        401: {"description": "Authentication required"},
    }
)
async def get_quota(
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
) -> dict:
    """
    Get the user's remaining daily job quota.
    
    Returns:
    - daily_limit: Maximum jobs allowed per day
    - used_today: Jobs created in last 24 hours
    - remaining: Jobs that can still be created
    """
    quota = job_service.get_remaining_daily_quota(user.user_id)
    return quota


@router.get(
    "/jobs/{job_id}",
    response_model=JobWithProfiles,
    summary="Get job details with profiles",
    description="Retrieve detailed job information including discovered profiles.",
    responses={
        200: {"description": "Job details with profiles"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
    }
)
async def get_job(
    job_id: str = Path(..., description="The job UUID"),
    min_score: Optional[int] = Query(
        None,
        ge=Defaults.MIN_SCORE,
        le=Defaults.MAX_SCORE,
        description="Filter profiles by minimum score"
    ),
    profile_status: Optional[str] = Query(
        None,
        description="Filter profiles by status (new, processing, scored, failed, skipped)"
    ),
    profile_limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum number of profiles to return"
    ),
    profile_offset: int = Query(
        0,
        ge=0,
        description="Number of profiles to skip"
    ),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> JobWithProfiles:
    """
    Get detailed job information with profiles.
    
    Returns the job details along with discovered profiles, scores, and brand DNA.
    Supports filtering profiles by score threshold and status.
    """
    try:
        result = job_service.get_job_with_profiles(
            job_id=job_id,
            min_score=min_score,
            profile_status=profile_status,
            profile_limit=profile_limit,
            profile_offset=profile_offset,
        )
        
        return JobWithProfiles(**result)
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.delete(
    "/jobs/{job_id}",
    response_model=JobDeleteResponse,
    summary="Delete a job",
    description="Delete a discovery job and all associated data.",
    responses={
        200: {"description": "Job deleted successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
    }
)
async def delete_job(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> JobDeleteResponse:
    """
    Delete a discovery job.
    
    Permanently deletes the job and all associated data including:
    - Brand DNA
    - Discovered profiles
    - Profile scores
    - Profile contacts
    
    **Warning:** This action cannot be undone.
    """
    try:
        result = job_service.delete_job(job_id)
        
        logger.info(f"Deleted job {job_id} for user {user.user_id}")
        return JobDeleteResponse(
            deleted=result["deleted"],
            job_id=UUID(job_id),
        )
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.patch(
    "/jobs/{job_id}",
    response_model=Job,
    summary="Update job metadata",
    description="Update job metadata such as name or brand description.",
    responses={
        200: {"description": "Job updated successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
        409: {"description": "Cannot modify completed job"},
        422: {"description": "Validation error"},
    }
)
async def update_job(
    request: UpdateJobRequest,
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> Job:
    """
    Update job metadata.
    
    Allows updating the job name and/or brand description.
    Cannot modify jobs that are in a terminal status (completed, failed, cancelled).
    """
    try:
        updated_job = job_service.update_job(
            job_id=job_id,
            name=request.name,
            brand_description=request.brand_description,
        )
        
        logger.info(f"Updated job {job_id} for user {user.user_id}")
        return Job(**updated_job)
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except JobAlreadyCompletedError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


# =============================================================================
# Job Action Endpoints
# =============================================================================

@router.post(
    "/jobs/{job_id}/start",
    response_model=JobStartResponse,
    status_code=HttpStatus.ACCEPTED,
    summary="Start discovery workflow",
    description="Trigger the discovery workflow via N8N for a pending job.",
    responses={
        202: {"description": "Discovery workflow initiated"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
        409: {"description": "Job cannot be started (wrong status)"},
        502: {"description": "N8N workflow trigger failed"},
    }
)
async def start_job(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> JobStartResponse:
    """
    Start the discovery workflow for a job.
    
    Triggers the N8N workflow to begin the discovery process:
    1. Brand analysis (extract hashtags, keywords, embedding)
    2. Profile discovery (search for similar profiles)
    3. Profile scoring (evaluate and rank profiles)
    
    The job must be in 'pending' status to start.
    """
    try:
        result = job_service.trigger_discovery(
            job_id=job_id,
            user_id=user.user_id,
        )
        
        logger.info(f"Started discovery for job {job_id}")
        return JobStartResponse(
            status=result["status"],
            job_id=UUID(job_id),
            message=result["message"],
        )
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except JobNotStartableError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except N8NError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.post(
    "/jobs/{job_id}/cancel",
    response_model=JobCancelResponse,
    summary="Cancel a running job",
    description="Cancel a pending or running discovery job.",
    responses={
        200: {"description": "Job cancelled successfully"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
        400: {"description": "Job cannot be cancelled from current status"},
    }
)
async def cancel_job(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> JobCancelResponse:
    """
    Cancel a discovery job.
    
    Cancels a job that is pending or currently running (analyzing, discovering, scoring).
    Jobs that are already completed, failed, or cancelled cannot be cancelled.
    
    This will stop any ongoing processing and mark the job as cancelled.
    """
    try:
        result = job_service.cancel_job(
            job_id=job_id,
            user_id=user.user_id,
        )
        
        logger.info(f"Cancelled job {job_id} for user {user.user_id}")
        return JobCancelResponse(
            status=result["status"],
            job_id=UUID(job_id),
            cancelled_at=result["cancelled_at"],
            message=result["message"],
        )
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


@router.post(
    "/jobs/{job_id}/retry",
    response_model=Job,
    summary="Retry a failed job",
    description="Reset a failed job to pending status for retry.",
    responses={
        200: {"description": "Job reset for retry"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
        400: {"description": "Job cannot be retried from current status"},
    }
)
async def retry_job(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> Job:
    """
    Retry a failed job.
    
    Resets the job status from 'failed' back to 'pending' so it can be started again.
    Only jobs with 'failed' status can be retried.
    """
    try:
        updated_job = job_service.retry_job(
            job_id=job_id,
            user_id=user.user_id,
        )
        
        logger.info(f"Reset job {job_id} for retry")
        return Job(**updated_job)
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
    except BusinessError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )


# =============================================================================
# Job Analytics Endpoint
# =============================================================================

@router.get(
    "/jobs/{job_id}/analytics",
    response_model=JobAnalytics,
    summary="Get job analytics",
    description="Retrieve analytics and statistics for a discovery job.",
    responses={
        200: {"description": "Job analytics"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
    }
)
async def get_job_analytics(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    job: dict = Depends(verify_job_owner_user_only),  # Verifies ownership
) -> JobAnalytics:
    """
    Get analytics for a discovery job.
    
    Returns statistics including:
    - Total profiles discovered
    - Profiles by status (new, processing, done, skipped)
    - Score statistics (average, min, max)
    - Number of profiles with email contacts
    - Number of high-scoring profiles (80+)
    """
    try:
        analytics = job_service.get_analytics(job_id)
        
        return JobAnalytics(
            job_id=UUID(job_id),
            total_profiles=analytics.get("profiles_discovered", 0),
            new_profiles=analytics.get("new_profiles", 0),
            processing_profiles=analytics.get("processing_profiles", 0),
            done_profiles=analytics.get("done_profiles", 0),
            skipped_profiles=analytics.get("skipped_profiles", 0),
            avg_score=analytics.get("average_score"),
            max_score=analytics.get("max_score"),
            min_score=analytics.get("min_score"),
            profiles_with_email=analytics.get("profiles_with_email", 0),
        )
        
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.to_dict()
        )
