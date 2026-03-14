"""
PartnerScout AI - Internal Orchestration Service

Runs the 4-phase pipeline:
  Phase 1: Brand Analysis
  Phase 2+3: Iterative Discovery & Scoring (loop until N quality profiles found)
  Phase 4: Contact Enrichment (website scraping + LLM)

Called by job_service.trigger_discovery() when N8N is unavailable.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, List, Set

from app.agents.brand_analyzer import get_brand_analyzer_agent
from app.agents.discovery import get_discovery_agent
from app.agents.scorer import get_scorer_agent
from app.agents.contact_enricher import get_contact_enricher_agent, ContactEnricherRequest
from app.core.constants import Defaults, ProfileStatus
from app.models.agent import BrandAnalyzerRequest, DiscoveryRequest, ScorerRequest
from app.services.apify_service import get_apify_service
from app.services.job_service import JobService
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository

logger = logging.getLogger(__name__)


def _get_profile_field(profile, field: str, default=None):
    """Safely extract a field from a profile (dict or object)."""
    if isinstance(profile, dict):
        return profile.get(field, default)
    return getattr(profile, field, default)


def _generate_country_hashtags(target_country: str) -> List[str]:
    """
    Generate country/region-specific discovery hashtags.

    These hashtags help find influencers located in the target country.

    Args:
        target_country: Country or region name (e.g., "India", "USA", "Germany")

    Returns:
        List of geo-specific hashtags with # prefix
    """
    clean = target_country.lower().replace(" ", "")
    hashtags = [
        f"#{clean}influencer",
        f"#{clean}blogger",
        f"#{clean}creator",
        f"#{clean}brand",
        f"#{clean}fashion",
        f"#{clean}beauty",
        f"#{clean}lifestyle",
        f"#madein{clean}",
    ]

    # Add major city hashtags for well-known countries
    city_map: Dict[str, List[str]] = {
        "india": ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", "pune", "kolkata"],
        "usa": ["nyc", "losangeles", "chicago", "miami", "houston", "sanfrancisco"],
        "uk": ["london", "manchester", "birmingham", "edinburgh"],
        "germany": ["berlin", "munich", "hamburg", "frankfurt"],
        "france": ["paris", "lyon", "marseille", "nice"],
        "australia": ["sydney", "melbourne", "brisbane", "perth"],
        "canada": ["toronto", "vancouver", "montreal", "calgary"],
        "brazil": ["saopaulo", "riodejaneiro", "brasilia"],
        "uae": ["dubai", "abudhabi"],
        "japan": ["tokyo", "osaka", "kyoto"],
        "southkorea": ["seoul", "busan"],
        "singapore": ["singapore"],
        "italy": ["milan", "rome", "florence"],
        "spain": ["madrid", "barcelona", "valencia"],
        "mexico": ["mexicocity", "cdmx", "guadalajara", "cancun"],
    }

    cities = city_map.get(clean, [])
    for city in cities[:5]:
        hashtags.append(f"#{city}")

    return hashtags


def _generate_keyword_hashtags(keywords: List[str]) -> List[str]:
    """
    Generate hashtag variants from keywords for fallback discovery.

    When the original brand-analysis hashtags are exhausted (return 0 new
    profiles), this function creates additional hashtags by appending common
    suffixes to each keyword.

    Args:
        keywords: List of brand-related keywords

    Returns:
        List of generated hashtags with # prefix
    """
    suffixes = ["", "lover", "community", "style", "life", "daily", "tips", "inspo"]
    hashtags: List[str] = []
    for kw in keywords:
        clean = kw.lower().replace(" ", "").replace("-", "")
        for suffix in suffixes:
            tag = f"#{clean}{suffix}"
            if tag not in hashtags:
                hashtags.append(tag)
    return hashtags


async def _try_keyword_user_search(
    job_id: str,
    partner_search_keywords: List[str],
    discover_count: int,
    follower_min: int,
    follower_max: int,
    excluded_usernames: Set[str],
) -> "DiscoveryRequest | None":
    """
    Try keyword user search and return a DiscoveryRequest, or None on failure.

    Uses apify/instagram-search-scraper with searchType="user" to find
    complementary partners (distributors, influencers, boutiques).
    """
    try:
        apify_service = get_apify_service()
        search_results = await apify_service.search_users(
            keywords=partner_search_keywords[:5],
            limit_per_keyword=max(10, discover_count // 5),
        )
        search_usernames = []
        for result in search_results:
            username = (
                result.get("username")
                or result.get("userName")
                or ""
            ).strip().lstrip("@")
            if username and username.lower() not in excluded_usernames:
                search_usernames.append(username)

        logger.info(
            f"[Orchestration] Job {job_id}: Keyword search found "
            f"{len(search_usernames)} new usernames"
        )

        if search_usernames:
            return DiscoveryRequest(
                job_id=job_id,
                reference_usernames=search_usernames[:discover_count],
                limit=discover_count,
                follower_min=follower_min,
                follower_max=follower_max,
                excluded_usernames=list(excluded_usernames),
                deprioritize_brands=True,
            )
    except Exception as e:
        logger.warning(
            f"[Orchestration] Job {job_id}: Keyword user search failed: {e}"
        )

    return None


async def _run_pipeline(job_id: str, job_data: Dict[str, Any]) -> None:
    """
    Run the full orchestration pipeline internally.

    The pipeline uses an iterative discovery-scoring loop:
    - Discovers 2x the remaining needed profiles per round
    - Scores each, keeps those above min_score_threshold
    - Repeats up to MAX_DISCOVERY_ROUNDS until enough quality profiles are found
    - Cross-job deduplication prevents the same user from seeing repeat profiles

    Args:
        job_id: The job UUID
        job_data: The job data dict (from job_repo)
    """
    job_service = JobService()
    job_repo = JobRepository()
    profile_repo = ProfileRepository()
    start_time = time.time()

    try:
        # =====================================================================
        # Phase 1: Brand Analysis (with retry for cold-start resource errors)
        # =====================================================================
        logger.info(f"[Orchestration] Job {job_id}: Starting Phase 1 - Brand Analysis")
        job_service.update_status(job_id, "analyzing", validate_transition=True)

        brand_agent = get_brand_analyzer_agent()
        brand_request = BrandAnalyzerRequest(
            job_id=job_id,
            max_posts_per_profile=12,
        )

        brand_response = None
        for _attempt in range(3):
            try:
                brand_response = await brand_agent.run(brand_request)
                break
            except Exception as e:
                err_str = str(e)
                is_resource_error = (
                    "Resource temporarily unavailable" in err_str
                    or "[Errno 11]" in err_str
                    or "Cannot allocate memory" in err_str
                )
                if is_resource_error and _attempt < 2:
                    wait_secs = 5 * (_attempt + 1)
                    logger.warning(
                        f"[Orchestration] Job {job_id}: Brand analysis hit resource error "
                        f"(attempt {_attempt + 1}/3), retrying in {wait_secs}s: {e}"
                    )
                    await asyncio.sleep(wait_secs)
                    continue
                raise

        if brand_response is None:
            raise Exception("Brand analysis failed after 3 attempts")

        hashtags = brand_response.hashtags or []
        keywords = brand_response.keywords or []
        related_usernames = brand_response.related_usernames_from_references or []
        reference_summaries = brand_response.reference_profile_summaries or []
        partner_search_keywords = brand_response.partner_search_keywords or []

        # Extract reference profile usernames for tagged-posts discovery
        reference_usernames_for_tagging = [
            s["username"] for s in reference_summaries if s.get("username")
        ]

        phase1_time = time.time() - start_time
        logger.info(
            f"[Orchestration] Job {job_id}: Phase 1 complete in {phase1_time:.1f}s - "
            f"{len(hashtags)} hashtags, {len(keywords)} keywords, "
            f"{len(related_usernames)} related usernames, "
            f"{len(reference_summaries)} reference summaries, "
            f"{len(partner_search_keywords)} partner search keywords, "
            f"{len(reference_usernames_for_tagging)} reference usernames for tag discovery"
        )

        # =====================================================================
        # Phase 2+3: Iterative Discovery & Scoring
        # =====================================================================
        logger.info(f"[Orchestration] Job {job_id}: Starting Phase 2+3 - Iterative Discovery & Scoring")
        job_service.update_status(job_id, "discovering", validate_transition=True)

        # Prepare discovery parameters — MERGE brand + job hashtags
        job_hashtags = job_data.get("hashtags", [])
        all_hashtags = list(dict.fromkeys(hashtags + job_hashtags))  # deduplicated, order preserved
        if not all_hashtags:
            all_hashtags = ["#sustainable", "#ecofriendly"]
        discovery_keywords = list(dict.fromkeys(
            (keywords[:5] if keywords else []) + (job_data.get("keywords", [])[:5])
        ))

        # Inject country-specific hashtags when target_country is set
        target_country = job_data.get("target_country")
        if target_country:
            geo_hashtags = _generate_country_hashtags(target_country)
            # Prepend geo hashtags so they're used in early rounds
            all_hashtags = geo_hashtags + [h for h in all_hashtags if h not in geo_hashtags]
            logger.info(
                f"[Orchestration] Job {job_id}: Added {len(geo_hashtags)} "
                f"geo-specific hashtags for {target_country}"
            )

        # Split hashtags into groups for rotation across rounds
        # Round 1 gets the first batch, Round 2 gets the next, etc.
        hashtags_per_round = max(5, len(all_hashtags) // Defaults.MAX_DISCOVERY_ROUNDS)
        hashtag_groups = [
            all_hashtags[i:i + hashtags_per_round]
            for i in range(0, len(all_hashtags), hashtags_per_round)
        ]
        # Ensure we have at least MAX_DISCOVERY_ROUNDS groups (reuse if needed)
        while len(hashtag_groups) < Defaults.MAX_DISCOVERY_ROUNDS:
            hashtag_groups.append(all_hashtags)

        logger.info(
            f"[Orchestration] Job {job_id}: {len(all_hashtags)} hashtags split into "
            f"{len(hashtag_groups)} groups for round rotation"
        )

        requested_count = job_data.get("discovery_limit", 10)
        min_score_threshold = job_data.get("min_score_threshold", Defaults.DEFAULT_MIN_SCORE_THRESHOLD)
        follower_min = job_data.get("follower_range_min", 5000)
        follower_max = job_data.get("follower_range_max", 500000)

        # Calibrate follower range from reference profiles.
        # We find COMPLEMENTARY partners — distributors, influencers, boutiques —
        # who typically have FEWER followers than the brand itself. So anchor
        # the range on the SMALLEST reference profile and use a wide band.
        if reference_summaries:
            ref_followers = sorted(
                [s.get("followers", 0) for s in reference_summaries if s.get("followers", 0) > 0]
            )
            if ref_followers:
                min_ref = ref_followers[0]
                max_ref = ref_followers[-1]

                # Partners can be smaller than the brand — use 10% of the
                # smallest reference as the floor, capped at 5000 so we
                # don't accidentally filter out small but real accounts.
                calibrated_min = max(follower_min, min(int(min_ref * 0.1), 5000))

                # Partners can be larger than some references — use 3x the
                # largest reference, but respect the job's upper bound.
                calibrated_max = min(follower_max, int(max_ref * 3.0))
                # Ensure at least a 50K-wide window
                calibrated_max = max(calibrated_max, calibrated_min + 50000)
                calibrated_max = min(calibrated_max, follower_max)

                if calibrated_min < calibrated_max:
                    logger.info(
                        f"[Orchestration] Job {job_id}: Follower range calibrated: "
                        f"{follower_min}-{follower_max} -> {calibrated_min}-{calibrated_max} "
                        f"(refs: {min_ref}-{max_ref})"
                    )
                    follower_min = calibrated_min
                    follower_max = calibrated_max

        # Detect if references are mostly business accounts
        is_mostly_business = False
        if reference_summaries:
            business_count = sum(1 for s in reference_summaries if s.get("is_business"))
            is_mostly_business = business_count > len(reference_summaries) * 0.6
            if is_mostly_business:
                logger.info(
                    f"[Orchestration] Job {job_id}: {business_count}/{len(reference_summaries)} "
                    f"references are business accounts - will require business accounts"
                )

        # Cross-job deduplication: get all usernames from past jobs for this user
        user_id = job_data.get("user_id")
        excluded_usernames: Set[str] = set()
        if user_id:
            try:
                excluded_usernames = profile_repo.get_usernames_by_user(user_id)
                logger.info(
                    f"[Orchestration] Job {job_id}: Cross-job dedup - "
                    f"{len(excluded_usernames)} usernames excluded from past jobs"
                )
            except Exception as e:
                logger.warning(
                    f"[Orchestration] Job {job_id}: Cross-job dedup failed, continuing without: {e}"
                )

        # Initialize agents
        discovery_agent = get_discovery_agent()
        scorer_agent = get_scorer_agent()
        # Disable scorer's own status updates — orchestration controls status
        # to prevent profiles from appearing as 'done' before qualification check
        scorer_agent._manage_profile_status = False

        SCORING_BATCH_SIZE = 3  # Score up to 3 profiles concurrently

        qualified_profiles: List[Dict[str, Any]] = []
        total_discovered = 0
        total_scored = 0
        total_skipped = 0
        # Track related usernames harvested from profile scraper for next rounds
        pending_related_usernames: List[str] = []
        # Track which hashtag sets have been tried (to avoid repeats)
        tried_hashtag_sets: Set[str] = set()
        # Generate keyword fallback hashtags upfront
        keyword_fallback_hashtags = _generate_keyword_hashtags(discovery_keywords) if discovery_keywords else []
        empty_rounds = 0  # consecutive rounds with 0 profiles

        for round_num in range(1, Defaults.MAX_DISCOVERY_ROUNDS + 1):
            remaining = requested_count - len(qualified_profiles)
            if remaining <= 0:
                break

            # Calculate how many to discover this round (2x the gap)
            discover_count = int(remaining * Defaults.OVER_DISCOVERY_MULTIPLIER)
            discover_count = max(discover_count, 15)  # At least 15

            logger.info(
                f"[Orchestration] Job {job_id}: Round {round_num}/{Defaults.MAX_DISCOVERY_ROUNDS} - "
                f"Need {remaining} more, discovering {discover_count} candidates"
            )

            # --- Discovery ---
            # Round strategy (priority order):
            #   Round 1: Tagged posts — who already tags the brand (warmest leads)
            #   Round 2: Keyword user search — partner_search_keywords (high quality)
            #   Round 3: Related profiles — deprioritize_brands (medium quality)
            #   Round 4+: Hashtag-based discovery (broadest net)

            if round_num == 1 and reference_usernames_for_tagging:
                # -------------------------------------------------------
                # Round 1: Tagged-posts discovery (WARMEST LEADS)
                # Find accounts that already tag the brand's profiles.
                # These are distributors reposting products, influencers
                # tagging in reviews, boutiques showcasing stock.
                # -------------------------------------------------------
                logger.info(
                    f"[Orchestration] Job {job_id}: Round 1 tagged-posts discovery "
                    f"for {len(reference_usernames_for_tagging)} reference profiles"
                )
                discovery_request = None
                try:
                    apify_service = get_apify_service()
                    tagger_usernames = await apify_service.search_tagged_posts(
                        usernames=reference_usernames_for_tagging,
                        results_limit=max(30, discover_count * 2),
                    )
                    # Filter out already-known usernames
                    new_taggers = [
                        u for u in tagger_usernames
                        if u.lower() not in excluded_usernames
                    ]
                    logger.info(
                        f"[Orchestration] Job {job_id}: Tagged-posts found "
                        f"{len(new_taggers)} new accounts that tag the brand"
                    )

                    if new_taggers:
                        discovery_request = DiscoveryRequest(
                            job_id=job_id,
                            reference_usernames=new_taggers[:discover_count],
                            limit=discover_count,
                            follower_min=follower_min,
                            follower_max=follower_max,
                            excluded_usernames=list(excluded_usernames),
                            deprioritize_brands=True,
                        )
                except Exception as e:
                    logger.warning(
                        f"[Orchestration] Job {job_id}: Tagged-posts discovery failed: {e}"
                    )

                # Fall back to keyword search if tagged-posts returned nothing
                if discovery_request is None and partner_search_keywords:
                    logger.info(
                        f"[Orchestration] Job {job_id}: Tagged-posts empty, "
                        f"falling back to keyword user search"
                    )
                    discovery_request = await _try_keyword_user_search(
                        job_id, partner_search_keywords, discover_count,
                        follower_min, follower_max, excluded_usernames,
                    )
                    # Mark keywords as consumed so Round 2 doesn't repeat
                    partner_search_keywords = []

                # Fall back to related profiles
                if discovery_request is None and related_usernames:
                    ref_batch = related_usernames[:discover_count]
                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        reference_usernames=ref_batch,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                        require_business_account=is_mostly_business,
                        deprioritize_brands=True,
                    )

                # Final fallback to hashtags
                if discovery_request is None:
                    round_hashtags = hashtag_groups[0]
                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        hashtags=round_hashtags,
                        keywords=discovery_keywords,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                    )

            elif round_num <= 2 and partner_search_keywords:
                # -------------------------------------------------------
                # Round 2 (or Round 1 if no tagged discovery):
                # Keyword user search (HIGH QUALITY)
                # Search for complementary partners by keyword using
                # apify/instagram-search-scraper with searchType="user"
                # -------------------------------------------------------
                logger.info(
                    f"[Orchestration] Job {job_id}: Round {round_num} keyword user search "
                    f"with {len(partner_search_keywords)} partner keywords"
                )
                discovery_request = await _try_keyword_user_search(
                    job_id, partner_search_keywords, discover_count,
                    follower_min, follower_max, excluded_usernames,
                )

                # Fall back to related profiles if keyword search failed/empty
                if discovery_request is None and related_usernames:
                    ref_batch = related_usernames[:discover_count]
                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        reference_usernames=ref_batch,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                        require_business_account=is_mostly_business,
                        deprioritize_brands=True,
                    )
                elif discovery_request is None:
                    round_hashtags = hashtag_groups[0]
                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        hashtags=round_hashtags,
                        keywords=discovery_keywords,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                    )

                # Mark keywords as consumed so we don't repeat
                partner_search_keywords = []

            elif round_num <= 3 and related_usernames:
                # -------------------------------------------------------
                # Round 3 (or earlier if prior rounds were skipped):
                # Reference-related discovery with brand deprioritization
                # -------------------------------------------------------
                ref_batch = related_usernames[:discover_count]
                logger.info(
                    f"[Orchestration] Job {job_id}: Round {round_num} using {len(ref_batch)} "
                    f"reference-related usernames (deprioritize_brands=True)"
                )
                discovery_request = DiscoveryRequest(
                    job_id=job_id,
                    reference_usernames=ref_batch,
                    limit=discover_count,
                    follower_min=follower_min,
                    follower_max=follower_max,
                    excluded_usernames=list(excluded_usernames),
                    require_business_account=is_mostly_business,
                    deprioritize_brands=True,
                )
                # Consume related usernames so we don't repeat
                related_usernames = []

            else:
                # -------------------------------------------------------
                # Rounds 4+: Prefer pending related usernames, then hashtags
                # -------------------------------------------------------
                if pending_related_usernames:
                    batch = pending_related_usernames[:discover_count]
                    pending_related_usernames = pending_related_usernames[discover_count:]
                    logger.info(
                        f"[Orchestration] Job {job_id}: Round {round_num} using "
                        f"{len(batch)} pending related usernames"
                    )
                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        reference_usernames=batch,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                        deprioritize_brands=True,
                    )
                else:
                    # Hashtag-based discovery (broadest net)
                    # Calculate hashtag group index, accounting for earlier rounds
                    rounds_used_for_non_hashtag = 0
                    if reference_usernames_for_tagging:
                        rounds_used_for_non_hashtag += 1
                    if brand_response.partner_search_keywords:
                        rounds_used_for_non_hashtag += 1
                    if brand_response.related_usernames_from_references:
                        rounds_used_for_non_hashtag += 1
                    hashtag_idx = max(0, round_num - 1 - rounds_used_for_non_hashtag)
                    round_hashtags = hashtag_groups[min(hashtag_idx, len(hashtag_groups) - 1)]

                    # If this exact hashtag set was already tried and returned 0,
                    # switch to keyword-derived fallback hashtags
                    hashtag_key = "|".join(sorted(round_hashtags))
                    if hashtag_key in tried_hashtag_sets and keyword_fallback_hashtags:
                        # Pick a fresh slice of fallback hashtags
                        fallback_start = (round_num - 1) * 8
                        fallback_slice = keyword_fallback_hashtags[fallback_start:fallback_start + 8]
                        if fallback_slice:
                            round_hashtags = fallback_slice
                            logger.info(
                                f"[Orchestration] Job {job_id}: Using keyword-fallback hashtags: {round_hashtags}"
                            )
                    tried_hashtag_sets.add(hashtag_key)

                    discovery_request = DiscoveryRequest(
                        job_id=job_id,
                        hashtags=round_hashtags,
                        keywords=discovery_keywords,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                    )

            try:
                discovery_response = await discovery_agent.run(discovery_request)
            except Exception as e:
                logger.error(f"[Orchestration] Job {job_id}: Discovery failed in round {round_num}: {e}")
                break

            round_profiles = discovery_response.profiles or []
            total_discovered += len(round_profiles)

            # Harvest related usernames for future rounds
            if discovery_response.related_usernames:
                new_related = [
                    u for u in discovery_response.related_usernames
                    if u.lower() not in excluded_usernames
                ]
                pending_related_usernames.extend(new_related)
                logger.info(
                    f"[Orchestration] Job {job_id}: Harvested {len(new_related)} "
                    f"related usernames ({len(pending_related_usernames)} pending total)"
                )

            if not round_profiles:
                # Try rescue from pending related usernames before declaring empty
                if pending_related_usernames:
                    rescue_batch = pending_related_usernames[:discover_count]
                    pending_related_usernames = pending_related_usernames[discover_count:]
                    logger.info(
                        f"[Orchestration] Job {job_id}: Round {round_num} empty, "
                        f"rescuing with {len(rescue_batch)} related usernames"
                    )
                    rescue_request = DiscoveryRequest(
                        job_id=job_id,
                        reference_usernames=rescue_batch,
                        limit=discover_count,
                        follower_min=follower_min,
                        follower_max=follower_max,
                        excluded_usernames=list(excluded_usernames),
                        deprioritize_brands=True,
                    )
                    try:
                        rescue_response = await discovery_agent.run(rescue_request)
                        round_profiles = rescue_response.profiles or []
                        total_discovered += len(round_profiles)
                        # Harvest related usernames from rescue
                        if rescue_response.related_usernames:
                            new_related = [
                                u for u in rescue_response.related_usernames
                                if u.lower() not in excluded_usernames
                            ]
                            pending_related_usernames.extend(new_related)
                    except Exception as e:
                        logger.warning(
                            f"[Orchestration] Job {job_id}: Rescue discovery failed: {e}"
                        )

            if not round_profiles:
                empty_rounds += 1
                logger.warning(
                    f"[Orchestration] Job {job_id}: No new profiles in round {round_num} "
                    f"(empty_rounds={empty_rounds})"
                )
                # Only break after 5 consecutive empty rounds to give fallback a chance
                if empty_rounds >= 5:
                    logger.warning(
                        f"[Orchestration] Job {job_id}: {empty_rounds} consecutive empty rounds, "
                        f"stopping discovery."
                    )
                    break
                continue
            else:
                empty_rounds = 0  # reset on successful round

            # Update profiles_discovered counter
            try:
                job_repo.update(str(job_id), {"profiles_discovered": total_discovered})
            except Exception:
                pass

            # Transition to scoring on first successful discovery round
            if total_scored == 0:
                job_service.update_status(job_id, "scoring", validate_transition=True)

            # --- Scoring (concurrent batches) ---
            async def _score_one(prof):
                """Score a single profile. Returns result dict or None."""
                pid = _get_profile_field(prof, "id")
                if not pid:
                    return None
                uname = _get_profile_field(prof, "username", "?")
                try:
                    # Keep profile in 'processing' state until qualification decided
                    try:
                        profile_repo.update_status(str(pid), ProfileStatus.PROCESSING)
                    except Exception:
                        pass
                    req = ScorerRequest(
                        profile_id=str(pid),
                        job_id=job_id,
                        reference_profile_summaries=reference_summaries if reference_summaries else None,
                    )
                    resp = await scorer_agent.run(req)
                    return {"profile": prof, "pid": pid, "username": uname, "response": resp}
                except Exception as e:
                    logger.error(f"[Orchestration] Job {job_id}: Failed to score @{uname}: {e}")
                    return None

            for batch_start in range(0, len(round_profiles), SCORING_BATCH_SIZE):
                if len(qualified_profiles) >= requested_count:
                    break
                batch = round_profiles[batch_start:batch_start + SCORING_BATCH_SIZE]
                results = await asyncio.gather(*[_score_one(p) for p in batch])

                for result in results:
                    if result is None:
                        continue
                    total_scored += 1
                    pid = result["pid"]
                    uname = result["username"]
                    resp = result["response"]

                    if resp.final_score >= min_score_threshold:
                        qualified_profiles.append(result["profile"])
                        try:
                            profile_repo.update_status(str(pid), ProfileStatus.SCORED)
                        except Exception:
                            pass
                        try:
                            job_repo.increment_profiles_scored(job_id)
                        except Exception:
                            pass
                        logger.info(
                            f"[Orchestration] Job {job_id}: R{round_num} - "
                            f"@{uname} QUALIFIED (score={resp.final_score})"
                        )
                    else:
                        total_skipped += 1
                        try:
                            profile_repo.update_status(str(pid), ProfileStatus.SKIPPED)
                        except Exception:
                            pass
                        logger.info(
                            f"[Orchestration] Job {job_id}: R{round_num} - "
                            f"@{uname} SKIPPED (score={resp.final_score} < {min_score_threshold})"
                        )

                if len(qualified_profiles) >= requested_count:
                    break

            # Add newly discovered usernames to exclusion set for next round
            for profile in round_profiles:
                uname = _get_profile_field(profile, "username")
                if uname:
                    excluded_usernames.add(uname.lower())

            logger.info(
                f"[Orchestration] Job {job_id}: Round {round_num} complete - "
                f"{len(qualified_profiles)}/{requested_count} qualified profiles so far"
            )

            if len(qualified_profiles) >= requested_count:
                break

        # Update final counts
        try:
            job_repo.update(str(job_id), {
                "profiles_discovered": total_discovered,
                "profiles_scored": len(qualified_profiles),
            })
        except Exception:
            pass

        if not qualified_profiles and total_discovered == 0:
            logger.warning(f"[Orchestration] Job {job_id}: No profiles discovered at all, completing.")
            # Ensure we transition through scoring before completing
            try:
                current_job = job_repo.get_by_id(job_id)
                if current_job.get("status") == "discovering":
                    job_service.update_status(job_id, "scoring", validate_transition=True)
            except Exception:
                pass
            job_service.update_status(job_id, "completed", validate_transition=True)
            return

        # =====================================================================
        # Phase 4: Contact Enrichment (only for qualified profiles)
        # =====================================================================
        enriched_count = 0
        try:
            logger.info(
                f"[Orchestration] Job {job_id}: Starting Phase 4 - "
                f"Contact Enrichment for {len(qualified_profiles)} qualified profiles"
            )

            enricher_agent = get_contact_enricher_agent()
            ENRICHMENT_BATCH_SIZE = 5

            async def _enrich_one(prof, idx):
                """Enrich a single profile. Returns enriched flag or None."""
                pid = _get_profile_field(prof, "id")
                if not pid:
                    return None
                uname = _get_profile_field(prof, "username", "?")
                try:
                    req = ContactEnricherRequest(
                        profile_id=str(pid),
                        job_id=job_id,
                        profile_data=prof if isinstance(prof, dict) else None,
                    )
                    res = await enricher_agent.run(req)
                    if res.email or res.phone or res.address:
                        logger.info(
                            f"[Orchestration] Job {job_id}: Enriched {idx+1}/{len(qualified_profiles)} - "
                            f"@{uname} (email={bool(res.email)}, phone={bool(res.phone)}, "
                            f"address={bool(res.address)})"
                        )
                        return True
                    else:
                        logger.info(
                            f"[Orchestration] Job {job_id}: No contacts found {idx+1}/{len(qualified_profiles)} - @{uname}"
                        )
                        return False
                except Exception as e:
                    logger.warning(f"[Orchestration] Job {job_id}: Contact enrichment failed for @{uname}: {e}")
                    return None

            for batch_start in range(0, len(qualified_profiles), ENRICHMENT_BATCH_SIZE):
                batch = qualified_profiles[batch_start:batch_start + ENRICHMENT_BATCH_SIZE]
                results = await asyncio.gather(*[
                    _enrich_one(p, batch_start + i) for i, p in enumerate(batch)
                ])
                enriched_count += sum(1 for r in results if r is True)
        except Exception as e:
            logger.error(
                f"[Orchestration] Job {job_id}: Phase 4 (Contact Enrichment) failed entirely: {e}. "
                f"Pipeline will still complete."
            )

        # =====================================================================
        # Complete
        # =====================================================================
        job_service.update_status(job_id, "completed", validate_transition=True)

        total_time = time.time() - start_time
        logger.info(
            f"[Orchestration] Job {job_id}: Pipeline complete in {total_time:.1f}s - "
            f"{total_discovered} discovered, {total_scored} scored, "
            f"{len(qualified_profiles)} qualified (>={min_score_threshold}), "
            f"{total_skipped} skipped, {enriched_count} contacts enriched"
        )

    except Exception as e:
        logger.exception(f"[Orchestration] Job {job_id}: Pipeline failed: {e}")
        try:
            job_service.update_status(
                job_id,
                "failed",
                error_message=str(e)[:500],
                validate_transition=False,
            )
        except Exception:
            logger.error(f"[Orchestration] Job {job_id}: Failed to update status to failed")


def _run_async_pipeline(job_id: str, job_data: Dict[str, Any]) -> None:
    """Thread target: create an event loop and run the pipeline."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run_pipeline(job_id, job_data))
    finally:
        loop.close()


def start_pipeline_background(job_id: str, job_data: Dict[str, Any]) -> None:
    """
    Start the orchestration pipeline in a background thread.

    This is called by job_service.trigger_discovery() when N8N is unavailable.
    The pipeline runs asynchronously in a separate thread so the API response
    returns immediately.
    """
    thread = threading.Thread(
        target=_run_async_pipeline,
        args=(job_id, job_data),
        name=f"orchestration-{job_id[:8]}",
        daemon=True,
    )
    thread.start()
    logger.info(f"[Orchestration] Started background pipeline for job {job_id}")
