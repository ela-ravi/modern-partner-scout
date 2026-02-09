"""
PartnerScout AI - Profile Routes

API endpoints for managing discovered profiles within jobs.

Endpoints:
- GET    /api/jobs/{job_id}/profiles           - List profiles for a job
- GET    /api/jobs/{job_id}/profiles/{profile_id} - Get a specific profile
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from app.core.constants import HttpStatus, Defaults, ProfileStatus
from app.core.exceptions import JobNotFoundError, ProfileNotFoundError
from app.guards.auth import UserContext, get_current_user
from app.guards.ownership import verify_job_owner_user_only
from app.repositories import ProfileRepository, JobRepository


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Response Models
# =============================================================================

class ProfileResponse(BaseModel):
    """Profile data matching frontend expectations."""
    id: str
    job_id: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_pic_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    engagement_rate: float = 0.0
    email: Optional[str] = None
    website: Optional[str] = None
    status: str = "new"
    score: Optional[dict] = None
    is_bookmarked: bool = False
    created_at: str
    updated_at: Optional[str] = None


class ProfilesListResponse(BaseModel):
    """Paginated profiles response matching frontend expectations."""
    profiles: list[ProfileResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# =============================================================================
# Helper Functions
# =============================================================================

def _format_reasoning(reasoning_data) -> str | None:
    """Convert reasoning dict/object to a readable string."""
    if reasoning_data is None:
        return None
    
    # If already a string, return as-is
    if isinstance(reasoning_data, str):
        return reasoning_data
    
    # If it's a dict, format key insights into a readable summary
    if isinstance(reasoning_data, dict):
        # Look for common reasoning fields and build a summary
        parts = []
        
        # Priority fields to include in summary
        priority_keys = [
            "visual_aesthetic_match",
            "content_theme_alignment",
            "engagement_rate_score",
            "follower_quality",
            "business_indicators",
        ]
        
        for key in priority_keys:
            if key in reasoning_data and reasoning_data[key]:
                # Clean up the key name for display
                clean_key = key.replace("_", " ").title()
                parts.append(f"{clean_key}: {reasoning_data[key]}")
        
        # If no priority fields found, use any available
        if not parts:
            for key, value in reasoning_data.items():
                if value and isinstance(value, str):
                    parts.append(value)
                    if len(parts) >= 3:
                        break
        
        return ". ".join(parts) if parts else None
    
    return None


def _transform_profile(profile_data: dict) -> ProfileResponse:
    """Transform database profile to API response format."""
    # Build score object if score data exists
    score = None
    if profile_data.get("final_score") is not None:
        score = {
            "overall_score": profile_data.get("final_score", 0),
            "engagement": profile_data.get("engagement_score"),
            "relevance": profile_data.get("relevance_score"),
            "authenticity": profile_data.get("authenticity_score"),
            "reach": profile_data.get("reach_score"),
            "content_quality": profile_data.get("content_quality_score"),
            "brand_alignment": profile_data.get("brand_fit_score"),
            "reasoning": _format_reasoning(profile_data.get("reasoning")),
        }
    
    return ProfileResponse(
        id=str(profile_data.get("id", "")),
        job_id=str(profile_data.get("job_id", "")),
        username=profile_data.get("username", "") or "",
        full_name=profile_data.get("full_name"),
        bio=profile_data.get("bio"),
        profile_pic_url=profile_data.get("profile_picture_url"),
        follower_count=profile_data.get("followers_count") or 0,
        following_count=profile_data.get("following_count") or 0,
        post_count=profile_data.get("posts_count") or 0,
        engagement_rate=profile_data.get("engagement_rate") or 0.0,
        email=profile_data.get("contact_email") or profile_data.get("business_email"),
        website=profile_data.get("external_url") or profile_data.get("contact_website"),
        status=profile_data.get("status") or "new",
        score=score,
        is_bookmarked=profile_data.get("is_bookmarked") or False,
        created_at=str(profile_data.get("created_at", "")),
        updated_at=str(profile_data.get("updated_at")) if profile_data.get("updated_at") else None,
    )


# =============================================================================
# Profile Endpoints
# =============================================================================

@router.get(
    "/jobs/{job_id}/profiles",
    response_model=ProfilesListResponse,
    summary="List profiles for a job",
    description="Retrieve paginated profiles for a discovery job with optional filtering.",
    responses={
        200: {"description": "List of profiles"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Job not found"},
    }
)
async def list_profiles(
    job_id: str = Path(..., description="The job UUID"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by profile status"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum score filter"),
    has_email: Optional[bool] = Query(None, description="Filter profiles with email"),
    is_bookmarked: Optional[bool] = Query(None, description="Filter bookmarked profiles"),
    sort_by: Optional[str] = Query("score", description="Sort field: score, created_at, follower_count, engagement_rate"),
    sort_direction: Optional[str] = Query("desc", description="Sort direction: asc or desc"),
    user: UserContext = Depends(get_current_user),
    job: dict = Depends(verify_job_owner_user_only),
) -> ProfilesListResponse:
    """
    List profiles for a discovery job.
    
    Returns paginated profiles with optional filtering by status, score, and email availability.
    Profiles include their scores and contact information.
    """
    profile_repo = ProfileRepository()
    
    # Calculate offset from page
    offset = (page - 1) * page_size
    
    # Get profiles with scores
    profiles = profile_repo.list_by_job_with_scores(
        job_id=job_id,
        min_score=min_score,
        status=status,
        limit=page_size,
        offset=offset,
    )
    
    # Apply additional filters that aren't in the repository method
    if has_email is not None:
        if has_email:
            profiles = [p for p in profiles if p.get("contact_email") or p.get("business_email")]
        else:
            profiles = [p for p in profiles if not p.get("contact_email") and not p.get("business_email")]
    
    if is_bookmarked is not None:
        profiles = [p for p in profiles if p.get("is_bookmarked", False) == is_bookmarked]
    
    # Get total count for pagination
    total = profile_repo.count_by_job(job_id, status=status)
    
    # Transform to response format
    profile_responses = [_transform_profile(p) for p in profiles]
    
    has_more = (page * page_size) < total
    
    return ProfilesListResponse(
        profiles=profile_responses,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.get(
    "/jobs/{job_id}/profiles/{profile_id}",
    response_model=ProfileResponse,
    summary="Get a specific profile",
    description="Retrieve detailed information for a specific profile.",
    responses={
        200: {"description": "Profile details"},
        401: {"description": "Authentication required"},
        403: {"description": "Access denied - not the owner"},
        404: {"description": "Profile not found"},
    }
)
async def get_profile(
    job_id: str = Path(..., description="The job UUID"),
    profile_id: str = Path(..., description="The profile UUID"),
    user: UserContext = Depends(get_current_user),
    job: dict = Depends(verify_job_owner_user_only),
) -> ProfileResponse:
    """
    Get detailed information for a specific profile.
    
    Returns the profile with score breakdown and contact information.
    """
    profile_repo = ProfileRepository()
    
    # Get profile with score data
    profile = profile_repo.get_profile_with_score(profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": "PROFILE_NOT_FOUND", "message": f"Profile not found: {profile_id}"}}
        )
    
    # Verify profile belongs to the job
    if str(profile.get("job_id")) != job_id:
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={"error": {"code": "PROFILE_NOT_FOUND", "message": f"Profile not found in this job"}}
        )
    
    return _transform_profile(profile)
