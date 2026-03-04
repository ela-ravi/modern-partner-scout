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
        phase1_time = time.time() - start_time
        logger.info(
            f"[Orchestration] Job {job_id}: Phase 1 complete in {phase1_time:.1f}s - "
            f"{len(hashtags)} hashtags, {len(keywords)} keywords"
        )

        # =====================================================================
        # Phase 2+3: Iterative Discovery & Scoring
        # =====================================================================
        logger.info(f"[Orchestration] Job {job_id}: Starting Phase 2+3 - Iterative Discovery & Scoring")
        job_service.update_status(job_id, "discovering", validate_transition=True)

        # Prepare discovery parameters — use ALL available hashtags
        all_hashtags = hashtags if hashtags else job_data.get("hashtags", [])
        if not all_hashtags:
            all_hashtags = ["#sustainable", "#ecofriendly"]
        discovery_keywords = keywords[:5] if keywords else job_data.get("keywords", [])[:5]

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
            discover_count = max(discover_count, 10)  # At least 10

            logger.info(
                f"[Orchestration] Job {job_id}: Round {round_num}/{Defaults.MAX_DISCOVERY_ROUNDS} - "
                f"Need {remaining} more, discovering {discover_count} candidates"
            )

            # --- Discovery (rotate hashtags per round) ---
            round_hashtags = hashtag_groups[round_num - 1]

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
                empty_rounds += 1
                logger.warning(
                    f"[Orchestration] Job {job_id}: No new profiles in round {round_num} "
                    f"(empty_rounds={empty_rounds})"
                )
                # Only break after 2 consecutive empty rounds to give fallback a chance
                if empty_rounds >= 2:
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

            # --- Scoring ---
            for i, profile in enumerate(round_profiles):
                profile_id = _get_profile_field(profile, "id")
                if not profile_id:
                    continue

                username = _get_profile_field(profile, "username", "?")

                try:
                    score_request = ScorerRequest(
                        profile_id=str(profile_id),
                        job_id=job_id,
                    )
                    score_response = await scorer_agent.run(score_request)
                    total_scored += 1

                    # Increment profiles_scored counter
                    try:
                        job_repo.increment_profiles_scored(job_id)
                    except Exception:
                        pass

                    # Safety net: ensure profile status is set to 'done'
                    # The scorer agent should do this, but verify it happened
                    try:
                        current_profile = profile_repo.get_by_id(str(profile_id))
                        if current_profile.get("status") != ProfileStatus.SCORED.value:
                            profile_repo.update_status(str(profile_id), ProfileStatus.SCORED)
                            logger.info(
                                f"[Orchestration] Job {job_id}: Fixed profile status for @{username} -> done"
                            )
                    except Exception as e:
                        logger.warning(f"[Orchestration] Job {job_id}: Status fix failed for @{username}: {e}")

                    # Check against threshold
                    if score_response.final_score >= min_score_threshold:
                        qualified_profiles.append(profile)
                        logger.info(
                            f"[Orchestration] Job {job_id}: R{round_num} - "
                            f"@{username} QUALIFIED (score={score_response.final_score})"
                        )
                    else:
                        # Mark below-threshold profiles as skipped
                        total_skipped += 1
                        try:
                            profile_repo.update_status(str(profile_id), ProfileStatus.SKIPPED)
                        except Exception:
                            pass
                        logger.info(
                            f"[Orchestration] Job {job_id}: R{round_num} - "
                            f"@{username} SKIPPED (score={score_response.final_score} < {min_score_threshold})"
                        )

                    # Stop early if we have enough
                    if len(qualified_profiles) >= requested_count:
                        break

                except Exception as e:
                    logger.error(
                        f"[Orchestration] Job {job_id}: Failed to score @{username}: {e}"
                    )

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
                "profiles_scored": total_scored,
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

            for i, profile in enumerate(qualified_profiles):
                profile_id = _get_profile_field(profile, "id")
                if not profile_id:
                    continue

                username = _get_profile_field(profile, "username", "?")

                try:
                    enrich_request = ContactEnricherRequest(
                        profile_id=str(profile_id),
                        job_id=job_id,
                        profile_data=profile if isinstance(profile, dict) else None,
                    )
                    result = await enricher_agent.run(enrich_request)

                    if result.email or result.phone or result.address:
                        enriched_count += 1
                        logger.info(
                            f"[Orchestration] Job {job_id}: Enriched {i+1}/{len(qualified_profiles)} - "
                            f"@{username} (email={bool(result.email)}, phone={bool(result.phone)}, "
                            f"address={bool(result.address)})"
                        )
                    else:
                        logger.info(
                            f"[Orchestration] Job {job_id}: No contacts found {i+1}/{len(qualified_profiles)} - @{username}"
                        )
                except Exception as e:
                    logger.warning(
                        f"[Orchestration] Job {job_id}: Contact enrichment failed for @{username}: {e}"
                    )
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
