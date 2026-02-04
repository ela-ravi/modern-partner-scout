"""
PartnerScout AI - Agent Routes Unit Tests (STORY-3.3.6)

Unit tests for Agent API routes:
- POST /api/agent/analyze-brand
- POST /api/agent/discover
- POST /api/agent/score
- GET /api/agent/status
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.agents import router
from app.core.config import settings
from app.core.constants import ErrorCodes, HttpStatus
from app.core.exceptions import AgentError, JobNotFoundError, ProfileNotFoundError
from app.guards.auth import ServiceContext, get_service_context
from app.models.agent import (
    BrandAnalyzerResponse,
    DiscoveryResponse,
    ScorerResponse,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Create test FastAPI application with agent routes."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api")
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
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
# Analyze Brand Endpoint Tests
# =============================================================================

class TestAnalyzeBrandEndpoint:
    """Tests for POST /api/agent/analyze-brand endpoint."""

    @pytest.mark.asyncio
    async def test_analyze_brand_success(
        self, app, client, service_key, valid_job_id
    ):
        """Test successful brand analysis."""
        mock_response = BrandAnalyzerResponse(
            job_id=valid_job_id,
            hashtags=["#sustainablefashion", "#ecofriendly"],
            keywords=["sustainable", "ethical"],
            visual_themes=["minimalist", "earth tones"],
            content_pillars=["sustainability", "fashion"],
            profiles_analyzed=3,
            posts_analyzed=45,
            analysis_duration_seconds=12.5,
        )

        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["job_id"] == valid_job_id
        assert len(data["hashtags"]) == 2
        assert len(data["keywords"]) == 2
        assert data["profiles_analyzed"] == 3
        assert data["posts_analyzed"] == 45
        assert "analysis_duration_seconds" in data

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_analyze_brand_job_not_found(
        self, app, client, service_key, valid_job_id
    ):
        """Test brand analysis when job not found returns 404."""
        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(side_effect=JobNotFoundError(valid_job_id))
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_analyze_brand_agent_error(
        self, app, client, service_key, valid_job_id
    ):
        """Test brand analysis when agent raises AgentError returns 500."""
        with patch("app.api.routes.agents.get_brand_analyzer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(
                side_effect=AgentError("LLM service unavailable")
            )
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/analyze-brand",
                json={"job_id": valid_job_id},
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"]["error"]["code"] == "AGENT_ERROR"

        app.dependency_overrides.clear()

    def test_analyze_brand_requires_service_key(
        self, app, client, valid_job_id
    ):
        """Test brand analysis without service key returns 401."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": valid_job_id},
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED

    def test_analyze_brand_invalid_job_id(self, app, client, service_key):
        """Test brand analysis with invalid job_id returns 422."""
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="n8n", is_admin=True
        )

        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": "invalid-uuid"},
            headers={"X-Service-Key": service_key},
        )
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY

        app.dependency_overrides.clear()


# =============================================================================
# Discover Profiles Endpoint Tests
# =============================================================================

