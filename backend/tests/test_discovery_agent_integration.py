"""
PartnerScout AI - Discovery Agent Integration Tests (STORY-3.3.3)

Integration tests for the DiscoveryAgent covering:
- API endpoint integration
- Full discovery workflow
- Service integration with mocked external dependencies
- Error handling scenarios

Test Markers:
- @pytest.mark.integration: Integration tests with real service interactions (mocked externals)
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import HttpStatus, JobStatus, ProfileStatus
from app.core.exceptions import AgentError, JobNotFoundError
from app.models.agent import DiscoveryRequest, DiscoveryResponse


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def service_key():
    """Get service key for internal API authentication."""
    return settings.supabase.service_role_key


@pytest.fixture
def service_headers(service_key):
    """Create service key headers for API requests."""
    return {"X-Service-Key": service_key}


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
        "brand_description": "A sustainable fashion brand",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": JobStatus.ANALYZING.value,
    }


@pytest.fixture
def sample_hashtag_results():
    """Create sample hashtag search results."""
    return {
        "sustainablefashion": [
            {"ownerUsername": "eco_influencer1", "likesCount": 5000},
            {"ownerUsername": "eco_influencer2", "likesCount": 3000},
        ],
        "slowfashion": [
            {"ownerUsername": "slow_style", "likesCount": 8000},
        ],
    }


@pytest.fixture
def sample_profile_data():
    """Create sample profile data."""
    return [
        {
            "username": "eco_influencer1",
            "fullName": "Eco One",
            "biography": "Sustainable living",
            "followersCount": 75000,
            "followsCount": 500,
            "postsCount": 850,
            "isBusinessAccount": True,
            "private": False,
        },
        {
            "username": "eco_influencer2",
            "fullName": "Eco Two",
            "biography": "Eco lifestyle",
            "followersCount": 120000,
            "followsCount": 300,
            "postsCount": 1200,
            "isBusinessAccount": True,
            "private": False,
        },
        {
            "username": "slow_style",
            "fullName": "Slow Style",
            "biography": "Quality fashion",
            "followersCount": 45000,
            "followsCount": 200,
            "postsCount": 500,
            "isBusinessAccount": False,
            "private": False,
        },
    ]


@pytest.fixture
def mock_apify_service(sample_hashtag_results, sample_profile_data):
    """Create a mock Apify service."""
    service = Mock()
    service.search_hashtags = AsyncMock(return_value=sample_hashtag_results)
    service.scrape_profiles = AsyncMock(return_value=sample_profile_data)
    return service


@pytest.fixture
def mock_job_repo(sample_job):
    """Create a mock job repository."""
    repo = Mock()
    repo.get_by_id.return_value = sample_job
    return repo


@pytest.fixture
def mock_profile_repo():
    """Create a mock profile repository."""
    repo = Mock()
    repo.list_by_job.return_value = []
    repo.check_duplicate.return_value = False
    repo.create.side_effect = lambda **kwargs: {
        "id": str(uuid4()),
        "job_id": kwargs.get("job_id"),
        "username": kwargs.get("username"),
        "followers_count": kwargs.get("followers_count", 0),
        "status": ProfileStatus.NEW.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return repo


# =============================================================================
# API Endpoint Integration Tests
# =============================================================================

@pytest.mark.integration
class TestDiscoveryEndpoint:
    """Integration tests for the /api/agent/discover endpoint."""
    
    def test_discover_endpoint_requires_auth(self, client, sample_job_id):
        """Test that endpoint requires service key authentication."""
        response = client.post(
            "/api/agent/discover",
            json={
                "job_id": sample_job_id,
                "hashtags": ["#sustainablefashion"],
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_discover_endpoint_invalid_service_key(self, client, sample_job_id):
        """Test that invalid service key is rejected."""
        response = client.post(
            "/api/agent/discover",
            headers={"X-Service-Key": "invalid-key"},
            json={
                "job_id": sample_job_id,
                "hashtags": ["#sustainablefashion"],
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    @patch('app.agents.discovery.DiscoveryAgent')
    def test_discover_endpoint_success(
        self,
        mock_agent_class,
        client,
        service_headers,
        sample_job_id
    ):
        """Test successful discovery via API endpoint."""
        # Setup mock agent
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=DiscoveryResponse(
            job_id=sample_job_id,
            profiles=[{"id": str(uuid4()), "username": "test_user"}],
            total_discovered=1,
            deduplicated=0,
            filtered_out=5,
            discovery_duration_seconds=10.5,
        ))
        mock_agent_class.return_value = mock_agent
        
        response = client.post(
            "/api/agent/discover",
            headers=service_headers,
            json={
                "job_id": sample_job_id,
                "hashtags": ["#sustainablefashion"],
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        assert data["total_discovered"] == 1
        assert data["deduplicated"] == 0
        assert data["filtered_out"] == 5
    
    @patch('app.api.routes.agents.get_discovery_agent')
    def test_discover_endpoint_job_not_found(
        self,
        mock_get_agent,
        client,
        service_headers,
        sample_job_id
    ):
        """Test endpoint handles job not found error."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=JobNotFoundError(sample_job_id))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/discover",
            headers=service_headers,
            json={
                "job_id": sample_job_id,
                "hashtags": ["#test"],
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        # HTTPException wraps error in "detail" key
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"
    
    @patch('app.api.routes.agents.get_discovery_agent')
    def test_discover_endpoint_agent_error(
        self,
        mock_get_agent,
        client,
        service_headers,
        sample_job_id
    ):
        """Test endpoint handles agent errors."""
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=AgentError(
            message="Discovery failed",
            agent_name="discovery",
            details={"reason": "test error"}
        ))
        mock_get_agent.return_value = mock_agent
        
        response = client.post(
            "/api/agent/discover",
            headers=service_headers,
            json={
                "job_id": sample_job_id,
                "hashtags": ["#test"],
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.INTERNAL_SERVER_ERROR
        data = response.json()
        # HTTPException wraps error in "detail" key
        assert data["detail"]["error"]["code"] == "AGENT_ERROR"
    
    def test_discover_endpoint_validates_request(
        self,
        client,
        service_headers,
        sample_job_id
    ):
        """Test that request validation works."""
        # Missing required hashtags
        response = client.post(
            "/api/agent/discover",
            headers=service_headers,
            json={
                "job_id": sample_job_id,
                "hashtags": [],  # Empty hashtags
                "limit": 10,
            }
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY


# =============================================================================
# Full Workflow Integration Tests
# =============================================================================

@pytest.mark.integration
class TestFullDiscoveryWorkflow:
    """Integration tests for the complete discovery workflow."""
    
    @patch('app.agents.discovery.get_apify_service')
    @patch('app.agents.discovery.ProfileRepository')
    @patch('app.agents.discovery.JobRepository')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_full_discovery_workflow(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo_class,
        mock_profile_repo_class,
        mock_get_apify,
        sample_job,
        sample_hashtag_results,
        sample_profile_data
    ):
        """Test complete discovery workflow end-to-end."""
        # Setup mocks
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        mock_apify = Mock()
        mock_apify.search_hashtags = AsyncMock(return_value=sample_hashtag_results)
        mock_apify.scrape_profiles = AsyncMock(return_value=sample_profile_data)
        mock_get_apify.return_value = mock_apify
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo_class.return_value = mock_job_repo
        
        stored_count = 0
        def mock_create(**kwargs):
            nonlocal stored_count
            stored_count += 1
            return {
                "id": str(uuid4()),
                "job_id": kwargs.get("job_id"),
                "username": kwargs.get("username"),
                "followers_count": kwargs.get("followers_count", 0),
                "status": ProfileStatus.NEW.value,
            }
        
        mock_profile_repo = Mock()
        mock_profile_repo.list_by_job.return_value = []
        mock_profile_repo.check_duplicate.return_value = False
        mock_profile_repo.create.side_effect = mock_create
        mock_profile_repo_class.return_value = mock_profile_repo
        
        # Create agent and run discovery
        from app.agents.discovery import DiscoveryAgent
        
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=sample_job["id"],
            hashtags=["#sustainablefashion", "#slowfashion"],
            limit=10,
            follower_min=5000,
            follower_max=200000
        )
        
        response = await agent.run(request)
        
        # Verify workflow completed
        assert isinstance(response, DiscoveryResponse)
        assert response.job_id == request.job_id
        assert response.total_discovered >= 0
        assert response.discovery_duration_seconds is not None
        
        # Verify Apify was called for hashtag search
        mock_apify.search_hashtags.assert_called_once()
        
        # Verify profiles were stored
        if response.total_discovered > 0:
            assert mock_profile_repo.create.called
    
    @patch('app.agents.discovery.get_apify_service')
    @patch('app.agents.discovery.ProfileRepository')
    @patch('app.agents.discovery.JobRepository')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_workflow_handles_apify_failure(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo_class,
        mock_profile_repo_class,
        mock_get_apify,
        sample_job
    ):
        """Test workflow handles Apify failures gracefully."""
        from app.core.exceptions import ApifyError
        
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        mock_apify = Mock()
        mock_apify.search_hashtags = AsyncMock(
            side_effect=ApifyError(message="API error", actor_id="test")
        )
        mock_get_apify.return_value = mock_apify
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo_class.return_value = mock_job_repo
        
        mock_profile_repo = Mock()
        mock_profile_repo.list_by_job.return_value = []
        mock_profile_repo_class.return_value = mock_profile_repo
        
        from app.agents.discovery import DiscoveryAgent
        
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=sample_job["id"],
            hashtags=["#test"],
            limit=10
        )
        
        # Should complete without raising, with 0 profiles
        response = await agent.run(request)
        
        assert response.total_discovered == 0
    
    @patch('app.agents.discovery.get_apify_service')
    @patch('app.agents.discovery.ProfileRepository')
    @patch('app.agents.discovery.JobRepository')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_workflow_respects_follower_limits(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo_class,
        mock_profile_repo_class,
        mock_get_apify,
        sample_job
    ):
        """Test that follower limits are respected in filtering."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        # Create profiles with varying follower counts
        profiles = [
            {"username": "small", "followersCount": 1000, "followsCount": 100, "postsCount": 50, "private": False},
            {"username": "medium", "followersCount": 50000, "followsCount": 500, "postsCount": 500, "private": False},
            {"username": "large", "followersCount": 1000000, "followsCount": 1000, "postsCount": 2000, "private": False},
        ]
        
        mock_apify = Mock()
        mock_apify.search_hashtags = AsyncMock(return_value={
            "test": [
                {"ownerUsername": "small"},
                {"ownerUsername": "medium"},
                {"ownerUsername": "large"},
            ]
        })
        mock_apify.scrape_profiles = AsyncMock(return_value=profiles)
        mock_get_apify.return_value = mock_apify
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo_class.return_value = mock_job_repo
        
        created_usernames = []
        def track_create(**kwargs):
            created_usernames.append(kwargs.get("username"))
            return {
                "id": str(uuid4()),
                "username": kwargs.get("username"),
                "status": ProfileStatus.NEW.value,
            }
        
        mock_profile_repo = Mock()
        mock_profile_repo.list_by_job.return_value = []
        mock_profile_repo.check_duplicate.return_value = False
        mock_profile_repo.create.side_effect = track_create
        mock_profile_repo_class.return_value = mock_profile_repo
        
        from app.agents.discovery import DiscoveryAgent
        
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=sample_job["id"],
            hashtags=["#test"],
            limit=10,
            follower_min=10000,  # Filter out "small"
            follower_max=500000  # Filter out "large"
        )
        
        await agent.run(request)
        
        # Only "medium" should be stored
        assert "medium" in created_usernames
        assert "small" not in created_usernames
        assert "large" not in created_usernames
    
    @patch('app.agents.discovery.get_apify_service')
    @patch('app.agents.discovery.ProfileRepository')
    @patch('app.agents.discovery.JobRepository')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_workflow_deduplicates_existing(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo_class,
        mock_profile_repo_class,
        mock_get_apify,
        sample_job,
        sample_profile_data
    ):
        """Test that existing profiles are deduplicated."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        mock_apify = Mock()
        mock_apify.search_hashtags = AsyncMock(return_value={
            "test": [
                {"ownerUsername": "existing_user"},
                {"ownerUsername": "new_user"},
            ]
        })
        mock_apify.scrape_profiles = AsyncMock(return_value=[
            {"username": "existing_user", "followersCount": 50000, "followsCount": 500, "postsCount": 500, "private": False},
            {"username": "new_user", "followersCount": 75000, "followsCount": 600, "postsCount": 600, "private": False},
        ])
        mock_get_apify.return_value = mock_apify
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo_class.return_value = mock_job_repo
        
        # Simulate existing_user already exists
        mock_profile_repo = Mock()
        mock_profile_repo.list_by_job.return_value = [{"username": "existing_user"}]
        mock_profile_repo.check_duplicate.side_effect = lambda job_id, username: username == "existing_user"
        
        created_usernames = []
        def track_create(**kwargs):
            created_usernames.append(kwargs.get("username"))
            return {"id": str(uuid4()), "username": kwargs.get("username")}
        
        mock_profile_repo.create.side_effect = track_create
        mock_profile_repo_class.return_value = mock_profile_repo
        
        from app.agents.discovery import DiscoveryAgent
        
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=sample_job["id"],
            hashtags=["#test"],
            limit=10
        )
        
        response = await agent.run(request)
        
        # Only new_user should be created
        assert "new_user" in created_usernames
        assert "existing_user" not in created_usernames
        assert response.deduplicated >= 1


