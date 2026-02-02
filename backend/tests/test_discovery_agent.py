"""
PartnerScout AI - Discovery Agent Unit Tests (STORY-3.3.3)

Comprehensive unit tests for the DiscoveryAgent covering:
- Agent initialization
- Hashtag search via Apify
- Follower range filtering
- Username deduplication
- Database storage
- Error handling

Test Markers:
- @pytest.mark.unit: Fast unit tests with mocked dependencies
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from app.agents.discovery import (
    DiscoveryAgent,
    DiscoveredProfile,
    ProfileRelevanceOutput,
    get_discovery_agent,
)
from app.core.constants import ProfileStatus, Defaults
from app.core.exceptions import AgentError, JobNotFoundError, ApifyError
from app.models.agent import DiscoveryRequest, DiscoveryResponse


# =============================================================================
# Test Fixtures
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
        "status": "analyzing",
    }


@pytest.fixture
def sample_hashtag_results():
    """Create sample hashtag search results from Apify."""
    return {
        "sustainablefashion": [
            {
                "id": "post1",
                "ownerUsername": "eco_influencer1",
                "caption": "Sustainable living #sustainablefashion",
                "likesCount": 5000,
                "commentsCount": 150,
            },
            {
                "id": "post2",
                "ownerUsername": "eco_influencer2",
                "caption": "My eco journey #sustainablefashion",
                "likesCount": 3000,
                "commentsCount": 80,
            },
            {
                "id": "post3",
                "ownerUsername": "eco_influencer1",  # Duplicate
                "caption": "Another post #sustainablefashion",
                "likesCount": 4000,
                "commentsCount": 100,
            },
        ],
        "slowfashion": [
            {
                "id": "post4",
                "ownerUsername": "slow_style",
                "caption": "Slow fashion movement #slowfashion",
                "likesCount": 8000,
                "commentsCount": 200,
            },
            {
                "id": "post5",
                "owner": {"username": "eco_lifestyle"},  # Different format
                "caption": "Quality over quantity",
                "likesCount": 6000,
                "commentsCount": 150,
            },
        ],
    }


@pytest.fixture
def sample_profile_data():
    """Create sample Instagram profile data."""
    return [
        {
            "username": "eco_influencer1",
            "fullName": "Eco Influencer One",
            "biography": "Sustainable fashion advocate #sustainablefashion",
            "followersCount": 75000,
            "followsCount": 500,
            "postsCount": 850,
            "isBusinessAccount": True,
            "businessEmail": "contact@eco1.com",
            "externalUrl": "https://eco1.com",
            "verified": False,
            "private": False,
            "profilePicUrl": "https://example.com/pic1.jpg",
            "recentPosts": [
                {"likesCount": 5000, "commentsCount": 150},
                {"likesCount": 4500, "commentsCount": 120},
            ],
        },
        {
            "username": "eco_influencer2",
            "fullName": "Eco Influencer Two",
            "biography": "Living sustainably #ecofriendly",
            "followersCount": 120000,
            "followsCount": 300,
            "postsCount": 1200,
            "isBusinessAccount": True,
            "businessEmail": "hello@eco2.com",
            "externalUrl": "https://eco2.com",
            "verified": True,
            "private": False,
            "profilePicUrl": "https://example.com/pic2.jpg",
        },
        {
            "username": "slow_style",
            "fullName": "Slow Style",
            "biography": "Quality over quantity in fashion",
            "followersCount": 45000,
            "followsCount": 200,
            "postsCount": 500,
            "isBusinessAccount": False,
            "private": False,
            "profilePicUrl": "https://example.com/pic3.jpg",
        },
        {
            "username": "eco_lifestyle",
            "fullName": "Eco Lifestyle",
            "biography": "Sustainable living tips",
            "followersCount": 200000,
            "followsCount": 400,
            "postsCount": 1500,
            "isBusinessAccount": True,
            "private": False,
        },
    ]


@pytest.fixture
def sample_profile_low_followers():
    """Create a profile with low follower count."""
    return {
        "username": "small_account",
        "fullName": "Small Account",
        "followersCount": 1000,  # Below default min
        "followsCount": 500,
        "postsCount": 50,
        "private": False,
    }


@pytest.fixture
def sample_profile_private():
    """Create a private profile."""
    return {
        "username": "private_account",
        "fullName": "Private Account",
        "followersCount": 50000,
        "followsCount": 300,
        "postsCount": 200,
        "private": True,
    }


@pytest.fixture
def sample_profile_fake():
    """Create a profile that appears fake."""
    return {
        "username": "fake_account",
        "fullName": "Definitely Not Fake",
        "followersCount": 50000,
        "followsCount": 200000,  # Following way more than followers
        "postsCount": 5,  # Very few posts
        "private": False,
    }


@pytest.fixture
def mock_job_repo(sample_job):
    """Create a mock job repository."""
    repo = Mock()
    repo.get_by_id.return_value = sample_job
    return repo


@pytest.fixture
def mock_brand_repo():
    """Create a mock brand repository."""
    repo = Mock()
    repo.get_by_job_id_optional.return_value = {
        "hashtags": ["#sustainablefashion", "#slowfashion"],
        "keywords": ["sustainable", "ethical"],
    }
    return repo


@pytest.fixture
def mock_profile_repo():
    """Create a mock profile repository."""
    repo = Mock()
    repo.list_by_job.return_value = []  # No existing profiles
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


@pytest.fixture
def mock_apify_service(sample_hashtag_results, sample_profile_data):
    """Create a mock Apify service."""
    service = Mock()
    service.search_hashtags = AsyncMock(return_value=sample_hashtag_results)
    service.scrape_profiles = AsyncMock(return_value=sample_profile_data)
    return service


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.llm = Mock()
    service.model = "gpt-4"
    return service


# =============================================================================
# DiscoveredProfile Model Tests
# =============================================================================

@pytest.mark.unit
class TestDiscoveredProfileModel:
    """Tests for DiscoveredProfile model."""
    
    def test_default_values(self):
        """Test default values for DiscoveredProfile."""
        profile = DiscoveredProfile(username="test_user", instagram_url="https://instagram.com/test_user")
        
        assert profile.username == "test_user"
        assert profile.full_name is None
        assert profile.followers_count == 0
        assert profile.is_verified is False
    
    def test_with_all_values(self, sample_profile_data):
        """Test DiscoveredProfile with full data."""
        data = sample_profile_data[0]
        profile = DiscoveredProfile(
            username=data["username"],
            full_name=data.get("fullName"),
            bio=data.get("biography"),
            followers_count=data.get("followersCount", 0),
            following_count=data.get("followsCount"),
            posts_count=data.get("postsCount"),
            is_verified=data.get("verified", False),
            is_business_account=data.get("isBusinessAccount"),
            instagram_url=f"https://instagram.com/{data['username']}"
        )
        
        assert profile.username == "eco_influencer1"
        assert profile.followers_count == 75000
        assert profile.is_business_account is True


# =============================================================================
# DiscoveryAgent Initialization Tests
# =============================================================================

@pytest.mark.unit
class TestDiscoveryAgentInit:
    """Tests for DiscoveryAgent initialization."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.discovery.get_apify_service')
    def test_agent_initializes_correctly(
        self,
        mock_get_apify,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that agent initializes correctly with default services."""
        mock_get_config.return_value = {
            "name": "Discovery Agent",
            "enabled": True,
            "prompts": {},
        }
        mock_load_prompts.return_value = {"system": "system", "user": "user"}
        
        agent = DiscoveryAgent()
        
        assert agent.agent_name == "discovery"
        mock_get_apify.assert_called_once()
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_with_custom_services(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo
    ):
        """Test agent initialization with custom services."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = DiscoveryAgent(
            apify_service=mock_apify_service,
            job_repo=mock_job_repo,
            brand_repo=mock_brand_repo,
            profile_repo=mock_profile_repo
        )
        
        assert agent._apify_service == mock_apify_service
        assert agent._job_repo == mock_job_repo
        assert agent._brand_repo == mock_brand_repo
        assert agent._profile_repo == mock_profile_repo


