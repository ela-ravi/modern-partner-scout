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
        # Phase 1: Brand Analysis
        # =====================================================================
        logger.info(f"[Orchestration] Job {job_id}: Starting Phase 1 - Brand Analysis")
        job_service.update_status(job_id, "analyzing", validate_transition=True)

        brand_agent = get_brand_analyzer_agent()
        brand_request = BrandAnalyzerRequest(
            job_id=job_id,
            max_posts_per_profile=12,
        )
        brand_response = await brand_agent.run(brand_request)

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

        for round_num in range(1, Defaults.MAX_DISCOVERY_ROUNDS + 1):
            remaining = requested_count - len(qualified_profiles)
            if remaining <= 0:
                break

            # Calculate how many to discover this round (2x the gap)
            discover_count = int(remaining * Defaults.OVER_DISCOVERY_MULTIPLIER)
            discover_count = max(discover_count, 5)  # At least 5

            logger.info(
                f"[Orchestration] Job {job_id}: Round {round_num}/{Defaults.MAX_DISCOVERY_ROUNDS} - "
                f"Need {remaining} more, discovering {discover_count} candidates"
            )

            # --- Discovery (rotate hashtags per round) ---
            round_hashtags = hashtag_groups[round_num - 1]
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

            if not round_profiles:
                logger.warning(
                    f"[Orchestration] Job {job_id}: No new profiles discovered in round {round_num}, "
                    f"source may be exhausted."
                )
                break

            # Update profiles_discovered counter
            try:
                job_repo.update(str(job_id), {"profiles_discovered": total_discovered})
            except Exception:
                pass

            # Transition to scoring on first round
            if round_num == 1:
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
