"""
PartnerScout AI - Ownership Guards

Implements resource ownership guards for securing access to user-specific resources.
- JobOwnerGuard: Ensures users can only access their own jobs
- ProfileOwnerGuard: Ensures users can only access profiles from their jobs
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, Path, Request

from app.core.constants import ErrorCodes, HttpStatus
from app.core.exceptions import ForbiddenError, JobNotFoundError, ProfileNotFoundError
from app.db import get_db, SupabaseClient
from app.guards.auth import (
    UserContext,
    ServiceContext,
    get_current_user,
    get_user_or_service,
)
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository


# =============================================================================
# Base Ownership Guard
# =============================================================================

class OwnershipGuard(ABC):
    """
    Abstract base class for resource ownership guards.
    
    Ensures that users can only access resources they own.
    Services (N8N) bypass ownership checks.
    """
    
    def __init__(self, db: Optional[SupabaseClient] = None):
        """
        Initialize the ownership guard.
        
        Args:
            db: Optional database client (uses default if not provided)
        """
        self.db = db or get_db()
    
    @abstractmethod
    def check_ownership(
        self,
        resource_id: str,
        user_id: str,
    ) -> bool:
        """
        Check if a user owns a specific resource.
        
        Args:
            resource_id: The ID of the resource
            user_id: The ID of the user
            
        Returns:
            True if the user owns the resource
            
        Raises:
            NotFoundError: If the resource doesn't exist
        """
        pass
    
    @abstractmethod
    def get_resource(self, resource_id: str) -> dict:
        """
        Get the resource by ID.
        
        Args:
            resource_id: The ID of the resource
            
        Returns:
            The resource data
            
        Raises:
            NotFoundError: If the resource doesn't exist
        """
        pass
    
    def verify_ownership(
        self,
        resource_id: str,
        context: Union[UserContext, ServiceContext],
    ) -> dict:
        """
        Verify that the context has access to the resource.
        
        Services always have access.
        Users must own the resource.
        
        Args:
            resource_id: The ID of the resource
            context: The authentication context
            
        Returns:
            The resource data if access is allowed
            
        Raises:
            ForbiddenError: If the user doesn't own the resource
            NotFoundError: If the resource doesn't exist
        """
        # Services bypass ownership checks
        if isinstance(context, ServiceContext):
            return self.get_resource(resource_id)
        
        # For users, check ownership
        if not self.check_ownership(resource_id, context.user_id):
            raise ForbiddenError(
                message=f"You do not have access to this {self.resource_type}",
                resource_type=self.resource_type,
                resource_id=resource_id,
            )
        
        return self.get_resource(resource_id)
    
    @property
    @abstractmethod
    def resource_type(self) -> str:
        """Return the type of resource being guarded."""
        pass


# =============================================================================
# Job Ownership Guard
# =============================================================================

class JobOwnerGuard(OwnershipGuard):
    """
    Guard for verifying job ownership.
    
    Ensures that users can only access discovery jobs they created.
    """
    
    def __init__(self, db: Optional[SupabaseClient] = None):
        super().__init__(db)
        self._repo = JobRepository(self.db)
    
    @property
    def resource_type(self) -> str:
        return "job"
    
    def get_resource(self, resource_id: str) -> dict:
        """
        Get a job by ID.
        
        Args:
            resource_id: The job UUID
            
        Returns:
            The job data
            
        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        return self._repo.get_by_id(resource_id)
    
    def check_ownership(
        self,
        resource_id: str,
        user_id: str,
    ) -> bool:
        """
        Check if a user owns a specific job.
        
        Args:
            resource_id: The job UUID
            user_id: The user ID
            
        Returns:
            True if the user owns the job
            
        Raises:
            JobNotFoundError: If the job doesn't exist
        """
        job = self._repo.get_by_id(resource_id)
        return job.get("user_id") == user_id
    
    def get_job_for_user(
        self,
        job_id: str,
        context: Union[UserContext, ServiceContext],
    ) -> dict:
        """
        Get a job if the user has access to it.
        
        Args:
            job_id: The job UUID
            context: The authentication context
            
        Returns:
            The job data
            
        Raises:
            ForbiddenError: If the user doesn't own the job
            JobNotFoundError: If the job doesn't exist
        """
        return self.verify_ownership(job_id, context)


