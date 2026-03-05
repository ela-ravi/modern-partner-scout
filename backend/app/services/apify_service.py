"""
PartnerScout AI - Apify Service (STORY-3.2.1)

Provides integration with Apify for Instagram profile and hashtag scraping.
Includes rate limiting, retry logic, and comprehensive error handling.

Features:
- Instagram Profile Scraper integration
- Hashtag Scraper integration
- Configurable rate limiting
- Exponential backoff retry logic
- Async/sync operation modes
"""

import asyncio
import logging
import time as _time
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from apify_client import ApifyClient
from apify_client.clients import ActorClient
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
    RetryError,
)

from app.core.config import settings
from app.core.constants import Defaults
from app.core.exceptions import ApifyError, ScrapingError


# =============================================================================
# Logger Configuration
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class ApifyActorType(str, Enum):
    """Types of Apify actors used in the application."""
    INSTAGRAM_PROFILE = "instagram_profile"
    INSTAGRAM_HASHTAG = "instagram_hashtag"


class ApifyRunStatus(str, Enum):
    """Apify actor run statuses."""
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"
    TIMED_OUT = "TIMED-OUT"


# Default Actor IDs (can be overridden via config)
DEFAULT_PROFILE_SCRAPER = "apify/instagram-profile-scraper"
DEFAULT_HASHTAG_SCRAPER = "apify/instagram-hashtag-scraper"
DEFAULT_GOOGLE_SEARCH_SCRAPER = "apify/google-search-scraper"
DEFAULT_SEARCH_SCRAPER = "apify/instagram-search-scraper"
DEFAULT_TAGGED_SCRAPER = "apify/instagram-tagged-scraper"

# Rate limiting defaults
DEFAULT_RATE_LIMIT_REQUESTS = 10  # requests per window
DEFAULT_RATE_LIMIT_WINDOW = 60  # seconds
DEFAULT_POLL_INTERVAL = 5  # seconds between status checks
DEFAULT_MAX_WAIT_TIME = 300  # 5 minutes max wait for a run


# =============================================================================
# Pydantic Models for Apify Responses
# =============================================================================

class InstagramProfile(BaseModel):
    """Parsed Instagram profile data from Apify scraper."""
    
    model_config = {"populate_by_name": True, "extra": "ignore"}
    
    username: str
    full_name: Optional[str] = Field(default=None, alias="fullName")
    biography: Optional[str] = None
    followers_count: int = Field(default=0, alias="followersCount")
    following_count: int = Field(default=0, alias="followsCount")
    posts_count: int = Field(default=0, alias="postsCount")
    is_verified: bool = Field(default=False, alias="verified")
    is_business_account: bool = Field(default=False, alias="isBusinessAccount")
    is_private: bool = Field(default=False, alias="private")
    profile_pic_url: Optional[str] = Field(default=None, alias="profilePicUrl")
    profile_pic_url_hd: Optional[str] = Field(default=None, alias="profilePicUrlHD")
    external_url: Optional[str] = Field(default=None, alias="externalUrl")
    business_email: Optional[str] = Field(default=None, alias="businessEmail")
    business_phone: Optional[str] = Field(default=None, alias="businessPhoneNumber")
    business_category: Optional[str] = Field(default=None, alias="businessCategoryName")
    engagement_rate: Optional[float] = Field(default=None, alias="engagementRate")
    
    # Additional fields that may be present
    id: Optional[str] = None
    url: Optional[str] = None


class HashtagPost(BaseModel):
    """Instagram post from hashtag search results."""
    
    model_config = {"populate_by_name": True, "extra": "ignore"}
    
    id: str
    shortcode: Optional[str] = None
    caption: Optional[str] = None
    likes_count: int = Field(default=0, alias="likesCount")
    comments_count: int = Field(default=0, alias="commentsCount")
    timestamp: Optional[datetime] = None
    owner_username: Optional[str] = Field(default=None, alias="ownerUsername")
    owner_id: Optional[str] = Field(default=None, alias="ownerId")
    display_url: Optional[str] = Field(default=None, alias="displayUrl")
    is_video: bool = Field(default=False, alias="isVideo")


class ApifyRunResult(BaseModel):
    """Result of an Apify actor run."""
    
    run_id: str
    status: ApifyRunStatus
    dataset_id: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    items_count: int = 0
    error_message: Optional[str] = None


