"""
PartnerScout AI - Validation Guards

Implements validation guards for ensuring data integrity and valid state transitions.
- StatusTransitionGuard: Validates job and profile status transitions
- Input sanitization functions for preventing injection attacks
"""

import html
import re
from typing import Any, Dict, List, Optional, Set, Union

from fastapi import Depends, HTTPException

from app.core.constants import (
    ErrorCodes,
    HttpStatus,
    JobStatus,
    ProfileStatus,
    VALID_JOB_TRANSITIONS,
    VALID_PROFILE_TRANSITIONS,
    is_valid_job_transition,
    is_valid_profile_transition,
    Defaults,
)
from app.core.exceptions import (
    InvalidStatusTransitionError,
    ValidationError,
)


# =============================================================================
# Status Transition Guard
# =============================================================================

class StatusTransitionGuard:
    """
    Guard for validating status transitions.
    
    Ensures that job and profile status changes follow the allowed
    state machine defined in the constants.
    """
    
    def validate_job_transition(
        self,
        current_status: Union[str, JobStatus],
        new_status: Union[str, JobStatus],
    ) -> JobStatus:
        """
        Validate a job status transition.
        
        Args:
            current_status: The current job status
            new_status: The target job status
            
        Returns:
            The validated new JobStatus enum
            
        Raises:
            InvalidStatusTransitionError: If the transition is not allowed
            ValidationError: If the status value is invalid
        """
        # Convert strings to enums
        current = self._to_job_status(current_status)
        target = self._to_job_status(new_status)
        
        # Check if transition is valid
        if not is_valid_job_transition(current, target):
            valid_transitions = VALID_JOB_TRANSITIONS.get(current, frozenset())
            raise InvalidStatusTransitionError(
                from_status=current.value,
                to_status=target.value,
                entity_type="job",
            )
        
        return target
    
    def validate_profile_transition(
        self,
        current_status: Union[str, ProfileStatus],
        new_status: Union[str, ProfileStatus],
    ) -> ProfileStatus:
        """
        Validate a profile status transition.
        
        Args:
            current_status: The current profile status
            new_status: The target profile status
            
        Returns:
            The validated new ProfileStatus enum
            
        Raises:
            InvalidStatusTransitionError: If the transition is not allowed
            ValidationError: If the status value is invalid
        """
        # Convert strings to enums
        current = self._to_profile_status(current_status)
        target = self._to_profile_status(new_status)
        
        # Check if transition is valid
        if not is_valid_profile_transition(current, target):
            valid_transitions = VALID_PROFILE_TRANSITIONS.get(current, frozenset())
            raise InvalidStatusTransitionError(
                from_status=current.value,
                to_status=target.value,
                entity_type="profile",
            )
        
        return target
    
    def get_valid_job_transitions(self, current_status: Union[str, JobStatus]) -> List[str]:
        """
        Get the list of valid next statuses for a job.
        
        Args:
            current_status: The current job status
            
        Returns:
            List of valid status values that can be transitioned to
        """
        current = self._to_job_status(current_status)
        valid = VALID_JOB_TRANSITIONS.get(current, frozenset())
        return [s.value for s in valid]
    
    def get_valid_profile_transitions(self, current_status: Union[str, ProfileStatus]) -> List[str]:
        """
        Get the list of valid next statuses for a profile.
        
        Args:
            current_status: The current profile status
            
        Returns:
            List of valid status values that can be transitioned to
        """
        current = self._to_profile_status(current_status)
        valid = VALID_PROFILE_TRANSITIONS.get(current, frozenset())
        return [s.value for s in valid]
    
    def is_terminal_job_status(self, status: Union[str, JobStatus]) -> bool:
        """Check if a job status is a terminal state."""
        status_enum = self._to_job_status(status)
        return status_enum in JobStatus.terminal_statuses()
    
    def is_terminal_profile_status(self, status: Union[str, ProfileStatus]) -> bool:
        """Check if a profile status is a terminal state."""
        status_enum = self._to_profile_status(status)
        return status_enum in ProfileStatus.terminal_statuses()
    
    @staticmethod
    def _to_job_status(status: Union[str, JobStatus]) -> JobStatus:
        """Convert a string or enum to JobStatus enum."""
        if isinstance(status, JobStatus):
            return status
        
        try:
            return JobStatus(status)
        except ValueError:
            valid_values = [s.value for s in JobStatus]
            raise ValidationError(
                message=f"Invalid job status: '{status}'",
                field="status",
                value=status,
                details={"valid_values": valid_values},
            )
    
    @staticmethod
    def _to_profile_status(status: Union[str, ProfileStatus]) -> ProfileStatus:
        """Convert a string or enum to ProfileStatus enum."""
        if isinstance(status, ProfileStatus):
            return status
        
        try:
            return ProfileStatus(status)
        except ValueError:
            valid_values = [s.value for s in ProfileStatus]
            raise ValidationError(
                message=f"Invalid profile status: '{status}'",
                field="status",
                value=status,
                details={"valid_values": valid_values},
            )


# =============================================================================
# Input Sanitization
# =============================================================================

