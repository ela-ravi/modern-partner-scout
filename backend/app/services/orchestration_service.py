"""
PartnerScout AI - Internal Orchestration Service

Runs the 4-phase pipeline:
  Phase 1: Brand Analysis
  Phase 2: Profile Discovery
  Phase 3: Profile Scoring
  Phase 4: Contact Enrichment (website scraping + LLM)

Called by job_service.trigger_discovery() when N8N is unavailable.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any

from app.agents.brand_analyzer import get_brand_analyzer_agent
from app.agents.discovery import get_discovery_agent
from app.agents.scorer import get_scorer_agent
from app.agents.contact_enricher import get_contact_enricher_agent, ContactEnricherRequest
from app.models.agent import BrandAnalyzerRequest, DiscoveryRequest, ScorerRequest
from app.services.job_service import JobService
from app.repositories.job_repo import JobRepository

logger = logging.getLogger(__name__)


async def _run_pipeline(job_id: str, job_data: Dict[str, Any]) -> None:
    """
    Run the full 4-phase orchestration pipeline internally.

    Args:
        job_id: The job UUID
        job_data: The job data dict (from job_repo)
    """
    job_service = JobService()
    job_repo = JobRepository()
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
        # Phase 2: Profile Discovery
        # =====================================================================
        logger.info(f"[Orchestration] Job {job_id}: Starting Phase 2 - Discovery")
        job_service.update_status(job_id, "discovering", validate_transition=True)

        # Use hashtags from brand DNA, fall back to job hashtags
        discovery_hashtags = hashtags[:5] if hashtags else job_data.get("hashtags", [])[:5]
        if not discovery_hashtags:
            discovery_hashtags = ["#sustainable", "#ecofriendly"]

        discovery_keywords = keywords[:5] if keywords else job_data.get("keywords", [])[:5]

        discovery_agent = get_discovery_agent()
        discovery_request = DiscoveryRequest(
            job_id=job_id,
            hashtags=discovery_hashtags,
            keywords=discovery_keywords,
            limit=job_data.get("discovery_limit", 10),
            follower_min=job_data.get("follower_range_min", 5000),
            follower_max=job_data.get("follower_range_max", 500000),
        )
        discovery_response = await discovery_agent.run(discovery_request)

        profiles = discovery_response.profiles or []
        phase2_time = time.time() - start_time - phase1_time
        logger.info(
            f"[Orchestration] Job {job_id}: Phase 2 complete in {phase2_time:.1f}s - "
            f"{discovery_response.total_discovered} discovered, "
            f"{discovery_response.deduplicated} deduplicated"
        )

        # Update profiles_discovered counter on job record
        try:
            job_repo.update(str(job_id), {"profiles_discovered": len(profiles)})
        except Exception as e:
            logger.warning(f"[Orchestration] Job {job_id}: Failed to update profiles_discovered: {e}")

        if not profiles:
            logger.warning(f"[Orchestration] Job {job_id}: No profiles discovered, completing.")
            job_service.update_status(job_id, "scoring", validate_transition=True)
            job_service.update_status(job_id, "completed", validate_transition=True)
            return

        # =====================================================================
        # Phase 3: Profile Scoring
        # =====================================================================
        logger.info(
            f"[Orchestration] Job {job_id}: Starting Phase 3 - Scoring {len(profiles)} profiles"
        )
        job_service.update_status(job_id, "scoring", validate_transition=True)

        scorer_agent = get_scorer_agent()
        scored_count = 0

        for i, profile in enumerate(profiles):
            profile_id = profile.get("id") if isinstance(profile, dict) else getattr(profile, "id", None)
            if not profile_id:
                continue

            try:
                score_request = ScorerRequest(
                    profile_id=str(profile_id),
                    job_id=job_id,
                )
                await scorer_agent.run(score_request)
                scored_count += 1

                # Increment profiles_scored counter on job record
                try:
                    job_repo.increment_profiles_scored(job_id)
                except Exception:
                    pass

                username = profile.get("username") if isinstance(profile, dict) else getattr(profile, "username", "?")
                logger.info(
                    f"[Orchestration] Job {job_id}: Scored profile {i+1}/{len(profiles)} - @{username}"
                )
            except Exception as e:
                username = profile.get("username") if isinstance(profile, dict) else getattr(profile, "username", "?")
                logger.error(
                    f"[Orchestration] Job {job_id}: Failed to score @{username}: {e}"
                )

        # Update profiles_scored to the actual count (in case increments failed)
        try:
            job_repo.update(str(job_id), {"profiles_scored": scored_count})
        except Exception:
            pass

        # =====================================================================
        # Phase 4: Contact Enrichment (non-fatal — pipeline completes even if this fails)
        # =====================================================================
        enriched_count = 0
        try:
            logger.info(
                f"[Orchestration] Job {job_id}: Starting Phase 4 - Contact Enrichment for {len(profiles)} profiles"
            )

            enricher_agent = get_contact_enricher_agent()

            for i, profile in enumerate(profiles):
                profile_id = profile.get("id") if isinstance(profile, dict) else getattr(profile, "id", None)
                if not profile_id:
                    continue

                username = profile.get("username") if isinstance(profile, dict) else getattr(profile, "username", "?")

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
                            f"[Orchestration] Job {job_id}: Enriched contact {i+1}/{len(profiles)} - "
                            f"@{username} (email={bool(result.email)}, phone={bool(result.phone)}, "
                            f"address={bool(result.address)})"
                        )
                    else:
                        logger.info(
                            f"[Orchestration] Job {job_id}: No contacts found {i+1}/{len(profiles)} - @{username}"
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
            f"{len(profiles)} discovered, {scored_count} scored, {enriched_count} contacts enriched"
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
