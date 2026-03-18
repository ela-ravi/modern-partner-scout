"""
PartnerScout AI - Brand Models

Pydantic models for brand DNA (extracted brand characteristics).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# Brand DNA Models
# =============================================================================

class BrandDNABase(BaseModel):
    """Base model for brand DNA data."""
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="Extracted relevant hashtags from reference profiles"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Extracted brand keywords and themes"
    )
    visual_themes: List[str] = Field(
        default_factory=list,
        description="Identified visual themes and aesthetics"
    )
    content_pillars: List[str] = Field(
        default_factory=list,
        description="Main content pillars and topics"
    )
    target_audience_description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Description of the target audience"
    )
    
    @field_validator("hashtags", "keywords", "visual_themes", "content_pillars", mode="before")
    @classmethod
    def normalize_lists(cls, v: List[str]) -> List[str]:
        """Normalize list items (strip whitespace, remove empty strings)."""
        if not v:
            return []
        return [item.strip() for item in v if item and item.strip()]


class BrandDNA(BrandDNABase):
    """Full brand DNA response model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    job_id: UUID
    embedding_vector: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding for semantic similarity (1536 dims for OpenAI)"
    )
    created_at: datetime
    
    @field_validator("embedding_vector", mode="before")
    @classmethod
    def validate_embedding_vector(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding vector dimensions if provided."""
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("embedding_vector must be a list of floats")
        # OpenAI text-embedding-ada-002 uses 1536 dimensions
        if len(v) != 1536:
            raise ValueError(f"embedding_vector must have 1536 dimensions, got {len(v)}")
        return v


class CreateBrandDNARequest(BrandDNABase):
    """Request model for creating brand DNA."""
    
    job_id: UUID
    embedding_vector: Optional[List[float]] = None
    
    @field_validator("embedding_vector", mode="before")
    @classmethod
    def validate_embedding(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding vector dimensions if provided."""
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("embedding_vector must be a list of floats")
        if len(v) != 1536:
            raise ValueError(f"embedding_vector must have 1536 dimensions, got {len(v)}")
        return v


class UpdateBrandDNARequest(BaseModel):
    """Request model for updating brand DNA."""
    
    hashtags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    visual_themes: Optional[List[str]] = None
    content_pillars: Optional[List[str]] = None
    target_audience_description: Optional[str] = None
    embedding_vector: Optional[List[float]] = None


class BrandDNASummary(BaseModel):
    """Condensed brand DNA information."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    job_id: UUID
    hashtags_count: int = 0
    keywords_count: int = 0
    has_embedding: bool = False
    created_at: datetime
    
    @classmethod
    def from_brand_dna(cls, brand_dna: BrandDNA) -> "BrandDNASummary":
        """Create summary from full brand DNA."""
        return cls(
            id=brand_dna.id,
            job_id=brand_dna.job_id,
            hashtags_count=len(brand_dna.hashtags),
            keywords_count=len(brand_dna.keywords),
            has_embedding=brand_dna.embedding_vector is not None,
            created_at=brand_dna.created_at,
        )


# =============================================================================
# Brand Analysis Response
# =============================================================================

class BrandAnalysisResponse(BaseModel):
    """Response from brand analysis agent."""
    
    job_id: UUID
    brand_dna: BrandDNA
    reference_profiles_analyzed: int = 0
    analysis_duration_seconds: Optional[float] = None
    message: str = "Brand analysis completed successfully"
