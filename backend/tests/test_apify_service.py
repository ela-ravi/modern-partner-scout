"""
PartnerScout AI - Apify Service Unit Tests (STORY-3.2.1)

Comprehensive unit tests for the ApifyService class including:
- Configuration and initialization
- Profile scraping
- Hashtag scraping
- Rate limiting
- Error handling
- Utility functions
"""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4

from app.services.apify_service import (
    ApifyService,
    ApifyActorType,
    ApifyRunStatus,
    InstagramProfile,
    HashtagPost,
    ApifyRunResult,
    RateLimiter,
    get_apify_service,
    create_apify_service,
    is_apify_configured,
    get_apify_config,
    DEFAULT_RATE_LIMIT_REQUESTS,
    DEFAULT_RATE_LIMIT_WINDOW,
)
from app.core.exceptions import ApifyError, ScrapingError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_apify_client():
    """Create a mock Apify client."""
    return Mock()


@pytest.fixture
def mock_actor_run():
    """Create a mock actor run response."""
    return {
        "id": "test-run-id",
        "status": "SUCCEEDED",
        "defaultDatasetId": "test-dataset-id",
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_profile_data():
    """Create sample Instagram profile data."""
    return {
        "username": "everlane",
        "fullName": "Everlane",
        "biography": "Modern essentials. Radical Transparency.",
        "followersCount": 850000,
        "followsCount": 500,
        "postsCount": 2500,
        "verified": True,
        "isBusinessAccount": True,
        "private": False,
        "profilePicUrl": "https://example.com/pic.jpg",
        "externalUrl": "https://everlane.com",
        "businessEmail": "collab@everlane.com",
        "businessCategoryName": "Clothing Store",
    }


@pytest.fixture
def sample_profile_data_fake():
    """Create sample fake/bot profile data."""
    return {
        "username": "fake_bot_12345",
        "fullName": "Fake Bot",
        "biography": "",
        "followersCount": 15000,
        "followsCount": 45000,  # High following/follower ratio
        "postsCount": 12,  # Too few posts
        "verified": False,
        "isBusinessAccount": False,
        "private": False,
        "profilePicUrl": None,
        "externalUrl": None,
        "businessEmail": None,
    }


@pytest.fixture
def sample_hashtag_posts():
    """Create sample hashtag search results."""
    return [
        {
            "id": "post1",
            "shortcode": "ABC123",
            "caption": "Sustainable fashion #sustainablefashion",
            "likesCount": 500,
            "commentsCount": 25,
            "ownerUsername": "user1",
            "hashtag": "sustainablefashion",
        },
        {
            "id": "post2",
            "shortcode": "DEF456",
            "caption": "Eco friendly outfit #sustainablefashion",
            "likesCount": 1000,
            "commentsCount": 50,
            "ownerUsername": "user2",
            "hashtag": "sustainablefashion",
        },
    ]


@pytest.fixture
def apify_service_mock():
    """Create an ApifyService with mocked client."""
    with patch('app.services.apify_service.ApifyClient') as mock_client_class:
        service = ApifyService(api_key="test-api-key")
        service._client = mock_client_class.return_value
        return service


# =============================================================================
# Configuration Tests
# =============================================================================

class TestApifyServiceConfiguration:
    """Test ApifyService configuration and initialization."""
    
    def test_init_with_default_settings(self):
        """Service should initialize with settings from config."""
        with patch('app.services.apify_service.settings') as mock_settings:
            mock_settings.apify.api_key = "test-key"
            mock_settings.apify.instagram_scraper_id = "apify/instagram-profile-scraper"
            mock_settings.apify.hashtag_scraper_id = "apify/instagram-hashtag-scraper"
            
            service = ApifyService()
            
            assert service._api_key == "test-key"
            assert service._profile_scraper_id == "apify/instagram-profile-scraper"
            assert service._hashtag_scraper_id == "apify/instagram-hashtag-scraper"
    
    def test_init_with_custom_api_key(self):
        """Service should accept custom API key."""
        service = ApifyService(api_key="custom-key")
        assert service._api_key == "custom-key"
    
    def test_init_with_custom_actor_ids(self):
        """Service should accept custom actor IDs."""
        service = ApifyService(
            api_key="test-key",
            profile_scraper_id="custom/profile-scraper",
            hashtag_scraper_id="custom/hashtag-scraper"
        )
        
        assert service._profile_scraper_id == "custom/profile-scraper"
        assert service._hashtag_scraper_id == "custom/hashtag-scraper"
    
    def test_is_configured_with_valid_key(self):
        """is_configured should return True for valid API key."""
        service = ApifyService(api_key="valid-api-key")
        assert service.is_configured() is True
    
    def test_is_configured_with_placeholder_key(self):
        """is_configured should return False for placeholder key."""
        service = ApifyService(api_key="your-apify-api-key")
        assert service.is_configured() is False
    
    def test_is_configured_with_empty_key(self):
        """is_configured should return False for empty key."""
        service = ApifyService(api_key="")
        assert service.is_configured() is False
    
    def test_client_raises_error_when_not_configured(self):
        """Accessing client should raise error when not configured."""
        service = ApifyService(api_key="your-apify-api-key")
        
        with pytest.raises(ApifyError) as exc:
            _ = service.client
        
        assert "not configured" in str(exc.value)
    
    def test_client_lazy_initialization(self):
        """Client should be lazily initialized."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            service = ApifyService(api_key="test-key")
            
            # Client not created yet
            assert service._client is None
            
            # Access client property
            _ = service.client
            
            # Now client should be created
            mock_client_class.assert_called_once_with("test-key")


# =============================================================================
# Pydantic Model Tests
# =============================================================================

class TestPydanticModels:
    """Test Pydantic models for Apify responses."""
    
    def test_instagram_profile_parsing(self, sample_profile_data):
        """InstagramProfile should parse Apify response correctly."""
        profile = InstagramProfile.model_validate(sample_profile_data)
        
        assert profile.username == "everlane"
        assert profile.full_name == "Everlane"
        assert profile.followers_count == 850000
        assert profile.following_count == 500
        assert profile.posts_count == 2500
        assert profile.is_verified is True
        assert profile.is_business_account is True
        assert profile.is_private is False
        assert profile.business_email == "collab@everlane.com"
    
    def test_instagram_profile_with_missing_fields(self):
        """InstagramProfile should handle missing optional fields."""
        minimal_data = {"username": "testuser"}
        profile = InstagramProfile.model_validate(minimal_data)
        
        assert profile.username == "testuser"
        assert profile.full_name is None
        assert profile.followers_count == 0
        assert profile.is_verified is False
    
    def test_hashtag_post_parsing(self, sample_hashtag_posts):
        """HashtagPost should parse Apify response correctly."""
        post = HashtagPost.model_validate(sample_hashtag_posts[0])
        
        assert post.id == "post1"
        assert post.shortcode == "ABC123"
        assert post.likes_count == 500
        assert post.comments_count == 25
        assert post.owner_username == "user1"
    
    def test_apify_run_result_model(self):
        """ApifyRunResult should validate correctly."""
        result = ApifyRunResult(
            run_id="test-run",
            status=ApifyRunStatus.SUCCEEDED,
            dataset_id="dataset-123",
            items_count=50
        )
        
        assert result.run_id == "test-run"
        assert result.status == ApifyRunStatus.SUCCEEDED
        assert result.dataset_id == "dataset-123"
        assert result.items_count == 50


# =============================================================================
# Rate Limiter Tests
# =============================================================================

class TestRateLimiter:
    """Test rate limiter functionality."""
    
    def test_rate_limiter_init(self):
        """Rate limiter should initialize with correct values."""
        limiter = RateLimiter(max_requests=5, window_seconds=30)
        
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 30
        assert limiter.tokens == 5
    
    def test_rate_limiter_acquire_sync_success(self):
        """Sync acquire should succeed when tokens available."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        # Should acquire successfully
        result = limiter.acquire_sync()
        assert result is True
        assert limiter.tokens < 10
    
    def test_rate_limiter_token_depletion(self):
        """Tokens should deplete on each acquire."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # Acquire all tokens
        for _ in range(3):
            limiter.acquire_sync()
        
        assert limiter.tokens < 1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_async_success(self):
        """Async acquire should succeed when tokens available."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        result = await limiter.acquire()
        assert result is True
    
    def test_rate_limiter_token_refill(self):
        """Tokens should refill over time."""
        limiter = RateLimiter(max_requests=10, window_seconds=1)  # Fast refill
        
        # Deplete some tokens
        limiter.tokens = 5
        
        # Wait a bit and check refill
        import time
        time.sleep(0.5)
        limiter._refill_tokens()
        
        # Should have more tokens now
        assert limiter.tokens > 5


# =============================================================================
# Profile Scraping Tests (Unit - Mocked)
# =============================================================================

class TestProfileScraping:
    """Test profile scraping functionality with mocks."""
    
    @pytest.mark.asyncio
    async def test_scrape_profile_success(self, sample_profile_data):
        """scrape_profile should return profile data."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            # Setup mocks
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter([sample_profile_data])
            
            service = ApifyService(api_key="test-key")
            result = await service.scrape_profile("everlane")
            
            assert result["username"] == "everlane"
            assert result["followersCount"] == 850000
    
    @pytest.mark.asyncio
    async def test_scrape_profile_cleans_username(self, sample_profile_data):
        """scrape_profile should clean @ from username."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter([sample_profile_data])
            
            service = ApifyService(api_key="test-key")
            await service.scrape_profile("@everlane")
            
            # Verify username was cleaned
            call_args = mock_actor.call.call_args
            assert "@everlane" not in call_args[1]["run_input"]["usernames"]
            assert "everlane" in call_args[1]["run_input"]["usernames"]
    
    @pytest.mark.asyncio
    async def test_scrape_profile_no_data_raises_error(self):
        """scrape_profile should raise error when no data returned."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter([])  # Empty results
            
            service = ApifyService(api_key="test-key")
            
            with pytest.raises(ScrapingError):
                await service.scrape_profile("nonexistent")
    
    @pytest.mark.asyncio
    async def test_scrape_profiles_multiple(self, sample_profile_data):
        """scrape_profiles should handle multiple usernames."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            profile2 = {**sample_profile_data, "username": "reformation"}
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter([sample_profile_data, profile2])
            
            service = ApifyService(api_key="test-key")
            results = await service.scrape_profiles(["everlane", "reformation"])
            
            assert len(results) == 2
    
    def test_scrape_profile_sync_success(self, sample_profile_data):
        """scrape_profile_sync should work synchronously."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter([sample_profile_data])
            
            service = ApifyService(api_key="test-key")
            result = service.scrape_profile_sync("everlane")
            
            assert result["username"] == "everlane"


# =============================================================================
# Hashtag Scraping Tests (Unit - Mocked)
# =============================================================================

class TestHashtagScraping:
    """Test hashtag scraping functionality with mocks."""
    
    @pytest.mark.asyncio
    async def test_search_hashtag_success(self, sample_hashtag_posts):
        """search_hashtag should return posts."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter(sample_hashtag_posts)
            
            service = ApifyService(api_key="test-key")
            results = await service.search_hashtag("#sustainablefashion", limit=50)
            
            assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_search_hashtag_cleans_hash(self, sample_hashtag_posts):
        """search_hashtag should remove # from hashtag."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter(sample_hashtag_posts)
            
            service = ApifyService(api_key="test-key")
            await service.search_hashtag("#sustainablefashion")
            
            call_args = mock_actor.call.call_args
            assert "#sustainablefashion" not in call_args[1]["run_input"]["hashtags"]
            assert "sustainablefashion" in call_args[1]["run_input"]["hashtags"]
    
    @pytest.mark.asyncio
    async def test_search_hashtags_multiple(self, sample_hashtag_posts):
        """search_hashtags should handle multiple hashtags."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            # Add posts for second hashtag
            posts_with_second = sample_hashtag_posts + [
                {
                    "id": "post3",
                    "likesCount": 200,
                    "ownerUsername": "user3",
                    "hashtag": "slowfashion",
                }
            ]
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter(posts_with_second)
            
            service = ApifyService(api_key="test-key")
            results = await service.search_hashtags(
                ["#sustainablefashion", "#slowfashion"]
            )
            
            assert "sustainablefashion" in results
            assert "slowfashion" in results
    
    def test_search_hashtag_sync_success(self, sample_hashtag_posts):
        """search_hashtag_sync should work synchronously."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter(sample_hashtag_posts)
            
            service = ApifyService(api_key="test-key")
            results = service.search_hashtag_sync("sustainablefashion")
            
            assert len(results) == 2


# =============================================================================
# Discovery Helper Tests
# =============================================================================

class TestDiscoveryHelpers:
    """Test discovery helper methods."""
    
    @pytest.mark.asyncio
    async def test_discover_profiles_by_hashtags(self, sample_hashtag_posts):
        """discover_profiles_by_hashtags should extract unique usernames."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_dataset = Mock()
            
            mock_client.actor.return_value = mock_actor
            mock_actor.call.return_value = {"defaultDatasetId": "test-dataset"}
            mock_client.dataset.return_value = mock_dataset
            mock_dataset.iterate_items.return_value = iter(sample_hashtag_posts)
            
            service = ApifyService(api_key="test-key")
            usernames = await service.discover_profiles_by_hashtags(
                ["#sustainablefashion"]
            )
            
            assert "user1" in usernames
            assert "user2" in usernames
            assert len(usernames) == 2  # Unique usernames


# =============================================================================
# Utility Function Tests
# =============================================================================

class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_extract_username_from_url_standard(self):
        """Should extract username from standard Instagram URL."""
        service = ApifyService(api_key="test-key")
        
        assert service.extract_username_from_url(
            "https://instagram.com/everlane"
        ) == "everlane"
        
        assert service.extract_username_from_url(
            "https://www.instagram.com/everlane/"
        ) == "everlane"
    
    def test_extract_username_from_url_short(self):
        """Should extract username from short Instagram URL."""
        service = ApifyService(api_key="test-key")
        
        assert service.extract_username_from_url(
            "https://instagr.am/everlane"
        ) == "everlane"
    
    def test_extract_username_filters_special_pages(self):
        """Should return None for special pages."""
        service = ApifyService(api_key="test-key")
        
        assert service.extract_username_from_url(
            "https://instagram.com/p/ABC123"
        ) is None
        
        assert service.extract_username_from_url(
            "https://instagram.com/explore"
        ) is None
    
    def test_extract_username_invalid_url(self):
        """Should return None for invalid URLs."""
        service = ApifyService(api_key="test-key")
        
        assert service.extract_username_from_url("not-a-url") is None
        assert service.extract_username_from_url(
            "https://twitter.com/everlane"
        ) is None
    
    def test_calculate_engagement_rate_with_posts(self):
        """Should calculate engagement rate from recent posts."""
        service = ApifyService(api_key="test-key")
        
        profile_data = {
            "followersCount": 10000,
            "recentPosts": [
                {"likesCount": 500, "commentsCount": 50},
                {"likesCount": 600, "commentsCount": 40},
            ]
        }
        
        rate = service.calculate_engagement_rate(profile_data)
        # (500+50 + 600+40) / 2 / 10000 * 100 = 5.95%
        assert 5.9 <= rate <= 6.0
    
    def test_calculate_engagement_rate_zero_followers(self):
        """Should return 0 for zero followers."""
        service = ApifyService(api_key="test-key")
        
        profile_data = {"followersCount": 0}
        assert service.calculate_engagement_rate(profile_data) == 0.0
    
    def test_is_likely_fake_profile_genuine(self, sample_profile_data):
        """Should return False for genuine profile."""
        service = ApifyService(api_key="test-key")
        assert service.is_likely_fake_profile(sample_profile_data) is False
    
    def test_is_likely_fake_profile_high_ratio(self, sample_profile_data_fake):
        """Should return True for high following/follower ratio."""
        service = ApifyService(api_key="test-key")
        assert service.is_likely_fake_profile(sample_profile_data_fake) is True
    
    def test_is_likely_fake_profile_few_posts(self):
        """Should return True for few posts with many followers."""
        service = ApifyService(api_key="test-key")
        
        profile = {
            "followersCount": 50000,
            "followsCount": 500,
            "postsCount": 10,  # Too few
        }
        
        assert service.is_likely_fake_profile(profile) is True
    
    def test_is_likely_fake_profile_zero_followers(self):
        """Should return True for zero followers."""
        service = ApifyService(api_key="test-key")
        
        profile = {"followersCount": 0, "followsCount": 100, "postsCount": 5}
        assert service.is_likely_fake_profile(profile) is True
    
    def test_calculate_fake_score_genuine(self, sample_profile_data):
        """Should return high score for genuine profile."""
        service = ApifyService(api_key="test-key")
        score = service.calculate_fake_score(sample_profile_data)
        
        # Genuine profile with business account, email, website
        assert score >= 70
    
    def test_calculate_fake_score_fake(self, sample_profile_data_fake):
        """Should return low score for fake profile."""
        service = ApifyService(api_key="test-key")
        score = service.calculate_fake_score(sample_profile_data_fake)
        
        # Fake profile with high ratio, few posts, no business indicators
        assert score < 50
    
    def test_calculate_fake_score_boundaries(self):
        """Score should be capped between 0-100."""
        service = ApifyService(api_key="test-key")
        
        # Very bad profile
        bad_profile = {
            "followersCount": 100,
            "followsCount": 10000,  # 100x ratio
            "postsCount": 0,
        }
        assert service.calculate_fake_score(bad_profile) >= 0
        
        # Very good profile
        good_profile = {
            "followersCount": 100000,
            "followsCount": 500,
            "postsCount": 1000,
            "isBusinessAccount": True,
            "businessEmail": "test@example.com",
            "externalUrl": "https://example.com",
        }
        assert service.calculate_fake_score(good_profile) <= 100


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestFactoryFunctions:
    """Test factory and utility functions."""
    
    def test_get_apify_service_returns_instance(self):
        """get_apify_service should return ApifyService instance."""
        # Clear cache to ensure fresh instance
        get_apify_service.cache_clear()
        
        service = get_apify_service()
        assert isinstance(service, ApifyService)
    
    def test_get_apify_service_cached(self):
        """get_apify_service should return cached instance."""
        get_apify_service.cache_clear()
        
        service1 = get_apify_service()
        service2 = get_apify_service()
        
        assert service1 is service2
    
    def test_create_apify_service_custom(self):
        """create_apify_service should create custom instance."""
        service = create_apify_service(
            api_key="custom-key",
            profile_scraper_id="custom/profile",
            hashtag_scraper_id="custom/hashtag",
        )
        
        assert service._api_key == "custom-key"
        assert service._profile_scraper_id == "custom/profile"
        assert service._hashtag_scraper_id == "custom/hashtag"
    
    def test_is_apify_configured_true(self):
        """is_apify_configured should return True when configured."""
        with patch('app.services.apify_service.settings') as mock_settings:
            mock_settings.apify.api_key = "real-api-key"
            assert is_apify_configured() is True
    
    def test_is_apify_configured_false(self):
        """is_apify_configured should return False when not configured."""
        with patch('app.services.apify_service.settings') as mock_settings:
            mock_settings.apify.api_key = "your-apify-api-key"
            assert is_apify_configured() is False
    
    def test_get_apify_config(self):
        """get_apify_config should return config dict."""
        with patch('app.services.apify_service.settings') as mock_settings:
            mock_settings.apify.api_key = "test-key"
            mock_settings.apify.instagram_scraper_id = "apify/profile"
            mock_settings.apify.hashtag_scraper_id = "apify/hashtag"
            
            config = get_apify_config()
            
            assert "configured" in config
            assert "profile_scraper_id" in config
            assert "hashtag_scraper_id" in config


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_scrape_profile_handles_api_error(self):
        """Should wrap API errors in ApifyError."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_actor.call.side_effect = Exception("API Error")
            mock_client.actor.return_value = mock_actor
            
            service = ApifyService(api_key="test-key")
            
            with pytest.raises(ApifyError) as exc:
                await service.scrape_profile("test")
            
            assert "Failed to scrape profiles" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_search_hashtag_handles_api_error(self):
        """Should wrap API errors in ApifyError for hashtag search."""
        with patch('app.services.apify_service.ApifyClient') as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_actor = Mock()
            mock_actor.call.side_effect = Exception("API Error")
            mock_client.actor.return_value = mock_actor
            
            service = ApifyService(api_key="test-key")
            
            with pytest.raises(ApifyError) as exc:
                await service.search_hashtag("#test")
            
            assert "Failed to search hashtags" in str(exc.value)


# =============================================================================
# Repr Tests
# =============================================================================

class TestRepr:
    """Test string representation."""
    
    def test_repr_configured(self):
        """Should show configured status."""
        service = ApifyService(api_key="real-key")
        assert "configured" in repr(service)
    
    def test_repr_not_configured(self):
        """Should show not configured status."""
        service = ApifyService(api_key="")
        assert "not configured" in repr(service)
