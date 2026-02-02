"""
PartnerScout AI - Agent Models

Pydantic models for AI agent request/response handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Brand Analyzer Agent Models
# =============================================================================

class BrandAnalyzerRequest(BaseModel):
    """Request model for Brand Analyzer Agent."""
    
    job_id: UUID = Field(..., description="ID of the discovery job")
    
    # Optional overrides
    max_posts_per_profile: int = Field(
        default=20,
        ge=5,
        le=50,
        description="Maximum posts to analyze per reference profile"
    )


class BrandAnalyzerResponse(BaseModel):
    """Response model from Brand Analyzer Agent."""
    
    job_id: UUID
    hashtags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    visual_themes: List[str] = Field(default_factory=list)
    content_pillars: List[str] = Field(default_factory=list)
    target_audience_description: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    profiles_analyzed: int = 0
    posts_analyzed: int = 0
    analysis_duration_seconds: Optional[float] = None


# =============================================================================
# Discovery Agent Models
# =============================================================================

class DiscoveryRequest(BaseModel):
    """Request model for Discovery Agent."""
    
    job_id: UUID = Field(..., description="ID of the discovery job")
    hashtags: List[str] = Field(
        ...,
        min_length=1,
        description="Hashtags to search for"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to filter by"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum profiles to discover"
    )
    follower_min: int = Field(
        default=5000,
        ge=1000,
        description="Minimum follower count"
    )
    follower_max: int = Field(
        default=500000,
        le=10000000,
        description="Maximum follower count"
    )
    
    @field_validator("hashtags", mode="before")
    @classmethod
    def normalize_hashtags(cls, v: List[str]) -> List[str]:
        """Normalize hashtags (ensure # prefix)."""
        if not v:
            raise ValueError("At least one hashtag is required")
        
        normalized = []
        for tag in v:
            tag = tag.strip()
            if not tag:
                continue
            if not tag.startswith("#"):
                tag = f"#{tag}"
            normalized.append(tag)
        
        return normalized


class DiscoveryResponse(BaseModel):
    """Response model from Discovery Agent."""
    
    job_id: UUID
    profiles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Discovered profile data"
    )
    total_discovered: int = 0
    deduplicated: int = 0
    filtered_out: int = 0
    discovery_duration_seconds: Optional[float] = None


# =============================================================================
# Scorer Agent Models
# =============================================================================

class ScorerRequest(BaseModel):
    """Request model for Scorer Agent."""
    
    profile_id: UUID = Field(..., description="ID of the profile to score")
    job_id: UUID = Field(..., description="ID of the discovery job")
    
    # Optional: include full data to avoid DB lookups
    profile_data: Optional[Dict[str, Any]] = None
    brand_dna: Optional[Dict[str, Any]] = None


class ScoreDimension(BaseModel):
    """Individual scoring dimension result."""
    
    name: str
    score: int = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    reasoning: str = ""


class ScorerResponse(BaseModel):
    """Response model from Scorer Agent."""
    
    profile_id: UUID
    job_id: UUID
    
    # Individual dimension scores
    visual_aesthetic_match: int = Field(..., ge=0, le=100)
    content_theme_alignment: int = Field(..., ge=0, le=100)
    engagement_rate_score: int = Field(..., ge=0, le=100)
    follower_quality: int = Field(..., ge=0, le=100)
    business_indicators: int = Field(..., ge=0, le=100)
    activity_recency: int = Field(..., ge=0, le=100)
    
    # Final score and recommendation
    final_score: int = Field(..., ge=0, le=100)
    recommendation: str = Field(
        ...,
        description="One of: highly_recommended, recommended, consider, not_recommended"
    )
    
    # Detailed reasoning
    reasoning: Dict[str, Any] = Field(default_factory=dict)
    dimensions: List[ScoreDimension] = Field(default_factory=list)
    
    # Fake detection
    is_fake_suspected: bool = False
    fake_indicators: List[str] = Field(default_factory=list)
    
    # Contact extraction
    contact: Optional[Dict[str, Any]] = None
    
    scoring_duration_seconds: Optional[float] = None


class BatchScorerRequest(BaseModel):
    """Request model for batch scoring."""
    
    job_id: UUID = Field(..., description="ID of the discovery job")
    profile_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of profile IDs to score"
    )


class BatchScorerResponse(BaseModel):
    """Response model for batch scoring."""
    
    job_id: UUID
    total_requested: int = 0
    total_scored: int = 0
    total_failed: int = 0
    results: List[ScorerResponse] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    batch_duration_seconds: Optional[float] = None


# =============================================================================
# Common Agent Models
# =============================================================================

class AgentError(BaseModel):
    """Error response from an agent."""
    
    agent: str = Field(..., description="Name of the agent that failed")
    job_id: Optional[UUID] = None
    profile_id: Optional[UUID] = None
    error_code: str
    error_message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentProgress(BaseModel):
    """Progress update from an agent."""
    
    agent: str
    job_id: UUID
    current_step: str
    total_steps: int = 0
    completed_steps: int = 0
    percentage: float = 0.0
    message: Optional[str] = None
    started_at: datetime
    estimated_completion: Optional[datetime] = None
