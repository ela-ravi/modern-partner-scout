"""
PartnerScout AI - Guards Package

Authentication, authorization, and validation guards for securing API endpoints.
"""

from app.guards.auth import (
    # Context models
    UserContext,
    ServiceContext,
    # Base class
    AuthGuard,
    # Guard implementations
    UserGuard,
    ServiceKeyGuard,
    CombinedAuthGuard,
    # FastAPI dependencies
    get_current_user,
    get_service_context,
    get_optional_user,
    get_user_or_service,
    # Utilities
    create_test_token,
)

from app.guards.ownership import (
    # Base class
    OwnershipGuard,
    # Guard implementations
    JobOwnerGuard,
    ProfileOwnerGuard,
    # FastAPI dependencies
    verify_job_owner,
    verify_job_owner_user_only,
    verify_profile_owner,
    verify_profile_owner_user_only,
    # Utilities
    reset_guards,
)

from app.guards.validation import (
    # Guard implementations
    StatusTransitionGuard,
    InputSanitizer,
    FollowerRangeValidator,
    DiscoveryLimitValidator,
    # FastAPI dependencies
    get_status_transition_guard,
    get_input_sanitizer,
    get_follower_range_validator,
    get_discovery_limit_validator,
    validate_job_status_transition,
    validate_profile_status_transition,
    # Utilities
    reset_validation_guards,
    sanitize_input,
    validate_instagram_url,
    validate_uuid,
)


__all__ = [
    # Context models
    "UserContext",
    "ServiceContext",
    # Base classes
    "AuthGuard",
    "OwnershipGuard",
    # Auth guard implementations
    "UserGuard",
    "ServiceKeyGuard",
    "CombinedAuthGuard",
    # Ownership guard implementations
    "JobOwnerGuard",
    "ProfileOwnerGuard",
    # Validation guard implementations
    "StatusTransitionGuard",
    "InputSanitizer",
    "FollowerRangeValidator",
    "DiscoveryLimitValidator",
    # Auth FastAPI dependencies
    "get_current_user",
    "get_service_context",
    "get_optional_user",
    "get_user_or_service",
    # Ownership FastAPI dependencies
    "verify_job_owner",
    "verify_job_owner_user_only",
    "verify_profile_owner",
    "verify_profile_owner_user_only",
    # Validation FastAPI dependencies
    "get_status_transition_guard",
    "get_input_sanitizer",
    "get_follower_range_validator",
    "get_discovery_limit_validator",
    "validate_job_status_transition",
    "validate_profile_status_transition",
    # Utilities
    "create_test_token",
    "reset_guards",
    "reset_validation_guards",
    "sanitize_input",
    "validate_instagram_url",
    "validate_uuid",
]