# =============================================================================
# Hashtag Search Tests (SUB-3.3.3.1.2)
# =============================================================================

@pytest.mark.unit
class TestHashtagSearch:
    """Tests for hashtag search via Apify."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    @pytest.mark.asyncio
    async def test_search_hashtags_calls_apify(self, agent, mock_apify_service):
        """Test that hashtags are searched via Apify."""
        hashtags = ["#sustainablefashion", "#slowfashion"]
        
        await agent._search_hashtags(hashtags)
        
        mock_apify_service.search_hashtags.assert_called_once()
        call_kwargs = mock_apify_service.search_hashtags.call_args.kwargs
        assert "sustainablefashion" in call_kwargs["hashtags"]
        assert "slowfashion" in call_kwargs["hashtags"]
    
    @pytest.mark.asyncio
    async def test_search_hashtags_strips_hash(self, agent, mock_apify_service):
        """Test that # prefix is stripped from hashtags."""
        hashtags = ["#sustainablefashion", "slowfashion"]  # One with, one without
        
        await agent._search_hashtags(hashtags)
        
        call_kwargs = mock_apify_service.search_hashtags.call_args.kwargs
        # Both should be without #
        assert all(not h.startswith("#") for h in call_kwargs["hashtags"])
    
    @pytest.mark.asyncio
    async def test_search_hashtags_handles_apify_error(self, agent, mock_apify_service):
        """Test graceful handling of Apify errors."""
        mock_apify_service.search_hashtags = AsyncMock(
            side_effect=ApifyError(message="API error", actor_id="test")
        )
        
        result = await agent._search_hashtags(["#test"])
        
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_search_hashtags_empty_list(self, agent):
        """Test with empty hashtag list."""
        result = await agent._search_hashtags([])
        
        assert result == {}


