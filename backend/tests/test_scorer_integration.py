"""
PartnerScout AI - Scorer Agent Integration Tests (STORY-3.3.4)

Integration tests for the ScorerAgent that test the complete scoring flow
including API endpoints and database interactions.

Test Markers:
- @pytest.mark.integration: Tests requiring real services or database
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.agents.scorer import ScorerAgent, ScoringAnalysisOutput, get_scorer_agent
from app.core.constants import HttpStatus, ProfileStatus
from app.models.agent import ScorerRequest, ScorerResponse


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def service_key():
    """Get service key from config."""
    from app.core.config import settings
    return settings.n8n.service_key


@pytest.fixture
def sample_profile_id():
    """Generate a sample profile ID."""
    return str(uuid4())


@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_profile(sample_profile_id, sample_job_id):
    """Create a sample profile dictionary."""
    return {
        "id": sample_profile_id,
        "job_id": sample_job_id,
        "username": "integration_test_user",
        "full_name": "Integration Test User",
        "bio": "Testing profile for integration tests | contact@test.com",
        "followers_count": 50000,
        "following_count": 500,
        "posts_count": 200,
        "engagement_rate": 3.0,
        "is_verified": False,
        "is_business_account": True,
        "external_url": "https://example.com",
        "business_email": "business@test.com",
        "instagram_url": "https://instagram.com/integration_test_user",
        "status": ProfileStatus.NEW.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_job(sample_job_id):
    """Create a sample job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": str(uuid4()),
        "brand_description": "A sustainable fashion brand for testing",
        "reference_profiles": ["https://instagram.com/test"],
        "status": "scoring",
    }


@pytest.fixture
def sample_brand_dna():
    """Create sample brand DNA."""
    return {
        "hashtags": ["#sustainable", "#fashion"],
        "keywords": ["sustainable", "ethical"],
        "visual_themes": ["minimalist"],
        "content_pillars": ["sustainability"],
    }


@pytest.fixture
def sample_analysis_output():
    """Create sample LLM analysis output."""
    return ScoringAnalysisOutput(
        visual_aesthetic_match=75,
        content_theme_alignment=80,
        engagement_rate_score=85,
        follower_quality=70,
        business_indicators=80,
        activity_recency=90,
        is_fake=False,
        fake_indicators=[],
        contact_email="business@test.com",
        contact_website="https://example.com",
        email_source="business_email",
        reasoning={
            "visual_aesthetic_match": "Good visual alignment",
            "content_theme_alignment": "Strong topic match",
            "engagement_rate_score": "Above average engagement",
            "follower_quality": "Good follower ratio",
            "business_indicators": "Professional setup",
            "activity_recency": "Recent activity",
        },
        recommendation="recommended"
    )


# =============================================================================
# API Endpoint Integration Tests
# =============================================================================

@pytest.mark.integration
class TestScorerAPIEndpoint:
    """Integration tests for the scorer API endpoint."""
    
    def test_score_endpoint_requires_auth(self, client, sample_profile_id, sample_job_id):
        """Test that scoring endpoint requires authentication."""
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        # Should return 401 Unauthorized
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_score_endpoint_with_invalid_service_key(
        self,
        client,
        sample_profile_id,
        sample_job_id
    ):
        """Test scoring endpoint with invalid service key."""
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": "invalid-key"},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        # Should return 401 or 403
        assert response.status_code in [HttpStatus.UNAUTHORIZED, HttpStatus.FORBIDDEN]
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_score_endpoint_profile_not_found(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test scoring endpoint with non-existent profile."""
        from app.core.exceptions import ProfileNotFoundError
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=ProfileNotFoundError(sample_profile_id))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert "PROFILE_NOT_FOUND" in str(data)
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_score_endpoint_job_not_found(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test scoring endpoint with non-existent job."""
        from app.core.exceptions import JobNotFoundError
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=JobNotFoundError(sample_job_id))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert "JOB_NOT_FOUND" in str(data)
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_score_endpoint_success(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test successful scoring endpoint call."""
        # Create mock response
        mock_response = ScorerResponse(
            profile_id=sample_profile_id,
            job_id=sample_job_id,
            visual_aesthetic_match=75,
            content_theme_alignment=80,
            engagement_rate_score=85,
            follower_quality=70,
            business_indicators=80,
            activity_recency=90,
            final_score=80,
            recommendation="recommended",
            reasoning={"test": "reason"},
            is_fake_suspected=False,
            contact={
                "email": "test@example.com",
                "source": "business_email"
            },
            scoring_duration_seconds=2.5,
        )
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=mock_response)
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert data["final_score"] == 80
        assert data["recommendation"] == "recommended"
        assert data["is_fake_suspected"] is False
        assert data["contact"]["email"] == "test@example.com"
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_score_endpoint_with_fake_profile(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test scoring endpoint with suspected fake profile."""
        mock_response = ScorerResponse(
            profile_id=sample_profile_id,
            job_id=sample_job_id,
            visual_aesthetic_match=30,
            content_theme_alignment=25,
            engagement_rate_score=10,
            follower_quality=15,
            business_indicators=20,
            activity_recency=40,
            final_score=22,
            recommendation="not_recommended",
            reasoning={"fake_detection": "Multiple indicators"},
            is_fake_suspected=True,
            fake_indicators=[
                "High following/follower ratio",
                "Very low engagement rate"
            ],
            scoring_duration_seconds=1.5,
        )
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=mock_response)
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert data["is_fake_suspected"] is True
        assert len(data["fake_indicators"]) > 0
        assert data["recommendation"] == "not_recommended"


