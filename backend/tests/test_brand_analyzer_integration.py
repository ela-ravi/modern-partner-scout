"""
PartnerScout AI - Brand Analyzer Integration Tests (STORY-3.3.2)

Integration tests for the BrandAnalyzerAgent that test:
- Full agent execution flow with mocked external services
- API endpoint integration
- Database interaction
- Error handling across components

Test Markers:
- @pytest.mark.integration: Integration tests requiring more setup
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.agents.brand_analyzer import BrandAnalyzerAgent, BrandAnalysisOutput
from app.core.config import settings
from app.core.constants import HttpStatus
from app.models.agent import BrandAnalyzerRequest, BrandAnalyzerResponse


# =============================================================================
# Test Client and Auth Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def service_key():
    """Get service key for internal API authentication."""
    return settings.supabase.service_role_key


def service_headers(key: str) -> dict:
    """Create service key headers."""
    return {"X-Service-Key": key}


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_job(sample_job_id):
    """Create a sample job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": str(uuid4()),
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_profile_data():
    """Create sample Instagram profile data."""
    return [
        {
            "username": "everlane",
            "fullName": "Everlane",
            "biography": "Radical transparency. #sustainablefashion",
            "followersCount": 1500000,
            "followsCount": 200,
            "postsCount": 3500,
            "isBusinessAccount": True,
            "businessEmail": "contact@everlane.com",
            "externalUrl": "https://everlane.com",
            "recentPosts": [
                {"caption": "New sustainable collection #ecofriendly", "likesCount": 5000},
                {"caption": "Ethical production matters #ethicalfashion", "likesCount": 4500},
            ],
        },
    ]