# =============================================================================
# Username Extraction Tests
# =============================================================================

@pytest.mark.unit
class TestUsernameExtraction:
    """Tests for extracting usernames from hashtag results."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    def test_extract_usernames_basic(self, agent, sample_hashtag_results):
        """Test basic username extraction."""
        usernames = agent._extract_usernames_from_posts(sample_hashtag_results)
        
        # Should find unique usernames
        assert "eco_influencer1" in usernames
        assert "eco_influencer2" in usernames
        assert "slow_style" in usernames
        assert "eco_lifestyle" in usernames
    
    def test_extract_usernames_deduplicates(self, agent, sample_hashtag_results):
        """Test that duplicate usernames are removed."""
        usernames = agent._extract_usernames_from_posts(sample_hashtag_results)
        
        # eco_influencer1 appears twice, should only be in list once
        assert usernames.count("eco_influencer1") == 1
    
    def test_extract_usernames_handles_different_formats(self, agent):
        """Test extraction handles different data formats."""
        results = {
            "test": [
                {"ownerUsername": "user1"},
                {"owner_username": "user2"},
                {"owner": {"username": "user3"}},
                {"ownerUsername": None},  # Should be skipped
                {},  # Should be skipped
            ]
        }
        
        usernames = agent._extract_usernames_from_posts(results)
        
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames
        assert len(usernames) == 3
    
    def test_extract_usernames_empty_results(self, agent):
        """Test with empty hashtag results."""
        usernames = agent._extract_usernames_from_posts({})
        
        assert usernames == []


# =============================================================================
# Follower Range Filtering Tests (SUB-3.3.3.1.3)
# =============================================================================

@pytest.mark.unit
class TestFollowerFiltering:
    """Tests for follower range filtering."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    def test_filter_by_follower_range(self, agent, sample_profile_data):
        """Test filtering by follower range."""
        # Filter for profiles with 50K-150K followers
        filtered, filtered_out = agent._filter_profiles(
            sample_profile_data,
            min_followers=50000,
            max_followers=150000,
            limit=100
        )
        
        # eco_influencer1 (75K) and eco_influencer2 (120K) should pass
        # slow_style (45K) and eco_lifestyle (200K) should be filtered
        usernames = [p["username"] for p in filtered]
        assert "eco_influencer1" in usernames
        assert "eco_influencer2" in usernames
        assert "slow_style" not in usernames
        assert "eco_lifestyle" not in usernames
    
    def test_filter_excludes_low_followers(self, agent, sample_profile_low_followers):
        """Test that low follower profiles are filtered."""
        profiles = [sample_profile_low_followers]
        
        filtered, filtered_out = agent._filter_profiles(
            profiles,
            min_followers=5000,
            max_followers=500000,
            limit=100
        )
        
        assert len(filtered) == 0
        assert filtered_out == 1
    
    def test_filter_excludes_private(self, agent, sample_profile_private):
        """Test that private profiles are filtered."""
        profiles = [sample_profile_private]
        
        filtered, filtered_out = agent._filter_profiles(
            profiles,
            min_followers=1000,
            max_followers=500000,
            limit=100,
            exclude_private=True
        )
        
        assert len(filtered) == 0
        assert filtered_out == 1
    
    def test_filter_allows_private_when_disabled(self, agent, sample_profile_private):
        """Test that private profiles pass when exclude_private=False."""
        profiles = [sample_profile_private]
        
        filtered, filtered_out = agent._filter_profiles(
            profiles,
            min_followers=1000,
            max_followers=500000,
            limit=100,
            exclude_private=False
        )
        
        assert len(filtered) == 1
    
    def test_filter_respects_limit(self, agent, sample_profile_data):
        """Test that limit is respected."""
        filtered, filtered_out = agent._filter_profiles(
            sample_profile_data,
            min_followers=1000,
            max_followers=500000,
            limit=2
        )
        
        assert len(filtered) <= 2
    
    def test_filter_excludes_fake_profiles(self, agent, sample_profile_fake):
        """Test that fake-looking profiles are filtered."""
        profiles = [sample_profile_fake]
        
        filtered, filtered_out = agent._filter_profiles(
            profiles,
            min_followers=1000,
            max_followers=500000,
            limit=100
        )
        
        assert len(filtered) == 0
        assert filtered_out == 1


