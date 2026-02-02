"""
Tests for STORY-2.1.1: Configuration Management

These tests validate that the configuration system works correctly,
including environment config, constants, exceptions, and YAML configs.
"""

import pytest
from typing import Dict, Any


class TestEnvironmentConfig:
    """Tests for app/core/config.py (TASK-2.1.1.1)"""
    
    def test_config_loads(self):
        """Test that settings can be loaded from environment."""
        from app.core.config import settings
        
        # Should have a URL (may be None if not set, but should not raise)
        assert settings is not None
        assert hasattr(settings, 'supabase')
        assert hasattr(settings, 'openai')
        assert hasattr(settings, 'gemini')
        assert hasattr(settings, 'ollama')
        assert hasattr(settings, 'apify')
        assert hasattr(settings, 'n8n')
    
    def test_supabase_settings_exist(self):
        """Test that Supabase settings are accessible."""
        from app.core.config import settings
        
        # Access nested settings
        assert hasattr(settings.supabase, 'url')
        assert hasattr(settings.supabase, 'anon_key')
        assert hasattr(settings.supabase, 'service_role_key')
        assert hasattr(settings.supabase, 'jwt_secret')
    
    def test_llm_provider_settings(self):
        """Test that LLM provider settings are accessible."""
        from app.core.config import settings
        
        # Check OpenAI settings
        assert hasattr(settings.openai, 'api_key')
        assert hasattr(settings.openai, 'model')
        
        # Check Gemini settings
        assert hasattr(settings.gemini, 'api_key')
        assert hasattr(settings.gemini, 'model')
        
        # Check Ollama settings
        assert hasattr(settings.ollama, 'base_url')
        assert hasattr(settings.ollama, 'model')
    
    def test_apify_settings(self):
        """Test that Apify settings are accessible."""
        from app.core.config import settings
        
        assert hasattr(settings.apify, 'api_key')
        assert hasattr(settings.apify, 'instagram_scraper_id')
        assert hasattr(settings.apify, 'hashtag_scraper_id')
    
    def test_n8n_settings(self):
        """Test that N8N settings are accessible."""
        from app.core.config import settings
        
        assert hasattr(settings.n8n, 'service_key')
        assert hasattr(settings.n8n, 'webhook_url')
    
    def test_cors_origins_list(self):
        """Test that CORS origins are parsed correctly."""
        from app.core.config import settings
        
        origins = settings.cors_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0
    
    def test_backward_compatibility_properties(self):
        """Test backward compatibility properties (SUPABASE_URL, etc.)."""
        from app.core.config import settings
        
        # These properties should work for backward compatibility
        assert settings.SUPABASE_URL is not None or settings.supabase.url is not None


