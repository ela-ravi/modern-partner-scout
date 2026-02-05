"""
Unit tests for configuration management.
TDD: These tests are written FIRST, before implementing config.py
"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test suite for Settings configuration class."""

    def test_settings_loads_from_environment(self):
        """Settings should load values from environment variables."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "testing",
            "DEBUG": "true",
            "USE_SQLITE_FALLBACK": "true",
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            assert settings.environment == "testing"
            assert settings.debug is True

    def test_settings_has_default_values(self):
        """Settings should have sensible defaults."""
        # Clear conftest mock by using clear=True to see actual defaults
        # Note: conftest sets ENVIRONMENT=testing, so we test other defaults
        with patch.dict(os.environ, {
            "USE_SQLITE_FALLBACK": "true",
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            # Note: environment defaults to "development" but conftest sets "testing"
            # This is expected behavior - test other defaults
            assert settings.api_host == "0.0.0.0"
            assert settings.api_port == 8000

    def test_settings_validates_database_config(self):
        """Settings should require database config when not using SQLite fallback."""
        with patch.dict(os.environ, {
            "USE_SQLITE_FALLBACK": "false",
            "SUPABASE_URL": "",
            "SUPABASE_KEY": "",
        }, clear=True):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            with pytest.raises(ValueError, match="SUPABASE_URL"):
                Settings()

    def test_settings_cors_origins_parses_json(self):
        """CORS origins should parse from JSON string."""
        with patch.dict(os.environ, {
            "USE_SQLITE_FALLBACK": "true",
            "CORS_ORIGINS": '["http://localhost:3000","http://localhost:5173"]',
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            assert len(settings.cors_origins) == 2
            assert "http://localhost:3000" in settings.cors_origins

    def test_settings_llm_provider_validates(self):
        """LLM provider should only accept valid values."""
        with patch.dict(os.environ, {
            "USE_SQLITE_FALLBACK": "true",
            "LLM_PROVIDER": "invalid_provider",
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            with pytest.raises(ValueError):
                Settings()

    def test_get_settings_singleton(self):
        """get_settings should return cached instance."""
        from app.core.config import get_settings
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2


class TestEnvironmentValidation:
    """Test environment-specific validation."""

    def test_production_requires_all_secrets(self):
        """Production environment should require all secrets."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
            "USE_SQLITE_FALLBACK": "false",
            # Missing SUPABASE_SERVICE_ROLE_KEY
        }, clear=True):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            with pytest.raises(ValueError, match="SUPABASE_SERVICE_ROLE_KEY"):
                Settings()

    def test_development_allows_sqlite_fallback(self):
        """Development can use SQLite fallback."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "USE_SQLITE_FALLBACK": "true",
            "SQLITE_DATABASE_PATH": "./test.db",
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            assert settings.use_sqlite_fallback is True


class TestSettingsProperties:
    """Test Settings helper properties."""

    def test_is_development_property(self):
        """is_development should return True for development environment."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "USE_SQLITE_FALLBACK": "true",
        }, clear=False):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            assert settings.is_development is True
            assert settings.is_production is False

    def test_is_production_property(self):
        """is_production should return True for production environment."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "USE_SQLITE_FALLBACK": "false",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
            "SUPABASE_JWT_SECRET": "test-jwt-secret",
            "OPENAI_API_KEY": "sk-test-key",  # Required for production
        }, clear=True):
            from app.core.config import Settings, get_settings
            get_settings.cache_clear()
            settings = Settings()
            
            assert settings.is_production is True
            assert settings.is_development is False
