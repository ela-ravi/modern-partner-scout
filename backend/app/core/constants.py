"""
PartnerScout AI - Constants and Enumerations

Centralized definitions for HTTP status codes, error codes, status enums,
valid state transitions, table names, route paths, and default values.
"""

from enum import Enum
from typing import Dict, FrozenSet


# =============================================================================
# HTTP Status Codes
# =============================================================================

class HttpStatus:
    """HTTP status code constants for consistent API responses."""
    
    # Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client Errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # Server Errors
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


# =============================================================================
# Error Codes
# =============================================================================

class ErrorCodes:
    """Application-specific error codes for client handling."""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    EXPIRED_TOKEN = "EXPIRED_TOKEN"
    INVALID_SERVICE_KEY = "INVALID_SERVICE_KEY"
    
    # Resource Errors
    NOT_FOUND = "NOT_FOUND"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    BRAND_DNA_NOT_FOUND = "BRAND_DNA_NOT_FOUND"
    
    # Validation Errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    INVALID_STATUS = "INVALID_STATUS"
    INVALID_URL = "INVALID_URL"
    
    # Business Logic Errors
    DAILY_LIMIT_EXCEEDED = "DAILY_LIMIT_EXCEEDED"
    PROFILE_LIMIT_EXCEEDED = "PROFILE_LIMIT_EXCEEDED"
    JOB_ALREADY_STARTED = "JOB_ALREADY_STARTED"
    JOB_NOT_STARTABLE = "JOB_NOT_STARTABLE"
    JOB_ALREADY_COMPLETED = "JOB_ALREADY_COMPLETED"
    
    # AI Agent Errors
    AGENT_ERROR = "AGENT_ERROR"
    LLM_ERROR = "LLM_ERROR"
    SCRAPING_ERROR = "SCRAPING_ERROR"
    SCORING_ERROR = "SCORING_ERROR"
    EMAIL_GENERATION_ERROR = "EMAIL_GENERATION_ERROR"
    
    # External Service Errors
    SUPABASE_ERROR = "SUPABASE_ERROR"
    APIFY_ERROR = "APIFY_ERROR"
    N8N_ERROR = "N8N_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Generic
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# =============================================================================
# Job Status Enum
# =============================================================================

class JobStatus(str, Enum):
    """
    Discovery job status values.
    
    Follows the workflow: pending -> analyzing -> discovering -> scoring -> completed
    With error states: failed, cancelled
    """
    
    PENDING = "pending"           # Job created, waiting to start
    ANALYZING = "analyzing"       # Brand analysis in progress
    DISCOVERING = "discovering"   # Profile discovery in progress
    SCORING = "scoring"           # Profile scoring in progress
    COMPLETED = "completed"       # Job finished successfully
    FAILED = "failed"            # Job encountered an error
    CANCELLED = "cancelled"      # Job was cancelled by user
    
    @classmethod
    def active_statuses(cls) -> FrozenSet["JobStatus"]:
        """Return statuses that indicate the job is currently running."""
        return frozenset({cls.ANALYZING, cls.DISCOVERING, cls.SCORING})
    
    @classmethod
    def terminal_statuses(cls) -> FrozenSet["JobStatus"]:
        """Return statuses that indicate the job is finished."""
        return frozenset({cls.COMPLETED, cls.FAILED, cls.CANCELLED})
    
    @classmethod
    def retryable_statuses(cls) -> FrozenSet["JobStatus"]:
        """Return statuses from which a job can be retried."""
        return frozenset({cls.FAILED})
    
    @classmethod
    def startable_statuses(cls) -> FrozenSet["JobStatus"]:
        """Return statuses from which a job can be started."""
        return frozenset({cls.PENDING})


# =============================================================================
# Profile Status Enum
# =============================================================================

class ProfileStatus(str, Enum):
    """
    Discovered profile status values.
    
    Follows the workflow: new -> processing -> scored
    With error state: failed
    """
    
    NEW = "new"               # Profile discovered, not yet processed
    PROCESSING = "processing" # Profile is being scored
    DONE = "done"             # Profile has been scored
    FAILED = "failed"         # Scoring failed for this profile
    SKIPPED = "skipped"       # Profile was skipped (e.g., duplicate, invalid)
    
    @classmethod
    def processable_statuses(cls) -> FrozenSet["ProfileStatus"]:
        """Return statuses that can be processed/scored."""
        return frozenset({cls.NEW, cls.FAILED})
    
    @classmethod
    def terminal_statuses(cls) -> FrozenSet["ProfileStatus"]:
        """Return statuses that indicate processing is complete."""
        return frozenset({cls.DONE, cls.SKIPPED})


# =============================================================================
# Valid State Transitions
# =============================================================================

VALID_JOB_TRANSITIONS: Dict[JobStatus, FrozenSet[JobStatus]] = {
    JobStatus.PENDING: frozenset({JobStatus.ANALYZING, JobStatus.CANCELLED}),
    JobStatus.ANALYZING: frozenset({JobStatus.DISCOVERING, JobStatus.FAILED, JobStatus.CANCELLED}),
    JobStatus.DISCOVERING: frozenset({JobStatus.SCORING, JobStatus.FAILED, JobStatus.CANCELLED}),
    JobStatus.SCORING: frozenset({JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}),
    JobStatus.COMPLETED: frozenset(),  # Terminal state
    JobStatus.FAILED: frozenset({JobStatus.PENDING}),  # Can retry -> goes back to pending
    JobStatus.CANCELLED: frozenset(),  # Terminal state
}

