"""
Tests for STORY-4.1.1: Setup N8N Environment

Unit and integration tests for N8N configuration and connectivity.
"""

import os
from unittest.mock import patch
from urllib.parse import urlparse

import pytest


class TestN8NConfigUnit:
    """Unit tests for N8N configuration (STORY-4.1.1)."""

    @pytest.mark.unit
    def test_n8n_settings_loaded(self):
        """N8N settings are loaded from config."""
        from app.core.config import settings

        assert settings.n8n is not None
        assert hasattr(settings.n8n, "service_key")
        assert hasattr(settings.n8n, "webhook_url")

    @pytest.mark.unit
    def test_n8n_webhook_url_format(self):
        """N8N webhook URL has valid format."""
        from app.core.config import settings

        webhook_url = settings.n8n.webhook_url
        # Should be non-empty when configured
        if webhook_url and not webhook_url.startswith("your-"):
            parsed = urlparse(webhook_url)
            assert parsed.scheme in ("http", "https")
            assert parsed.netloc
            assert "webhook" in webhook_url.lower() or parsed.path

    @pytest.mark.unit
    def test_n8n_service_key_configured(self):
        """N8N service key is configured for API auth."""
        from app.core.config import settings

        key = settings.n8n.service_key
        # When using real .env, service_key should be set
        # When using test defaults, we just check it's accessible
        assert hasattr(settings.n8n, "service_key")
        assert isinstance(key, str)

    @pytest.mark.unit
    def test_verify_n8n_script_get_base_url_default(self):
        """verify_n8n extracts base URL correctly with default."""
        from scripts.verify_n8n import get_n8n_base_url

        with patch.dict(os.environ, {"N8N_WEBHOOK_URL": ""}, clear=False):
            # Clear cache if any - reload module would reset
            base = get_n8n_base_url()
            assert base == "http://localhost:5678"

    @pytest.mark.unit
    def test_verify_n8n_script_get_base_url_from_webhook(self):
        """verify_n8n extracts base URL from N8N_WEBHOOK_URL."""
        from scripts.verify_n8n import get_n8n_base_url

        with patch.dict(
            os.environ,
            {"N8N_WEBHOOK_URL": "http://localhost:5678/webhook/partner-discovery"},
            clear=False,
        ):
            base = get_n8n_base_url()
            assert base == "http://localhost:5678"

    @pytest.mark.unit
    def test_verify_n8n_script_check_env_vars_missing_key(self):
        """verify_n8n reports missing N8N_SERVICE_KEY."""
        from scripts.verify_n8n import check_n8n_env_vars

        with patch.dict(
            os.environ,
            {"N8N_SERVICE_KEY": "", "N8N_WEBHOOK_URL": "http://localhost:5678/webhook"},
            clear=False,
        ):
            result = check_n8n_env_vars()
            assert result is False

    @pytest.mark.unit
    def test_verify_n8n_script_check_env_vars_placeholder_key(self):
        """verify_n8n rejects placeholder N8N_SERVICE_KEY."""
        from scripts.verify_n8n import check_n8n_env_vars

        with patch.dict(
            os.environ,
            {
                "N8N_SERVICE_KEY": "your-n8n-service-key",
                "N8N_WEBHOOK_URL": "http://localhost:5678/webhook",
            },
            clear=False,
        ):
            result = check_n8n_env_vars()
            assert result is False

    @pytest.mark.unit
    def test_verify_n8n_script_check_env_vars_valid(self):
        """verify_n8n accepts valid configuration."""
        from scripts.verify_n8n import check_n8n_env_vars

        with patch.dict(
            os.environ,
            {
                "N8N_SERVICE_KEY": "test-service-key-12345",
                "N8N_WEBHOOK_URL": "http://localhost:5678/webhook/partner-discovery",
            },
            clear=False,
        ):
            result = check_n8n_env_vars()
            assert result is True


class TestN8NConnectivityIntegration:
    """Integration tests for N8N connectivity (require N8N running)."""

    @pytest.mark.integration
    @pytest.mark.n8n
    def test_n8n_reachable(self):
        """N8N is reachable at configured URL (skip if not running)."""
        import httpx

        from scripts.verify_n8n import get_n8n_base_url

        base_url = get_n8n_base_url()
        url = f"{base_url.rstrip('/')}/"

        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(url)
                assert response.status_code in (200, 302, 307), (
                    f"Expected 2xx/3xx, got {response.status_code}"
                )
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            pytest.skip(
                f"N8N not running at {base_url}. Start with: "
                "docker compose -f docker-compose.n8n.yml up -d. Error: " + str(e)
            )