# =============================================================================
# Rate Limiter
# =============================================================================

class RateLimiter:
    """
    Simple token bucket rate limiter for API requests.
    
    Thread-safe rate limiting with configurable requests per window.
    """
    
    def __init__(
        self,
        max_requests: int = DEFAULT_RATE_LIMIT_REQUESTS,
        window_seconds: int = DEFAULT_RATE_LIMIT_WINDOW
    ):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Window duration in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.tokens = max_requests
        self.last_update = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = datetime.now(timezone.utc)
        elapsed = (now - self.last_update).total_seconds()
        
        # Calculate tokens to add
        tokens_to_add = (elapsed / self.window_seconds) * self.max_requests
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
        self.last_update = now
    
    async def acquire(self) -> bool:
        """
        Acquire a token for making a request.
        
        Returns:
            True if token acquired, waits if rate limited
        """
        async with self._lock:
            self._refill_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            
            # Calculate wait time for next token
            wait_time = (1 - self.tokens) * (self.window_seconds / self.max_requests)
            
        # Wait outside the lock
        logger.info(f"Rate limited, waiting {wait_time:.2f} seconds")
        await asyncio.sleep(wait_time)
        
        # Try again after waiting
        return await self.acquire()
    
    def acquire_sync(self) -> bool:
        """
        Synchronous version of acquire.
        
        Returns:
            True when token is acquired
        """
        self._refill_tokens()
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        # Calculate wait time for next token
        wait_time = (1 - self.tokens) * (self.window_seconds / self.max_requests)
        logger.info(f"Rate limited, waiting {wait_time:.2f} seconds")
        import time
        time.sleep(wait_time)
        
        # Try again after waiting
        return self.acquire_sync()


# =============================================================================
# Profile Cache (avoids re-scraping same profiles across jobs)
# =============================================================================