VALID_PROFILE_TRANSITIONS: Dict[ProfileStatus, FrozenSet[ProfileStatus]] = {
    ProfileStatus.NEW: frozenset({ProfileStatus.PROCESSING, ProfileStatus.SKIPPED}),
    ProfileStatus.PROCESSING: frozenset({ProfileStatus.DONE, ProfileStatus.FAILED}),
    ProfileStatus.DONE: frozenset(),  # Terminal state
    ProfileStatus.FAILED: frozenset({ProfileStatus.PROCESSING}),  # Can retry
    ProfileStatus.SKIPPED: frozenset(),  # Terminal state
}


def is_valid_job_transition(from_status: JobStatus, to_status: JobStatus) -> bool:
    """
    Check if a job status transition is valid.
    
    Args:
        from_status: Current job status
        to_status: Target job status
        
    Returns:
        bool: True if the transition is allowed
    """
    valid_targets = VALID_JOB_TRANSITIONS.get(from_status, frozenset())
    return to_status in valid_targets


def is_valid_profile_transition(from_status: ProfileStatus, to_status: ProfileStatus) -> bool:
    """
    Check if a profile status transition is valid.
    
    Args:
        from_status: Current profile status
        to_status: Target profile status
        
    Returns:
        bool: True if the transition is allowed
    """
    valid_targets = VALID_PROFILE_TRANSITIONS.get(from_status, frozenset())
    return to_status in valid_targets


# =============================================================================
# Database Table Names
# =============================================================================

class Tables:
    """Supabase table name constants."""
    
    DISCOVERY_JOBS = "discovery_jobs"
    BRAND_DNA = "brand_dna"
    DISCOVERED_PROFILES = "discovered_profiles"
    PROFILE_SCORES = "profile_scores"
    PROFILE_CONTACTS = "profile_contacts"
    
    # Views
    V_COMPLETE_PROFILES = "v_complete_profiles"
    V_JOB_SUMMARY = "v_job_summary"


# =============================================================================
# API Route Paths
# =============================================================================

class Routes:
    """API route path constants."""
    
    # Health
    HEALTH = "/health"
    
    # Jobs
    JOBS = "/jobs"
    JOB_BY_ID = "/jobs/{job_id}"
    JOB_START = "/jobs/{job_id}/start"
    JOB_STATUS = "/jobs/{job_id}/status"
    JOB_ANALYTICS = "/jobs/{job_id}/analytics"
    JOB_RETRY = "/jobs/{job_id}/retry"
    
    # Profiles
    PROFILES = "/profiles"
    PROFILE_BY_ID = "/profiles/{profile_id}"
    PROFILE_STATUS = "/profiles/{profile_id}/status"
    JOB_PROFILES_STATUS = "/jobs/{job_id}/profiles/status"
    
    # Agents
    AGENT_ANALYZE_BRAND = "/agent/analyze-brand"
    AGENT_DISCOVER = "/agent/discover"
    AGENT_SCORE = "/agent/score"
    
    # Email
    EMAIL_GENERATE = "/email/generate"
    EMAIL_SEND = "/email/send"


# =============================================================================
# Default Values
# =============================================================================

class Defaults:
    """Default configuration values."""
    
    # Pagination
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Discovery
    MIN_REFERENCE_PROFILES = 2
    MAX_REFERENCE_PROFILES = 10
    DEFAULT_DISCOVERY_LIMIT = 50
    MAX_DISCOVERY_LIMIT = 100
    
    # Follower Ranges
    MIN_FOLLOWERS = 1000
    MAX_FOLLOWERS = 1000000
    DEFAULT_MIN_FOLLOWERS = 5000
    DEFAULT_MAX_FOLLOWERS = 500000
    
    # Scoring
    MIN_SCORE = 0
    MAX_SCORE = 100
    DEFAULT_MIN_SCORE_THRESHOLD = 50
    HIGH_SCORE_THRESHOLD = 80
    
    # Scoring Weights (must sum to 1.0)
    WEIGHT_VISUAL_AESTHETIC = 0.15
    WEIGHT_CONTENT_THEME = 0.20
    WEIGHT_ENGAGEMENT_RATE = 0.25
    WEIGHT_FOLLOWER_QUALITY = 0.15
    WEIGHT_BUSINESS_INDICATORS = 0.15
    WEIGHT_ACTIVITY_RECENCY = 0.10
    
    # Timeouts (seconds)
    LLM_TIMEOUT = 60
    SCRAPING_TIMEOUT = 120
    API_REQUEST_TIMEOUT = 30
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 2
    
    # Email Tones
    EMAIL_TONES = ["professional", "friendly", "casual"]
    DEFAULT_EMAIL_TONE = "friendly"


# =============================================================================
# Scoring Dimension Names
# =============================================================================

class ScoringDimensions:
    """Names of the 6 scoring dimensions."""
    
    VISUAL_AESTHETIC_MATCH = "visual_aesthetic_match"
    CONTENT_THEME_ALIGNMENT = "content_theme_alignment"
    ENGAGEMENT_RATE_SCORE = "engagement_rate_score"
    FOLLOWER_QUALITY = "follower_quality"
    BUSINESS_INDICATORS = "business_indicators"
    ACTIVITY_RECENCY = "activity_recency"
    
    @classmethod
    def all_dimensions(cls) -> tuple:
        """Return all dimension names as a tuple."""
        return (
            cls.VISUAL_AESTHETIC_MATCH,
            cls.CONTENT_THEME_ALIGNMENT,
            cls.ENGAGEMENT_RATE_SCORE,
            cls.FOLLOWER_QUALITY,
            cls.BUSINESS_INDICATORS,
            cls.ACTIVITY_RECENCY,
        )