# =============================================================================
# Fake Profile Detection Tests
# =============================================================================

@pytest.mark.unit
class TestFakeDetection:
    """Tests for fake profile detection."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    def test_detects_high_following_ratio(self, agent):
        """Test detection of high following/follower ratio."""
        profile = {
            "followersCount": 10000,
            "followsCount": 50000,  # 5x following ratio
            "postsCount": 100,
        }
        
        assert agent._is_likely_fake(profile) is True
    
    def test_detects_high_followers_low_posts(self, agent):
        """Test detection of high followers with few posts."""
        profile = {
            "followersCount": 50000,
            "followsCount": 500,
            "postsCount": 5,  # Very few posts for follower count
        }
        
        assert agent._is_likely_fake(profile) is True
    
    def test_detects_zero_followers(self, agent):
        """Test detection of zero followers."""
        profile = {
            "followersCount": 0,
            "followsCount": 100,
            "postsCount": 50,
        }
        
        assert agent._is_likely_fake(profile) is True
    
    def test_passes_normal_profile(self, agent, sample_profile_data):
        """Test that normal profiles pass."""
        profile = sample_profile_data[0]
        
        assert agent._is_likely_fake(profile) is False


# =============================================================================
# Deduplication Tests (SUB-3.3.3.1.4)
# =============================================================================

@pytest.mark.unit
class TestDeduplication:
    """Tests for username deduplication."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    @pytest.mark.asyncio
    async def test_get_existing_usernames(self, agent, mock_profile_repo, sample_job_id):
        """Test retrieval of existing usernames."""
        mock_profile_repo.list_by_job.return_value = [
            {"username": "existing1"},
            {"username": "existing2"},
        ]
        
        existing = await agent._get_existing_usernames(sample_job_id)
        
        assert "existing1" in existing
        assert "existing2" in existing
    
    @pytest.mark.asyncio
    async def test_get_existing_usernames_empty(self, agent, mock_profile_repo, sample_job_id):
        """Test with no existing profiles."""
        mock_profile_repo.list_by_job.return_value = []
        
        existing = await agent._get_existing_usernames(sample_job_id)
        
        assert len(existing) == 0


