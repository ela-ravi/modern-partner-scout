"""
Integration Tests for STORY-3.3.6: Agent API Routes

These tests validate the full request/response cycle for agent endpoints,
including authentication, validation, and integration with the main application.

Tests the following endpoints:
- POST /api/agent/analyze-brand
- POST /api/agent/discover
- POST /api/agent/score
- GET /api/agent/status

Note: These tests use mocked agents to avoid requiring LLM/Apify services.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import ErrorCodes, HttpStatus
from app.core.exceptions import AgentError, JobNotFoundError, ProfileNotFoundError
from app.models.agent import (
    BrandAnalyzerResponse,
    DiscoveryResponse,
    ScorerResponse,
)


# =============================================================================
# Pytest Markers
# =============================================================================

pytestmark = pytest.mark.integration


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create test client for the full application."""
    return TestClient(app)


@pytest.fixture
def service_key():
    """Get service key for authentication."""
    return settings.n8n.service_key


@pytest.fixture
def valid_job_id():
    """Generate a valid job UUID."""
    return str(uuid4())


@pytest.fixture
def valid_profile_id():
    """Generate a valid profile UUID."""
    return str(uuid4())


# =============================================================================
# Integration Test: Full Application Agent Endpoints
# =============================================================================

class TestAgentEndpointsIntegration:
    """Integration tests for agent endpoints with full application."""

    def test_agent_status_endpoint_integration(self, client):
        """Test GET /api/agent/status with full application."""
        response = client.get("/api/agent/status")

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert "agents" in data
        assert "brand_analyzer" in data["agents"]
        assert data["agents"]["brand_analyzer"]["status"] == "available"
        assert data["agents"]["discovery"]["status"] == "available"
        assert data["agents"]["scorer"]["status"] == "available"

    @pytest.mark.asyncio
    async def test_analyze_brand_full_flow(
        self, client, service_key, valid_job_id
    ):
        """Test POST /api/agent/analyze-brand full request/response cycle."""
        mock_response = BrandAnalyzerResponse(
            job_id=valid_job_id,
            hashtags=["#sustainablefashion", "#ecofriendly"],
            keywords=["sustainable", "ethical"],
            visual_themes=["minimalist"],
            content_pillars=["sustainability"],
            profiles_analyzed=2,
            posts_analyzed=30,
            analysis_duration_seconds=10.0,
        )

        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["job_id"] == valid_job_id
        assert len(data["hashtags"]) >= 1
        assert data["profiles_analyzed"] == 2

    @pytest.mark.asyncio
    async def test_discover_full_flow(
        self, client, service_key, valid_job_id
    ):
        """Test POST /api/agent/discover full request/response cycle."""
        mock_response = DiscoveryResponse(
            job_id=valid_job_id,
            profiles=[
                {
                    "id": str(uuid4()),
                    "username": "eco_influencer",
                    "followers_count": 75000,
                    "status": "new",
                }
            ],
            total_discovered=5,
            deduplicated=2,
            filtered_out=3,
            discovery_duration_seconds=30.0,
        )

        with patch("app.api.routes.agents.get_discovery_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/discover",
                json={
                    "job_id": valid_job_id,
                    "hashtags": ["#sustainablefashion", "#slowfashion"],
                    "keywords": ["sustainable"],
                    "limit": 10,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["job_id"] == valid_job_id
        assert data["total_discovered"] == 5
        assert len(data["profiles"]) == 1

    @pytest.mark.asyncio
    async def test_score_full_flow(
        self, client, service_key, valid_job_id, valid_profile_id
    ):
        """Test POST /api/agent/score full request/response cycle."""
        mock_response = ScorerResponse(
            profile_id=valid_profile_id,
            job_id=valid_job_id,
            visual_aesthetic_match=75,
            content_theme_alignment=82,
            engagement_rate_score=88,
            follower_quality=70,
            business_indicators=85,
            activity_recency=90,
            final_score=82,
            recommendation="highly_recommended",
            is_fake_suspected=False,
            contact={"email": "contact@example.com", "source": "bio"},
            scoring_duration_seconds=3.5,
        )

        with patch("app.api.routes.agents.get_scorer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/score",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["profile_id"] == valid_profile_id
        assert data["job_id"] == valid_job_id
        assert data["final_score"] == 82
        assert "contact" in data


# =============================================================================
# Integration Test: Error Handling
# =============================================================================

class TestAgentErrorHandlingIntegration:
    """Integration tests for agent endpoint error handling."""

    @pytest.mark.asyncio
    async def test_analyze_brand_job_not_found_returns_404(
        self, client, service_key, valid_job_id
    ):
        """Test brand analysis returns 404 when job not found."""
        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(
                side_effect=JobNotFoundError(valid_job_id)
            )
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND
        assert response.json()["detail"]["error"]["code"] == "JOB_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_score_profile_not_found_returns_404(
        self, client, service_key, valid_job_id, valid_profile_id
    ):
        """Test scoring returns 404 when profile not found."""
        with patch("app.api.routes.agents.get_scorer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(
                side_effect=ProfileNotFoundError(valid_profile_id)
            )
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/score",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND
        assert response.json()["detail"]["error"]["code"] == "PROFILE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_analyze_brand_agent_error_returns_500(
        self, client, service_key, valid_job_id
    ):
        """Test brand analysis returns 500 when agent fails."""
        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(
                side_effect=AgentError("LLM unavailable")
            )
            mock_get.return_value = mock_agent

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        assert response.json()["detail"]["error"]["code"] == "AGENT_ERROR"


# =============================================================================
# Integration Test: OpenAPI Schema
# =============================================================================

class TestAgentOpenAPISchema:
    """Integration tests for agent routes in OpenAPI schema."""

    def test_agent_routes_in_openapi(self, client):
        """Test that agent routes are documented in OpenAPI."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        paths = data.get("paths", {})

        assert "/api/agent/analyze-brand" in paths
        assert "post" in paths["/api/agent/analyze-brand"]

        assert "/api/agent/discover" in paths
        assert "post" in paths["/api/agent/discover"]

        assert "/api/agent/score" in paths
        assert "post" in paths["/api/agent/score"]

        assert "/api/agent/status" in paths
        assert "get" in paths["/api/agent/status"]

    def test_root_endpoint_lists_agent_routes(self, client):
        """Test that root endpoint includes agent route information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "agents" in data["endpoints"]
        agents = data["endpoints"]["agents"]
        assert "analyze_brand" in agents
        assert "discover" in agents
        assert "score" in agents
        assert "status" in agents or "analyze_brand" in agents


# =============================================================================
# Integration Test: Request Validation
# =============================================================================

class TestAgentRequestValidation:
    """Integration tests for agent request validation."""

    def test_discover_requires_hashtags(
        self, client, service_key, valid_job_id
    ):
        """Test discovery endpoint validates hashtags requirement."""
        response = client.post(
            "/api/agent/discover",
            json={
                "job_id": valid_job_id,
                "hashtags": [],
                "limit": 5,
            },
            headers={"X-Service-Key": service_key},
        )
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY

    def test_analyze_brand_validates_job_id_format(
        self, client, service_key
    ):
        """Test brand analysis validates job_id format."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": "not-a-valid-uuid"},
            headers={"X-Service-Key": service_key},
        )
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY

    def test_score_validates_profile_id_format(
        self, client, service_key, valid_job_id
    ):
        """Test scoring validates profile_id format."""
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": "invalid-uuid",
                "job_id": valid_job_id,
            },
            headers={"X-Service-Key": service_key},
        )
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY


# =============================================================================
# Integration Test: Authentication
# =============================================================================

class TestAgentAuthenticationIntegration:
    """Integration tests for agent endpoint authentication."""

    def test_analyze_brand_requires_service_key(
        self, client, valid_job_id
    ):
        """Test brand analysis requires service key."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": valid_job_id},
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED

    def test_discover_requires_service_key(
        self, client, valid_job_id
    ):
        """Test discovery requires service key."""
        response = client.post(
            "/api/agent/discover",
            json={
                "job_id": valid_job_id,
                "hashtags": ["#test"],
                "limit": 5,
            },
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED

    def test_score_requires_service_key(
        self, client, valid_job_id, valid_profile_id
    ):
        """Test scoring requires service key."""
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
            },
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED

    def test_agent_status_no_auth_required(self, client):
        """Test agent status does not require authentication."""
        response = client.get("/api/agent/status")
        assert response.status_code == HttpStatus.OK


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
