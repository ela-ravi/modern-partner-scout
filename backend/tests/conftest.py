"""
Pytest fixtures and configuration for PartnerScout AI tests.
"""
import os
import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_env_for_tests():
    """
    Automatically mock environment variables for all tests.
    Uses SQLite fallback to avoid needing real Supabase credentials.
    """
    env_vars = {
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "USE_SQLITE_FALLBACK": "true",
        "SQLITE_DATABASE_PATH": "./data/test_partner_scout.db",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8000",
        "API_PREFIX": "/api",
        "CORS_ORIGINS": '["http://localhost:3000","http://localhost:5173"]',
        "LLM_PROVIDER": "openai",
        "RATE_LIMIT_REQUESTS": "100",
        "RATE_LIMIT_PERIOD": "60",
    }
    with patch.dict(os.environ, env_vars, clear=False):
        # Clear the settings cache before each test
        from app.core.config import get_settings
        get_settings.cache_clear()
        yield
        # Clear the cache after each test as well
        get_settings.cache_clear()


@pytest.fixture
def test_settings():
    """Get test settings instance."""
    from app.core.config import get_settings
    return get_settings()
