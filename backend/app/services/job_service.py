"""
PartnerScout AI - Job Service

Service layer for managing discovery jobs. Implements business logic
for job creation, management, and orchestration.

STORY-2.3.1: Implement Job Service
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID
import httpx

from app.core.config import settings
from app.core.constants import (
    JobStatus,
    ProfileStatus,
    VALID_JOB_TRANSITIONS,
    is_valid_job_transition,
)
from app.core.exceptions import (
    BusinessError,
    DailyLimitExceededError,
    InvalidStatusTransitionError,
    JobNotFoundError,
    JobNotStartableError,
    JobAlreadyCompletedError,
    N8NError,
)
from app.repositories import JobRepository, ProfileRepository


logger = logging.getLogger(__name__)


class JobService:
    """
    Service class for managing discovery jobs.
    
    Handles business logic including:
    - Daily limit enforcement
    - Job lifecycle management
    - N8N workflow triggering
    - Analytics computation
    """
    
    def __init__(
        self,
        job_repo: Optional[JobRepository] = None,
        profile_repo: Optional[ProfileRepository] = None,
    ):
        """
        Initialize the JobService.
        
        Args:
            job_repo: Optional JobRepository instance (creates new if not provided)
            profile_repo: Optional ProfileRepository instance (creates new if not provided)
        """
        self.job_repo = job_repo or JobRepository()
        self.profile_repo = profile_repo or ProfileRepository()
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create_job(
        self,
        user_id: str,
        brand_description: str,
        reference_profiles: List[str],
        name: Optional[str] = None,
        follower_range_min: int = 5000,
        follower_range_max: int = 500000,
        discovery_limit: int = 50,
        keywords: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        min_score_threshold: int = 50,
    ) -> Dict[str, Any]:
        """
        Create a new discovery job with daily limit enforcement.
        
        Args:
            user_id: ID of the user creating the job
            brand_description: Description of the brand
            reference_profiles: List of Instagram profile URLs
            name: Optional job name
            follower_range_min: Minimum followers for discovery
            follower_range_max: Maximum followers for discovery
            discovery_limit: Maximum profiles to discover
            keywords: Optional target keywords for discovery
            hashtags: Optional target hashtags for discovery
            min_score_threshold: Minimum score filter (0-100)
            
        Returns:
            Created job data
            
        Raises:
            DailyLimitExceededError: If user has exceeded daily job limit
            BusinessError: If job creation fails
        """
        # Check daily limit
        daily_limit = settings.daily_job_limit
        jobs_today = self.job_repo.count_user_jobs_today(user_id)
        
        if jobs_today >= daily_limit:
            logger.warning(
                f"User {user_id} exceeded daily job limit ({jobs_today}/{daily_limit})"
            )
            raise DailyLimitExceededError(
                limit=daily_limit,
                message=f"Daily job limit of {daily_limit} exceeded. You have created {jobs_today} jobs today.",
                details={
                    "limit": daily_limit,
                    "current_count": jobs_today,
                    "user_id": user_id,
                }
            )
        
        # Create the job
        try:
            job = self.job_repo.create(
                user_id=user_id,
                brand_description=brand_description,
                reference_profiles=reference_profiles,
                name=name,
                follower_range_min=follower_range_min,
                follower_range_max=follower_range_max,
                discovery_limit=discovery_limit,
                keywords=keywords or [],
                hashtags=hashtags or [],
                min_score_threshold=min_score_threshold,
            )
            
            logger.info(f"Created job {job['id']} for user {user_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to create job for user {user_id}: {e}")
            raise BusinessError(
                message=f"Failed to create discovery job: {str(e)}",
                details={"user_id": user_id, "error": str(e)}
            )
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Job data
            
        Raises:
            JobNotFoundError: If job is not found
        """
        return self.job_repo.get_by_id(job_id)
    
    def list_user_jobs(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List jobs for a specific user.
        
        Args:
            user_id: User ID to filter by
            status: Optional status filter
            limit: Maximum results
            offset: Results to skip
            
        Returns:
            Dict with jobs list and pagination info
        """
        jobs = self.job_repo.list_by_user(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        
        return {
            "jobs": jobs,
            "total": len(jobs),  # Note: For accurate total, need count query
            "limit": limit,
            "offset": offset,
        }
    
    def get_job_with_profiles(
        self,
        job_id: str,
        min_score: Optional[int] = None,
        profile_status: Optional[str] = None,
        profile_limit: int = 100,
        profile_offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get a job with its associated profiles.
        
        Args:
            job_id: Job UUID
            min_score: Optional minimum score filter for profiles
            profile_status: Optional profile status filter
            profile_limit: Maximum profiles to return
            profile_offset: Profile pagination offset
            
        Returns:
            Job data with profiles included
            
        Raises:
            JobNotFoundError: If job is not found
        """
        # Get the job first
        job = self.job_repo.get_by_id(job_id)
        
        # Get profiles with scores
        profiles = self.profile_repo.list_by_job_with_scores(
            job_id=job_id,
            min_score=min_score,
            status=profile_status,
            limit=profile_limit,
            offset=profile_offset,
        )
        
        # Get brand DNA if available
        try:
            job_with_brand = self.job_repo.get_with_brand_dna(job_id)
            brand_dna = job_with_brand.get("brand_dna")
        except Exception:
            brand_dna = None
        
        return {
            **job,
            "profiles": profiles,
            "brand_dna": brand_dna,
        }
    
    def get_analytics(self, job_id: str) -> Dict[str, Any]:
        """
        Get analytics for a job.
        
        Computes statistics about discovered profiles including
        score distributions and email availability.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Analytics data for the job
            
        Raises:
            JobNotFoundError: If job is not found
        """
        # Verify job exists
        job = self.job_repo.get_by_id(job_id)
        
        # Get job summary from view (includes aggregated stats)
        summary = self.job_repo.get_job_summary(job_id)
        
        if summary:
            return {
                "job_id": job_id,
                "profiles_discovered": summary.get("total_profiles", 0),
                "profiles_scored": summary.get("scored_profiles", 0),
                "new_profiles": summary.get("new_profiles", 0),
                "processing_profiles": summary.get("processing_profiles", 0),
                "done_profiles": summary.get("done_profiles", 0),
                "skipped_profiles": summary.get("skipped_profiles", 0),
                "average_score": summary.get("avg_score"),
                "max_score": summary.get("max_score"),
                "min_score": summary.get("min_score"),
                "profiles_with_email": summary.get("profiles_with_email", 0),
                "high_score_count": summary.get("high_score_count", 0),
            }
        
        # Fallback: Compute from profile counts if view not available
        profiles = self.profile_repo.list_by_job_with_scores(
            job_id=job_id,
            limit=1000,
        )
        
        total = len(profiles)
        scores = [p.get("final_score") for p in profiles if p.get("final_score")]
        emails = [p for p in profiles if p.get("contact_email")]
        
        # Count by status
        status_counts = {}
        for p in profiles:
            status = p.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "job_id": job_id,
            "profiles_discovered": total,
            "profiles_scored": len(scores),
            "new_profiles": status_counts.get(ProfileStatus.NEW.value, 0),
            "processing_profiles": status_counts.get(ProfileStatus.PROCESSING.value, 0),
            "done_profiles": status_counts.get(ProfileStatus.SCORED.value, 0),
            "skipped_profiles": status_counts.get(ProfileStatus.SKIPPED.value, 0),
            "average_score": round(sum(scores) / len(scores), 1) if scores else None,
            "max_score": max(scores) if scores else None,
            "min_score": min(scores) if scores else None,
            "profiles_with_email": len(emails),
            "high_score_count": len([s for s in scores if s >= settings.high_score_threshold]),
        }
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_status(
        self,
        job_id: str,
        new_status: str | JobStatus,
        error_message: Optional[str] = None,
        validate_transition: bool = True,
    ) -> Dict[str, Any]:
        """
        Update job status with transition validation.
        
        Args:
            job_id: Job UUID
            new_status: New status value
            error_message: Optional error message (for failed status)
            validate_transition: Whether to validate the status transition
            
        Returns:
            Updated job data
            
        Raises:
            JobNotFoundError: If job is not found
            InvalidStatusTransitionError: If transition is not valid
        """
        # Get current job
        job = self.job_repo.get_by_id(job_id)
        current_status = JobStatus(job["status"])
        target_status = JobStatus(new_status) if isinstance(new_status, str) else new_status
        
        # Validate transition if required
        if validate_transition:
            if not is_valid_job_transition(current_status, target_status):
                valid_targets = VALID_JOB_TRANSITIONS.get(current_status, frozenset())
                raise InvalidStatusTransitionError(
                    from_status=current_status.value,
                    to_status=target_status.value,
                    entity_type="job",
                    message=f"Cannot transition job from '{current_status.value}' to '{target_status.value}'. "
                           f"Valid transitions: {[s.value for s in valid_targets] or 'none'}"
                )
        
        # Update the status
        updated_job = self.job_repo.update_status(
            id=job_id,
            status=target_status,
            error_message=error_message,
        )
        
        logger.info(
            f"Updated job {job_id} status: {current_status.value} -> {target_status.value}"
        )
        
        return updated_job
    
    def update_job(
        self,
        job_id: str,
        name: Optional[str] = None,
        brand_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update job metadata.
        
        Args:
            job_id: Job UUID
            name: New job name
            brand_description: New brand description
            
        Returns:
            Updated job data
            
        Raises:
            JobNotFoundError: If job is not found
            JobAlreadyCompletedError: If job is in terminal state
        """
        # Get current job
        job = self.job_repo.get_by_id(job_id)
        current_status = JobStatus(job["status"])
        
        # Check if job can be modified
        if current_status in JobStatus.terminal_statuses():
            raise JobAlreadyCompletedError(
                job_id=job_id,
                message=f"Cannot modify job with status '{current_status.value}'"
            )
        
        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if brand_description is not None:
            update_data["brand_description"] = brand_description
        
        if not update_data:
            return job  # No changes
        
        # Update via repository base method
        from app.repositories.base_repo import BaseRepository
        updated_job = self.job_repo.update(job_id, update_data)
        
        logger.info(f"Updated job {job_id} metadata: {list(update_data.keys())}")
        
        return updated_job
    
    # =========================================================================
    # Workflow Operations
    # =========================================================================
    
    def trigger_discovery(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """
        Trigger the discovery workflow via N8N webhook.
        
        Args:
            job_id: Job UUID to start discovery for
            user_id: ID of the user triggering the workflow
            
        Returns:
            Response from N8N webhook
            
        Raises:
            JobNotFoundError: If job is not found
            JobNotStartableError: If job cannot be started
            N8NError: If webhook call fails
        """
        # Get and validate job
        job = self.job_repo.get_by_id(job_id)
        current_status = JobStatus(job["status"])
        
        # Check if job can be started
        if current_status not in JobStatus.startable_statuses():
            raise JobNotStartableError(
                job_id=job_id,
                current_status=current_status.value,
                message=f"Job cannot be started from status '{current_status.value}'. "
                       f"Job must be in 'pending' status."
            )
        
        # Prepare webhook payload
        webhook_url = settings.n8n.webhook_url
        service_key = settings.n8n.service_key
        
        payload = {
            "job_id": job_id,
            "user_id": user_id,
            "brand_description": job["brand_description"],
            "reference_profiles": job["reference_profiles"],
            "follower_range_min": job["follower_range_min"],
            "follower_range_max": job["follower_range_max"],
            "discovery_limit": job["discovery_limit"],
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Service-Key": service_key,
        }
        
        try:
            # Call N8N webhook
            with httpx.Client(timeout=settings.request_timeout_seconds) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code >= 400:
                    raise N8NError(
                        message=f"N8N webhook returned error: {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "response": response.text[:500],
                        }
                    )
                
                logger.info(f"Triggered discovery workflow for job {job_id}")
                
                return {
                    "status": "accepted",
                    "job_id": job_id,
                    "message": "Discovery workflow initiated",
                    "webhook_response": response.json() if response.text else None,
                }
                
        except httpx.RequestError as e:
            logger.error(f"Failed to call N8N webhook for job {job_id}: {e}")
            raise N8NError(
                message=f"Failed to trigger discovery workflow: {str(e)}",
                details={"job_id": job_id, "error": str(e)}
            )
    
    def cancel_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """
        Cancel a running or pending job.
        
        Args:
            job_id: Job UUID to cancel
            user_id: User ID (for logging/verification)
            
        Returns:
            Cancellation confirmation with status, job_id, cancelled_at, message
            
        Raises:
            JobNotFoundError: If job is not found
            BusinessError: If job cannot be cancelled from current status
        """
        from datetime import datetime, timezone
        
        # Get current job
        job = self.job_repo.get_by_id(job_id)
        current_status = JobStatus(job["status"])
        
        # Check if job can be cancelled (pending or active statuses)
        cancellable_statuses = JobStatus.active_statuses() | {JobStatus.PENDING}
        if current_status not in cancellable_statuses:
            raise BusinessError(
                message=f"Job cannot be cancelled from status '{current_status.value}'",
                details={
                    "job_id": job_id,
                    "current_status": current_status.value,
                    "cancellable_statuses": [s.value for s in cancellable_statuses],
                }
            )
        
        # Update status to cancelled
        self.update_status(
            job_id=job_id,
            new_status=JobStatus.CANCELLED,
            validate_transition=True,
        )
        
        logger.info(f"Cancelled job {job_id} (was {current_status.value})")
        
        return {
            "status": "cancelled",
            "job_id": job_id,
            "cancelled_at": datetime.now(timezone.utc).isoformat(),
            "message": "Discovery job cancelled successfully",
        }
    
    def retry_job(self, job_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retry a failed job.
        
        Resets the job status to pending and optionally triggers discovery.
        
        Args:
            job_id: Job UUID to retry
            user_id: ID of the user retrying the job
            
        Returns:
            Updated job data
            
        Raises:
            JobNotFoundError: If job is not found
            BusinessError: If job cannot be retried
        """
        # Get current job
        job = self.job_repo.get_by_id(job_id)
        current_status = JobStatus(job["status"])
        
        # Check if job can be retried
        if current_status not in JobStatus.retryable_statuses():
            raise BusinessError(
                message=f"Job cannot be retried from status '{current_status.value}'",
                details={
                    "job_id": job_id,
                    "current_status": current_status.value,
                    "retryable_statuses": [s.value for s in JobStatus.retryable_statuses()],
                }
            )
        
        # Reset to pending
        updated_job = self.update_status(
            job_id=job_id,
            new_status=JobStatus.PENDING,
            error_message=None,
            validate_transition=True,
        )
        
        logger.info(f"Reset job {job_id} for retry (was {current_status.value})")
        
        return updated_job
    
    # =========================================================================
    # Delete Operations
    # =========================================================================
    
    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete a job and all associated data.
        
        Args:
            job_id: Job UUID to delete
            
        Returns:
            Deletion confirmation
            
        Raises:
            JobNotFoundError: If job is not found
        """
        # Verify job exists
        job = self.job_repo.get_by_id(job_id)
        
        # Delete (cascades to related tables via foreign keys)
        deleted = self.job_repo.delete_job(job_id)
        
        if deleted:
            logger.info(f"Deleted job {job_id}")
            return {
                "deleted": True,
                "job_id": job_id,
            }
        else:
            raise BusinessError(
                message="Failed to delete job",
                details={"job_id": job_id}
            )
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_remaining_daily_quota(self, user_id: str) -> Dict[str, Any]:
        """
        Get the remaining daily job quota for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Quota information
        """
        daily_limit = settings.daily_job_limit
        jobs_today = self.job_repo.count_user_jobs_today(user_id)
        remaining = max(0, daily_limit - jobs_today)
        
        return {
            "daily_limit": daily_limit,
            "used_today": jobs_today,
            "remaining": remaining,
        }
    
    def can_create_job(self, user_id: str) -> bool:
        """
        Check if a user can create a new job.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user can create a job
        """
        quota = self.get_remaining_daily_quota(user_id)
        return quota["remaining"] > 0
    
    def get_active_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active (in-progress) jobs for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active jobs
        """
        return self.job_repo.get_active_jobs_for_user(user_id)


# Create a singleton instance for easy importing
def get_job_service() -> JobService:
    """
    Get a JobService instance.
    
    This is the recommended way to get a JobService instance,
    as it can be used as a FastAPI dependency.
    
    Returns:
        JobService instance
    """
    return JobService()