# =============================================================================
# Agent Status Endpoint Tests
# =============================================================================

@pytest.mark.integration
class TestAgentStatusEndpoint:
    """Tests for the agent status endpoint."""
    
    def test_agent_status_shows_scorer_available(self, client):
        """Test that agent status shows scorer as available."""
        response = client.get("/api/agent/status")
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert "agents" in data
        assert "scorer" in data["agents"]
        assert data["agents"]["scorer"]["status"] == "available"


# =============================================================================
# Full Scoring Flow Integration Tests
# =============================================================================

@pytest.mark.integration
class TestFullScoringFlow:
    """Integration tests for the complete scoring flow."""
    
    @patch('app.agents.scorer.ScorerAgent._fetch_profile')
    @patch('app.agents.scorer.ScorerAgent._fetch_job')
    @patch('app.agents.scorer.ScorerAgent._fetch_brand_dna')
    @patch('app.agents.scorer.ScorerAgent._analyze_profile')
    @patch('app.agents.scorer.ScorerAgent._store_results')
    @patch('app.agents.scorer.ScorerAgent._update_profile_status')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_full_scoring_flow(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_update_status,
        mock_store_results,
        mock_analyze,
        mock_fetch_brand,
        mock_fetch_job,
        mock_fetch_profile,
        sample_profile,
        sample_job,
        sample_brand_dna,
        sample_analysis_output,
        sample_profile_id,
        sample_job_id
    ):
        """Test the complete scoring flow from request to response."""
        # Setup mocks
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        mock_fetch_profile.return_value = sample_profile
        mock_fetch_job.return_value = sample_job
        mock_fetch_brand.return_value = sample_brand_dna
        mock_analyze.return_value = sample_analysis_output
        mock_store_results.return_value = ({}, None)
        mock_update_status.return_value = None
        
        # Create scoring service mock
        mock_scoring_service = Mock()
        mock_scoring_service.calculate_final_score_from_dict.return_value = 80
        mock_scoring_service.get_recommendation.return_value = "recommended"
        
        # Create agent
        agent = ScorerAgent(scoring_service=mock_scoring_service)
        
        # Create request
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=sample_job_id
        )
        
        # Run scoring
        response = await agent.run(request)
        
        # Verify response
        assert isinstance(response, ScorerResponse)
        assert response.final_score == 80
        assert response.recommendation == "recommended"
        
        # Verify flow was executed
        mock_fetch_profile.assert_called_once()
        mock_fetch_job.assert_called_once()
        mock_fetch_brand.assert_called_once()
        mock_analyze.assert_called_once()
        mock_store_results.assert_called_once()
        mock_update_status.assert_called_once()
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_scoring_with_provided_data(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        sample_profile,
        sample_brand_dna,
        sample_analysis_output,
        sample_profile_id,
        sample_job_id
    ):
        """Test scoring with profile data and brand DNA provided in request."""
        # Setup mocks
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        # Create mocks
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = {
            "id": sample_job_id,
            "brand_description": "Test brand"
        }
        
        mock_score_repo = Mock()
        mock_score_repo.get_by_profile_id_optional.return_value = None
        mock_score_repo.create_full_score.return_value = {"id": str(uuid4())}
        
        mock_contact_repo = Mock()
        mock_contact_repo.upsert.return_value = {"id": str(uuid4())}
        
        mock_profile_repo = Mock()
        mock_profile_repo.update_status.return_value = sample_profile
        
        mock_scoring_service = Mock()
        mock_scoring_service.calculate_final_score_from_dict.return_value = 80
        mock_scoring_service.get_recommendation.return_value = "recommended"
        
        # Create agent
        agent = ScorerAgent(
            job_repo=mock_job_repo,
            profile_repo=mock_profile_repo,
            score_repo=mock_score_repo,
            contact_repo=mock_contact_repo,
            scoring_service=mock_scoring_service
        )
        
        # Mock LLM analysis
        agent._analyze_profile = AsyncMock(return_value=sample_analysis_output)
        
        # Create request with data
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=sample_job_id,
            profile_data=sample_profile,
            brand_dna=sample_brand_dna
        )
        
        # Run scoring
        response = await agent.run(request)
        
        # Verify response
        assert isinstance(response, ScorerResponse)
        assert response.final_score == 80


