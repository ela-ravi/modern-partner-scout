"""
PartnerScout AI - Pydantic Models Package

Centralized Pydantic models for request/response validation and data serialization.
"""

# =============================================================================
# Job Models
# =============================================================================
from app.models.job import (
    CreateJobRequest,
    UpdateJobRequest,
    JobBase,
    Job,
    JobSummary,
    JobWithBrandDNA,
    JobWithProfiles,
    JobAnalytics,
    JobListResponse,
    JobStartResponse,
    JobDeleteResponse,
)

# =============================================================================
# Profile Models
# =============================================================================
from app.models.profile import (
    # Score models
    ProfileScoreBase,
    ProfileScore,
    CreateProfileScoreRequest,
    # Contact models
    ProfileContactBase,
    ProfileContact,
    CreateProfileContactRequest,
    # Profile models
    ProfileBase,
    Profile,
    CreateProfileRequest,
    ProfileWithScore,
    ProfileWithContact,
    CompleteProfile,
    # List responses
    ProfileListResponse,
    CompleteProfileListResponse,
    # Batch operations
    BatchCreateProfilesRequest,
    BatchCreateProfilesResponse,
)

# =============================================================================
# Brand Models
# =============================================================================
from app.models.brand import (
    BrandDNABase,
    BrandDNA,
    CreateBrandDNARequest,
    UpdateBrandDNARequest,
    BrandDNASummary,
    BrandAnalysisResponse,
)

# =============================================================================
# Agent Models
# =============================================================================
from app.models.agent import (
    # Brand Analyzer
    BrandAnalyzerRequest,
    BrandAnalyzerResponse,
    # Discovery
    DiscoveryRequest,
    DiscoveryResponse,
    # Scorer
    ScorerRequest,
    ScoreDimension,
    ScorerResponse,
    BatchScorerRequest,
    BatchScorerResponse,
    # Common
    AgentError,
    AgentProgress,
)

# =============================================================================
# Email Models
# =============================================================================
from app.models.email import (
    EmailTone,
    GenerateEmailRequest,
    GeneratedEmail,
    GenerateEmailResponse,
    RegenerateEmailRequest,
    SendEmailRequest,
    SendEmailResponse,
    BatchSendEmailRequest,
    BatchSendEmailResponse,
    EmailTemplate,
    CreateEmailTemplateRequest,
    EmailHistory,
)

# =============================================================================
# Status Models
# =============================================================================
from app.models.status import (
    # Job status
    UpdateJobStatusRequest,
    JobStatusResponse,
    JobStatusHistory,
    # Profile status
    UpdateProfileStatusRequest,
    ProfileStatusResponse,
    BatchUpdateProfileStatusRequest,
    BatchProfileStatusResponse,
    # Progress
    JobProgressStatus,
    # Workflow
    WorkflowStatusUpdate,
    WorkflowStepResult,
    # Health
    HealthStatus,
    DetailedHealthStatus,
)


# =============================================================================
# All Exports
# =============================================================================
__all__ = [
    # Job Models
    "CreateJobRequest",
    "UpdateJobRequest",
    "JobBase",
    "Job",
    "JobSummary",
    "JobWithBrandDNA",
    "JobWithProfiles",
    "JobAnalytics",
    "JobListResponse",
    "JobStartResponse",
    "JobDeleteResponse",
    
    # Profile Models
    "ProfileScoreBase",
    "ProfileScore",
    "CreateProfileScoreRequest",
    "ProfileContactBase",
    "ProfileContact",
    "CreateProfileContactRequest",
    "ProfileBase",
    "Profile",
    "CreateProfileRequest",
    "ProfileWithScore",
    "ProfileWithContact",
    "CompleteProfile",
    "ProfileListResponse",
    "CompleteProfileListResponse",
    "BatchCreateProfilesRequest",
    "BatchCreateProfilesResponse",
    
    # Brand Models
    "BrandDNABase",
    "BrandDNA",
    "CreateBrandDNARequest",
    "UpdateBrandDNARequest",
    "BrandDNASummary",
    "BrandAnalysisResponse",
    
    # Agent Models
    "BrandAnalyzerRequest",
    "BrandAnalyzerResponse",
    "DiscoveryRequest",
    "DiscoveryResponse",
    "ScorerRequest",
    "ScoreDimension",
    "ScorerResponse",
    "BatchScorerRequest",
    "BatchScorerResponse",
    "AgentError",
    "AgentProgress",
    
    # Email Models
    "EmailTone",
    "GenerateEmailRequest",
    "GeneratedEmail",
    "GenerateEmailResponse",
    "RegenerateEmailRequest",
    "SendEmailRequest",
    "SendEmailResponse",
    "BatchSendEmailRequest",
    "BatchSendEmailResponse",
    "EmailTemplate",
    "CreateEmailTemplateRequest",
    "EmailHistory",
    
    # Status Models
    "UpdateJobStatusRequest",
    "JobStatusResponse",
    "JobStatusHistory",
    "UpdateProfileStatusRequest",
    "ProfileStatusResponse",
    "BatchUpdateProfileStatusRequest",
    "BatchProfileStatusResponse",
    "JobProgressStatus",
    "WorkflowStatusUpdate",
    "WorkflowStepResult",
    "HealthStatus",
    "DetailedHealthStatus",
]
