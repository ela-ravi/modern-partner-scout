"""
PartnerScout AI - Job Models

Pydantic models for discovery job request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import Defaults, JobStatus


# =============================================================================
# Request Models
# =============================================================================

class CreateJobRequest(BaseModel):
    """Request model for creating a new discovery job."""
    
    brand_description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the brand and its values"
    )
    reference_profiles: List[str] = Field(
        ...,
        min_length=Defaults.MIN_REFERENCE_PROFILES,
        max_length=Defaults.MAX_REFERENCE_PROFILES,
        description="List of Instagram profile URLs to use as reference"
    )
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional name for the discovery job"
    )
    follower_range_min: int = Field(
        default=Defaults.DEFAULT_MIN_FOLLOWERS,
        ge=Defaults.MIN_FOLLOWERS,
        le=Defaults.MAX_FOLLOWERS,
        description="Minimum followers for discovered profiles"
    )
    follower_range_max: int = Field(
        default=Defaults.DEFAULT_MAX_FOLLOWERS,
        ge=Defaults.MIN_FOLLOWERS,
        le=Defaults.MAX_FOLLOWERS,
        description="Maximum followers for discovered profiles"
    )
    discovery_limit: int = Field(
        default=Defaults.DEFAULT_DISCOVERY_LIMIT,
        ge=1,
        le=Defaults.MAX_DISCOVERY_LIMIT,
        description="Maximum number of profiles to discover"
    )
    
    # Enhancement fields (Item 5)
    keywords: List[str] = Field(
        default_factory=list,
        description="Target keywords for discovery (optional, AI will extract if empty)"
    )
    hashtags: List[str] = Field(
        default_factory=list,
        description="Target hashtags for discovery (optional, AI will extract if empty)"
    )
    min_score_threshold: int = Field(
        default=Defaults.DEFAULT_MIN_SCORE_THRESHOLD,
        ge=0,
        le=100,
        description="Minimum score threshold for profile filtering"
    )
    
    @field_validator("keywords", mode="before")
    @classmethod
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Clean and validate keywords - normalize to lowercase."""
        if not v:
            return []
        return [kw.strip().lower() for kw in v if kw and kw.strip()]
    
    @field_validator("hashtags", mode="before")
    @classmethod
    def validate_hashtags(cls, v: List[str]) -> List[str]:
        """Clean and normalize hashtags (ensure # prefix)."""
        if not v:
            return []
        normalized = []
        for tag in v:
            if not tag:
                continue
            tag = tag.strip().lower()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            normalized.append(tag)
        return normalized
    
    @field_validator("reference_profiles", mode="before")
    @classmethod
    def validate_reference_profiles(cls, v: List[str]) -> List[str]:
        """Validate and normalize Instagram profile URLs."""
        if not v:
            raise ValueError("At least 2 reference profiles are required")
        
        normalized = []
        for url in v:
            url = url.strip()
            # Basic validation - must look like an Instagram URL
            if not url:
                continue
            if "instagram.com" not in url.lower() and not url.startswith("@"):
                raise ValueError(f"Invalid Instagram URL: {url}")
            normalized.append(url)
        
        if len(normalized) < Defaults.MIN_REFERENCE_PROFILES:
            raise ValueError(
                f"At least {Defaults.MIN_REFERENCE_PROFILES} valid reference profiles are required"
            )
        
        return normalized
    
    @model_validator(mode="after")
    def validate_follower_range(self) -> "CreateJobRequest":
        """Validate that min followers is less than max followers."""
        if self.follower_range_min >= self.follower_range_max:
            raise ValueError("follower_range_min must be less than follower_range_max")
        return self


class UpdateJobRequest(BaseModel):
    """Request model for updating an existing discovery job."""
    
    name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Updated name for the discovery job"
    )
    brand_description: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=2000,
        description="Updated brand description"
    )
    
    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "UpdateJobRequest":
        """Ensure at least one field is being updated."""
        if self.name is None and self.brand_description is None:
            raise ValueError("At least one field must be provided for update")
        return self


# =============================================================================
# Response Models
# =============================================================================

class JobBase(BaseModel):
    """Base job model with common fields."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    brand_description: str
    reference_profiles: List[str]
    follower_range_min: int
    follower_range_max: int
    discovery_limit: int
    # Enhancement fields (Item 5)
    keywords: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    min_score_threshold: int = Field(default=Defaults.DEFAULT_MIN_SCORE_THRESHOLD)
    # Status fields
    status: JobStatus
    profiles_discovered: int = 0
    profiles_scored: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class Job(JobBase):
    """Full job response model."""
    pass


class JobSummary(BaseModel):
    """Condensed job information for list views."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: Optional[str] = None
    brand_description: str
    # Enhancement fields (Item 5)
    keywords: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    min_score_threshold: int = Field(default=Defaults.DEFAULT_MIN_SCORE_THRESHOLD)
    # Status fields
    status: JobStatus
    profiles_discovered: int = 0
    profiles_scored: int = 0
    created_at: datetime
    updated_at: datetime


class JobWithBrandDNA(JobBase):
    """Job with brand DNA relationship included."""
    
    brand_dna: Optional[Dict[str, Any]] = None


class JobWithProfiles(JobBase):
    """Job with profiles included for detailed view."""
    
    profiles: List[Dict[str, Any]] = Field(default_factory=list)
    brand_dna: Optional[Dict[str, Any]] = None


class JobAnalytics(BaseModel):
    """Analytics summary for a job."""
    
    model_config = ConfigDict(from_attributes=True)
    
    job_id: UUID
    total_profiles: int = 0
    new_profiles: int = 0
    processing_profiles: int = 0
    done_profiles: int = 0
    skipped_profiles: int = 0
    avg_score: Optional[float] = None
    max_score: Optional[int] = None
    min_score: Optional[int] = None
    profiles_with_email: int = 0


class JobListResponse(BaseModel):
    """Response model for listing jobs."""
    
    jobs: List[JobSummary]
    total: int = 0
    limit: int = Defaults.PAGE_SIZE
    offset: int = 0


class JobStartResponse(BaseModel):
    """Response model for starting a job."""
    
    status: str = "accepted"
    job_id: UUID
    message: str = "Discovery workflow initiated"


class JobDeleteResponse(BaseModel):
    """Response model for deleting a job."""
    
    deleted: bool = True
    job_id: UUID


class JobCancelResponse(BaseModel):
    """Response model for cancelling a job."""
    
    status: str = "cancelled"
    job_id: UUID
    cancelled_at: datetime
    message: str = "Discovery job cancelled successfully"