# =============================================================================
# Database Storage Tests (SUB-3.3.3.1.5)
# =============================================================================

@pytest.mark.unit
class TestDatabaseStorage:
    """Tests for profile database storage."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    @pytest.mark.asyncio
    async def test_store_profiles_creates_records(
        self,
        agent,
        mock_profile_repo,
        sample_job_id,
        sample_profile_data
    ):
        """Test that profiles are stored in database."""
        await agent._store_profiles(sample_job_id, sample_profile_data)
        
        # Should call create for each profile
        assert mock_profile_repo.create.call_count == len(sample_profile_data)
    
    @pytest.mark.asyncio
    async def test_store_profiles_checks_duplicates(
        self,
        agent,
        mock_profile_repo,
        sample_job_id,
        sample_profile_data
    ):
        """Test that duplicates are checked before storing."""
        mock_profile_repo.check_duplicate.return_value = True
        
        stored = await agent._store_profiles(sample_job_id, sample_profile_data)
        
        # All should be skipped as duplicates
        assert len(stored) == 0
        assert mock_profile_repo.create.call_count == 0
    
    @pytest.mark.asyncio
    async def test_store_profiles_builds_instagram_url(
        self,
        agent,
        mock_profile_repo,
        sample_job_id,
        sample_profile_data
    ):
        """Test that Instagram URL is built correctly."""
        await agent._store_profiles(sample_job_id, sample_profile_data[:1])
        
        call_kwargs = mock_profile_repo.create.call_args.kwargs
        assert call_kwargs["instagram_url"] == "https://instagram.com/eco_influencer1"
    
    @pytest.mark.asyncio
    async def test_store_profiles_handles_errors(
        self,
        agent,
        mock_profile_repo,
        sample_job_id,
        sample_profile_data
    ):
        """Test graceful handling of storage errors."""
        mock_profile_repo.create.side_effect = Exception("DB error")
        
        # Should not raise, just skip failed profiles
        stored = await agent._store_profiles(sample_job_id, sample_profile_data)
        
        assert len(stored) == 0


# =============================================================================
# Engagement Rate Calculation Tests
# =============================================================================

@pytest.mark.unit
class TestEngagementCalculation:
    """Tests for engagement rate calculation."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    def test_calculate_from_posts(self, agent, sample_profile_data):
        """Test engagement rate calculation from posts."""
        profile = sample_profile_data[0]  # Has recentPosts
        
        rate = agent._calculate_engagement_rate(profile)
        
        assert rate is not None
        # (5000+150 + 4500+120) / 2 / 75000 * 100 ≈ 6.51%
        assert 6 < rate < 7
    
    def test_calculate_zero_followers(self, agent):
        """Test with zero followers returns None."""
        profile = {"followersCount": 0}
        
        rate = agent._calculate_engagement_rate(profile)
        
        assert rate is None
    
    def test_calculate_uses_existing_rate(self, agent):
        """Test that existing engagement rate is used if available."""
        profile = {"followersCount": 50000, "engagementRate": 3.5}
        
        rate = agent._calculate_engagement_rate(profile)
        
        assert rate == 3.5


# =============================================================================
# Run Method Tests
# =============================================================================

