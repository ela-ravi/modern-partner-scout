"""
Discovery job and Brand DNA Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, FieldValidationInfo, field_validator, HttpUrl

from app.core.constants import (
    DiscoveryStatus,
    MAX_REFERENCE_PROFILES,
    DEFAULT_DISCOVERY_LIMIT,
    MIN_FOLLOWER_COUNT,
    MAX_FOLLOWER_COUNT,
)
from app.models.base import BaseEntity


class DiscoverySettings(BaseModel):
    """
    Settings for a discovery job.
    """

    discovery_limit: int = Field(
        default=DEFAULT_DISCOVERY_LIMIT,
        ge=10,
        le=200,
        description="Maximum profiles to discover"
    )
    min_followers: int = Field(
        default=MIN_FOLLOWER_COUNT,
        ge=0,
        description="Minimum follower count"
    )
    max_followers: int = Field(
        default=MAX_FOLLOWER_COUNT,
        ge=0,
        description="Maximum follower count"
    )
    score_threshold: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Minimum score to include"
    )
    include_verified: bool = Field(
        default=True,
        description="Include verified accounts"
    )
    business_only: bool = Field(
        default=False,
        description="Only include business accounts"
    )

    @field_validator("max_followers")
    @classmethod
    def validate_max_followers(cls, v: int, info: FieldValidationInfo) -> int:
        """Ensure max_followers >= min_followers."""
        if "min_followers" in info.data and v < info.data["min_followers"]:
            raise ValueError("max_followers must be >= min_followers")
        return v


class DiscoveryJob(BaseEntity):
    """
    Discovery job entity.

    Represents a partner discovery session.
    """

    user_id: str
    status: DiscoveryStatus = DiscoveryStatus.PENDING
    reference_profiles: List[str] = Field(default_factory=list)
    settings: DiscoverySettings = Field(default_factory=DiscoverySettings)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: DiscoveryStatus | str) -> DiscoveryStatus:
        """Convert string to enum if needed."""
        if isinstance(v, str):
            return DiscoveryStatus(v)
        return v


class DiscoveryCreate(BaseModel):
    """
    Request to create a new discovery job.
    """

    reference_profiles: List[str] = Field(
        ...,
        min_length=1,
        max_length=MAX_REFERENCE_PROFILES,
        description="Instagram profile URLs or usernames to analyze"
    )
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Discovery settings"
    )

    @field_validator("reference_profiles")
    @classmethod
    def validate_profiles(cls, v: List[str]) -> List[str]:
        """Validate and normalize profile references."""
        if len(v) > MAX_REFERENCE_PROFILES:
            raise ValueError(f"Maximum {MAX_REFERENCE_PROFILES} reference profiles allowed")
        return v


class DiscoveryUpdate(BaseModel):
    """
    Request to update a discovery job.
    """

    status: Optional[DiscoveryStatus] = None
    settings: Optional[Dict[str, Any]] = None


class DiscoveryResponse(BaseModel):
    """
    Discovery job API response.
    """

    id: UUID
    user_id: str
    status: DiscoveryStatus
    reference_profiles: List[str]
    settings: DiscoverySettings
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed fields for response
    profile_count: int = 0
    scored_count: int = 0
    avg_score: Optional[float] = None


class BrandDNA(BaseEntity):
    """
    Brand DNA extracted from reference profiles.
    """

    job_id: str
    hashtags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    competitors: List[str] = Field(default_factory=list)
    embedding: List[float] = Field(default_factory=list)
    analysis: Dict[str, Any] = Field(default_factory=dict)


class BrandDNAResponse(BaseModel):
    """
    Brand DNA API response.
    """

    id: UUID
    job_id: str
    hashtags: List[str]
    keywords: List[str]
    competitors: List[str]
    analysis: Dict[str, Any]
    created_at: datetime