class TestConstants:
    """Tests for app/core/constants.py (TASK-2.1.1.2)"""
    
    def test_http_status_codes(self):
        """Test HttpStatus class has expected values."""
        from app.core.constants import HttpStatus
        
        assert HttpStatus.OK == 200
        assert HttpStatus.CREATED == 201
        assert HttpStatus.BAD_REQUEST == 400
        assert HttpStatus.UNAUTHORIZED == 401
        assert HttpStatus.FORBIDDEN == 403
        assert HttpStatus.NOT_FOUND == 404
        assert HttpStatus.INTERNAL_SERVER_ERROR == 500
    
    def test_error_codes(self):
        """Test ErrorCodes class has expected values."""
        from app.core.constants import ErrorCodes
        
        assert ErrorCodes.UNAUTHORIZED == "UNAUTHORIZED"
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"
        assert ErrorCodes.DAILY_LIMIT_EXCEEDED == "DAILY_LIMIT_EXCEEDED"
        assert ErrorCodes.AGENT_ERROR == "AGENT_ERROR"
    
    def test_job_status_enum(self):
        """Test JobStatus enum has all expected values."""
        from app.core.constants import JobStatus
        
        assert JobStatus.PENDING == "pending"
        assert JobStatus.ANALYZING == "analyzing"
        assert JobStatus.DISCOVERING == "discovering"
        assert JobStatus.SCORING == "scoring"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
        assert JobStatus.CANCELLED == "cancelled"
    
    def test_job_status_helper_methods(self):
        """Test JobStatus helper methods."""
        from app.core.constants import JobStatus
        
        active = JobStatus.active_statuses()
        assert JobStatus.ANALYZING in active
        assert JobStatus.PENDING not in active
        
        terminal = JobStatus.terminal_statuses()
        assert JobStatus.COMPLETED in terminal
        assert JobStatus.FAILED in terminal
    
    def test_profile_status_enum(self):
        """Test ProfileStatus enum has all expected values."""
        from app.core.constants import ProfileStatus
        
        assert ProfileStatus.NEW == "new"
        assert ProfileStatus.PROCESSING == "processing"
        assert ProfileStatus.SCORED == "scored"
        assert ProfileStatus.FAILED == "failed"
    
    def test_valid_job_transitions(self):
        """Test valid job status transitions."""
        from app.core.constants import (
            JobStatus,
            VALID_JOB_TRANSITIONS,
            is_valid_job_transition
        )
        
        # Valid transitions
        assert is_valid_job_transition(JobStatus.PENDING, JobStatus.ANALYZING)
        assert is_valid_job_transition(JobStatus.ANALYZING, JobStatus.DISCOVERING)
        assert is_valid_job_transition(JobStatus.SCORING, JobStatus.COMPLETED)
        
        # Invalid transitions
        assert not is_valid_job_transition(JobStatus.PENDING, JobStatus.COMPLETED)
        assert not is_valid_job_transition(JobStatus.COMPLETED, JobStatus.PENDING)
    
    def test_valid_profile_transitions(self):
        """Test valid profile status transitions."""
        from app.core.constants import (
            ProfileStatus,
            is_valid_profile_transition
        )
        
        # Valid transitions
        assert is_valid_profile_transition(ProfileStatus.NEW, ProfileStatus.PROCESSING)
        assert is_valid_profile_transition(ProfileStatus.PROCESSING, ProfileStatus.SCORED)
        
        # Invalid transitions
        assert not is_valid_profile_transition(ProfileStatus.NEW, ProfileStatus.SCORED)
        assert not is_valid_profile_transition(ProfileStatus.SCORED, ProfileStatus.NEW)
    
    def test_tables_class(self):
        """Test Tables class has expected table names."""
        from app.core.constants import Tables
        
        assert Tables.DISCOVERY_JOBS == "discovery_jobs"
        assert Tables.BRAND_DNA == "brand_dna"
        assert Tables.DISCOVERED_PROFILES == "discovered_profiles"
        assert Tables.PROFILE_SCORES == "profile_scores"
        assert Tables.PROFILE_CONTACTS == "profile_contacts"
    
    def test_defaults_class(self):
        """Test Defaults class has expected default values."""
        from app.core.constants import Defaults
        
        assert Defaults.MIN_REFERENCE_PROFILES == 2
        assert Defaults.MAX_REFERENCE_PROFILES == 10
        assert Defaults.DEFAULT_DISCOVERY_LIMIT == 50
        
        # Verify weights sum to 1.0
        total_weight = (
            Defaults.WEIGHT_VISUAL_AESTHETIC +
            Defaults.WEIGHT_CONTENT_THEME +
            Defaults.WEIGHT_ENGAGEMENT_RATE +
            Defaults.WEIGHT_FOLLOWER_QUALITY +
            Defaults.WEIGHT_BUSINESS_INDICATORS +
            Defaults.WEIGHT_ACTIVITY_RECENCY
        )
        assert abs(total_weight - 1.0) < 0.001