# =============================================================================
# Agent Status Endpoint Test
# =============================================================================

@pytest.mark.integration
class TestAgentStatusEndpoint:
    """Tests for the agent status endpoint."""
    
    def test_agent_status_shows_discovery_available(self, client):
        """Test that agent status shows discovery as available."""
        response = client.get("/api/agent/status")
        
        assert response.status_code == HttpStatus.OK
        data = response.json()
        
        assert "discovery" in data["agents"]
        assert data["agents"]["discovery"]["status"] == "available"


# =============================================================================
# Performance Integration Tests
# =============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestDiscoveryPerformance:
    """Performance-related integration tests."""
    
    @patch('app.agents.discovery.get_apify_service')
    @patch('app.agents.discovery.ProfileRepository')
    @patch('app.agents.discovery.JobRepository')
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @pytest.mark.asyncio
    async def test_discovery_completes_within_timeout(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo_class,
        mock_profile_repo_class,
        mock_get_apify,
        sample_job,
        sample_profile_data
    ):
        """Test that discovery completes within reasonable time."""
        import time
        
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        # Create 50 posts
        posts = {f"hashtag{i}": [{"ownerUsername": f"user{j}"} for j in range(10)] for i in range(5)}
        profiles = [
            {"username": f"user{i}", "followersCount": 50000, "followsCount": 500, "postsCount": 500, "private": False}
            for i in range(50)
        ]
        
        mock_apify = Mock()
        mock_apify.search_hashtags = AsyncMock(return_value=posts)
        mock_apify.scrape_profiles = AsyncMock(return_value=profiles)
        mock_get_apify.return_value = mock_apify
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo_class.return_value = mock_job_repo
        
        mock_profile_repo = Mock()
        mock_profile_repo.list_by_job.return_value = []
        mock_profile_repo.check_duplicate.return_value = False
        mock_profile_repo.create.return_value = {"id": str(uuid4())}
        mock_profile_repo_class.return_value = mock_profile_repo
        
        from app.agents.discovery import DiscoveryAgent
        
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=sample_job["id"],
            hashtags=["#test1", "#test2"],
            limit=50
        )
        
        start_time = time.time()
        response = await agent.run(request)
        duration = time.time() - start_time
        
        # Should complete within 30 seconds (with mocked services, should be near-instant)
        assert duration < 30
        assert response.discovery_duration_seconds is not None
