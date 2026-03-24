"""
PartnerScout AI - Status Models

Pydantic models for status updates and transitions.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.constants import JobStatus, ProfileStatus


# =============================================================================
# Job Status Models
# =============================================================================

class UpdateJobStatusRequest(BaseModel):
    """Request model for updating job status."""
    
    status: JobStatus = Field(..., description="New status for the job")
    error_message: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Error message if status is 'failed'"
    )
    
    @model_validator(mode="after")
    def validate_error_message(self) -> "UpdateJobStatusRequest":
        """Ensure error_message is provided for failed status."""
        if self.status == JobStatus.FAILED and not self.error_message:
            raise ValueError("error_message is required when status is 'failed'")
        return self


class JobStatusResponse(BaseModel):
    """Response model for job status update."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: JobStatus
    previous_status: Optional[JobStatus] = None
    error_message: Optional[str] = None
    updated_at: datetime


class JobStatusHistory(BaseModel):
    """Job status change history entry."""
    
    job_id: UUID
    from_status: Optional[JobStatus] = None
    to_status: JobStatus
    changed_at: datetime
    changed_by: Optional[str] = None
    reason: Optional[str] = None


# =============================================================================
# Profile Status Models
# =============================================================================

class UpdateProfileStatusRequest(BaseModel):
    """Request model for updating profile status."""
    
    status: ProfileStatus = Field(..., description="New status for the profile")
    error_message: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Error message if status is 'failed'"
    )


class ProfileStatusResponse(BaseModel):
    """Response model for profile status update."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    status: ProfileStatus
    previous_status: Optional[ProfileStatus] = None
    updated_at: datetime


class BatchUpdateProfileStatusRequest(BaseModel):
    """Request model for batch profile status updates."""
    
    profile_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of profile IDs to update"
    )
    status: ProfileStatus = Field(..., description="New status for all profiles")
    error_message: Optional[str] = None


class BatchProfileStatusResponse(BaseModel):
    """Response model for batch profile status update."""
    
    updated: int = 0
    failed: int = 0
    results: List[ProfileStatusResponse] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Combined Status Models
# =============================================================================

class JobProgressStatus(BaseModel):
    """Current progress status for a job."""
    
    job_id: UUID
    status: JobStatus
    current_phase: str = Field(
        ...,
        description="Current phase: brand_analysis, discovery, scoring, completed"
    )
    
    # Progress metrics
    profiles_discovered: int = 0
    profiles_scored: int = 0
    discovery_limit: int = 50
    
    # Derived progress
    discovery_progress: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Discovery progress percentage"
    )
    scoring_progress: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Scoring progress percentage"
    )
    overall_progress: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Overall job progress percentage"
    )
    
    # Timing
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Status details
    error_message: Optional[str] = None
    last_activity: Optional[str] = None
    
    @classmethod
    def calculate_progress(
        cls,
        job_id: UUID,
        status: JobStatus,
        profiles_discovered: int,
        profiles_scored: int,
        discovery_limit: int,
        error_message: Optional[str] = None
    ) -> "JobProgressStatus":
        """Calculate progress status from job data."""
        
        # Determine current phase
        if status == JobStatus.PENDING:
            current_phase = "pending"
            overall = 0.0
        elif status == JobStatus.ANALYZING:
            current_phase = "brand_analysis"
            overall = 10.0
        elif status == JobStatus.DISCOVERING:
            current_phase = "discovery"
            overall = 20.0 + (min(profiles_discovered / discovery_limit, 1.0) * 30.0)
        elif status == JobStatus.SCORING:
            current_phase = "scoring"
            if profiles_discovered > 0:
                scoring_pct = profiles_scored / profiles_discovered
            else:
                scoring_pct = 0
            overall = 50.0 + (scoring_pct * 50.0)
        elif status == JobStatus.COMPLETED:
            current_phase = "completed"
            overall = 100.0
        elif status == JobStatus.FAILED:
            current_phase = "failed"
            overall = 0.0
        else:
            current_phase = "unknown"
            overall = 0.0
        
        # Calculate individual progress percentages
        discovery_progress = min((profiles_discovered / discovery_limit) * 100, 100) if discovery_limit > 0 else 0
        scoring_progress = (profiles_scored / profiles_discovered * 100) if profiles_discovered > 0 else 0
        
        return cls(
            job_id=job_id,
            status=status,
            current_phase=current_phase,
            profiles_discovered=profiles_discovered,
            profiles_scored=profiles_scored,
            discovery_limit=discovery_limit,
            discovery_progress=discovery_progress,
            scoring_progress=scoring_progress,
            overall_progress=overall,
            error_message=error_message,
        )


# =============================================================================
# Workflow Status Models (for orchestration pipeline)
# =============================================================================

class WorkflowStatusUpdate(BaseModel):
    """Status update from the orchestration pipeline."""
    
    job_id: UUID
    workflow_id: Optional[str] = None
    step: str = Field(..., description="Current workflow step")
    status: str = Field(..., description="Step status: started, completed, failed")
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStepResult(BaseModel):
    """Result from a workflow step."""
    
    job_id: UUID
    step: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    duration_seconds: Optional[float] = None
    next_step: Optional[str] = None


# =============================================================================
# Health & System Status
# =============================================================================

class HealthStatus(BaseModel):
    """System health status."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: Optional[str] = None
    
    # Component statuses
    database: str = "unknown"
    llm_service: str = "unknown"
    apify_service: str = "unknown"
    orchestration_service: str = "unknown"
    
    # Metrics
    active_jobs: int = 0
    pending_jobs: int = 0


class DetailedHealthStatus(HealthStatus):
    """Detailed system health status."""
    
    uptime_seconds: float = 0.0
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Recent activity
    jobs_completed_24h: int = 0
    profiles_scored_24h: int = 0
    errors_24h: int = 0
    
    # Rate limiting status
    api_requests_remaining: Optional[int] = None
    apify_credits_remaining: Optional[float] = None
