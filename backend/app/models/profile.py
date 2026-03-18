"""
PartnerScout AI - Profile Models

Pydantic models for discovered profiles, scores, and contacts.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import Defaults, ProfileStatus, ScoringDimensions


# =============================================================================
# Score Models
# =============================================================================

class ProfileScoreBase(BaseModel):
    """Base model for profile scoring data."""
    
    visual_aesthetic_match: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Visual aesthetic match score (0-100)"
    )
    content_theme_alignment: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Content theme alignment score (0-100)"
    )
    engagement_rate_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Engagement rate score (0-100)"
    )
    follower_quality: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Follower quality score (0-100)"
    )
    business_indicators: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Business indicators score (0-100)"
    )
    activity_recency: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Activity recency score (0-100)"
    )
    final_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Final weighted score (0-100)"
    )


class ProfileScore(ProfileScoreBase):
    """Full profile score response model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    profile_id: UUID
    recommendation: Optional[str] = Field(
        default=None,
        description="AI recommendation: highly_recommended, recommended, consider, not_recommended"
    )
    reasoning: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed AI reasoning for each dimension"
    )
    is_fake_suspected: bool = False
    created_at: datetime


class CreateProfileScoreRequest(ProfileScoreBase):
    """Request model for creating a profile score."""
    
    profile_id: UUID
    recommendation: Optional[str] = None
    reasoning: Dict[str, Any] = Field(default_factory=dict)
    is_fake_suspected: bool = False
    
    @field_validator("recommendation")
    @classmethod
    def validate_recommendation(cls, v: Optional[str]) -> Optional[str]:
        """Validate recommendation value."""
        valid_values = {"highly_recommended", "recommended", "consider", "not_recommended"}
        if v is not None and v not in valid_values:
            raise ValueError(f"recommendation must be one of: {valid_values}")
        return v


# =============================================================================
# Contact Models
# =============================================================================

class ProfileContactBase(BaseModel):
    """Base model for profile contact information."""
    
    email: Optional[str] = None
    email_source: Optional[str] = Field(
        default=None,
        description="Source of email: bio, business_email, website, extracted"
    )
    phone: Optional[str] = None
    website: Optional[str] = None
    other_contacts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional contact methods (linktree, twitter, etc.)"
    )


class ProfileContact(ProfileContactBase):
    """Full profile contact response model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    profile_id: UUID
    created_at: datetime


class CreateProfileContactRequest(ProfileContactBase):
    """Request model for creating profile contact."""
    
    profile_id: UUID
    
    @field_validator("email_source")
    @classmethod
    def validate_email_source(cls, v: Optional[str]) -> Optional[str]:
        """Validate email source value."""
        valid_sources = {"bio", "business_email", "website", "extracted"}
        if v is not None and v not in valid_sources:
            raise ValueError(f"email_source must be one of: {valid_sources}")
        return v


# =============================================================================
# Profile Models
# =============================================================================

class ProfileBase(BaseModel):
    """Base model for discovered profiles."""
    
    instagram_url: str = Field(..., description="Full Instagram profile URL")
    username: str = Field(..., description="Instagram username")
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = Field(default=0, ge=0)
    following_count: Optional[int] = Field(default=None, ge=0)
    posts_count: Optional[int] = Field(default=None, ge=0)
    engagement_rate: Optional[Decimal] = Field(
        default=None,
        description="Engagement rate as decimal (e.g., 3.5 for 3.5%)"
    )
    following_ratio: Optional[Decimal] = Field(
        default=None,
        description="Following / Followers ratio for fake detection"
    )
    is_verified: bool = False
    is_business_account: Optional[bool] = None
    external_url: Optional[str] = None
    business_email: Optional[str] = None
    business_category: Optional[str] = None


class Profile(ProfileBase):
    """Full profile response model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    job_id: UUID
    status: ProfileStatus = ProfileStatus.NEW
    created_at: datetime


class CreateProfileRequest(ProfileBase):
    """Request model for creating a profile."""
    
    job_id: UUID
    status: ProfileStatus = ProfileStatus.NEW


class ProfileWithScore(Profile):
    """Profile with score included."""
    
    score: Optional[ProfileScore] = None


class ProfileWithContact(Profile):
    """Profile with contact included."""
    
    contact: Optional[ProfileContact] = None


class CompleteProfile(Profile):
    """Complete profile with score and contact information."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # Bookmark
    is_bookmarked: bool = False

    # Flatten score fields for convenience
    final_score: Optional[int] = None
    visual_aesthetic_match: Optional[int] = None
    content_theme_alignment: Optional[int] = None
    engagement_rate_score: Optional[int] = None
    follower_quality: Optional[int] = None
    business_indicators_score: Optional[int] = Field(default=None, alias="business_indicators")
    activity_recency: Optional[int] = None
    recommendation: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    is_fake_suspected: bool = False
    
    # Contact fields
    contact_email: Optional[str] = None
    email_source: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_website: Optional[str] = None


# =============================================================================
# List Response Models
# =============================================================================

class ProfileListResponse(BaseModel):
    """Response model for listing profiles."""
    
    profiles: List[Profile]
    total: int = 0
    limit: int = Defaults.PAGE_SIZE
    offset: int = 0


class CompleteProfileListResponse(BaseModel):
    """Response model for listing complete profiles."""
    
    profiles: List[CompleteProfile]
    total: int = 0
    limit: int = Defaults.PAGE_SIZE
    offset: int = 0


# =============================================================================
# Batch Operations
# =============================================================================

class BookmarkResponse(BaseModel):
    """Response model for bookmark toggle."""

    id: UUID
    is_bookmarked: bool


class BatchCreateProfilesRequest(BaseModel):
    """Request model for creating multiple profiles."""
    
    job_id: UUID
    profiles: List[ProfileBase] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of profiles to create (max 100)"
    )


class BatchCreateProfilesResponse(BaseModel):
    """Response model for batch profile creation."""
    
    created: int = 0
    duplicates: int = 0
    errors: int = 0
    profile_ids: List[UUID] = Field(default_factory=list)
