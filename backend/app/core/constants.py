"""
Application constants and enums.

This module contains all constant values and enumerations used throughout
the PartnerScout AI application. Centralizing constants here makes it
easy to maintain consistency and modify values in one place.
"""
from enum import Enum


class DiscoveryStatus(str, Enum):
    """
    Status values for discovery jobs.
    
    Represents the lifecycle of a discovery job from creation to completion.
    Status transitions should follow this order:
    PENDING -> ANALYZING -> DISCOVERING -> SCORING -> COMPLETED
    Any status can transition to FAILED.
    """
    # Initial state when job is created
    PENDING = "pending"
    # Analyzing brand DNA from reference profiles
    ANALYZING = "analyzing"
    # Discovering similar profiles
    DISCOVERING = "discovering"
    # Scoring discovered profiles
    SCORING = "scoring"
    # Job completed successfully
    COMPLETED = "completed"
    # Job failed at some stage
    FAILED = "failed"


class ProfileStatus(str, Enum):
    """
    Status values for discovered profiles.
    
    Represents the processing state of individual profiles
    discovered during a discovery job.
    """
    # Newly discovered, not yet processed
    NEW = "new"
    # Currently being processed (scraped, analyzed)
    PROCESSING = "processing"
    # Successfully scored and ready for review
    SCORED = "scored"
    # Skipped due to filtering criteria
    SKIPPED = "skipped"
    # Error during processing
    ERROR = "error"


class LLMProvider(str, Enum):
    """
    Supported LLM providers.
    
    The application supports multiple LLM providers for flexibility
    and cost optimization.
    """
    # OpenAI GPT models (default, most capable)
    OPENAI = "openai"
    # Google Gemini models
    GEMINI = "gemini"
    # Ollama for local/self-hosted models
    OLLAMA = "ollama"


class ScoreCategory(str, Enum):
    """
    Categories for profile scoring.
    
    Each discovered profile is scored across multiple categories
    to provide a comprehensive partnership potential assessment.
    """
    # How well the profile aligns with brand values and aesthetic
    BRAND_ALIGNMENT = "brand_alignment"
    # Overlap and relevance of the profile's audience
    AUDIENCE_FIT = "audience_fit"
    # Quality and authenticity of engagement metrics
    ENGAGEMENT_QUALITY = "engagement_quality"
    # Production quality and creativity of content
    CONTENT_QUALITY = "content_quality"
    # Overall potential for successful partnership
    PARTNERSHIP_POTENTIAL = "partnership_potential"


# =============================================================================
# API Constants
# =============================================================================

# Current API version
API_VERSION = "v1"

# Default number of items per page in paginated responses
DEFAULT_PAGE_SIZE = 20

# Maximum items per page to prevent excessive loads
MAX_PAGE_SIZE = 100


# =============================================================================
# Discovery Constants
# =============================================================================

# Maximum reference profiles a user can provide per job
MAX_REFERENCE_PROFILES = 5

# Default number of profiles to discover per job
DEFAULT_DISCOVERY_LIMIT = 50

# Maximum profiles that can be discovered in a single job
MAX_DISCOVERY_LIMIT = 200

# Minimum follower count for profiles to be considered
MIN_FOLLOWER_COUNT = 1000

# Maximum follower count (to filter out mega-influencers)
MAX_FOLLOWER_COUNT = 1000000


# =============================================================================
# Scoring Constants
# =============================================================================

# Minimum possible score
MIN_SCORE = 0

# Maximum possible score  
MAX_SCORE = 100

# Default minimum score threshold for "good" matches
DEFAULT_SCORE_THRESHOLD = 70


# =============================================================================
# Rate Limiting Constants
# =============================================================================

# Default maximum requests per period
DEFAULT_RATE_LIMIT = 100

# Default rate limit period in seconds
DEFAULT_RATE_PERIOD = 60  # 1 minute


# =============================================================================
# Timeout Constants
# =============================================================================

# HTTP request timeout for external APIs (seconds)
HTTP_TIMEOUT = 30

# LLM API timeout (seconds) - longer for complex prompts
LLM_TIMEOUT = 60

# Apify actor run timeout (seconds)
APIFY_TIMEOUT = 300  # 5 minutes


# =============================================================================
# Error Codes
# =============================================================================

class ErrorCode(str, Enum):
    """
    Standard error codes for API responses.
    
    These codes help clients handle errors programmatically.
    """
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    LLM_ERROR = "LLM_ERROR"
    APIFY_ERROR = "APIFY_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