# =============================================================================
# Profile Ownership Guard
# =============================================================================

class ProfileOwnerGuard(OwnershipGuard):
    """
    Guard for verifying profile ownership.
    
    Profiles belong to jobs, so ownership is checked through the job.
    A user owns a profile if they own the job that the profile belongs to.
    """
    
    def __init__(self, db: Optional[SupabaseClient] = None):
        super().__init__(db)
        self._profile_repo = ProfileRepository(self.db)
        self._job_repo = JobRepository(self.db)
    
    @property
    def resource_type(self) -> str:
        return "profile"
    
    def get_resource(self, resource_id: str) -> dict:
        """
        Get a profile by ID.
        
        Args:
            resource_id: The profile UUID
            
        Returns:
            The profile data
            
        Raises:
            ProfileNotFoundError: If the profile doesn't exist
        """
        return self._profile_repo.get_by_id(resource_id)
    
    def check_ownership(
        self,
        resource_id: str,
        user_id: str,
    ) -> bool:
        """
        Check if a user owns a specific profile (via job ownership).
        
        Args:
            resource_id: The profile UUID
            user_id: The user ID
            
        Returns:
            True if the user owns the profile's job
            
        Raises:
            ProfileNotFoundError: If the profile doesn't exist
            JobNotFoundError: If the profile's job doesn't exist
        """
        profile = self._profile_repo.get_by_id(resource_id)
        job_id = profile.get("job_id")
        
        if not job_id:
            # Profile has no job_id, shouldn't happen but handle gracefully
            return False
        
        # Check if the user owns the job
        job = self._job_repo.get_by_id(job_id)
        return job.get("user_id") == user_id
    
    def get_profile_for_user(
        self,
        profile_id: str,
        context: Union[UserContext, ServiceContext],
    ) -> dict:
        """
        Get a profile if the user has access to it.
        
        Args:
            profile_id: The profile UUID
            context: The authentication context
            
        Returns:
            The profile data
            
        Raises:
            ForbiddenError: If the user doesn't own the profile's job
            ProfileNotFoundError: If the profile doesn't exist
        """
        return self.verify_ownership(profile_id, context)
    
    def check_profile_job_ownership(
        self,
        profile_id: str,
        job_id: str,
        context: Union[UserContext, ServiceContext],
    ) -> tuple:
        """
        Verify that a profile belongs to a job and the user owns both.
        
        Args:
            profile_id: The profile UUID
            job_id: The job UUID
            context: The authentication context
            
        Returns:
            Tuple of (profile, job) data
            
        Raises:
            ForbiddenError: If the user doesn't own the job or profile mismatch
            ProfileNotFoundError: If the profile doesn't exist
            JobNotFoundError: If the job doesn't exist
        """
        profile = self._profile_repo.get_by_id(profile_id)
        
        # Verify profile belongs to the specified job
        if profile.get("job_id") != job_id:
            raise ForbiddenError(
                message="Profile does not belong to the specified job",
                resource_type="profile",
                resource_id=profile_id,
                details={"expected_job_id": job_id, "actual_job_id": profile.get("job_id")},
            )
        
        # Services bypass ownership checks
        if isinstance(context, ServiceContext):
            job = self._job_repo.get_by_id(job_id)
            return profile, job
        
        # Check job ownership for users
        job = self._job_repo.get_by_id(job_id)
        if job.get("user_id") != context.user_id:
            raise ForbiddenError(
                message="You do not have access to this job",
                resource_type="job",
                resource_id=job_id,
            )
        
        return profile, job


# =============================================================================
# FastAPI Dependencies
# =============================================================================

# Guard instances (singletons)
_job_owner_guard: Optional[JobOwnerGuard] = None
_profile_owner_guard: Optional[ProfileOwnerGuard] = None