@pytest.fixture
def sample_analysis_result():
    """Create sample LLM analysis result."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly", "#ethicalfashion", "#slowfashion", "#greenlifestyle"],
        "keywords": ["sustainable", "ethical", "eco-friendly", "fashion", "recycled"],
        "visual_themes": ["minimalist", "earth tones"],
        "content_pillars": ["sustainability", "fashion"],
        "target_audience_description": "Eco-conscious consumers",
        "confidence_score": 85
    }


@pytest.fixture
def sample_embedding():
    """Create a sample 1536-dimensional embedding vector."""
    return [0.01 * i for i in range(1536)]


# =============================================================================
# API Endpoint Integration Tests
# =============================================================================

@pytest.mark.integration
class TestAnalyzeBrandEndpoint:
    """Integration tests for POST /api/agent/analyze-brand endpoint."""
    
    def test_analyze_brand_requires_service_key(self, client, sample_job_id):
        """Test that endpoint requires service key authentication."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": sample_job_id}
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_analyze_brand_invalid_service_key(self, client, sample_job_id):
        """Test that invalid service key is rejected."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": sample_job_id},
            headers={"X-Service-Key": "invalid-key"}
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    @patch('app.api.routes.agents.get_brand_analyzer_agent')
    def test_analyze_brand_success(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_job_id,
        sample_analysis_result,
        sample_embedding
    ):
        """Test successful brand analysis via API."""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=BrandAnalyzerResponse(
            job_id=sample_job_id,
            hashtags=sample_analysis_result["hashtags"],
            keywords=sample_analysis_result["keywords"],
            visual_themes=sample_analysis_result["visual_themes"],
            content_pillars=sample_analysis_result["content_pillars"],
            target_audience_description=sample_analysis_result["target_audience_description"],
            embedding_vector=sample_embedding,
            profiles_analyzed=2,
            posts_analyzed=10,
            analysis_duration_seconds=5.5
        ))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": sample_job_id},
            headers=service_headers(service_key)
        )
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert data["job_id"] == sample_job_id
        assert len(data["hashtags"]) >= 5
        assert len(data["keywords"]) >= 5
        assert data["profiles_analyzed"] == 2
        assert data["posts_analyzed"] == 10
    
    @patch('app.api.routes.agents.get_brand_analyzer_agent')
    def test_analyze_brand_job_not_found(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_job_id
    ):
        """Test handling of job not found error."""
        from app.core.exceptions import JobNotFoundError
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=JobNotFoundError(sample_job_id))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": sample_job_id},
            headers=service_headers(service_key)
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert "JOB_NOT_FOUND" in str(data)
    
    @patch('app.api.routes.agents.get_brand_analyzer_agent')
    def test_analyze_brand_agent_error(
        self,
        mock_get_agent,
        client,
        service_key,
        sample_job_id
    ):
        """Test handling of agent processing error."""
        from app.core.exceptions import AgentError
        
        mock_agent = Mock()
        mock_agent.run = AsyncMock(
            side_effect=AgentError(
                message="Processing failed",
                agent_name="brand_analyzer",
                details={"reason": "LLM timeout"}
            )
        )
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": sample_job_id},
            headers=service_headers(service_key)
        )
        
        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        data = response.json()
        assert "AGENT_ERROR" in str(data)
    
    def test_analyze_brand_invalid_job_id_format(self, client, service_key):
        """Test handling of invalid job ID format."""
        response = client.post(
            "/api/agent/analyze-brand",
            json={"job_id": "not-a-uuid"},
            headers=service_headers(service_key)
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY


# =============================================================================
# Agent Status Endpoint Tests
# =============================================================================

@pytest.mark.integration
class TestAgentStatusEndpoint:
    """Integration tests for GET /api/agent/status endpoint."""
    
    def test_get_agent_status(self, client):
        """Test getting agent status."""
        response = client.get("/api/agent/status")
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert "agents" in data
        assert "brand_analyzer" in data["agents"]
        assert data["agents"]["brand_analyzer"]["status"] == "available"


# =============================================================================
# Placeholder Endpoint Tests
# =============================================================================

@pytest.mark.integration
class TestPlaceholderEndpoints:
    """Tests for placeholder endpoints (not yet implemented)."""
    
    # Note: Discovery endpoint is now implemented (STORY-3.3.3)
    # See tests/test_discovery_agent_integration.py for discovery tests
    
    # Note: Score endpoint is now implemented (STORY-3.3.4)
    # See tests/test_scorer_integration.py for scorer tests
    
    def test_score_endpoint_requires_auth(self, client, sample_job_id):
        """Test that score endpoint requires service key authentication."""
        profile_id = str(uuid4())
        
        # Call without service key should return 401
        response = client.post(
            "/api/agent/score",
            json={
                "profile_id": profile_id,
                "job_id": sample_job_id
            }
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED


# =============================================================================
# Full Agent Flow Integration Tests
# =============================================================================

@pytest.mark.integration
class TestBrandAnalyzerFullFlow:
    """Integration tests for full brand analyzer flow."""
    
    @pytest.fixture
    def mock_services(self, sample_job, sample_profile_data, sample_analysis_result, sample_embedding):
        """Setup mock services for full flow testing."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    with patch('app.agents.brand_analyzer.get_apify_service') as mock_apify_factory:
                        with patch('langchain_openai.OpenAIEmbeddings') as mock_embed:
                            # Setup config mock
                            mock_config.return_value = {
                                "name": "Brand Analyzer",
                                "enabled": True,
                                "prompts": {},
                                "output": {"min_hashtags": 5, "min_keywords": 5}
                            }
                            mock_prompts.return_value = {"system": "system", "user": "user"}
                            
                            # Setup LLM mock
                            mock_llm_instance = Mock()
                            mock_llm_instance.llm = Mock()
                            mock_llm_instance.model = "gpt-4"
                            mock_llm.return_value = mock_llm_instance
                            
                            # Setup Apify mock
                            mock_apify = Mock()
                            mock_apify.scrape_profiles = AsyncMock(return_value=sample_profile_data)
                            mock_apify.extract_username_from_url.side_effect = lambda url: url.split("/")[-1]
                            mock_apify_factory.return_value = mock_apify
                            
                            # Setup embeddings mock
                            mock_embed_instance = Mock()
                            mock_embed_instance.aembed_query = AsyncMock(return_value=sample_embedding)
                            mock_embed.return_value = mock_embed_instance
                            
                            yield {
                                "config": mock_config,
                                "prompts": mock_prompts,
                                "llm": mock_llm,
                                "apify": mock_apify,
                                "embeddings": mock_embed,
                            }
    
    @pytest.mark.asyncio
    async def test_full_analysis_flow_with_mocked_llm(
        self,
        mock_services,
        sample_job,
        sample_analysis_result,
        sample_embedding
    ):
        """Test full analysis flow with mocked LLM response."""
        # Setup repositories
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        
        mock_brand_repo = Mock()
        mock_brand_repo.get_by_job_id_optional.return_value = None
        mock_brand_repo.create.return_value = {
            "id": str(uuid4()),
            "job_id": sample_job["id"],
            "hashtags": sample_analysis_result["hashtags"],
            "keywords": sample_analysis_result["keywords"],
        }
        
        # Create agent
        agent = BrandAnalyzerAgent(
            job_repo=mock_job_repo,
            brand_repo=mock_brand_repo
        )
        
        # Mock the LLM analysis
        agent._analyze_brand = AsyncMock(
            return_value=BrandAnalysisOutput(**sample_analysis_result)
        )
        
        # Run analysis
        request = BrandAnalyzerRequest(job_id=sample_job["id"])
        response = await agent.run(request)
        
        # Verify response
        assert str(response.job_id) == sample_job["id"]
        assert len(response.hashtags) >= 5
        assert len(response.keywords) >= 5
        assert response.profiles_analyzed >= 0
        
        # Verify repositories were called
        mock_job_repo.get_by_id.assert_called_once_with(sample_job["id"])
        mock_brand_repo.create.assert_called_once()