# =============================================================================
# Error Handling Integration Tests
# =============================================================================

@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling."""
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_agent_error_returns_500(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test that agent errors return 500."""
        from app.core.exceptions import AgentError
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(
            side_effect=AgentError(
                message="Test error",
                agent_name="scorer",
                details={"test": "details"}
            )
        )
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        data = response.json()
        assert "AGENT_ERROR" in str(data)
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_unexpected_error_returns_500(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test that unexpected errors return 500."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=RuntimeError("Unexpected error"))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        data = response.json()
        assert "INTERNAL_ERROR" in str(data)


# =============================================================================
# Request Validation Integration Tests
# =============================================================================

@pytest.mark.integration
class TestRequestValidation:
    """Integration tests for request validation."""
    
    def test_missing_profile_id(self, client, service_key, sample_job_id):
        """Test request validation for missing profile_id."""
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "job_id": sample_job_id,
            }
        )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
    
    def test_missing_job_id(self, client, service_key, sample_profile_id):
        """Test request validation for missing job_id."""
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
            }
        )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
    
    def test_invalid_uuid_format(self, client, service_key):
        """Test request validation for invalid UUID format."""
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": "not-a-valid-uuid",
                "job_id": "also-not-valid",
            }
        )
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422


# =============================================================================
# Response Format Integration Tests
# =============================================================================

@pytest.mark.integration
class TestResponseFormat:
    """Integration tests for response format validation."""
    
    @patch('app.api.routes.agents.get_scorer_agent')
    def test_response_contains_all_dimensions(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_profile_id,
        sample_job_id
    ):
        """Test that response contains all 6 scoring dimensions."""
        mock_response = ScorerResponse(
            profile_id=sample_profile_id,
            job_id=sample_job_id,
            visual_aesthetic_match=75,
            content_theme_alignment=80,
            engagement_rate_score=85,
            follower_quality=70,
            business_indicators=80,
            activity_recency=90,
            final_score=80,
            recommendation="recommended",
        )
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=mock_response)
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/score",
            headers={"X-Service-Key": service_key},
            json={
                "profile_id": sample_profile_id,
                "job_id": sample_job_id,
            }
        )
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        # Verify all dimensions are present
        assert "visual_aesthetic_match" in data
        assert "content_theme_alignment" in data
        assert "engagement_rate_score" in data
        assert "follower_quality" in data
        assert "business_indicators" in data
        assert "activity_recency" in data
        
        # Verify core fields
        assert "final_score" in data
        assert "recommendation" in data
        assert "is_fake_suspected" in data
        
        # Verify dimension scores are within range
        for dim in ["visual_aesthetic_match", "content_theme_alignment", 
                    "engagement_rate_score", "follower_quality",
                    "business_indicators", "activity_recency"]:
            assert 0 <= data[dim] <= 100
        
        assert 0 <= data["final_score"] <= 100
