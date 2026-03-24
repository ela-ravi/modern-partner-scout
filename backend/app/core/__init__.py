"""
PartnerScout AI - Core Module

Provides centralized configuration, constants, exceptions, and settings
for the entire application.

Usage:
    from app.core.config import settings
    from app.core.constants import JobStatus, ErrorCodes
    from app.core.exceptions import NotFoundError, BusinessError
    from app.core.settings import get_scoring_config, get_agents_config
"""

from app.core.config import Settings, get_settings, settings
from app.core.constants import (
    Defaults,
    ErrorCodes,
    HttpStatus,
    JobStatus,
    ProfileStatus,
    Routes,
    ScoringDimensions,
    Tables,
    VALID_JOB_TRANSITIONS,
    VALID_PROFILE_TRANSITIONS,
    is_valid_job_transition,
    is_valid_profile_transition,
)
from app.core.exceptions import (
    AgentError,
    ApifyError,
    BrandDNANotFoundError,
    BusinessError,
    DailyLimitExceededError,
    EmailGenerationError,
    ExpiredTokenError,
    ExternalServiceError,
    ForbiddenError,
    InvalidServiceKeyError,
    InvalidStatusTransitionError,
    InvalidTokenError,
    InvalidURLError,
    JobAlreadyCompletedError,
    JobNotFoundError,
    JobNotStartableError,
    LLMError,
    NotFoundError,
    PartnerScoutError,
    ProfileLimitExceededError,
    ProfileNotFoundError,
    ScrapingError,
    ScoringError,
    SupabaseError,
    UnauthorizedError,
    ValidationError,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    "settings",
    # Constants
    "Defaults",
    "ErrorCodes",
    "HttpStatus",
    "JobStatus",
    "ProfileStatus",
    "Routes",
    "ScoringDimensions",
    "Tables",
    "VALID_JOB_TRANSITIONS",
    "VALID_PROFILE_TRANSITIONS",
    "is_valid_job_transition",
    "is_valid_profile_transition",
    # Exceptions
    "AgentError",
    "ApifyError",
    "BrandDNANotFoundError",
    "BusinessError",
    "DailyLimitExceededError",
    "EmailGenerationError",
    "ExpiredTokenError",
    "ExternalServiceError",
    "ForbiddenError",
    "InvalidServiceKeyError",
    "InvalidStatusTransitionError",
    "InvalidTokenError",
    "InvalidURLError",
    "JobAlreadyCompletedError",
    "JobNotFoundError",
    "JobNotStartableError",
    "LLMError",
    "NotFoundError",
    "PartnerScoutError",
    "ProfileLimitExceededError",
    "ProfileNotFoundError",
    "ScrapingError",
    "ScoringError",
    "SupabaseError",
    "UnauthorizedError",
    "ValidationError",
]