# =============================================================================
# Error Recovery Tests
# =============================================================================

@pytest.mark.integration
class TestErrorRecovery:
    """Tests for error recovery scenarios."""
    
    @pytest.mark.asyncio
    async def test_agent_recovers_from_apify_failure(
        self,
        sample_job
    ):
        """Test that agent handles Apify failures gracefully."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    with patch('app.agents.brand_analyzer.get_apify_service') as mock_apify_factory:
                        mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                        mock_prompts.return_value = {"system": "s", "user": "u"}
                        
                        # Apify fails
                        mock_apify = Mock()
                        mock_apify.scrape_profiles = AsyncMock(side_effect=Exception("API down"))
                        mock_apify.extract_username_from_url.side_effect = lambda url: url.split("/")[-1]
                        mock_apify_factory.return_value = mock_apify
                        
                        mock_job_repo = Mock()
                        mock_job_repo.get_by_id.return_value = sample_job
                        
                        mock_brand_repo = Mock()
                        mock_brand_repo.get_by_job_id_optional.return_value = None
                        mock_brand_repo.create.return_value = {"id": str(uuid4())}
                        
                        agent = BrandAnalyzerAgent(
                            job_repo=mock_job_repo,
                            brand_repo=mock_brand_repo
                        )
                        
                        # Mock LLM analysis (should still work with empty profile data)
                        agent._analyze_brand = AsyncMock(
                            return_value=BrandAnalysisOutput(
                                hashtags=["#test1", "#test2", "#test3", "#test4", "#test5"],
                                keywords=["kw1", "kw2", "kw3", "kw4", "kw5"],
                                confidence_score=50  # Lower confidence due to missing data
                            )
                        )
                        agent._generate_embedding = AsyncMock(return_value=[0.0] * 1536)
                        
                        request = BrandAnalyzerRequest(job_id=sample_job["id"])
                        response = await agent.run(request)
                        
                        # Agent should still complete, just with limited data
                        assert response is not None
                        assert response.profiles_analyzed == 0  # No profiles due to Apify failure
    
    @pytest.mark.asyncio
    async def test_agent_handles_embedding_failure(
        self,
        sample_job
    ):
        """Test that agent handles embedding generation failures gracefully."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    with patch('app.agents.brand_analyzer.get_apify_service') as mock_apify_factory:
                        with patch('langchain_openai.OpenAIEmbeddings') as mock_embed:
                            mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                            mock_prompts.return_value = {"system": "s", "user": "u"}
                            
                            mock_apify = Mock()
                            mock_apify.scrape_profiles = AsyncMock(return_value=[])
                            mock_apify.extract_username_from_url.side_effect = lambda url: url.split("/")[-1]
                            mock_apify_factory.return_value = mock_apify
                            
                            # Embeddings fail
                            mock_embed_instance = Mock()
                            mock_embed_instance.aembed_query = AsyncMock(
                                side_effect=Exception("OpenAI API error")
                            )
                            mock_embed.return_value = mock_embed_instance
                            
                            mock_job_repo = Mock()
                            mock_job_repo.get_by_id.return_value = sample_job
                            
                            mock_brand_repo = Mock()
                            mock_brand_repo.get_by_job_id_optional.return_value = None
                            mock_brand_repo.create.return_value = {"id": str(uuid4())}
                            
                            agent = BrandAnalyzerAgent(
                                job_repo=mock_job_repo,
                                brand_repo=mock_brand_repo
                            )
                            
                            agent._analyze_brand = AsyncMock(
                                return_value=BrandAnalysisOutput(
                                    hashtags=["#test1", "#test2", "#test3", "#test4", "#test5"],
                                    keywords=["kw1", "kw2", "kw3", "kw4", "kw5"],
                                )
                            )
                            
                            request = BrandAnalyzerRequest(job_id=sample_job["id"])
                            response = await agent.run(request)
                            
                            # Agent should complete but embedding should be None
                            assert response is not None
                            assert response.embedding_vector is None