def _get_job_owner_guard() -> JobOwnerGuard:
    """Get or create the job owner guard singleton."""
    global _job_owner_guard
    if _job_owner_guard is None:
        _job_owner_guard = JobOwnerGuard()
    return _job_owner_guard


def _get_profile_owner_guard() -> ProfileOwnerGuard:
    """Get or create the profile owner guard singleton."""
    global _profile_owner_guard
    if _profile_owner_guard is None:
        _profile_owner_guard = ProfileOwnerGuard()
    return _profile_owner_guard


async def verify_job_owner(
    job_id: str = Path(..., description="The job UUID"),
    auth: tuple = Depends(get_user_or_service),
) -> dict:
    """
    FastAPI dependency to verify job ownership.
    
    Usage:
        @app.get("/api/jobs/{job_id}")
        async def get_job(job: dict = Depends(verify_job_owner)):
            return job
    
    Args:
        job_id: The job UUID from the path
        auth: The authentication context (user or service)
        
    Returns:
        The job data if access is allowed
        
    Raises:
        HTTPException(403): If the user doesn't own the job
        HTTPException(404): If the job doesn't exist
    """
    context, auth_type = auth
    guard = _get_job_owner_guard()
    
    try:
        return guard.get_job_for_user(job_id, context)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def verify_job_owner_user_only(
    job_id: str = Path(..., description="The job UUID"),
    user: UserContext = Depends(get_current_user),
) -> dict:
    """
    FastAPI dependency to verify job ownership (user authentication only).
    
    Unlike verify_job_owner, this only accepts user JWT authentication,
    not service keys. Use this for user-facing endpoints.
    
    Args:
        job_id: The job UUID from the path
        user: The authenticated user context
        
    Returns:
        The job data if access is allowed
        
    Raises:
        HTTPException(401): If not authenticated
        HTTPException(403): If the user doesn't own the job
        HTTPException(404): If the job doesn't exist
    """
    guard = _get_job_owner_guard()
    
    try:
        return guard.get_job_for_user(job_id, user)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except JobNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def verify_profile_owner(
    profile_id: str = Path(..., description="The profile UUID"),
    auth: tuple = Depends(get_user_or_service),
) -> dict:
    """
    FastAPI dependency to verify profile ownership.
    
    Usage:
        @app.get("/api/profiles/{profile_id}")
        async def get_profile(profile: dict = Depends(verify_profile_owner)):
            return profile
    
    Args:
        profile_id: The profile UUID from the path
        auth: The authentication context (user or service)
        
    Returns:
        The profile data if access is allowed
        
    Raises:
        HTTPException(403): If the user doesn't own the profile's job
        HTTPException(404): If the profile doesn't exist
    """
    context, auth_type = auth
    guard = _get_profile_owner_guard()
    
    try:
        return guard.get_profile_for_user(profile_id, context)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except ProfileNotFoundError as e:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except JobNotFoundError as e:
        # Profile exists but job doesn't - shouldn't happen normally
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def verify_profile_owner_user_only(
    profile_id: str = Path(..., description="The profile UUID"),
    user: UserContext = Depends(get_current_user),
) -> dict:
    """
    FastAPI dependency to verify profile ownership (user authentication only).
    
    Args:
        profile_id: The profile UUID from the path
        user: The authenticated user context
        
    Returns:
        The profile data if access is allowed
        
    Raises:
        HTTPException(401): If not authenticated
        HTTPException(403): If the user doesn't own the profile's job
        HTTPException(404): If the profile doesn't exist
    """
    guard = _get_profile_owner_guard()
    
    try:
        return guard.get_profile_for_user(profile_id, user)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=HttpStatus.FORBIDDEN,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
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


# =============================================================================
# Utility Functions
# =============================================================================

def reset_guards() -> None:
    """
    Reset guard singletons.
    
    Useful for testing to ensure fresh instances.
    """
    global _job_owner_guard, _profile_owner_guard
    _job_owner_guard = None
    _profile_owner_guard = None