class TestExceptions:
    """Tests for app/core/exceptions.py (TASK-2.1.1.3)"""
    
    def test_base_exception(self):
        """Test PartnerScoutError base class."""
        from app.core.exceptions import PartnerScoutError
        
        error = PartnerScoutError("Test error", code="TEST_ERROR", status_code=400)
        
        assert str(error) == "[TEST_ERROR] Test error"
        assert error.code == "TEST_ERROR"
        assert error.status_code == 400
        
        error_dict = error.to_dict()
        assert error_dict["error"]["code"] == "TEST_ERROR"
        assert error_dict["error"]["message"] == "Test error"
    
    def test_business_error(self):
        """Test BusinessError class."""
        from app.core.exceptions import BusinessError
        from app.core.constants import HttpStatus
        
        error = BusinessError("Business rule violated")
        
        assert error.status_code == HttpStatus.BAD_REQUEST
    
    def test_not_found_error(self):
        """Test NotFoundError class."""
        from app.core.exceptions import NotFoundError
        from app.core.constants import HttpStatus
        
        error = NotFoundError("Resource not found", resource_type="job", resource_id="123")
        
        assert error.status_code == HttpStatus.NOT_FOUND
        assert error.details["resource_type"] == "job"
        assert error.details["resource_id"] == "123"
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError class."""
        from app.core.exceptions import UnauthorizedError
        from app.core.constants import HttpStatus
        
        error = UnauthorizedError()
        
        assert error.status_code == HttpStatus.UNAUTHORIZED
    
    def test_forbidden_error(self):
        """Test ForbiddenError class."""
        from app.core.exceptions import ForbiddenError
        from app.core.constants import HttpStatus
        
        error = ForbiddenError("Access denied", resource_type="job", resource_id="123")
        
        assert error.status_code == HttpStatus.FORBIDDEN
        assert error.details["resource_type"] == "job"
    
    def test_agent_error(self):
        """Test AgentError class."""
        from app.core.exceptions import AgentError
        
        error = AgentError("Agent failed", agent_name="scorer")
        
        assert error.details["agent"] == "scorer"
    
    def test_job_not_found_error(self):
        """Test JobNotFoundError class."""
        from app.core.exceptions import JobNotFoundError
        
        error = JobNotFoundError("job-123")
        
        assert "job-123" in error.message
        assert error.details["resource_id"] == "job-123"
    
    def test_invalid_status_transition_error(self):
        """Test InvalidStatusTransitionError class."""
        from app.core.exceptions import InvalidStatusTransitionError
        
        error = InvalidStatusTransitionError("pending", "completed", "job")
        
        assert "pending" in error.message
        assert "completed" in error.message
        assert error.details["from_status"] == "pending"
        assert error.details["to_status"] == "completed"
    
    def test_daily_limit_exceeded_error(self):
        """Test DailyLimitExceededError class."""
        from app.core.exceptions import DailyLimitExceededError
        from app.core.constants import HttpStatus
        
        error = DailyLimitExceededError(limit=10)
        
        assert error.status_code == HttpStatus.TOO_MANY_REQUESTS
        assert error.details["limit"] == 10


class TestYAMLConfig:
    """Tests for app/core/settings/ (TASK-2.1.1.4)"""
    
    def test_yaml_config_loads(self):
        """Test that YAML configs load successfully."""
        from app.core.settings import get_agents_config, get_scoring_config, get_limits_config
        
        agents = get_agents_config()
        assert agents is not None
        assert "agents" in agents
        
        scoring = get_scoring_config()
        assert scoring is not None
        assert "weights" in scoring
        
        limits = get_limits_config()
        assert limits is not None
        assert "rate_limits" in limits
    
    def test_scoring_weights_sum_to_one(self):
        """Test that scoring weights sum to 1.0."""
        from app.core.settings import get_scoring_config
        
        config = get_scoring_config()
        weights = config["weights"]
        total = sum(weights.values())
        
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"
    
    def test_scoring_weights_structure(self):
        """Test scoring weights have correct dimensions."""
        from app.core.settings import get_scoring_weights
        
        weights = get_scoring_weights()
        
        expected_dimensions = [
            "visual_aesthetic_match",
            "content_theme_alignment",
            "engagement_rate_score",
            "follower_quality",
            "business_indicators",
            "activity_recency",
        ]
        
        for dim in expected_dimensions:
            assert dim in weights, f"Missing dimension: {dim}"
            assert 0 <= weights[dim] <= 1, f"Invalid weight for {dim}: {weights[dim]}"
    
    def test_agents_config_structure(self):
        """Test agents config has expected structure."""
        from app.core.settings import get_agents_config
        
        config = get_agents_config()
        agents = config.get("agents", {})
        
        expected_agents = ["brand_analyzer", "discovery", "scorer", "email_composer"]
        
        for agent in expected_agents:
            assert agent in agents, f"Missing agent: {agent}"
            assert "name" in agents[agent]
            assert "enabled" in agents[agent]
    
    def test_get_agent_config(self):
        """Test getting specific agent configuration."""
        from app.core.settings import get_agent_config
        
        scorer_config = get_agent_config("scorer")
        
        assert scorer_config["name"] == "Profile Scorer"
        assert scorer_config["enabled"] == True
    
    def test_get_agent_config_not_found(self):
        """Test getting non-existent agent raises error."""
        from app.core.settings import get_agent_config, ConfigurationError
        
        with pytest.raises(ConfigurationError):
            get_agent_config("non_existent_agent")
    
    def test_limits_config_structure(self):
        """Test limits config has expected structure."""
        from app.core.settings import get_limits_config
        
        config = get_limits_config()
        
        assert "rate_limits" in config
        assert "timeouts" in config
        assert "retry" in config
    
    def test_get_rate_limits(self):
        """Test getting rate limits."""
        from app.core.settings import get_rate_limits
        
        limits = get_rate_limits()
        
        assert "jobs" in limits
        assert "daily_limit" in limits["jobs"]
    
    def test_get_timeouts(self):
        """Test getting timeouts."""
        from app.core.settings import get_timeouts
        
        timeouts = get_timeouts()
        
        assert "api_request" in timeouts
        assert isinstance(timeouts["api_request"], int)
    
    def test_validate_scoring_weights(self):
        """Test scoring weights validation."""
        from app.core.settings import validate_scoring_weights
        
        # Should not raise an exception
        result = validate_scoring_weights()
        assert result == True
    
    def test_reload_configs(self):
        """Test that configs can be reloaded."""
        from app.core.settings import reload_configs, get_scoring_config
        
        # Get initial config
        config1 = get_scoring_config()
        
        # Reload
        reload_configs()
        
        # Get config again
        config2 = get_scoring_config()
        
        # Should be equal (same files)
        assert config1 == config2


class TestCoreModuleImports:
    """Test that the core module exports everything correctly."""
    
    def test_import_from_core(self):
        """Test importing from app.core module."""
        from app.core import (
            settings,
            JobStatus,
            ProfileStatus,
            ErrorCodes,
            HttpStatus,
            NotFoundError,
            UnauthorizedError,
            BusinessError,
            Tables,
            Defaults,
        )
        
        assert settings is not None
        assert JobStatus.PENDING == "pending"
        assert ProfileStatus.NEW == "new"
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"
        assert HttpStatus.OK == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