# =============================================================================
# Response Validation Tests
# =============================================================================

@pytest.mark.integration
class TestResponseValidation:
    """Tests for response format validation."""
    
    def test_response_has_required_fields(self, sample_job_id):
        """Test that response has all required fields."""
        response = BrandAnalyzerResponse(
            job_id=sample_job_id,
            hashtags=["#test"],
            keywords=["keyword"],
        )
        
        # Check required fields exist
        assert hasattr(response, "job_id")
        assert hasattr(response, "hashtags")
        assert hasattr(response, "keywords")
        assert hasattr(response, "visual_themes")
        assert hasattr(response, "content_pillars")
        assert hasattr(response, "target_audience_description")
        assert hasattr(response, "embedding_vector")
        assert hasattr(response, "profiles_analyzed")
        assert hasattr(response, "posts_analyzed")
        assert hasattr(response, "analysis_duration_seconds")
    
    def test_response_json_serialization(self, sample_job_id, sample_embedding):
        """Test that response serializes to JSON correctly."""
        response = BrandAnalyzerResponse(
            job_id=sample_job_id,
            hashtags=["#sustainablefashion", "#ecofriendly"],
            keywords=["sustainable", "eco"],
            visual_themes=["minimalist"],
            content_pillars=["sustainability"],
            target_audience_description="Eco-conscious consumers",
            embedding_vector=sample_embedding,
            profiles_analyzed=3,
            posts_analyzed=45,
            analysis_duration_seconds=12.5,
        )
        
        json_data = response.model_dump()
        
        assert isinstance(json_data, dict)
        assert json_data["hashtags"] == ["#sustainablefashion", "#ecofriendly"]
        assert json_data["profiles_analyzed"] == 3
        assert len(json_data["embedding_vector"]) == 1536
