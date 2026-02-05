"""
Profile-related Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator

from app.core.constants import ProfileStatus, MIN_SCORE, MAX_SCORE
from app.models.base import BaseEntity


class DiscoveredProfile(BaseEntity):
    """
    Discovered Instagram profile entity.
    """

    job_id: str
    username: str
    profile_url: str = ""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    profile_pic_url: Optional[str] = None
    is_verified: bool = False
    is_business: bool = False
    status: ProfileStatus = ProfileStatus.NEW
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    # Engagement metrics (optional)
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if not self.profile_url and self.username:
            self.profile_url = f"https://www.instagram.com/{self.username}/"

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: ProfileStatus | str) -> ProfileStatus:
        """Convert string to enum if needed."""
        if isinstance(v, str):
            return ProfileStatus(v)
        return v

    @computed_field(return_type=Optional[float])
    def engagement_rate(self) -> Optional[float]:
        """Calculate engagement rate as percentage."""
        if self.follower_count > 0 and self.avg_likes is not None:
            comments = self.avg_comments or 0
            return round((self.avg_likes + comments) / self.follower_count * 100, 2)
        return None


class ProfileCreate(BaseModel):
    """
    Request to create a discovered profile.
    """

    job_id: str
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    profile_pic_url: Optional[str] = None
    is_verified: bool = False
    is_business: bool = False


class ProfileUpdate(BaseModel):
    """
    Request to update a discovered profile.
    """

    status: Optional[ProfileStatus] = None
    bio: Optional[str] = None
    follower_count: Optional[int] = None
    is_verified: Optional[bool] = None
    is_business: Optional[bool] = None


class ProfileResponse(BaseModel):
    """
    Profile API response.
    """

    id: UUID
    job_id: str
    username: str
    profile_url: str
    display_name: Optional[str]
    bio: Optional[str]
    follower_count: int
    following_count: int
    post_count: int
    profile_pic_url: Optional[str]
    is_verified: bool
    is_business: bool
    status: ProfileStatus
    discovered_at: datetime
    engagement_rate: Optional[float] = None

    # Include score and contact if available
    score: Optional["ProfileScoreResponse"] = None
    contact: Optional["ProfileContactResponse"] = None


class ProfileScore(BaseEntity):
    """
    AI-generated score for a discovered profile.
    """

    profile_id: str
    overall_score: int = Field(ge=MIN_SCORE, le=MAX_SCORE)
    category_scores: Dict[str, int] = Field(default_factory=dict)
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scored_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("category_scores")
    @classmethod
    def validate_category_scores(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate all category scores are in range."""
        for category, score in v.items():
            if not MIN_SCORE <= score <= MAX_SCORE:
                raise ValueError(f"Score for {category} must be between {MIN_SCORE} and {MAX_SCORE}")
        return v


class ProfileScoreCreate(BaseModel):
    """
    Request to create a profile score.
    """

    profile_id: str
    overall_score: int = Field(ge=MIN_SCORE, le=MAX_SCORE)
    category_scores: Dict[str, int] = Field(default_factory=dict)
    reasoning: Optional[str] = None


class ProfileScoreResponse(BaseModel):
    """
    Profile score API response.
    """

    id: UUID
    profile_id: str
    overall_score: int
    category_scores: Dict[str, int]
    reasoning: Optional[str]
    scored_at: datetime


class ProfileContact(BaseEntity):
    """
    Extracted contact information for a profile.
    """

    profile_id: str
    email: Optional[EmailStr] = None
    source: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class ProfileContactCreate(BaseModel):
    """
    Request to create a profile contact.
    """

    profile_id: str
    email: EmailStr
    source: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ProfileContactResponse(BaseModel):
    """
    Profile contact API response.
    """

    id: UUID
    profile_id: str
    email: Optional[str]
    source: Optional[str]
    confidence: float
    extracted_at: datetime


# Update forward references
ProfileResponse.model_rebuild()
