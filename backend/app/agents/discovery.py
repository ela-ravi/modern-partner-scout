"""
PartnerScout AI - Discovery Agent (STORY-3.3.3)

AI agent that discovers similar Instagram profiles using hashtags and keywords
extracted from brand DNA. Finds potential partnership candidates that match
the brand's aesthetic, audience, and content themes.

Subtasks completed:
- SUB-3.3.3.1.1: Create app/agents/discovery.py
- SUB-3.3.3.1.2: Implement hashtag search via Apify
- SUB-3.3.3.1.3: Implement follower range filtering
- SUB-3.3.3.1.4: Implement deduplication by username
- SUB-3.3.3.1.5: Implement database storage in discovered_profiles table
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.agents.base import AgentResult, BaseAgent
from app.core.config import settings
from app.core.constants import Defaults, ProfileStatus
from app.core.exceptions import AgentError, ApifyError, JobNotFoundError
from app.models.agent import DiscoveryRequest, DiscoveryResponse
from app.repositories.brand_repo import BrandRepository
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository
from app.services.apify_service import ApifyService, get_apify_service
from app.services.llm_service import LLMService


# =============================================================================
# Logger Configuration
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Output Schema for Profile Analysis
# =============================================================================

class ProfileRelevanceOutput(BaseModel):
    """Schema for LLM profile relevance analysis output."""
    
    profiles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Analyzed profiles with relevance scores"
    )
    filtered_count: int = Field(
        default=0,
        description="Number of profiles filtered out"
    )
    filter_reasons: Dict[str, int] = Field(
        default_factory=dict,
        description="Mapping of filter reasons to counts"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Top recommended usernames to prioritize"
    )


class DiscoveredProfile(BaseModel):
    """Schema for a discovered profile ready for database storage."""
    
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: Optional[int] = None
    posts_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    is_verified: bool = False
    is_business_account: Optional[bool] = None
    profile_picture_url: Optional[str] = None
    external_url: Optional[str] = None
    business_email: Optional[str] = None
    business_category: Optional[str] = None
    instagram_url: str = ""
    relevance_score: Optional[int] = None
    discovery_source: Optional[str] = None


# =============================================================================
# Discovery Agent
# =============================================================================

class DiscoveryAgent(BaseAgent[DiscoveryRequest, DiscoveryResponse]):
    """
    AI agent for discovering Instagram profiles similar to reference profiles.
    
    This agent:
    1. Searches Instagram hashtags via Apify to find posts
    2. Extracts unique profile usernames from posts
    3. Fetches detailed profile data
    4. Filters by follower range and quality indicators
    5. Deduplicates profiles by username
    6. Stores discovered profiles in the database
    
    Example:
        ```python
        agent = DiscoveryAgent()
        request = DiscoveryRequest(
            job_id=UUID("..."),
            hashtags=["#sustainablefashion", "#slowfashion"],
            keywords=["sustainable", "ethical"],
            limit=50
        )
        response = await agent.run(request)
        print(f"Discovered {response.total_discovered} profiles")
        ```
    """
    
    agent_name = "discovery"
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        apify_service: Optional[ApifyService] = None,
        job_repo: Optional[JobRepository] = None,
        brand_repo: Optional[BrandRepository] = None,
        profile_repo: Optional[ProfileRepository] = None,
        **kwargs
    ):
        """
        Initialize the Discovery Agent.
        
        Args:
            llm_service: LLM service for text generation (optional)
            apify_service: Apify service for Instagram scraping (optional)
            job_repo: Job repository for accessing job data (optional)
            brand_repo: Brand repository for accessing brand DNA (optional)
            profile_repo: Profile repository for storing profiles (optional)
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(llm_service=llm_service, **kwargs)
        
        # Initialize services
        self._apify_service = apify_service or get_apify_service()
        self._job_repo = job_repo or JobRepository()
        self._brand_repo = brand_repo or BrandRepository()
        self._profile_repo = profile_repo or ProfileRepository()
        
        logger.debug(f"Initialized {self.agent_name} agent")
    
    # =========================================================================
    # Main Run Method (SUB-3.3.3.1.1)
    # =========================================================================
    
    async def run(self, input_data: DiscoveryRequest) -> DiscoveryResponse:
        """
        Execute profile discovery for a discovery job.
        
        This method:
        1. Validates the job exists
        2. Searches hashtags via Apify to find posts
        3. Extracts unique usernames from posts
        4. Fetches detailed profile data
        5. Filters by follower range and quality
        6. Deduplicates profiles
        7. Stores profiles in database
        
        Args:
            input_data: DiscoveryRequest containing job_id and search criteria
            
        Returns:
            DiscoveryResponse with discovered profiles
            
        Raises:
            AgentError: If discovery fails
            JobNotFoundError: If job doesn't exist
        """
        start_time = time.time()
        metrics = self._start_metrics()
        
        job_id = str(input_data.job_id)
        logger.info(
            f"Starting discovery for job: {job_id}, "
            f"hashtags: {input_data.hashtags}, "
            f"reference_usernames: {len(input_data.reference_usernames)}, "
            f"limit: {input_data.limit}"
        )
        
        try:
            # Step 1: Validate job exists
            job = await self._fetch_job(job_id)

            # Step 2: Get existing profiles for deduplication (SUB-3.3.3.1.4)
            existing_usernames = await self._get_existing_usernames(job_id)

            # Merge cross-job excluded usernames into dedup set
            if input_data.excluded_usernames:
                existing_usernames.update(
                    u.lower() for u in input_data.excluded_usernames
                )

            if input_data.reference_usernames:
                # -------------------------------------------------------
                # Reference-based discovery: scrape provided usernames
                # directly (skip hashtag search entirely)
                # -------------------------------------------------------
                logger.info(
                    f"Reference-based discovery: {len(input_data.reference_usernames)} "
                    f"usernames provided, skipping hashtag search"
                )

                # Filter out already-known usernames
                new_usernames = [
                    u for u in input_data.reference_usernames
                    if u.lower() not in existing_usernames
                ]
                deduplicated_count = len(input_data.reference_usernames) - len(new_usernames)

                usernames_to_fetch = new_usernames[:input_data.limit]
                profiles_data = await self._fetch_profiles(usernames_to_fetch)
                discovery_source = "reference_related_profiles"
            else:
                # -------------------------------------------------------
                # Hashtag-based discovery: existing behavior
                # -------------------------------------------------------
                raw_posts = await self._search_hashtags(
                    input_data.hashtags,
                    limit_per_hashtag=max(30, (input_data.limit * 3) // max(len(input_data.hashtags), 1))
                )

                candidate_usernames = self._extract_usernames_from_posts(raw_posts)
                logger.info(f"Extracted {len(candidate_usernames)} unique usernames from posts")

                new_usernames = [u for u in candidate_usernames if u not in existing_usernames]
                deduplicated_count = len(candidate_usernames) - len(new_usernames)

                usernames_to_fetch = new_usernames[:input_data.limit]
                profiles_data = await self._fetch_profiles(usernames_to_fetch)
                discovery_source = ", ".join(input_data.hashtags[:3])

            logger.info(
                f"After deduplication: {len(new_usernames)} new usernames "
                f"({deduplicated_count} duplicates removed)"
            )

            # Step 7: Filter by follower range + business account + relevance (SUB-3.3.3.1.3)
            filtered_profiles, filtered_out_count = self._filter_profiles(
                profiles_data,
                min_followers=input_data.follower_min,
                max_followers=input_data.follower_max,
                limit=input_data.limit,
                require_business_account=input_data.require_business_account,
                deprioritize_brands=input_data.deprioritize_brands,
                relevance_keywords=input_data.keywords if input_data.keywords else None,
            )

            # Step 7b: Extract related usernames from fetched profiles
            related_usernames = self._extract_related_usernames(
                profiles_data, existing_usernames
            )

            # Step 8: Store profiles in database (SUB-3.3.3.1.5)
            stored_profiles = await self._store_profiles(
                job_id=job_id,
                profiles=filtered_profiles,
                discovery_source=discovery_source,
            )

            # Calculate duration
            duration = time.time() - start_time
            self._complete_metrics(success=True)

            logger.info(
                f"Discovery completed for job {job_id}: "
                f"{len(stored_profiles)} profiles discovered, "
                f"{deduplicated_count} deduplicated, "
                f"{filtered_out_count} filtered out, "
                f"{len(related_usernames)} related usernames harvested, "
                f"duration={duration:.2f}s"
            )

            return DiscoveryResponse(
                job_id=input_data.job_id,
                profiles=stored_profiles,
                total_discovered=len(stored_profiles),
                deduplicated=deduplicated_count,
                filtered_out=filtered_out_count,
                discovery_duration_seconds=duration,
                related_usernames=related_usernames,
            )
            
        except JobNotFoundError:
            raise
        except AgentError:
            raise
        except Exception as e:
            self._complete_metrics(success=False, error_message=str(e))
            logger.error(f"Discovery failed for job {job_id}: {e}")
            raise AgentError(
                message=f"Discovery failed: {str(e)}",
                agent_name=self.agent_name,
                details={"job_id": job_id, "error": str(e)}
            )
    
    # =========================================================================
    # Job Fetching
    # =========================================================================
    
    async def _fetch_job(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch job data from the database.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            Job data dictionary
            
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        logger.debug(f"Fetching job: {job_id}")
        return self._job_repo.get_by_id(job_id)
    
    # =========================================================================
    # Hashtag Search via Apify (SUB-3.3.3.1.2)
    # =========================================================================
    
    async def _search_hashtags(
        self,
        hashtags: List[str],
        limit_per_hashtag: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search Instagram hashtags via Apify to find posts.
        
        Args:
            hashtags: List of hashtags to search
            limit_per_hashtag: Maximum posts per hashtag
            
        Returns:
            Dictionary mapping hashtag to list of posts
        """
        logger.info(f"Searching {len(hashtags)} hashtags via Apify")
        
        # Clean hashtags (remove # prefix for Apify)
        clean_hashtags = [h.lstrip("#").strip() for h in hashtags if h.strip()]
        
        if not clean_hashtags:
            logger.warning("No valid hashtags provided")
            return {}
        
        try:
            results = await self._apify_service.search_hashtags(
                hashtags=clean_hashtags,
                limit_per_hashtag=limit_per_hashtag
            )
            
            total_posts = sum(len(posts) for posts in results.values())
            logger.info(
                f"Found {total_posts} posts across {len(clean_hashtags)} hashtags"
            )
            
            return results
            
        except ApifyError as e:
            logger.warning(f"Apify hashtag search failed: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Hashtag search failed: {e}")
            return {}
    
    # =========================================================================
    # Username Extraction
    # =========================================================================
    
    def _extract_usernames_from_posts(
        self,
        hashtag_results: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """
        Extract unique usernames from hashtag search results.
        
        Args:
            hashtag_results: Dictionary mapping hashtag to posts
            
        Returns:
            List of unique usernames
        """
        usernames: Set[str] = set()
        
        for hashtag, posts in hashtag_results.items():
            for post in posts:
                # Try different field names for owner username
                owner_username = (
                    post.get("ownerUsername") or
                    post.get("owner_username") or
                    (post.get("owner", {}) or {}).get("username")
                )
                
                if owner_username and isinstance(owner_username, str):
                    # Clean the username
                    clean_username = owner_username.strip().lstrip("@")
                    if clean_username and len(clean_username) > 0:
                        usernames.add(clean_username)
        
        return list(usernames)
    
    # =========================================================================
    # Related Profile Extraction
    # =========================================================================

    def _extract_related_usernames(
        self,
        profiles: List[Dict[str, Any]],
        existing_usernames: Set[str],
    ) -> List[str]:
        """
        Extract related usernames from Apify profile scraper results.

        The Apify instagram-profile-scraper returns a `relatedProfiles` field
        with suggested similar accounts. These are free discovery candidates
        that don't require additional API calls.

        Args:
            profiles: List of scraped profile data dicts
            existing_usernames: Set of already-known usernames to exclude

        Returns:
            List of new related usernames not yet in the exclusion set
        """
        related: Set[str] = set()

        for profile in profiles:
            related_list = profile.get("relatedProfiles") or []
            for rp in related_list:
                if isinstance(rp, dict):
                    username = rp.get("username", "")
                elif isinstance(rp, str):
                    username = rp
                else:
                    continue

                username = username.strip().lstrip("@").lower()
                if username and username not in existing_usernames:
                    related.add(username)

        if related:
            logger.info(f"Harvested {len(related)} related usernames from profile scraper")

        return list(related)

    # =========================================================================
    # Profile Fetching
    # =========================================================================
    
    async def _fetch_profiles(
        self,
        usernames: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Fetch detailed profile data for discovered usernames.

        Sends ALL usernames in a single Apify actor call to minimize
        costs (each actor.call() has a startup cost).

        Args:
            usernames: List of usernames to fetch

        Returns:
            List of profile data dictionaries
        """
        if not usernames:
            return []

        logger.info(f"Fetching profile data for {len(usernames)} usernames (single batch)")

        try:
            profiles = await self._apify_service.scrape_profiles(
                usernames=usernames,
                results_limit=1,  # Only need profile metadata, not posts
            )
            logger.info(f"Successfully fetched {len(profiles)} profiles")
            return profiles

        except ApifyError as e:
            logger.warning(f"Profile fetching failed: {e}")
            return []
        except Exception as e:
            logger.warning(f"Profile fetching error: {e}")
            return []
    
    # =========================================================================
    # Profile Classification
    # =========================================================================

    def _classify_profile(self, profile: Dict[str, Any]) -> str:
        """
        Classify a profile as distributor, influencer, boutique, brand, personal, or unknown.

        Uses businessCategoryName and bio text signals to determine the profile type.

        Args:
            profile: Profile data dictionary

        Returns:
            One of: "distributor", "influencer", "boutique", "brand", "personal", "unknown"
        """
        category = (
            profile.get("businessCategoryName")
            or profile.get("business_category")
            or ""
        ).lower()
        bio = (profile.get("biography") or profile.get("bio") or "").lower()

        # Distributor / Retailer signals
        distributor_categories = {
            "shopping & retail", "retail company",
            "e-commerce website", "grocery store",
            "shopping district", "beauty supply",
        }
        distributor_bio_words = [
            "we carry", "stockist", "wholesale", "authorized dealer",
            "shop our collection of", "multi-brand", "featuring brands",
            "distributor", "retailer", "reseller", "official dealer",
            "all brands", "brands under one roof", "authentic fragrance",
            "original scent", "100% original", "best prices",
            "free delivery", "shop now", "order now", "we sell",
            "we ship", "we deliver", "your one stop", "one-stop",
            "multi brand", "various brands", "top brands",
            "authorized reseller", "official store", "fragrance shop",
            "perfume shop", "beauty store", "cosmetics store",
            "encargos", "tienda", "importador",
        ]

        if category in distributor_categories:
            return "distributor"
        for word in distributor_bio_words:
            if word in bio:
                return "distributor"

        # Influencer / Creator signals
        influencer_categories = {
            "digital creator", "creator", "video creator",
            "blogger", "public figure", "personal blog",
        }
        influencer_bio_words = [
            "review", "collab", "brand ambassador", "dm for collabs",
            "content creator", "blogger", "vlogger", "youtuber",
            "pr friendly", "partnerships", "fragrance lover",
            "perfume lover", "beauty lover", "scent lover",
            "fragrance enthusiast", "perfume enthusiast",
            "my favorite", "i love fragrance", "i love perfume",
            "fragrance community", "perfume community",
            "honest review", "fragrance journey",
        ]

        if category in influencer_categories:
            return "influencer"
        for word in influencer_bio_words:
            if word in bio:
                return "influencer"

        # Boutique signals
        boutique_bio_words = [
            "boutique", "curated", "select shop", "concept store",
            "handpicked", "carefully selected", "niche perfumery",
            "niche fragrance", "artisanal selection", "luxury selection",
        ]
        for word in boutique_bio_words:
            if word in bio:
                return "boutique"

        # Brand signals — account that only promotes its own products
        brand_categories = {"product/service", "health/beauty", "clothing (brand)"}
        brand_bio_words = [
            "our products", "founded by", "our brand", "our collection",
            "handcrafted by us", "we create", "made by us", "est.",
            "established", "founder", "co-founder",
            "maison de", "crafted in france", "made in france",
            "our fragrances", "our perfumes", "our scents",
            "discover our", "explore our", "the art of perfum",
            "the house of", "parfumerie", "haute parfumerie",
            "the world of", "step into the world",
            "captivating blend", "unique fragrance",
            "inspired by music", "inspired by nature",
            "fuses", "bridge between",
            "luxury perfume", "premium fragrance", "artisan perfume",
            "niche perfume", "perfume brand", "fragrance brand",
            "official account", "official page",
            "our line", "our range", "we craft", "we blend",
            "handmade perfume", "handmade fragrance",
            "by appointment", "bespoke fragrance",
            "perfume house", "fragrance house",
            "scent brand", "scent house",
        ]

        if category in brand_categories:
            # Only classify as brand if bio also contains brand signals
            for word in brand_bio_words:
                if word in bio:
                    return "brand"

        for word in brand_bio_words:
            if word in bio:
                return "brand"

        # Category-based brand fallback: business account in brand category
        # with no distributor/influencer/boutique signals = likely a self-brand
        is_business = (
            profile.get("isBusinessAccount")
            or profile.get("is_business_account")
            or False
        )
        if category in brand_categories and is_business:
            return "brand"

        # Personal account (no business category, generic bio)
        if not is_business and not category:
            return "personal"

        return "unknown"

    # =========================================================================
    # Relevance Pre-Filter
    # =========================================================================

    def _check_relevance(
        self, profile: Dict[str, Any], keywords: List[str]
    ) -> bool:
        """
        Check if a profile has any topical relevance to brand keywords.

        Two-tier matching to avoid false positives from generic business
        terms (e.g. "wholesale", "distributor") while keeping niche terms:

        1. Any FULL keyword phrase found in profile text → immediate PASS
           (e.g. "specialty coffee" or "perfume boutique" in bio)
        2. Otherwise, count distinct individual word matches (≥4 chars).
           Require 2+ distinct words to PASS. This rejects profiles that
           only match a single generic word like "wholesale" but keeps
           profiles matching "coffee" + "roaster".

        Returns True when no keywords are provided (no filtering).
        """
        if not keywords:
            return True

        bio = (
            profile.get("biography") or profile.get("bio") or ""
        ).lower()
        category = (
            profile.get("businessCategoryName")
            or profile.get("category_name")
            or ""
        ).lower()
        full_name = (
            profile.get("fullName") or profile.get("full_name") or ""
        ).lower()
        username = (
            profile.get("username") or profile.get("userName") or ""
        ).lower()

        # Collect text from recent post captions and hashtags
        posts = (
            profile.get("latestPosts")
            or profile.get("recentPosts")
            or profile.get("posts")
            or []
        )
        post_text_parts: List[str] = []
        for post in posts[:5]:
            caption = post.get("caption") or post.get("text") or ""
            if caption:
                post_text_parts.append(caption.lower())
            # Also check hashtags array if present
            tags = post.get("hashtags") or []
            if tags:
                post_text_parts.append(" ".join(str(t).lower() for t in tags))
        post_text = " ".join(post_text_parts)

        searchable = f"{bio} {category} {full_name} {username} {post_text}"

        # Tier 1: Full keyword phrase match (strong signal — one is enough)
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower and kw_lower in searchable:
                return True

        # Tier 2: Individual word matching — require 2+ distinct words
        matched_words: Set[str] = set()
        for kw in keywords:
            for word in kw.lower().split():
                if len(word) >= 4 and word not in matched_words and word in searchable:
                    matched_words.add(word)
                    if len(matched_words) >= 2:
                        return True

        return False

    # =========================================================================
    # Follower Range Filtering (SUB-3.3.3.1.3)
    # =========================================================================

    def _filter_profiles(
        self,
        profiles: List[Dict[str, Any]],
        min_followers: int = Defaults.DEFAULT_MIN_FOLLOWERS,
        max_followers: int = Defaults.DEFAULT_MAX_FOLLOWERS,
        limit: int = Defaults.DEFAULT_DISCOVERY_LIMIT,
        exclude_private: bool = True,
        exclude_no_posts: bool = True,
        require_business_account: bool = False,
        deprioritize_brands: bool = False,
        relevance_keywords: Optional[List[str]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Filter profiles by various criteria including follower range.

        When deprioritize_brands is True, profiles are classified and sorted so
        distributors/influencers/boutiques come first and brands/personal come last.
        Brands are NOT excluded entirely — they are just ranked lower.

        Args:
            profiles: List of profile data
            min_followers: Minimum follower count
            max_followers: Maximum follower count
            limit: Maximum profiles to return
            exclude_private: Exclude private accounts
            exclude_no_posts: Exclude accounts with no posts
            require_business_account: Only keep business accounts
            deprioritize_brands: Sort results so partners come first, brands last

        Returns:
            Tuple of (filtered_profiles, filtered_out_count)
        """
        logger.debug(
            f"Filtering profiles: {len(profiles)} candidates, "
            f"range {min_followers}-{max_followers}, limit {limit}, "
            f"require_business={require_business_account}, "
            f"deprioritize_brands={deprioritize_brands}"
        )

        filtered = []
        filtered_out_reasons = {
            "follower_range": 0,
            "private": 0,
            "no_posts": 0,
            "fake_suspected": 0,
            "not_business": 0,
            "irrelevant": 0,
            "brand_deprioritized": 0,
        }

        for profile in profiles:
            # Get follower count
            followers = (
                profile.get("followersCount") or
                profile.get("followers_count") or
                0
            )

            # Check follower range
            if followers < min_followers or followers > max_followers:
                filtered_out_reasons["follower_range"] += 1
                continue

            # Check private account
            is_private = profile.get("private") or profile.get("is_private", False)
            if exclude_private and is_private:
                filtered_out_reasons["private"] += 1
                continue

            # Check posts count
            posts_count = (
                profile.get("postsCount") or
                profile.get("posts_count") or
                0
            )
            if exclude_no_posts and posts_count == 0:
                filtered_out_reasons["no_posts"] += 1
                continue

            # Check business account requirement
            if require_business_account:
                is_business = (
                    profile.get("isBusinessAccount")
                    or profile.get("is_business_account")
                )
                if not is_business:
                    filtered_out_reasons["not_business"] += 1
                    continue

            # Check for fake profile indicators
            if self._is_likely_fake(profile):
                filtered_out_reasons["fake_suspected"] += 1
                continue

            # Check topical relevance against brand keywords
            if relevance_keywords and not self._check_relevance(profile, relevance_keywords):
                uname = profile.get("username") or profile.get("userName") or "?"
                logger.debug(f"Filtered out @{uname}: no relevance to brand keywords")
                filtered_out_reasons["irrelevant"] += 1
                continue

            # Profile passed all filters
            filtered.append(profile)

        # When deprioritize_brands is enabled, classify and sort
        if deprioritize_brands and filtered:
            # Priority: distributor=0, influencer=1, boutique=2, unknown=3, personal=4, brand=5
            priority_map = {
                "distributor": 0,
                "influencer": 1,
                "boutique": 2,
                "unknown": 3,
                "personal": 4,
                "brand": 5,
            }

            classified = []
            for profile in filtered:
                profile_type = self._classify_profile(profile)
                priority = priority_map.get(profile_type, 3)
                classified.append((priority, profile_type, profile))

                if profile_type == "brand":
                    filtered_out_reasons["brand_deprioritized"] += 1

            # Sort by priority (partners first, brands last)
            classified.sort(key=lambda x: x[0])
            filtered = [item[2] for item in classified]

            # Log classification breakdown
            type_counts: Dict[str, int] = {}
            for _, ptype, _ in classified:
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            logger.info(
                f"Profile classification: {type_counts} "
                f"({filtered_out_reasons['brand_deprioritized']} brands deprioritized)"
            )

        total_filtered_out = sum(
            v for k, v in filtered_out_reasons.items() if k != "brand_deprioritized"
        )
        logger.info(
            f"Filtering complete: {len(filtered)} passed, "
            f"{total_filtered_out} filtered out ({filtered_out_reasons})"
        )

        return filtered[:limit], total_filtered_out
    
    def _is_likely_fake(self, profile: Dict[str, Any]) -> bool:
        """
        Check if a profile shows signs of being fake or low quality.
        
        Uses heuristics from the fake detection algorithm.
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            True if profile appears fake
        """
        followers = (
            profile.get("followersCount") or
            profile.get("followers_count") or
            0
        )
        following = (
            profile.get("followsCount") or
            profile.get("following_count") or
            profile.get("followingCount") or
            0
        )
        posts = (
            profile.get("postsCount") or
            profile.get("posts_count") or
            0
        )
        
        # No followers is suspicious
        if followers == 0:
            return True
        
        # Check following/follower ratio
        ratio = following / followers if followers > 0 else 0
        if ratio > 3.0:  # Following 3x more than followers
            return True
        
        # High followers with very few posts
        if followers > 10000 and posts < 10:
            return True
        
        return False
    
    # =========================================================================
    # Deduplication (SUB-3.3.3.1.4)
    # =========================================================================
    
    async def _get_existing_usernames(self, job_id: str) -> Set[str]:
        """
        Get set of usernames already discovered for this job.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            Set of existing usernames
        """
        existing_profiles = self._profile_repo.list_by_job(job_id, limit=1000)
        return {p.get("username", "").lower() for p in existing_profiles if p.get("username")}
    
    # =========================================================================
    # Database Storage (SUB-3.3.3.1.5)
    # =========================================================================
    
    async def _store_profiles(
        self,
        job_id: str,
        profiles: List[Dict[str, Any]],
        discovery_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Store discovered profiles in the database.
        
        Args:
            job_id: Job UUID string
            profiles: List of profile data to store
            discovery_source: Optional source description (e.g., hashtags used)
            
        Returns:
            List of stored profile records
        """
        logger.debug(f"Storing {len(profiles)} profiles for job: {job_id}")
        
        if not profiles:
            return []
        
        stored_profiles = []
        
        for profile in profiles:
            try:
                # Extract profile data with field mapping
                username = (
                    profile.get("username") or
                    profile.get("userName") or
                    ""
                )
                
                if not username:
                    continue
                
                # Check for duplicate one more time before insert
                if self._profile_repo.check_duplicate(job_id, username):
                    logger.debug(f"Skipping duplicate username: {username}")
                    continue
                
                # Build Instagram URL
                instagram_url = f"https://instagram.com/{username}"
                
                # Create profile in database
                stored_profile = self._profile_repo.create(
                    job_id=job_id,
                    instagram_url=instagram_url,
                    username=username,
                    full_name=profile.get("fullName") or profile.get("full_name"),
                    profile_picture_url=(
                        profile.get("profilePicUrl") or
                        profile.get("profile_pic_url") or
                        profile.get("profilePicUrlHD")
                    ),
                    bio=profile.get("biography") or profile.get("bio"),
                    followers_count=(
                        profile.get("followersCount") or
                        profile.get("followers_count") or
                        0
                    ),
                    following_count=(
                        profile.get("followsCount") or
                        profile.get("following_count") or
                        profile.get("followingCount")
                    ),
                    posts_count=(
                        profile.get("postsCount") or
                        profile.get("posts_count")
                    ),
                    engagement_rate=self._calculate_engagement_rate(profile),
                    is_verified=(
                        profile.get("verified") or
                        profile.get("is_verified") or
                        False
                    ),
                    is_business_account=(
                        profile.get("isBusinessAccount") or
                        profile.get("is_business_account")
                    ),
                    external_url=(
                        profile.get("externalUrl") or
                        profile.get("external_url")
                    ),
                    business_email=(
                        profile.get("businessEmail") or
                        profile.get("business_email")
                    ),
                    business_category=(
                        profile.get("businessCategoryName") or
                        profile.get("business_category")
                    )
                )
                
                stored_profiles.append(stored_profile)
                
            except Exception as e:
                logger.warning(f"Failed to store profile {profile.get('username')}: {e}")
                continue
        
        logger.info(f"Successfully stored {len(stored_profiles)} profiles")
        return stored_profiles
    
    def _calculate_engagement_rate(self, profile: Dict[str, Any]) -> Optional[float]:
        """
        Calculate engagement rate from profile data.
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            Engagement rate as percentage or None
        """
        followers = (
            profile.get("followersCount") or
            profile.get("followers_count") or
            0
        )
        
        if followers == 0:
            return None
        
        # Check if engagement rate is already provided
        existing_rate = profile.get("engagementRate") or profile.get("engagement_rate")
        if existing_rate:
            return float(existing_rate)
        
        # Calculate from recent posts if available
        recent_posts = profile.get("recentPosts") or profile.get("recent_posts") or []
        if recent_posts:
            total_engagement = sum(
                (post.get("likesCount", 0) or 0) + (post.get("commentsCount", 0) or 0)
                for post in recent_posts
            )
            avg_engagement = total_engagement / len(recent_posts)
            engagement_rate = (avg_engagement / followers) * 100
            return round(engagement_rate, 2)
        
        return None
    
    # =========================================================================
    # Input Validation
    # =========================================================================
    
    async def validate_input(self, input_data: DiscoveryRequest) -> bool:
        """
        Validate input data before processing.

        Args:
            input_data: Input request data

        Returns:
            True if valid

        Raises:
            AgentError: If validation fails
        """
        if not input_data.job_id:
            raise AgentError(
                message="job_id is required",
                agent_name=self.agent_name,
                details={"field": "job_id"}
            )

        if not input_data.hashtags and not input_data.reference_usernames:
            raise AgentError(
                message="At least one of hashtags or reference_usernames is required",
                agent_name=self.agent_name,
                details={"field": "hashtags/reference_usernames"}
            )

        if input_data.follower_min >= input_data.follower_max:
            raise AgentError(
                message="follower_min must be less than follower_max",
                agent_name=self.agent_name,
                details={
                    "follower_min": input_data.follower_min,
                    "follower_max": input_data.follower_max
                }
            )

        return True


# =============================================================================
# Factory Function
# =============================================================================

def get_discovery_agent(
    llm_service: Optional[LLMService] = None,
    apify_service: Optional[ApifyService] = None,
) -> DiscoveryAgent:
    """
    Factory function to create a Discovery Agent.
    
    Args:
        llm_service: Optional custom LLM service
        apify_service: Optional custom Apify service
        
    Returns:
        DiscoveryAgent instance
    """
    return DiscoveryAgent(
        llm_service=llm_service,
        apify_service=apify_service,
    )