class TestDiscoverProfilesEndpoint:
    """Tests for POST /api/agent/discover endpoint."""

    @pytest.mark.asyncio
    async def test_discover_profiles_success(
        self, app, client, service_key, valid_job_id
    ):
        """Test successful profile discovery."""
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
            total_discovered=10,
            deduplicated=5,
            filtered_out=15,
            discovery_duration_seconds=45.2,
        )

        with patch("app.api.routes.agents.get_discovery_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/discover",
                json={
                    "job_id": valid_job_id,
                    "hashtags": ["#sustainablefashion", "#slowfashion"],
                    "keywords": ["sustainable", "ethical"],
                    "limit": 10,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["job_id"] == valid_job_id
        assert data["total_discovered"] == 10
        assert data["deduplicated"] == 5
        assert len(data["profiles"]) == 1
        assert data["profiles"][0]["username"] == "eco_influencer"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_discover_profiles_job_not_found(
        self, app, client, service_key, valid_job_id
    ):
        """Test discovery when job not found returns 404."""
        with patch("app.api.routes.agents.get_discovery_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(side_effect=JobNotFoundError(valid_job_id))
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/discover",
                json={
                    "job_id": valid_job_id,
                    "hashtags": ["#test"],
                    "limit": 5,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND

        app.dependency_overrides.clear()

    def test_discover_profiles_validates_hashtags(
        self, app, client, service_key, valid_job_id
    ):
        """Test discovery requires at least one hashtag."""
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="n8n", is_admin=True
        )

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

        app.dependency_overrides.clear()

    def test_discover_profiles_requires_service_key(
        self, client, valid_job_id
    ):
        """Test discovery without service key returns 401."""
        response = client.post(
            "/api/agent/discover",
            json={
                "job_id": valid_job_id,
                "hashtags": ["#test"],
                "limit": 5,
            },
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED


# =============================================================================
# Score Profile Endpoint Tests
# =============================================================================

class TestScoreProfileEndpoint:
    """Tests for POST /api/agent/score endpoint."""

    @pytest.mark.asyncio
    async def test_score_profile_success(
        self, app, client, service_key, valid_job_id, valid_profile_id
    ):
        """Test successful profile scoring."""
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
            contact={"email": "contact@example.com", "source": "business_email"},
            scoring_duration_seconds=3.5,
        )

        with patch("app.api.routes.agents.get_scorer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value=mock_response)
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

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
        assert data["recommendation"] == "highly_recommended"
        assert data["contact"]["email"] == "contact@example.com"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_score_profile_not_found(
        self, app, client, service_key, valid_job_id, valid_profile_id
    ):
        """Test scoring when profile not found returns 404."""
        with patch("app.api.routes.agents.get_scorer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(
                side_effect=ProfileNotFoundError(valid_profile_id)
            )
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/score",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == "PROFILE_NOT_FOUND"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_score_profile_job_not_found(
        self, app, client, service_key, valid_job_id, valid_profile_id
    ):
        """Test scoring when job not found returns 404."""
        with patch("app.api.routes.agents.get_scorer_agent") as mock_get:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(side_effect=JobNotFoundError(valid_job_id))
            mock_get.return_value = mock_agent

            app.dependency_overrides[get_service_context] = lambda: ServiceContext(
                service_name="n8n", is_admin=True
            )

            response = client.post(
                "/api/agent/score",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                },
                headers={"X-Service-Key": service_key},
            )

        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"

        app.dependency_overrides.clear()

    def test_score_profile_requires_service_key(
        self, client, valid_job_id, valid_profile_id
    ):
        """Test scoring without service key returns 401."""
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
            },
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED


# =============================================================================
# Agent Status Endpoint Tests
# =============================================================================

class TestAgentStatusEndpoint:
    """Tests for GET /api/agent/status endpoint."""

    def test_agent_status_returns_all_agents(self, client):
        """Test agent status endpoint returns status of all agents."""
        response = client.get("/api/agent/status")

        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert "agents" in data
        assert "brand_analyzer" in data["agents"]
        assert "discovery" in data["agents"]
        assert "scorer" in data["agents"]
        assert "email_composer" in data["agents"]

        for agent_name, agent_info in data["agents"].items():
            assert "status" in agent_info
            assert "description" in agent_info

    def test_agent_status_no_auth_required(self, client):
        """Test agent status endpoint does not require authentication."""
        response = client.get("/api/agent/status")
        assert response.status_code == HttpStatus.OK


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAgentRoutesAuthentication:
    """Tests for authentication requirements on agent routes."""

    def test_analyze_brand_invalid_service_key(
        self, client, valid_job_id
    ):
        """Test brand analysis with invalid service key returns 401."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": valid_job_id},
            headers={"X-Service-Key": "invalid-key"},
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED
        assert response.json()["detail"]["error"]["code"] == ErrorCodes.INVALID_SERVICE_KEY

    def test_discover_invalid_service_key(
        self, client, valid_job_id
    ):
        """Test discovery with invalid service key returns 401."""
        response = client.post(
            "/api/agent/discover",
            json={
                "job_id": valid_job_id,
                "hashtags": ["#test"],
                "limit": 5,
            },
            headers={"X-Service-Key": "invalid-key"},
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED

    def test_score_invalid_service_key(
        self, client, valid_job_id, valid_profile_id
    ):
        """Test scoring with invalid service key returns 401."""
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
            },
            headers={"X-Service-Key": "invalid-key"},
        )
        assert response.status_code == HttpStatus.UNAUTHORIZED