class ProfileCache:
    """
    Simple TTL cache for scraped profile data.

    Prevents redundant Apify API calls for profiles that were
    recently scraped, saving compute units on the free tier.
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 500):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size

    def get(self, username: str) -> Optional[Dict[str, Any]]:
        """Get cached profile data if still valid."""
        username = username.lower()
        if username in self._cache:
            if _time.time() - self._timestamps[username] < self._ttl:
                logger.debug(f"Cache HIT for @{username} (saved 1 Apify call)")
                return self._cache[username]
            else:
                del self._cache[username]
                del self._timestamps[username]
        return None

    def put(self, username: str, data: Dict[str, Any]) -> None:
        """Cache profile data."""
        username = username.lower()
        if len(self._cache) >= self._max_size:
            oldest = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest]
            del self._timestamps[oldest]
        self._cache[username] = data
        self._timestamps[username] = _time.time()

    def put_many(self, profiles: List[Dict[str, Any]]) -> None:
        """Cache multiple profile results."""
        for profile in profiles:
            username = profile.get("username", "")
            if username:
                self.put(username, profile)

    @property
    def size(self) -> int:
        return len(self._cache)


# =============================================================================
# Apify Service Class
# =============================================================================

class ApifyService:
    """
    Service for interacting with Apify scraping platform.
    
    Provides methods for:
    - Scraping Instagram profiles
    - Discovering profiles via hashtag search
    - Managing actor runs
    - Handling rate limits and retries
    
    Example:
        ```python
        service = ApifyService()
        
        # Scrape a single profile
        profile = await service.scrape_profile("everlane")
        
        # Scrape multiple profiles
        profiles = await service.scrape_profiles(["everlane", "reformation"])
        
        # Discover profiles by hashtag
        posts = await service.search_hashtag("#sustainablefashion", limit=50)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        profile_scraper_id: Optional[str] = None,
        hashtag_scraper_id: Optional[str] = None,
        search_scraper_id: Optional[str] = None,
        tagged_scraper_id: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        """
        Initialize the Apify service.

        Args:
            api_key: Apify API key (defaults to env var)
            profile_scraper_id: Actor ID for profile scraping
            hashtag_scraper_id: Actor ID for hashtag scraping
            search_scraper_id: Actor ID for user/keyword search
            tagged_scraper_id: Actor ID for tagged posts scraping
            rate_limiter: Optional custom rate limiter
        """
        self._api_key = api_key or settings.apify.api_key
        self._profile_scraper_id = profile_scraper_id or settings.apify.instagram_scraper_id
        self._hashtag_scraper_id = hashtag_scraper_id or settings.apify.hashtag_scraper_id
        self._search_scraper_id = search_scraper_id or settings.apify.search_scraper_id
        self._tagged_scraper_id = tagged_scraper_id or settings.apify.tagged_scraper_id
        self._rate_limiter = rate_limiter or RateLimiter()

        # Profile cache to avoid redundant scrapes (1 hour TTL)
        self._profile_cache = ProfileCache(ttl_seconds=3600, max_size=500)

        # Lazy-initialized client
        self._client: Optional[ApifyClient] = None
    
    @property
    def client(self) -> ApifyClient:
        """
        Get or create the Apify client (lazy initialization).
        
        Returns:
            ApifyClient instance
            
        Raises:
            ApifyError: If API key is not configured
        """
        if self._client is None:
            if not self._api_key or self._api_key == "your-apify-api-key":
                raise ApifyError(
                    message="Apify API key is not configured",
                    details={"hint": "Set APIFY_API_KEY in your .env file"}
                )
            self._client = ApifyClient(self._api_key)
        return self._client
    
    def is_configured(self) -> bool:
        """
        Check if the Apify service is properly configured.
        
        Returns:
            True if API key is set
        """
        return bool(self._api_key and self._api_key != "your-apify-api-key")
    
    # =========================================================================
    # Profile Scraping Methods
    # =========================================================================
    
    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def scrape_profile(
        self,
        username: str,
        results_limit: int = 5,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> Dict[str, Any]:
        """
        Scrape a single Instagram profile.
        
        Args:
            username: Instagram username to scrape (without @)
            results_limit: Max number of recent posts to include
            timeout: Maximum wait time in seconds
            
        Returns:
            Dict containing profile data
            
        Raises:
            ApifyError: If scraping fails
            TimeoutError: If run exceeds timeout
        """
        profiles = await self.scrape_profiles([username], results_limit, timeout)
        
        if not profiles:
            raise ScrapingError(
                message=f"No data returned for profile: {username}",
                target=username,
                details={"username": username}
            )
        
        return profiles[0]
    
    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def scrape_profiles(
        self,
        usernames: List[str],
        results_limit: int = 5,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple Instagram profiles.
        
        Args:
            usernames: List of Instagram usernames to scrape
            results_limit: Max number of recent posts to include per profile
            timeout: Maximum wait time in seconds
            
        Returns:
            List of dicts containing profile data
            
        Raises:
            ApifyError: If scraping fails
            TimeoutError: If run exceeds timeout
        """
        # Clean usernames (remove @ if present)
        clean_usernames = [u.lstrip("@").strip() for u in usernames]

        # Check cache first - only scrape profiles we don't already have
        cached_results = []
        uncached_usernames = []
        for username in clean_usernames:
            cached = self._profile_cache.get(username)
            if cached is not None:
                cached_results.append(cached)
            else:
                uncached_usernames.append(username)

        if cached_results:
            logger.info(
                f"Cache: {len(cached_results)} cached, "
                f"{len(uncached_usernames)} need scraping"
            )

        # If all profiles are cached, return immediately (no Apify call!)
        if not uncached_usernames:
            logger.info(f"All {len(clean_usernames)} profiles served from cache")
            return cached_results

        # Acquire rate limit token
        await self._rate_limiter.acquire()

        logger.info(f"Scraping {len(uncached_usernames)} profiles: {uncached_usernames}")

        # Prepare input for the actor
        run_input = {
            "usernames": uncached_usernames,
            "resultsLimit": results_limit,
        }

        try:
            # Start the actor run
            run = self.client.actor(self._profile_scraper_id).call(
                run_input=run_input,
                timeout_secs=timeout,
            )

            # Get results from the default dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Cache the new results
            self._profile_cache.put_many(items)

            logger.info(f"Successfully scraped {len(items)} profiles")
            return cached_results + items

        except Exception as e:
            logger.error(f"Profile scraping failed: {e}")
            raise ApifyError(
                message=f"Failed to scrape profiles: {str(e)}",
                actor_id=self._profile_scraper_id,
                details={"usernames": uncached_usernames, "error": str(e)}
            )
    
    async def scrape_profile_parsed(
        self,
        username: str,
        results_limit: int = 5,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> InstagramProfile:
        """
        Scrape a profile and return parsed Pydantic model.
        
        Args:
            username: Instagram username to scrape
            results_limit: Max posts to include
            timeout: Max wait time
            
        Returns:
            InstagramProfile model instance
        """
        data = await self.scrape_profile(username, results_limit, timeout)
        return InstagramProfile.model_validate(data)
    
    def scrape_profile_sync(
        self,
        username: str,
        results_limit: int = 5,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> Dict[str, Any]:
        """
        Synchronous version of scrape_profile.
        
        Args:
            username: Instagram username to scrape
            results_limit: Max posts to include
            timeout: Max wait time
            
        Returns:
            Dict containing profile data
        """
        profiles = self.scrape_profiles_sync([username], results_limit, timeout)
        
        if not profiles:
            raise ScrapingError(
                message=f"No data returned for profile: {username}",
                target=username,
            )
        
        return profiles[0]
    
    def scrape_profiles_sync(
        self,
        usernames: List[str],
        results_limit: int = 5,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of scrape_profiles.
        
        Args:
            usernames: List of usernames to scrape
            results_limit: Max posts per profile
            timeout: Max wait time
            
        Returns:
            List of profile data dicts
        """
        # Clean usernames
        clean_usernames = [u.lstrip("@").strip() for u in usernames]

        # Check cache first
        cached_results = []
        uncached_usernames = []
        for username in clean_usernames:
            cached = self._profile_cache.get(username)
            if cached is not None:
                cached_results.append(cached)
            else:
                uncached_usernames.append(username)

        if not uncached_usernames:
            logger.info(f"All {len(clean_usernames)} profiles served from cache (sync)")
            return cached_results

        # Acquire rate limit token
        self._rate_limiter.acquire_sync()

        logger.info(f"Scraping {len(uncached_usernames)} profiles (sync): {uncached_usernames}")

        run_input = {
            "usernames": uncached_usernames,
            "resultsLimit": results_limit,
        }

        try:
            run = self.client.actor(self._profile_scraper_id).call(
                run_input=run_input,
                timeout_secs=timeout,
            )

            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Cache the new results
            self._profile_cache.put_many(items)

            logger.info(f"Successfully scraped {len(items)} profiles (sync)")
            return cached_results + items

        except Exception as e:
            logger.error(f"Profile scraping failed (sync): {e}")
            raise ApifyError(
                message=f"Failed to scrape profiles: {str(e)}",
                actor_id=self._profile_scraper_id,
                details={"usernames": uncached_usernames, "error": str(e)}
            )
    
    # =========================================================================
    # Hashtag Scraping Methods
    # =========================================================================
    
    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def search_hashtag(
        self,
        hashtag: str,
        limit: int = 20,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[Dict[str, Any]]:
        """
        Search for posts by hashtag.
        
        Args:
            hashtag: Hashtag to search (with or without #)
            limit: Maximum number of posts to return
            timeout: Maximum wait time in seconds
            
        Returns:
            List of post data dicts
            
        Raises:
            ApifyError: If search fails
        """
        results = await self.search_hashtags([hashtag], limit, timeout)
        return results.get(hashtag.lstrip("#"), [])
    
    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def search_hashtags(
        self,
        hashtags: List[str],
        limit_per_hashtag: int = 20,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for posts by multiple hashtags.
        
        Args:
            hashtags: List of hashtags to search
            limit_per_hashtag: Max posts per hashtag
            timeout: Maximum wait time in seconds
            
        Returns:
            Dict mapping hashtag to list of posts
            
        Raises:
            ApifyError: If search fails
        """
        # Acquire rate limit token
        await self._rate_limiter.acquire()
        
        # Clean hashtags (remove # if present)
        clean_hashtags = [h.lstrip("#").strip() for h in hashtags]
        
        logger.info(f"Searching {len(clean_hashtags)} hashtags: {clean_hashtags}")
        
        run_input = {
            "hashtags": clean_hashtags,
            "resultsLimit": limit_per_hashtag,
        }
        
        try:
            run = self.client.actor(self._hashtag_scraper_id).call(
                run_input=run_input,
                timeout_secs=timeout,
            )
            
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            # Group results by hashtag
            results: Dict[str, List[Dict[str, Any]]] = {h: [] for h in clean_hashtags}
            for item in items:
                # Try to determine which hashtag this belongs to
                item_hashtag = item.get("hashtag", "").lstrip("#")
                if item_hashtag in results:
                    results[item_hashtag].append(item)
                else:
                    # If no hashtag field, add to first hashtag
                    if clean_hashtags:
                        results[clean_hashtags[0]].append(item)
            
            total_posts = sum(len(posts) for posts in results.values())
            logger.info(f"Found {total_posts} posts across {len(clean_hashtags)} hashtags")
            
            return results
            
        except Exception as e:
            logger.error(f"Hashtag search failed: {e}")
            raise ApifyError(
                message=f"Failed to search hashtags: {str(e)}",
                actor_id=self._hashtag_scraper_id,
                details={"hashtags": clean_hashtags, "error": str(e)}
            )
    
    def search_hashtag_sync(
        self,
        hashtag: str,
        limit: int = 20,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[Dict[str, Any]]:
        """
        Synchronous version of search_hashtag.
        
        Args:
            hashtag: Hashtag to search
            limit: Max posts to return
            timeout: Max wait time
            
        Returns:
            List of post data dicts
        """
        results = self.search_hashtags_sync([hashtag], limit, timeout)
        return results.get(hashtag.lstrip("#"), [])
    
    def search_hashtags_sync(
        self,
        hashtags: List[str],
        limit_per_hashtag: int = 20,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Synchronous version of search_hashtags.
        
        Args:
            hashtags: List of hashtags to search
            limit_per_hashtag: Max posts per hashtag
            timeout: Max wait time
            
        Returns:
            Dict mapping hashtag to list of posts
        """
        # Acquire rate limit token
        self._rate_limiter.acquire_sync()
        
        # Clean hashtags
        clean_hashtags = [h.lstrip("#").strip() for h in hashtags]
        
        logger.info(f"Searching {len(clean_hashtags)} hashtags (sync): {clean_hashtags}")
        
        run_input = {
            "hashtags": clean_hashtags,
            "resultsLimit": limit_per_hashtag,
        }
        
        try:
            run = self.client.actor(self._hashtag_scraper_id).call(
                run_input=run_input,
                timeout_secs=timeout,
            )
            
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            # Group results by hashtag
            results: Dict[str, List[Dict[str, Any]]] = {h: [] for h in clean_hashtags}
            for item in items:
                item_hashtag = item.get("hashtag", "").lstrip("#")
                if item_hashtag in results:
                    results[item_hashtag].append(item)
                elif clean_hashtags:
                    results[clean_hashtags[0]].append(item)
            
            total_posts = sum(len(posts) for posts in results.values())
            logger.info(f"Found {total_posts} posts across {len(clean_hashtags)} hashtags (sync)")
            
            return results
            
        except Exception as e:
            logger.error(f"Hashtag search failed (sync): {e}")
            raise ApifyError(
                message=f"Failed to search hashtags: {str(e)}",
                actor_id=self._hashtag_scraper_id,
                details={"hashtags": clean_hashtags, "error": str(e)}
            )
    
    # =========================================================================
    # Keyword User Search Methods
    # =========================================================================

    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def search_users(
        self,
        keywords: List[str],
        limit_per_keyword: int = 20,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[Dict[str, Any]]:
        """
        Search for Instagram users by keyword using apify/instagram-search-scraper.

        This finds user accounts matching search queries like "perfume distributor"
        or "fragrance boutique" — useful for discovering complementary partners
        rather than competitors.

        Args:
            keywords: List of search query strings
            limit_per_keyword: Maximum user results per keyword
            timeout: Maximum wait time per keyword in seconds

        Returns:
            Flat list of user profile results (may contain duplicates across keywords)

        Raises:
            ApifyError: If all keyword searches fail
        """
        all_results: List[Dict[str, Any]] = []
        seen_usernames: set = set()

        for keyword in keywords:
            keyword = keyword.strip()
            if not keyword:
                continue

            await self._rate_limiter.acquire()

            logger.info(f"Keyword user search: {keyword!r} (limit={limit_per_keyword})")

            run_input = {
                "search": keyword,
                "searchType": "user",
                "resultsLimit": limit_per_keyword,
            }

            try:
                run = self.client.actor(self._search_scraper_id).call(
                    run_input=run_input,
                    timeout_secs=timeout,
                )

                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

                # Deduplicate by username across keywords
                for item in items:
                    username = (
                        item.get("username")
                        or item.get("userName")
                        or ""
                    ).lower()
                    if username and username not in seen_usernames:
                        seen_usernames.add(username)
                        all_results.append(item)

                logger.info(
                    f"Keyword search {keyword!r} returned {len(items)} results "
                    f"({len(all_results)} unique total)"
                )

            except Exception as e:
                logger.warning(f"Keyword user search failed for {keyword!r}: {e}")
                continue

        logger.info(
            f"Keyword user search complete: {len(all_results)} unique users "
            f"from {len(keywords)} keywords"
        )
        return all_results

    # =========================================================================
    # Tagged Posts Discovery
    # =========================================================================

    @retry(
        retry=retry_if_exception_type((ApifyError, TimeoutError)),
        stop=stop_after_attempt(Defaults.MAX_RETRIES),
        wait=wait_exponential(multiplier=Defaults.RETRY_DELAY_SECONDS, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def search_tagged_posts(
        self,
        usernames: List[str],
        results_limit: int = 50,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[str]:
        """
        Find accounts that tag the given brand profiles.

        Uses apify/instagram-tagged-scraper to scrape the "Tagged" tab of
        brand profiles. People who tag a brand are warm leads — distributors
        showcasing stock, influencers reviewing products, boutiques featuring
        the brand.

        Args:
            usernames: Brand profile usernames to check tagged posts for
            results_limit: Maximum tagged posts to retrieve per username
            timeout: Maximum wait time in seconds

        Returns:
            Deduplicated list of usernames who tagged the brand profiles
        """
        await self._rate_limiter.acquire()

        clean_usernames = [u.lstrip("@").strip() for u in usernames if u.strip()]
        if not clean_usernames:
            return []

        logger.info(
            f"Tagged posts discovery: checking who tags {clean_usernames} "
            f"(limit={results_limit})"
        )

        run_input = {
            "usernames": clean_usernames,
            "resultsLimit": results_limit,
        }

        try:
            run = self.client.actor(self._tagged_scraper_id).call(
                run_input=run_input,
                timeout_secs=timeout,
            )

            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Extract unique usernames of people who tagged the brand
            taggers: set = set()
            brand_set = {u.lower() for u in clean_usernames}

            for item in items:
                # The tagged scraper returns posts — extract the post owner
                owner = (
                    item.get("ownerUsername")
                    or item.get("owner_username")
                    or (item.get("owner") or {}).get("username")
                    or item.get("username")
                    or ""
                ).lower().strip().lstrip("@")

                if owner and owner not in brand_set:
                    taggers.add(owner)

            logger.info(
                f"Tagged posts discovery: {len(taggers)} unique accounts "
                f"tag {clean_usernames} (from {len(items)} tagged posts)"
            )
            return list(taggers)

        except Exception as e:
            logger.warning(f"Tagged posts discovery failed: {e}")
            return []

    # =========================================================================
    # Helper Methods for Discovery
    # =========================================================================
    
    async def discover_profiles_by_hashtags(
        self,
        hashtags: List[str],
        limit_per_hashtag: int = 20,
        min_followers: int = Defaults.DEFAULT_MIN_FOLLOWERS,
        max_followers: int = Defaults.DEFAULT_MAX_FOLLOWERS,
        timeout: int = DEFAULT_MAX_WAIT_TIME,
    ) -> List[str]:
        """
        Discover unique usernames from hashtag posts.
        
        Args:
            hashtags: Hashtags to search
            limit_per_hashtag: Max posts per hashtag
            min_followers: Minimum follower count filter
            max_followers: Maximum follower count filter
            timeout: Max wait time
            
        Returns:
            List of unique usernames
        """
        hashtag_results = await self.search_hashtags(
            hashtags, 
            limit_per_hashtag, 
            timeout
        )
        
        # Extract unique usernames
        usernames = set()
        for hashtag, posts in hashtag_results.items():
            for post in posts:
                owner = post.get("ownerUsername") or post.get("owner", {}).get("username")
                if owner:
                    usernames.add(owner)
        
        logger.info(f"Discovered {len(usernames)} unique usernames from {len(hashtags)} hashtags")
        return list(usernames)
    
    async def get_profiles_with_filters(
        self,
        usernames: List[str],
        min_followers: int = Defaults.DEFAULT_MIN_FOLLOWERS,
        max_followers: int = Defaults.DEFAULT_MAX_FOLLOWERS,
        exclude_private: bool = True,
        batch_size: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get profile data and filter by criteria.
        
        Args:
            usernames: Usernames to scrape
            min_followers: Minimum follower count
            max_followers: Maximum follower count
            exclude_private: Exclude private accounts
            batch_size: Number of profiles to scrape per batch
            
        Returns:
            List of filtered profile data
        """
        filtered_profiles = []
        
        # Process in batches to respect rate limits
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            
            try:
                profiles = await self.scrape_profiles(batch)
                
                for profile in profiles:
                    followers = profile.get("followersCount", 0)
                    is_private = profile.get("private", False)
                    
                    # Apply filters
                    if followers < min_followers or followers > max_followers:
                        continue
                    if exclude_private and is_private:
                        continue
                    
                    filtered_profiles.append(profile)
                    
            except ApifyError as e:
                logger.warning(f"Failed to scrape batch {i // batch_size + 1}: {e}")
                continue
        
        logger.info(f"Filtered to {len(filtered_profiles)} profiles from {len(usernames)} candidates")
        return filtered_profiles
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract Instagram username from a URL.
        
        Args:
            url: Instagram profile URL
            
        Returns:
            Username or None if invalid URL
        """
        import re
        
        # Handle various Instagram URL formats
        patterns = [
            r"instagram\.com/([a-zA-Z0-9_.]+)/?",
            r"instagr\.am/([a-zA-Z0-9_.]+)/?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Filter out special pages
                if username not in ["p", "reel", "stories", "explore", "accounts"]:
                    return username
        
        return None
    
    def calculate_engagement_rate(self, profile_data: Dict[str, Any]) -> float:
        """
        Calculate engagement rate from profile data.
        
        Args:
            profile_data: Profile data dict
            
        Returns:
            Engagement rate as a percentage (0-100)
        """
        followers = profile_data.get("followersCount", 0)
        if followers == 0:
            return 0.0
        
        # If recent posts are available, calculate from them
        recent_posts = profile_data.get("recentPosts", [])
        if recent_posts:
            total_engagement = sum(
                post.get("likesCount", 0) + post.get("commentsCount", 0)
                for post in recent_posts
            )
            avg_engagement = total_engagement / len(recent_posts)
            engagement_rate = (avg_engagement / followers) * 100
            return round(engagement_rate, 2)
        
        # Fallback to provided engagement rate if available
        return profile_data.get("engagementRate", 0.0)
    
    def is_likely_fake_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Determine if a profile is likely fake/bot based on signals.
        
        Uses the detection algorithm from Apify_Fake_Detection_Guide.md
        
        Args:
            profile_data: Profile data dict
            
        Returns:
            True if profile appears fake
        """
        followers = profile_data.get("followersCount", 0)
        following = profile_data.get("followsCount", profile_data.get("followingCount", 0))
        posts = profile_data.get("postsCount", 0)
        
        # Prevent division by zero
        if followers == 0:
            return True  # No followers is suspicious
        
        # Check 1: Following/Follower ratio
        ratio = following / followers
        if ratio > 2.0:
            return True  # Too many following compared to followers
        
        # Check 2: Posts vs Followers
        if followers > 5000 and posts < 20:
            return True  # Too few posts for follower count
        
        # Check 3: Zero posts
        if posts == 0:
            return True  # No posts at all
        
        return False
    
    def calculate_fake_score(self, profile_data: Dict[str, Any]) -> int:
        """
        Calculate authenticity score (0-100) for a profile.
        
        Higher score = more likely genuine.
        Based on the algorithm from Apify_Fake_Detection_Guide.md
        
        Args:
            profile_data: Profile data dict
            
        Returns:
            Authenticity score (0-100)
        """
        score = 100
        
        followers = profile_data.get("followersCount", 0)
        following = profile_data.get("followsCount", profile_data.get("followingCount", 0))
        posts = profile_data.get("postsCount", 0)
        is_business = profile_data.get("isBusinessAccount", False)
        has_email = bool(profile_data.get("businessEmail"))
        has_website = bool(profile_data.get("externalUrl"))
        
        # Prevent division by zero
        if followers == 0:
            return 0
        
        # Check 1: Following/Follower ratio
        ratio = following / followers
        if ratio > 2.0:
            score -= 30
        elif ratio > 1.5:
            score -= 15
        
        # Check 2: Posts vs Followers
        if followers > 5000 and posts < 20:
            score -= 25
        
        # Bonuses
        if is_business:
            score += 5
        if has_email:
            score += 5
        if has_website:
            score += 5
        
        # Cap score
        return max(0, min(100, score))
    
    # =========================================================================
    # Google Search
    # =========================================================================

    async def google_search(
        self,
        query: str,
        max_results: int = 5,
        timeout: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Search Google using Apify's Google Search Results Scraper.

        Args:
            query: The search query string
            max_results: Maximum number of results to return
            timeout: Maximum wait time in seconds

        Returns:
            List of search result dicts with keys: title, url, description
        """
        await self._rate_limiter.acquire()

        logger.info(f"Google search: {query!r} (max_results={max_results})")

        run_input = {
            "queries": query,
            "maxPagesPerQuery": 1,
            "resultsPerPage": max_results,
            "languageCode": "en",
            "mobileResults": False,
        }

        try:
            run = self.client.actor(DEFAULT_GOOGLE_SEARCH_SCRAPER).call(
                run_input=run_input,
                timeout_secs=timeout,
            )

            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Apify Google Search returns organic results nested inside each item
            results = []
            for item in items:
                organic = item.get("organicResults", [])
                for result in organic[:max_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                    })

            logger.info(f"Google search returned {len(results)} results")
            return results[:max_results]

        except Exception as e:
            logger.warning(f"Google search failed for query {query!r}: {e}")
            return []

    def __repr__(self) -> str:
        configured = "configured" if self.is_configured() else "not configured"
        return f"ApifyService({configured})"


# =============================================================================
# Factory Functions
# =============================================================================

@lru_cache()
def get_apify_service() -> ApifyService:
    """
    Get a cached ApifyService instance.
    
    Uses LRU cache to ensure only one instance is created.
    
    Returns:
        ApifyService instance
    """
    return ApifyService()


def create_apify_service(
    api_key: Optional[str] = None,
    profile_scraper_id: Optional[str] = None,
    hashtag_scraper_id: Optional[str] = None,
    search_scraper_id: Optional[str] = None,
    tagged_scraper_id: Optional[str] = None,
) -> ApifyService:
    """
    Create a new ApifyService instance with custom configuration.

    Args:
        api_key: Custom API key
        profile_scraper_id: Custom profile scraper actor ID
        hashtag_scraper_id: Custom hashtag scraper actor ID
        search_scraper_id: Custom search scraper actor ID
        tagged_scraper_id: Custom tagged posts scraper actor ID

    Returns:
        ApifyService instance
    """
    return ApifyService(
        api_key=api_key,
        profile_scraper_id=profile_scraper_id,
        hashtag_scraper_id=hashtag_scraper_id,
        search_scraper_id=search_scraper_id,
        tagged_scraper_id=tagged_scraper_id,
    )


# =============================================================================
# Utility Functions
# =============================================================================

def is_apify_configured() -> bool:
    """
    Check if Apify is properly configured.
    
    Returns:
        True if APIFY_API_KEY is set
    """
    return bool(
        settings.apify.api_key and 
        settings.apify.api_key != "your-apify-api-key"
    )


def get_apify_config() -> Dict[str, Any]:
    """
    Get current Apify configuration info.
    
    Returns:
        Dict with configuration details
    """
    return {
        "configured": is_apify_configured(),
        "profile_scraper_id": settings.apify.instagram_scraper_id,
        "hashtag_scraper_id": settings.apify.hashtag_scraper_id,
        "search_scraper_id": settings.apify.search_scraper_id,
        "tagged_scraper_id": settings.apify.tagged_scraper_id,
    }
