"""
PartnerScout AI - Status Update Routes

STORY-2.4.2: Implement Status Update Endpoints

Provides endpoints for the orchestration pipeline to update job and profile statuses
during the discovery workflow.

Endpoints:
- PATCH /api/jobs/{job_id}/status - Update job status
- PATCH /api/profiles/{profile_id}/status - Update profile status
- PATCH /api/jobs/{job_id}/profiles/status - Batch update profile statuses
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import (
    ErrorCodes,
    HttpStatus,
    JobStatus,
    ProfileStatus,
    Routes,
)
from app.core.exceptions import (
    InvalidStatusTransitionError,
    JobNotFoundError,
    ProfileNotFoundError,
    ValidationError,
)
from app.guards.auth import ServiceContext, get_service_context
from app.guards.validation import (
    StatusTransitionGuard,
    get_status_transition_guard,
)
from app.models.status import (
    BatchProfileStatusResponse,
    BatchUpdateProfileStatusRequest,
    JobStatusResponse,
    ProfileStatusResponse,
    UpdateJobStatusRequest,
    UpdateProfileStatusRequest,
)
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository


# Configure logging
logger = logging.getLogger(__name__)


# =============================================================================
# Router Configuration
# =============================================================================

router = APIRouter()


# =============================================================================
# Dependency Injection
# =============================================================================

def get_job_repository() -> JobRepository:
    """Get job repository instance."""
    return JobRepository()


def get_profile_repository() -> ProfileRepository:
    """Get profile repository instance."""
    return ProfileRepository()


# =============================================================================
# Job Status Endpoints
# =============================================================================

@router.patch(
    "/jobs/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Update Job Status",
    description="""
    Update the status of a discovery job.
    
    This endpoint is used by the orchestration pipeline to update job status
    during the discovery workflow.
    
    **Valid Transitions:**
    - pending → analyzing, cancelled
    - analyzing → discovering, failed, cancelled
    - discovering → scoring, failed, cancelled
    - scoring → completed, failed, cancelled
    - failed → pending (retry)
    
    **Authentication:** Requires X-Service-Key header.
    """,
    responses={
        200: {"description": "Job status updated successfully"},
        400: {"description": "Invalid status transition"},
        401: {"description": "Invalid or missing service key"},
        404: {"description": "Job not found"},
        422: {"description": "Invalid status value"},
    },
)
async def update_job_status(
    job_id: UUID,
    request: UpdateJobStatusRequest,
    service: ServiceContext = Depends(get_service_context),
    job_repo: JobRepository = Depends(get_job_repository),
    transition_guard: StatusTransitionGuard = Depends(get_status_transition_guard),
) -> JobStatusResponse:
    """
    Update job status with transition validation.
    
    Args:
        job_id: The job UUID to update
        request: The status update request
        service: Service authentication context
        job_repo: Job repository
        transition_guard: Status transition validator
        
    Returns:
        Updated job status information
        
    Raises:
        HTTPException: If job not found, invalid transition, or invalid status
    """
    logger.info(
        f"Service '{service.service_name}' updating job {job_id} status to '{request.status.value}'"
    )
    
    try:
        # Get current job
        job = job_repo.get_by_id(str(job_id))
        current_status = job["status"]
        
        # Validate transition
        validated_status = transition_guard.validate_job_transition(
            current_status, request.status
        )
        
        # Update status in database
        updated_job = job_repo.update_status(
            id=str(job_id),
            status=validated_status,
            error_message=request.error_message,
        )
        
        logger.info(
            f"Job {job_id} status updated: {current_status} → {validated_status.value}"
        )
        
        return JobStatusResponse(
            id=UUID(updated_job["id"]),
            status=JobStatus(updated_job["status"]),
            previous_status=JobStatus(current_status),
            error_message=updated_job.get("error_message"),
            updated_at=datetime.fromisoformat(
                updated_job["updated_at"].replace("Z", "+00:00")
            ) if isinstance(updated_job["updated_at"], str) else updated_job["updated_at"],
        )
        
    except JobNotFoundError as e:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail=e.to_dict(),
        )
    except InvalidStatusTransitionError as e:
        logger.warning(
            f"Invalid status transition for job {job_id}: {e.message}"
        )
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail=e.to_dict(),
        )
    except ValidationError as e:
        logger.warning(f"Validation error for job {job_id}: {e.message}")
        raise HTTPException(
            status_code=HttpStatus.UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )


# =============================================================================
# Profile Status Endpoints
# =============================================================================

@router.patch(
    "/profiles/{profile_id}/status",
    response_model=ProfileStatusResponse,
    summary="Update Profile Status",
    description="""
    Update the status of a discovered profile.
    
    This endpoint is used by the orchestrator to update individual profile
    status during the scoring phase.
    
    **Valid Transitions:**
    - new → processing, skipped
    - processing → scored, failed
    - failed → processing (retry)
    
    **Authentication:** Requires X-Service-Key header.
    """,
    responses={
        200: {"description": "Profile status updated successfully"},
        400: {"description": "Invalid status transition"},
        401: {"description": "Invalid or missing service key"},
        404: {"description": "Profile not found"},
        422: {"description": "Invalid status value"},
    },
)
async def update_profile_status(
    profile_id: UUID,
    request: UpdateProfileStatusRequest,
    service: ServiceContext = Depends(get_service_context),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    transition_guard: StatusTransitionGuard = Depends(get_status_transition_guard),
) -> ProfileStatusResponse:
    """
    Update profile status with transition validation.
    
    Args:
        profile_id: The profile UUID to update
        request: The status update request
        service: Service authentication context
        profile_repo: Profile repository
        transition_guard: Status transition validator
        
    Returns:
        Updated profile status information
        
    Raises:
        HTTPException: If profile not found, invalid transition, or invalid status
    """
    logger.info(
        f"Service '{service.service_name}' updating profile {profile_id} status to '{request.status.value}'"
    )
    
    try:
        # Get current profile
        profile = profile_repo.get_by_id(str(profile_id))
        current_status = profile["status"]
        
        # Validate transition
        validated_status = transition_guard.validate_profile_transition(
            current_status, request.status
        )
        
        # Update status in database
        updated_profile = profile_repo.update_status(
            id=str(profile_id),
            status=validated_status,
        )
        
        logger.info(
            f"Profile {profile_id} status updated: {current_status} → {validated_status.value}"
        )
        
        return ProfileStatusResponse(
            id=UUID(updated_profile["id"]),
            status=ProfileStatus(updated_profile["status"]),
            previous_status=ProfileStatus(current_status),
            updated_at=datetime.fromisoformat(
                updated_profile["updated_at"].replace("Z", "+00:00")
            ) if isinstance(updated_profile["updated_at"], str) else updated_profile["updated_at"],
        )
        
    except ProfileNotFoundError as e:
        logger.warning(f"Profile not found: {profile_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail=e.to_dict(),
        )
    except InvalidStatusTransitionError as e:
        logger.warning(
            f"Invalid status transition for profile {profile_id}: {e.message}"
        )
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail=e.to_dict(),
        )
    except ValidationError as e:
        logger.warning(f"Validation error for profile {profile_id}: {e.message}")
        raise HTTPException(
            status_code=HttpStatus.UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )


# =============================================================================
# Batch Profile Status Endpoints
# =============================================================================

@router.patch(
    "/jobs/{job_id}/profiles/status",
    response_model=BatchProfileStatusResponse,
    summary="Batch Update Profile Statuses",
    description="""
    Update the status of multiple profiles for a job in a single request.
    
    This endpoint is used by the orchestrator to efficiently update multiple
    profile statuses at once, such as marking all new profiles as processing.
    
    **Notes:**
    - Individual profile failures don't fail the entire request
    - Returns counts of successful and failed updates
    - Each profile transition is validated individually
    
    **Authentication:** Requires X-Service-Key header.
    """,
    responses={
        200: {"description": "Batch update completed (may include partial failures)"},
        401: {"description": "Invalid or missing service key"},
        404: {"description": "Job not found"},
        422: {"description": "Invalid request format"},
    },
)
async def batch_update_profile_statuses(
    job_id: UUID,
    request: BatchUpdateProfileStatusRequest,
    service: ServiceContext = Depends(get_service_context),
    job_repo: JobRepository = Depends(get_job_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    transition_guard: StatusTransitionGuard = Depends(get_status_transition_guard),
) -> BatchProfileStatusResponse:
    """
    Batch update profile statuses for a job.
    
    Args:
        job_id: The job UUID owning the profiles
        request: Batch update request with profile IDs and target status
        service: Service authentication context
        job_repo: Job repository
        profile_repo: Profile repository
        transition_guard: Status transition validator
        
    Returns:
        Batch update results with success/failure counts
    """
    logger.info(
        f"Service '{service.service_name}' batch updating {len(request.profile_ids)} profiles "
        f"for job {job_id} to status '{request.status.value}'"
    )
    
    # Verify job exists
    try:
        job_repo.get_by_id(str(job_id))
    except JobNotFoundError as e:
        logger.warning(f"Job not found for batch update: {job_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail=e.to_dict(),
        )
    
    # Process each profile
    results: List[ProfileStatusResponse] = []
    errors: List[Dict[str, Any]] = []
    
    for profile_id in request.profile_ids:
        try:
            # Get current profile
            profile = profile_repo.get_by_id(str(profile_id))
            
            # Verify profile belongs to the job
            if profile["job_id"] != str(job_id):
                errors.append({
                    "profile_id": str(profile_id),
                    "error": "Profile does not belong to this job",
                    "code": ErrorCodes.FORBIDDEN,
                })
                continue
            
            current_status = profile["status"]
            
            # Validate transition
            validated_status = transition_guard.validate_profile_transition(
                current_status, request.status
            )
            
            # Update status
            updated_profile = profile_repo.update_status(
                id=str(profile_id),
                status=validated_status,
            )
            
            results.append(ProfileStatusResponse(
                id=UUID(updated_profile["id"]),
                status=ProfileStatus(updated_profile["status"]),
                previous_status=ProfileStatus(current_status),
                updated_at=datetime.fromisoformat(
                    updated_profile["updated_at"].replace("Z", "+00:00")
                ) if isinstance(updated_profile["updated_at"], str) else updated_profile["updated_at"],
            ))
            
        except ProfileNotFoundError:
            errors.append({
                "profile_id": str(profile_id),
                "error": f"Profile not found: {profile_id}",
                "code": ErrorCodes.PROFILE_NOT_FOUND,
            })
        except InvalidStatusTransitionError as e:
            errors.append({
                "profile_id": str(profile_id),
                "error": e.message,
                "code": ErrorCodes.INVALID_TRANSITION,
                "details": e.details,
            })
        except ValidationError as e:
            errors.append({
                "profile_id": str(profile_id),
                "error": e.message,
                "code": ErrorCodes.VALIDATION_ERROR,
            })
        except Exception as e:
            logger.error(f"Unexpected error updating profile {profile_id}: {e}")
            errors.append({
                "profile_id": str(profile_id),
                "error": "Unexpected error occurred",
                "code": ErrorCodes.INTERNAL_ERROR,
            })
    
    updated_count = len(results)
    failed_count = len(errors)
    
    logger.info(
        f"Batch update for job {job_id} completed: {updated_count} updated, {failed_count} failed"
    )
    
    return BatchProfileStatusResponse(
        updated=updated_count,
        failed=failed_count,
        results=results,
        errors=errors,
    )