@pytest.mark.unit
class TestRunMethod:
    """Tests for the main run method."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service,
        sample_hashtag_results,
        sample_profile_data
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    @pytest.mark.asyncio
    async def test_run_success(self, agent, sample_job_id):
        """Test successful run method execution."""
        request = DiscoveryRequest(
            job_id=sample_job_id,
            hashtags=["#sustainablefashion", "#slowfashion"],
            limit=10
        )
        
        response = await agent.run(request)
        
        assert isinstance(response, DiscoveryResponse)
        assert response.job_id == request.job_id
        assert response.total_discovered >= 0
        assert response.discovery_duration_seconds is not None
    
    @pytest.mark.asyncio
    async def test_run_job_not_found(self, agent, mock_job_repo):
        """Test run method with non-existent job."""
        mock_job_repo.get_by_id.side_effect = JobNotFoundError("test-id")
        
        request = DiscoveryRequest(
            job_id=uuid4(),
            hashtags=["#test"],
            limit=10
        )
        
        with pytest.raises(JobNotFoundError):
            await agent.run(request)
    
    @pytest.mark.asyncio
    async def test_run_tracks_deduplication(
        self,
        agent,
        mock_profile_repo,
        sample_job_id
    ):
        """Test that deduplication count is tracked."""
        # Set up existing profiles
        mock_profile_repo.list_by_job.return_value = [
            {"username": "eco_influencer1"},  # Will be deduplicated
        ]
        
        request = DiscoveryRequest(
            job_id=sample_job_id,
            hashtags=["#sustainablefashion"],
            limit=10
        )
        
        response = await agent.run(request)
        
        # Should report deduplication
        assert response.deduplicated >= 0


# =============================================================================
# Input Validation Tests
# =============================================================================

@pytest.mark.unit
class TestInputValidation:
    """Tests for input validation."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_profile_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return DiscoveryAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo,
                    profile_repo=mock_profile_repo
                )
    
    @pytest.mark.asyncio
    async def test_validate_valid_input(self, agent, sample_job_id):
        """Test validation of valid input."""
        request = DiscoveryRequest(
            job_id=sample_job_id,
            hashtags=["#test"],
            limit=10
        )
        
        result = await agent.validate_input(request)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_invalid_follower_range(self, agent, sample_job_id):
        """Test validation fails with invalid follower range."""
        request = DiscoveryRequest(
            job_id=sample_job_id,
            hashtags=["#test"],
            follower_min=100000,
            follower_max=50000,  # Max < Min
            limit=10
        )
        
        with pytest.raises(AgentError) as exc_info:
            await agent.validate_input(request)
        
        assert "follower_min must be less than follower_max" in str(exc_info.value)


# =============================================================================
# Factory Function Tests
# =============================================================================

@pytest.mark.unit
class TestFactoryFunction:
    """Tests for the factory function."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.discovery.get_apify_service')
    def test_get_discovery_agent(
        self,
        mock_get_apify,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test factory function creates agent correctly."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = get_discovery_agent()
        
        assert isinstance(agent, DiscoveryAgent)
        assert agent.agent_name == "discovery"


# =============================================================================
# Contract Tests
# =============================================================================

@pytest.mark.contract
class TestDiscoveryAgentContracts:
    """Contract tests verifying response format contracts."""
    
    def test_discovery_request_validates(self):
        """Test that DiscoveryRequest validates correctly."""
        job_id = uuid4()
        request = DiscoveryRequest(
            job_id=job_id,
            hashtags=["#sustainablefashion"],
            limit=50
        )
        
        assert request.job_id == job_id
        assert "#sustainablefashion" in request.hashtags
        assert request.limit == 50
    
    def test_discovery_request_normalizes_hashtags(self):
        """Test that hashtags are normalized with # prefix."""
        request = DiscoveryRequest(
            job_id=uuid4(),
            hashtags=["sustainablefashion", "#slowfashion"],  # One without #
            limit=10
        )
        
        # Both should have # prefix after normalization
        assert all(h.startswith("#") for h in request.hashtags)
    
    def test_discovery_response_serializes(self):
        """Test that DiscoveryResponse serializes correctly."""
        job_id = uuid4()
        response = DiscoveryResponse(
            job_id=job_id,
            profiles=[{"id": str(uuid4()), "username": "test"}],
            total_discovered=1,
            deduplicated=5,
            filtered_out=10,
            discovery_duration_seconds=45.2,
        )
        
        response_dict = response.model_dump()
        
        assert isinstance(response_dict, dict)
        assert response_dict["total_discovered"] == 1
        assert response_dict["deduplicated"] == 5
        assert response_dict["filtered_out"] == 10
