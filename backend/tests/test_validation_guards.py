"""
Tests for Validation Guards

Tests for STORY-2.2.3: Implement Validation Guards
- StatusTransitionGuard: Validates job and profile status transitions
- InputSanitizer: Input sanitization for preventing injection attacks
- FollowerRangeValidator: Validates follower range values
- DiscoveryLimitValidator: Validates discovery limit values
"""

import pytest

from app.core.constants import (
    JobStatus,
    ProfileStatus,
    ErrorCodes,
    Defaults,
    VALID_JOB_TRANSITIONS,
    VALID_PROFILE_TRANSITIONS,
)
from app.core.exceptions import InvalidStatusTransitionError, ValidationError
from app.guards.validation import (
    StatusTransitionGuard,
    InputSanitizer,
    FollowerRangeValidator,
    DiscoveryLimitValidator,
    get_status_transition_guard,
    get_input_sanitizer,
    get_follower_range_validator,
    get_discovery_limit_validator,
    reset_validation_guards,
    sanitize_input,
    validate_instagram_url,
    validate_uuid,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances before each test."""
    reset_validation_guards()
    yield
    reset_validation_guards()


@pytest.fixture
def status_guard():
    """Create a StatusTransitionGuard instance."""
    return StatusTransitionGuard()


@pytest.fixture
def sanitizer():
    """Create an InputSanitizer instance."""
    return InputSanitizer()


@pytest.fixture
def follower_validator():
    """Create a FollowerRangeValidator instance."""
    return FollowerRangeValidator()


@pytest.fixture
def discovery_validator():
    """Create a DiscoveryLimitValidator instance."""
    return DiscoveryLimitValidator()


# =============================================================================
# StatusTransitionGuard Tests
# =============================================================================

class TestStatusTransitionGuard:
    """Tests for StatusTransitionGuard class."""
    
    # -------------------------------------------------------------------------
    # Job Status Transition Tests
    # -------------------------------------------------------------------------
    
    def test_validate_job_transition_pending_to_analyzing(self, status_guard):
        """Test valid transition from pending to analyzing."""
        result = status_guard.validate_job_transition(
            JobStatus.PENDING, JobStatus.ANALYZING
        )
        assert result == JobStatus.ANALYZING
    
    def test_validate_job_transition_pending_to_cancelled(self, status_guard):
        """Test valid transition from pending to cancelled."""
        result = status_guard.validate_job_transition(
            JobStatus.PENDING, JobStatus.CANCELLED
        )
        assert result == JobStatus.CANCELLED
    
    def test_validate_job_transition_analyzing_to_discovering(self, status_guard):
        """Test valid transition from analyzing to discovering."""
        result = status_guard.validate_job_transition(
            JobStatus.ANALYZING, JobStatus.DISCOVERING
        )
        assert result == JobStatus.DISCOVERING
    
    def test_validate_job_transition_discovering_to_scoring(self, status_guard):
        """Test valid transition from discovering to scoring."""
        result = status_guard.validate_job_transition(
            JobStatus.DISCOVERING, JobStatus.SCORING
        )
        assert result == JobStatus.SCORING
    
    def test_validate_job_transition_scoring_to_completed(self, status_guard):
        """Test valid transition from scoring to completed."""
        result = status_guard.validate_job_transition(
            JobStatus.SCORING, JobStatus.COMPLETED
        )
        assert result == JobStatus.COMPLETED
    
    def test_validate_job_transition_failed_to_pending(self, status_guard):
        """Test valid retry transition from failed to pending."""
        result = status_guard.validate_job_transition(
            JobStatus.FAILED, JobStatus.PENDING
        )
        assert result == JobStatus.PENDING
    
    def test_validate_job_transition_string_input(self, status_guard):
        """Test transition validation with string inputs."""
        result = status_guard.validate_job_transition("pending", "analyzing")
        assert result == JobStatus.ANALYZING
    
    def test_validate_job_transition_invalid_pending_to_completed(self, status_guard):
        """Test invalid direct transition from pending to completed."""
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            status_guard.validate_job_transition(
                JobStatus.PENDING, JobStatus.COMPLETED
            )
        
        assert exc_info.value.code == ErrorCodes.INVALID_TRANSITION
        assert "pending" in exc_info.value.message
        assert "completed" in exc_info.value.message
    
    def test_validate_job_transition_invalid_completed_to_pending(self, status_guard):
        """Test invalid transition from terminal state completed."""
        with pytest.raises(InvalidStatusTransitionError):
            status_guard.validate_job_transition(
                JobStatus.COMPLETED, JobStatus.PENDING
            )
    
    def test_validate_job_transition_invalid_cancelled_to_any(self, status_guard):
        """Test that cancelled is a terminal state."""
        with pytest.raises(InvalidStatusTransitionError):
            status_guard.validate_job_transition(
                JobStatus.CANCELLED, JobStatus.PENDING
            )
    
    def test_validate_job_transition_invalid_status_string(self, status_guard):
        """Test validation error for invalid status string."""
        with pytest.raises(ValidationError) as exc_info:
            status_guard.validate_job_transition("invalid_status", "analyzing")
        
        assert "invalid_status" in exc_info.value.message
        assert "valid_values" in exc_info.value.details
    
    # -------------------------------------------------------------------------
    # Profile Status Transition Tests
    # -------------------------------------------------------------------------
    
    def test_validate_profile_transition_new_to_processing(self, status_guard):
        """Test valid transition from new to processing."""
        result = status_guard.validate_profile_transition(
            ProfileStatus.NEW, ProfileStatus.PROCESSING
        )
        assert result == ProfileStatus.PROCESSING
    
    def test_validate_profile_transition_new_to_skipped(self, status_guard):
        """Test valid transition from new to skipped."""
        result = status_guard.validate_profile_transition(
            ProfileStatus.NEW, ProfileStatus.SKIPPED
        )
        assert result == ProfileStatus.SKIPPED
    
    def test_validate_profile_transition_processing_to_scored(self, status_guard):
        """Test valid transition from processing to scored."""
        result = status_guard.validate_profile_transition(
            ProfileStatus.PROCESSING, ProfileStatus.SCORED
        )
        assert result == ProfileStatus.SCORED
    
    def test_validate_profile_transition_processing_to_new(self, status_guard):
        """Test valid retry transition from processing to new."""
        result = status_guard.validate_profile_transition(
            ProfileStatus.PROCESSING, ProfileStatus.NEW
        )
        assert result == ProfileStatus.NEW

    def test_validate_profile_transition_processing_to_skipped(self, status_guard):
        """Test valid transition from processing to skipped."""
        result = status_guard.validate_profile_transition(
            ProfileStatus.PROCESSING, ProfileStatus.SKIPPED
        )
        assert result == ProfileStatus.SKIPPED
    
    def test_validate_profile_transition_string_input(self, status_guard):
        """Test transition validation with string inputs."""
        result = status_guard.validate_profile_transition("new", "processing")
        assert result == ProfileStatus.PROCESSING
    
    def test_validate_profile_transition_invalid_new_to_scored(self, status_guard):
        """Test invalid direct transition from new to scored."""
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            status_guard.validate_profile_transition(
                ProfileStatus.NEW, ProfileStatus.SCORED
            )
        
        assert exc_info.value.code == ErrorCodes.INVALID_TRANSITION
        assert "profile" in exc_info.value.details.get("entity_type", "")
    
    def test_validate_profile_transition_invalid_scored_to_any(self, status_guard):
        """Test that scored is a terminal state."""
        with pytest.raises(InvalidStatusTransitionError):
            status_guard.validate_profile_transition(
                ProfileStatus.SCORED, ProfileStatus.NEW
            )
    
    # -------------------------------------------------------------------------
    # Helper Method Tests
    # -------------------------------------------------------------------------
    
    def test_get_valid_job_transitions(self, status_guard):
        """Test getting valid transitions for a job status."""
        transitions = status_guard.get_valid_job_transitions(JobStatus.PENDING)
        
        assert "analyzing" in transitions
        assert "cancelled" in transitions
        assert "completed" not in transitions
    
    def test_get_valid_profile_transitions(self, status_guard):
        """Test getting valid transitions for a profile status."""
        transitions = status_guard.get_valid_profile_transitions(ProfileStatus.NEW)
        
        assert "processing" in transitions
        assert "skipped" in transitions
        assert "scored" not in transitions
    
    def test_is_terminal_job_status_completed(self, status_guard):
        """Test that completed is recognized as terminal."""
        assert status_guard.is_terminal_job_status(JobStatus.COMPLETED) is True
    
    def test_is_terminal_job_status_pending(self, status_guard):
        """Test that pending is not terminal."""
        assert status_guard.is_terminal_job_status(JobStatus.PENDING) is False
    
    def test_is_terminal_profile_status_scored(self, status_guard):
        """Test that scored is recognized as terminal."""
        assert status_guard.is_terminal_profile_status(ProfileStatus.SCORED) is True
    
    def test_is_terminal_profile_status_new(self, status_guard):
        """Test that new is not terminal."""
        assert status_guard.is_terminal_profile_status(ProfileStatus.NEW) is False


# =============================================================================
# InputSanitizer Tests
# =============================================================================

class TestInputSanitizer:
    """Tests for InputSanitizer class."""
    
    # -------------------------------------------------------------------------
    # String Sanitization Tests
    # -------------------------------------------------------------------------
    
    def test_sanitize_string_html_escape(self, sanitizer):
        """Test that HTML is escaped."""
        result = sanitizer.sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_sanitize_string_removes_null_bytes(self, sanitizer):
        """Test that null bytes are removed."""
        result = sanitizer.sanitize_string("hello\x00world")
        assert "\x00" not in result
        assert "helloworld" in result
    
    def test_sanitize_string_normalizes_whitespace(self, sanitizer):
        """Test that whitespace is normalized."""
        result = sanitizer.sanitize_string("hello   \n\t  world")
        assert result == "hello world"
    
    def test_sanitize_string_max_length(self, sanitizer):
        """Test string truncation."""
        result = sanitizer.sanitize_string("a" * 100, max_length=50)
        assert len(result) == 50
    
    def test_sanitize_string_empty(self, sanitizer):
        """Test empty string handling."""
        assert sanitizer.sanitize_string("") == ""
        assert sanitizer.sanitize_string(None) is None
    
    # -------------------------------------------------------------------------
    # HTML Sanitization Tests
    # -------------------------------------------------------------------------
    
    def test_sanitize_html_removes_tags(self, sanitizer):
        """Test that HTML tags are removed."""
        result = sanitizer.sanitize_html("<p>Hello <b>World</b></p>")
        assert "<p>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "World" in result
    
    def test_sanitize_html_removes_script(self, sanitizer):
        """Test that script tags are removed."""
        result = sanitizer.sanitize_html("<script>malicious()</script>text")
        assert "script" not in result.lower()
        assert "text" in result
    
    # -------------------------------------------------------------------------
    # URL Validation Tests
    # -------------------------------------------------------------------------
    
    def test_validate_instagram_url_valid(self, sanitizer):
        """Test valid Instagram URLs."""
        valid_urls = [
            "https://instagram.com/username",
            "https://www.instagram.com/username/",
            "http://instagram.com/user_name",
            "https://instagram.com/user.name",
        ]
        for url in valid_urls:
            assert sanitizer.validate_instagram_url(url) is True, f"Expected {url} to be valid"
    
    def test_validate_instagram_url_invalid(self, sanitizer):
        """Test invalid Instagram URLs."""
        invalid_urls = [
            "https://twitter.com/username",
            "instagram.com/username",
            "https://instagram.com/",
            "https://instagram.com/user name",
            "https://instagram.com/username?query=1",
        ]
        for url in invalid_urls:
            assert sanitizer.validate_instagram_url(url) is False, f"Expected {url} to be invalid"
    
    # -------------------------------------------------------------------------
    # Username Validation Tests
    # -------------------------------------------------------------------------
    
    def test_validate_instagram_username_valid(self, sanitizer):
        """Test valid Instagram usernames."""
        valid_usernames = [
            "username",
            "user_name",
            "user.name",
            "user123",
            "a",
        ]
        for username in valid_usernames:
            assert sanitizer.validate_instagram_username(username) is True
    
    def test_validate_instagram_username_invalid(self, sanitizer):
        """Test invalid Instagram usernames."""
        invalid_usernames = [
            "user name",
            "user@name",
            "user-name",
            "",
            "a" * 31,  # Too long
        ]
        for username in invalid_usernames:
            assert sanitizer.validate_instagram_username(username) is False
    
    # -------------------------------------------------------------------------
    # Email Validation Tests
    # -------------------------------------------------------------------------
    
    def test_validate_email_valid(self, sanitizer):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
        ]
        for email in valid_emails:
            assert sanitizer.validate_email(email) is True
    
    def test_validate_email_invalid(self, sanitizer):
        """Test invalid email addresses."""
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user@domain",
        ]
        for email in invalid_emails:
            assert sanitizer.validate_email(email) is False
    
    # -------------------------------------------------------------------------
    # UUID Validation Tests
    # -------------------------------------------------------------------------
    
    def test_validate_uuid_valid(self, sanitizer):
        """Test valid UUIDs."""
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000",
        ]
        for uuid in valid_uuids:
            assert sanitizer.validate_uuid(uuid) is True
    
    def test_validate_uuid_invalid(self, sanitizer):
        """Test invalid UUIDs."""
        invalid_uuids = [
            "not-a-uuid",
            "123e4567-e89b-12d3-a456",
            "123e4567-e89b-12d3-a456-426614174000-extra",
        ]
        for uuid in invalid_uuids:
            assert sanitizer.validate_uuid(uuid) is False
    
    # -------------------------------------------------------------------------
    # Username Extraction Tests
    # -------------------------------------------------------------------------
    
    def test_extract_username_from_url(self, sanitizer):
        """Test username extraction from URL."""
        assert sanitizer.extract_username_from_url(
            "https://instagram.com/everlane"
        ) == "everlane"
        assert sanitizer.extract_username_from_url(
            "https://www.instagram.com/everlane/"
        ) == "everlane"
    
    def test_extract_username_from_url_with_query(self, sanitizer):
        """Test username extraction ignores query params."""
        result = sanitizer.extract_username_from_url(
            "https://instagram.com/everlane?hl=en"
        )
        assert result == "everlane"
    
    def test_extract_username_from_url_invalid(self, sanitizer):
        """Test username extraction returns None for invalid URLs."""
        assert sanitizer.extract_username_from_url("https://twitter.com/user") is None
        assert sanitizer.extract_username_from_url("") is None
        assert sanitizer.extract_username_from_url(None) is None
    
    # -------------------------------------------------------------------------
    # Brand Description Sanitization Tests
    # -------------------------------------------------------------------------
    
    def test_sanitize_brand_description(self, sanitizer):
        """Test brand description sanitization."""
        description = "A <script>alert('xss')</script> fashion brand"
        result = sanitizer.sanitize_brand_description(description)
        
        # HTML tags should be escaped (making them harmless)
        assert "<script>" not in result
        assert "</script>" not in result
        # The escaped version should be present (harmless text)
        assert "&lt;script&gt;" in result or "script" not in result.lower()
        assert "fashion brand" in result
    
    def test_sanitize_brand_description_length(self, sanitizer):
        """Test brand description length limit."""
        long_description = "a" * 3000
        result = sanitizer.sanitize_brand_description(long_description)
        
        assert len(result) <= 2000
    
    # -------------------------------------------------------------------------
    # Profile URL Sanitization Tests
    # -------------------------------------------------------------------------
    
    def test_sanitize_profile_urls_valid(self, sanitizer):
        """Test sanitizing valid profile URLs."""
        urls = [
            "https://instagram.com/user1",
            "https://instagram.com/user2/",
        ]
        result = sanitizer.sanitize_profile_urls(urls)
        
        assert len(result) == 2
        assert "https://instagram.com/user1" in result
    
    def test_sanitize_profile_urls_invalid(self, sanitizer):
        """Test sanitizing invalid profile URLs raises error."""
        urls = [
            "https://instagram.com/user1",
            "https://twitter.com/user2",  # Invalid
        ]
        
        with pytest.raises(ValidationError) as exc_info:
            sanitizer.sanitize_profile_urls(urls)
        
        assert "invalid_urls" in exc_info.value.details
    
    # -------------------------------------------------------------------------
    # Security Pattern Detection Tests
    # -------------------------------------------------------------------------
    
    def test_check_for_sql_injection(self, sanitizer):
        """Test SQL injection detection."""
        assert sanitizer.check_for_sql_injection("SELECT * FROM users") is True
        assert sanitizer.check_for_sql_injection("DROP TABLE users;") is True
        assert sanitizer.check_for_sql_injection("'; DELETE FROM users --") is True
        assert sanitizer.check_for_sql_injection("normal text") is False
    
    def test_check_for_xss(self, sanitizer):
        """Test XSS detection."""
        assert sanitizer.check_for_xss("<script>alert('xss')</script>") is True
        assert sanitizer.check_for_xss("javascript:alert(1)") is True
        assert sanitizer.check_for_xss("onclick=alert(1)") is True
        assert sanitizer.check_for_xss("normal text") is False


# =============================================================================
# FollowerRangeValidator Tests
# =============================================================================

class TestFollowerRangeValidator:
    """Tests for FollowerRangeValidator class."""
    
    def test_validate_valid_range(self, follower_validator):
        """Test validating a valid follower range."""
        min_val, max_val = follower_validator.validate(5000, 100000)
        
        assert min_val == 5000
        assert max_val == 100000
    
    def test_validate_clamps_to_bounds(self, follower_validator):
        """Test that values are clamped to allowed bounds."""
        min_val, max_val = follower_validator.validate(100, 2000000)
        
        # Should be clamped to MIN_FOLLOWERS and MAX_FOLLOWERS
        assert min_val >= Defaults.MIN_FOLLOWERS
        assert max_val <= Defaults.MAX_FOLLOWERS
    
    def test_validate_min_greater_than_max_raises_error(self, follower_validator):
        """Test that min > max raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            follower_validator.validate(100000, 50000)
        
        assert "less than" in exc_info.value.message.lower()
    
    def test_validate_equal_values_raises_error(self, follower_validator):
        """Test that min == max raises ValidationError."""
        with pytest.raises(ValidationError):
            follower_validator.validate(50000, 50000)
    
    def test_custom_bounds(self):
        """Test validator with custom bounds."""
        validator = FollowerRangeValidator(min_allowed=500, max_allowed=10000)
        
        min_val, max_val = validator.validate(100, 50000)
        
        assert min_val == 500  # Clamped to min_allowed
        assert max_val == 10000  # Clamped to max_allowed


# =============================================================================
# DiscoveryLimitValidator Tests
# =============================================================================

class TestDiscoveryLimitValidator:
    """Tests for DiscoveryLimitValidator class."""
    
    def test_validate_valid_limit(self, discovery_validator):
        """Test validating a valid discovery limit."""
        result = discovery_validator.validate(50)
        assert result == 50
    
    def test_validate_minimum_limit(self, discovery_validator):
        """Test validating the minimum limit."""
        result = discovery_validator.validate(1)
        assert result == 1
    
    def test_validate_maximum_limit(self, discovery_validator):
        """Test validating the maximum limit."""
        result = discovery_validator.validate(Defaults.MAX_DISCOVERY_LIMIT)
        assert result == Defaults.MAX_DISCOVERY_LIMIT
    
    def test_validate_below_minimum_raises_error(self, discovery_validator):
        """Test that value below minimum raises error."""
        with pytest.raises(ValidationError) as exc_info:
            discovery_validator.validate(0)
        
        assert "at least" in exc_info.value.message.lower()
    
    def test_validate_above_maximum_raises_error(self, discovery_validator):
        """Test that value above maximum raises error."""
        with pytest.raises(ValidationError) as exc_info:
            discovery_validator.validate(1000)
        
        assert "exceed" in exc_info.value.message.lower()
    
    def test_custom_limits(self):
        """Test validator with custom limits."""
        validator = DiscoveryLimitValidator(min_limit=10, max_limit=25)
        
        assert validator.validate(15) == 15
        
        with pytest.raises(ValidationError):
            validator.validate(5)
        
        with pytest.raises(ValidationError):
            validator.validate(30)


# =============================================================================
# Singleton and Utility Function Tests
# =============================================================================

class TestSingletonsAndUtilities:
    """Tests for singleton getters and utility functions."""
    
    def test_get_status_transition_guard_singleton(self):
        """Test that get_status_transition_guard returns singleton."""
        guard1 = get_status_transition_guard()
        guard2 = get_status_transition_guard()
        
        assert guard1 is guard2
    
    def test_get_input_sanitizer_singleton(self):
        """Test that get_input_sanitizer returns singleton."""
        sanitizer1 = get_input_sanitizer()
        sanitizer2 = get_input_sanitizer()
        
        assert sanitizer1 is sanitizer2
    
    def test_get_follower_range_validator_singleton(self):
        """Test that get_follower_range_validator returns singleton."""
        validator1 = get_follower_range_validator()
        validator2 = get_follower_range_validator()
        
        assert validator1 is validator2
    
    def test_get_discovery_limit_validator_singleton(self):
        """Test that get_discovery_limit_validator returns singleton."""
        validator1 = get_discovery_limit_validator()
        validator2 = get_discovery_limit_validator()
        
        assert validator1 is validator2
    
    def test_reset_validation_guards(self):
        """Test that reset clears singletons."""
        guard1 = get_status_transition_guard()
        reset_validation_guards()
        guard2 = get_status_transition_guard()
        
        assert guard1 is not guard2
    
    def test_sanitize_input_utility(self):
        """Test the sanitize_input utility function."""
        result = sanitize_input("<script>test</script>")
        assert "<script>" not in result
    
    def test_validate_instagram_url_utility(self):
        """Test the validate_instagram_url utility function."""
        assert validate_instagram_url("https://instagram.com/user") is True
        assert validate_instagram_url("https://twitter.com/user") is False
    
    def test_validate_uuid_utility(self):
        """Test the validate_uuid utility function."""
        assert validate_uuid("123e4567-e89b-12d3-a456-426614174000") is True
        assert validate_uuid("not-a-uuid") is False


# =============================================================================
# Export Tests
# =============================================================================

class TestValidationGuardsExports:
    """Test that all validation guard components are properly exported."""
    
    def test_guards_package_exports(self):
        """Test that guards package exports validation components."""
        from app.guards import (
            StatusTransitionGuard,
            InputSanitizer,
            FollowerRangeValidator,
            DiscoveryLimitValidator,
            get_status_transition_guard,
            get_input_sanitizer,
            get_follower_range_validator,
            get_discovery_limit_validator,
            validate_job_status_transition,
            validate_profile_status_transition,
            reset_validation_guards,
            sanitize_input,
            validate_instagram_url,
            validate_uuid,
        )
        
        assert StatusTransitionGuard is not None
        assert InputSanitizer is not None
        assert FollowerRangeValidator is not None
        assert DiscoveryLimitValidator is not None
        assert get_status_transition_guard is not None
        assert get_input_sanitizer is not None
        assert get_follower_range_validator is not None
        assert get_discovery_limit_validator is not None
        assert validate_job_status_transition is not None
        assert validate_profile_status_transition is not None
        assert reset_validation_guards is not None
        assert sanitize_input is not None
        assert validate_instagram_url is not None
        assert validate_uuid is not None


# =============================================================================
# All Valid Transitions Tests
# =============================================================================

class TestAllValidTransitions:
    """Test all defined valid transitions work correctly."""
    
    def test_all_valid_job_transitions(self, status_guard):
        """Test all valid job transitions succeed."""
        for from_status, valid_targets in VALID_JOB_TRANSITIONS.items():
            for to_status in valid_targets:
                result = status_guard.validate_job_transition(from_status, to_status)
                assert result == to_status
    
    def test_all_valid_profile_transitions(self, status_guard):
        """Test all valid profile transitions succeed."""
        for from_status, valid_targets in VALID_PROFILE_TRANSITIONS.items():
            for to_status in valid_targets:
                result = status_guard.validate_profile_transition(from_status, to_status)
                assert result == to_status
    
    def test_all_invalid_job_transitions(self, status_guard):
        """Test all invalid job transitions raise errors."""
        for from_status, valid_targets in VALID_JOB_TRANSITIONS.items():
            for to_status in JobStatus:
                if to_status not in valid_targets:
                    with pytest.raises(InvalidStatusTransitionError):
                        status_guard.validate_job_transition(from_status, to_status)
    
    def test_all_invalid_profile_transitions(self, status_guard):
        """Test all invalid profile transitions raise errors."""
        for from_status, valid_targets in VALID_PROFILE_TRANSITIONS.items():
            for to_status in ProfileStatus:
                if to_status not in valid_targets:
                    with pytest.raises(InvalidStatusTransitionError):
                        status_guard.validate_profile_transition(from_status, to_status)