class InputSanitizer:
    """
    Input sanitization utilities for preventing injection attacks.
    
    Provides methods for cleaning and validating user input.
    """
    
    # Patterns for validation
    INSTAGRAM_URL_PATTERN = re.compile(
        r'^https?://(www\.)?instagram\.com/[a-zA-Z0-9_\.]+/?$'
    )
    
    INSTAGRAM_USERNAME_PATTERN = re.compile(
        r'^[a-zA-Z0-9_\.]{1,30}$'
    )
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    UUID_PATTERN = re.compile(
        r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'
    )
    
    # Dangerous patterns to remove or escape
    SQL_INJECTION_PATTERNS = [
        r"(?i)(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|'|\")",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
    ]
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize a string input by escaping HTML and removing dangerous patterns.
        
        Args:
            value: The string to sanitize
            max_length: Optional maximum length to truncate to
            
        Returns:
            Sanitized string
        """
        if not value:
            return value
        
        # HTML escape to prevent XSS
        sanitized = html.escape(value)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def sanitize_html(self, value: str) -> str:
        """
        Sanitize a string by removing all HTML tags and escaping remaining content.
        
        Args:
            value: The string to sanitize
            
        Returns:
            Sanitized string with no HTML
        """
        if not value:
            return value
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', value)
        
        # HTML escape remaining content
        clean = html.escape(clean)
        
        return clean
    
    def validate_instagram_url(self, url: str) -> bool:
        """
        Validate that a URL is a valid Instagram profile URL.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if valid
        """
        return bool(self.INSTAGRAM_URL_PATTERN.match(url))
    
    def validate_instagram_username(self, username: str) -> bool:
        """
        Validate that a string is a valid Instagram username.
        
        Args:
            username: The username to validate
            
        Returns:
            True if valid
        """
        return bool(self.INSTAGRAM_USERNAME_PATTERN.match(username))
    
    def validate_email(self, email: str) -> bool:
        """
        Validate that a string is a valid email address format.
        
        Args:
            email: The email to validate
            
        Returns:
            True if valid
        """
        return bool(self.EMAIL_PATTERN.match(email))
    
    def validate_uuid(self, value: str) -> bool:
        """
        Validate that a string is a valid UUID format.
        
        Args:
            value: The UUID string to validate
            
        Returns:
            True if valid
        """
        return bool(self.UUID_PATTERN.match(value))
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract the Instagram username from a profile URL.
        
        Args:
            url: The Instagram profile URL
            
        Returns:
            Username or None if extraction fails
        """
        if not url:
            return None
        
        # Remove trailing slash and query params
        url = url.split('?')[0].rstrip('/')
        
        # Extract username from URL path
        match = re.search(r'instagram\.com/([a-zA-Z0-9_\.]+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def sanitize_brand_description(self, description: str) -> str:
        """
        Sanitize a brand description input.
        
        Args:
            description: The brand description text
            
        Returns:
            Sanitized description
        """
        # HTML escape
        sanitized = self.sanitize_string(description, max_length=2000)
        
        # Remove any remaining script-like content
        for pattern in self.XSS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def sanitize_profile_urls(self, urls: List[str]) -> List[str]:
        """
        Sanitize and validate a list of Instagram profile URLs.
        
        Args:
            urls: List of URLs to sanitize
            
        Returns:
            List of valid, sanitized URLs
            
        Raises:
            ValidationError: If any URL is invalid
        """
        sanitized_urls = []
        invalid_urls = []
        
        for url in urls:
            # Basic sanitization
            url = url.strip()
            
            if not self.validate_instagram_url(url):
                invalid_urls.append(url)
            else:
                sanitized_urls.append(url)
        
        if invalid_urls:
            raise ValidationError(
                message="Invalid Instagram URL format",
                field="reference_profiles",
                details={"invalid_urls": invalid_urls},
            )
        
        return sanitized_urls
    
    def check_for_sql_injection(self, value: str) -> bool:
        """
        Check if a string contains SQL injection patterns.
        
        Args:
            value: The string to check
            
        Returns:
            True if suspicious patterns are found
        """
        if not value:
            return False
        
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    def check_for_xss(self, value: str) -> bool:
        """
        Check if a string contains XSS patterns.
        
        Args:
            value: The string to check
            
        Returns:
            True if XSS patterns are found
        """
        if not value:
            return False
        
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False


# =============================================================================
# Follower Range Validator
# =============================================================================

class FollowerRangeValidator:
    """
    Validator for follower count ranges.
    
    Ensures follower range values are within acceptable bounds.
    """
    
    def __init__(
        self,
        min_allowed: int = Defaults.MIN_FOLLOWERS,
        max_allowed: int = Defaults.MAX_FOLLOWERS,
    ):
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed
    
    def validate(
        self,
        min_followers: int,
        max_followers: int,
    ) -> tuple:
        """
        Validate and normalize follower range values.
        
        Args:
            min_followers: Minimum follower count
            max_followers: Maximum follower count
            
        Returns:
            Tuple of (validated_min, validated_max)
            
        Raises:
            ValidationError: If range is invalid
        """
        # Clamp to allowed bounds
        min_followers = max(self.min_allowed, min_followers)
        max_followers = min(self.max_allowed, max_followers)
        
        # Ensure min < max
        if min_followers >= max_followers:
            raise ValidationError(
                message="Minimum followers must be less than maximum followers",
                field="follower_range",
                details={
                    "min_followers": min_followers,
                    "max_followers": max_followers,
                },
            )
        
        return (min_followers, max_followers)


# =============================================================================
# Discovery Limit Validator
# =============================================================================

class DiscoveryLimitValidator:
    """
    Validator for discovery limit values.
    
    Ensures discovery limits are within acceptable bounds.
    """
    
    def __init__(
        self,
        min_limit: int = 1,
        max_limit: int = Defaults.MAX_DISCOVERY_LIMIT,
    ):
        self.min_limit = min_limit
        self.max_limit = max_limit
    
    def validate(self, limit: int) -> int:
        """
        Validate and normalize discovery limit.
        
        Args:
            limit: The discovery limit value
            
        Returns:
            Validated limit value
            
        Raises:
            ValidationError: If limit is out of bounds
        """
        if limit < self.min_limit:
            raise ValidationError(
                message=f"Discovery limit must be at least {self.min_limit}",
                field="discovery_limit",
                value=limit,
                details={"min": self.min_limit, "max": self.max_limit},
            )
        
        if limit > self.max_limit:
            raise ValidationError(
                message=f"Discovery limit cannot exceed {self.max_limit}",
                field="discovery_limit",
                value=limit,
                details={"min": self.min_limit, "max": self.max_limit},
            )
        
        return limit


# =============================================================================
# FastAPI Dependencies
# =============================================================================

# Singleton instances
_status_transition_guard: Optional[StatusTransitionGuard] = None
_input_sanitizer: Optional[InputSanitizer] = None
_follower_range_validator: Optional[FollowerRangeValidator] = None
_discovery_limit_validator: Optional[DiscoveryLimitValidator] = None


def get_status_transition_guard() -> StatusTransitionGuard:
    """Get or create the status transition guard singleton."""
    global _status_transition_guard
    if _status_transition_guard is None:
        _status_transition_guard = StatusTransitionGuard()
    return _status_transition_guard


def get_input_sanitizer() -> InputSanitizer:
    """Get or create the input sanitizer singleton."""
    global _input_sanitizer
    if _input_sanitizer is None:
        _input_sanitizer = InputSanitizer()
    return _input_sanitizer


def get_follower_range_validator() -> FollowerRangeValidator:
    """Get or create the follower range validator singleton."""
    global _follower_range_validator
    if _follower_range_validator is None:
        _follower_range_validator = FollowerRangeValidator()
    return _follower_range_validator


def get_discovery_limit_validator() -> DiscoveryLimitValidator:
    """Get or create the discovery limit validator singleton."""
    global _discovery_limit_validator
    if _discovery_limit_validator is None:
        _discovery_limit_validator = DiscoveryLimitValidator()
    return _discovery_limit_validator


async def validate_job_status_transition(
    current_status: str,
    new_status: str,
    guard: StatusTransitionGuard = Depends(get_status_transition_guard),
) -> JobStatus:
    """
    FastAPI dependency for validating job status transitions.
    
    Usage:
        @app.patch("/api/jobs/{job_id}/status")
        async def update_status(
            new_status: str,
            job: dict = Depends(verify_job_owner),
            validated_status: JobStatus = Depends(validate_job_status_transition),
        ):
            ...
    """
    try:
        return guard.validate_job_transition(current_status, new_status)
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=HttpStatus.UNPROCESSABLE_ENTITY,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def validate_profile_status_transition(
    current_status: str,
    new_status: str,
    guard: StatusTransitionGuard = Depends(get_status_transition_guard),
) -> ProfileStatus:
    """
    FastAPI dependency for validating profile status transitions.
    """
    try:
        return guard.validate_profile_transition(current_status, new_status)
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=HttpStatus.UNPROCESSABLE_ENTITY,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


# =============================================================================
# Utility Functions
# =============================================================================

def reset_validation_guards() -> None:
    """
    Reset validation guard singletons.
    
    Useful for testing to ensure fresh instances.
    """
    global _status_transition_guard, _input_sanitizer
    global _follower_range_validator, _discovery_limit_validator
    _status_transition_guard = None
    _input_sanitizer = None
    _follower_range_validator = None
    _discovery_limit_validator = None


def sanitize_input(value: str, max_length: Optional[int] = None) -> str:
    """
    Convenience function for sanitizing string input.
    
    Args:
        value: The string to sanitize
        max_length: Optional maximum length
        
    Returns:
        Sanitized string
    """
    return get_input_sanitizer().sanitize_string(value, max_length)


def validate_instagram_url(url: str) -> bool:
    """
    Convenience function for validating Instagram URLs.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid
    """
    return get_input_sanitizer().validate_instagram_url(url)


def validate_uuid(value: str) -> bool:
    """
    Convenience function for validating UUID strings.
    
    Args:
        value: The UUID string to validate
        
    Returns:
        True if valid
    """
    return get_input_sanitizer().validate_uuid(value)
