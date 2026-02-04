"""
PartnerScout AI - Python Fallback Orchestrator

STORY-4.2.1: Implement Python Fallback Script

This script provides a Python-based fallback orchestrator that mirrors the N8N workflow.
It can be used when N8N is unavailable or for local development/testing.

The script calls the same FastAPI endpoints that N8N uses, ensuring identical behavior.

Usage:
    python -m scripts.run_discovery <job_id>

Example:
    python -m scripts.run_discovery 11111111-1111-1111-1111-111111111111
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Optional

import httpx

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

settings = get_settings()

# FastAPI base URL - defaults to localhost:8000
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# Service key for authentication (same as N8N uses)
SERVICE_KEY = settings.n8n.service_key

if not SERVICE_KEY:
    logger.error("N8N_SERVICE_KEY environment variable is required")
    sys.exit(1)


# =============================================================================
# Status Update Functions (calls Status Update APIs)
# =============================================================================

async def update_job_status(
    job_id: str,
    status: str,
    error_message: Optional[str] = None
) -> Dict:
    """
    Update job status via API.
    
    Calls: PATCH /api/jobs/{job_id}/status (Section 2.1)
    Same endpoint used by N8N nodes: Set Job Analyzing, Set Job Discovering, etc.
    
    Args:
        job_id: UUID of the discovery job
        status: One of: pending, analyzing, discovering, scoring, completed, failed
        error_message: Optional error message (only when status=failed)
    
    Returns:
        Updated job data from API response
        
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    async with httpx.AsyncClient() as client:
        payload = {"status": status}
        if error_message:
            payload["error_message"] = error_message
        
        logger.debug(f"Updating job {job_id} status to '{status}'")
        
        response = await client.patch(
            f"{FASTAPI_BASE_URL}/api/jobs/{job_id}/status",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


async def update_profile_status(profile_id: str, status: str) -> Dict:
    """
    Update profile status via API.
    
    Calls: PATCH /api/profiles/{profile_id}/status (Section 2.2)
    Same endpoint used by N8N nodes: Set Profile Processing, Set Profile Done.
    
    Args:
        profile_id: UUID of the discovered profile
        status: One of: new, processing, done, skipped
    
    Returns:
        Updated profile data from API response
        
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    async with httpx.AsyncClient() as client:
        logger.debug(f"Updating profile {profile_id} status to '{status}'")
        
        response = await client.patch(
            f"{FASTAPI_BASE_URL}/api/profiles/{profile_id}/status",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={"status": status},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# =============================================================================
# Agent Call Functions (calls Agent APIs)
# =============================================================================

async def call_brand_analyzer(job_id: str) -> Dict:
    """
    Call Brand Analyzer Agent API.
    
    Calls: POST /api/agent/analyze-brand
    Same endpoint used by N8N Node: Brand Analyzer Agent.
    
    Args:
        job_id: UUID of the discovery job
        
    Returns:
        Brand DNA response with hashtags, keywords, and embedding vector
        
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    async with httpx.AsyncClient() as client:
        logger.debug(f"Calling Brand Analyzer for job {job_id}")
        
        response = await client.post(
            f"{FASTAPI_BASE_URL}/api/agent/analyze-brand",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={"job_id": job_id},
            timeout=120.0  # Same timeout as N8N node
        )
        response.raise_for_status()
        return response.json()


async def call_discovery_agent(
    job_id: str,
    hashtags: list[str],
    keywords: list[str],
    limit: int = 50
) -> Dict:
    """
    Call Discovery Agent API.
    
    Calls: POST /api/agent/discover
    Same endpoint used by N8N Node: Discovery Agent.
    
    Args:
        job_id: UUID of the discovery job
        hashtags: List of hashtags to search
        keywords: List of keywords to search
        limit: Maximum number of profiles to discover
        
    Returns:
        Discovery response with list of discovered profiles
        
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    async with httpx.AsyncClient() as client:
        logger.debug(
            f"Calling Discovery Agent for job {job_id} "
            f"with {len(hashtags)} hashtags, limit={limit}"
        )
        
        response = await client.post(
            f"{FASTAPI_BASE_URL}/api/agent/discover",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={
                "job_id": job_id,
                "hashtags": hashtags,
                "keywords": keywords,
                "limit": limit
            },
            timeout=180.0  # Same timeout as N8N node
        )
        response.raise_for_status()
        return response.json()


async def call_scorer_agent(profile_id: str, job_id: str) -> Dict:
    """
    Call Scorer Agent API.
    
    Calls: POST /api/agent/score
    Same endpoint used by N8N Node: Scorer Agent.
    
    Args:
        profile_id: UUID of the profile to score
        job_id: UUID of the discovery job
        
    Returns:
        Scoring response with score, reasoning, and contact info
        
    Raises:
        httpx.HTTPStatusError: If API call fails
    """
    async with httpx.AsyncClient() as client:
        logger.debug(f"Calling Scorer Agent for profile {profile_id}, job {job_id}")
        
        response = await client.post(
            f"{FASTAPI_BASE_URL}/api/agent/score",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={
                "profile_id": profile_id,
                "job_id": job_id
            },
            timeout=60.0  # Same timeout as N8N node
        )
        response.raise_for_status()
        return response.json()


# =============================================================================
# Main Orchestration Function
# =============================================================================

async def run_discovery(job_id: str) -> None:
    """
    Main orchestration function.
    
    Mirrors the N8N workflow exactly, using the same APIs.
    
    Workflow:
    1. Set job status to 'analyzing'
    2. Call Brand Analyzer Agent
    3. Set job status to 'discovering'
    4. Call Discovery Agent
    5. Set job status to 'scoring'
    6. For each profile:
       a. Set profile status to 'processing'
       b. Call Scorer Agent
       c. Set profile status to 'done'
    7. Set job status to 'completed'
    
    On any error:
    - Set job status to 'failed' with error message
    
    Args:
        job_id: UUID of the discovery job to process
        
    Raises:
        Exception: If any phase fails
    """
    logger.info(f"[Orchestrator] Starting discovery for job: {job_id}")
    
    try:
        # =====================================================================
        # Phase 1: Brand Analysis
        # Equivalent to N8N Nodes 05-06
        # =====================================================================
        logger.info("[Phase 1] Analyzing brand...")
        await update_job_status(job_id, "analyzing")
        
        brand_result = await call_brand_analyzer(job_id)
        
        # Extract brand DNA from response
        # Response format: {"hashtags": [...], "keywords": [...], ...}
        # or nested: {"brand_dna": {"hashtags": [...], "keywords": [...]}}
        if "brand_dna" in brand_result:
            brand_dna = brand_result["brand_dna"]
        else:
            brand_dna = brand_result
        
        hashtags = brand_dna.get("hashtags", [])
        keywords = brand_dna.get("keywords", [])
        
        logger.info(
            f"[Phase 1] Extracted {len(hashtags)} hashtags, "
            f"{len(keywords)} keywords"
        )
        
        # =====================================================================
        # Phase 2: Profile Discovery
        # Equivalent to N8N Nodes 07-08
        # =====================================================================
        logger.info("[Phase 2] Discovering profiles...")
        await update_job_status(job_id, "discovering")
        
        discovery_result = await call_discovery_agent(
            job_id=job_id,
            hashtags=hashtags,
            keywords=keywords,
            limit=50
        )
        
        # Extract profiles from response
        profiles = discovery_result.get("profiles", [])
        total_discovered = discovery_result.get("total_discovered", len(profiles))
        
        logger.info(
            f"[Phase 2] Discovered {total_discovered} profiles "
            f"({len(profiles)} returned)"
        )
        
        if not profiles:
            logger.warning("[Phase 2] No profiles discovered, completing job")
            await update_job_status(job_id, "completed")
            logger.info(f"[Complete] Discovery job {job_id} completed (no profiles)")
            return
        
        # =====================================================================
        # Phase 3: Scoring
        # Equivalent to N8N Nodes 09-14
        # =====================================================================
        logger.info(f"[Phase 3] Scoring {len(profiles)} profiles...")
        await update_job_status(job_id, "scoring")
        
        scored_count = 0
        high_score_count = 0
        skipped_count = 0
        
        for i, profile in enumerate(profiles):
            profile_id = profile.get("id")
            username = profile.get("username", "unknown")
            
            if not profile_id:
                logger.warning(f"[Phase 3] Profile {i+1} missing ID, skipping")
                skipped_count += 1
                continue
            
            logger.info(
                f"[Phase 3] Scoring profile {i+1}/{len(profiles)}: "
                f"@{username} ({profile_id})"
            )
            
            try:
                # Set profile to processing (N8N Node 11)
                await update_profile_status(profile_id, "processing")
                
                # Call scorer (N8N Node 12)
                score_result = await call_scorer_agent(profile_id, job_id)
                
                # Extract score from response
                # Response format: {"score": 75, ...} or {"final_score": 75, ...}
                score = score_result.get("score") or score_result.get("final_score", 0)
                
                # Set profile to done (N8N Node 13)
                await update_profile_status(profile_id, "done")
                
                scored_count += 1
                if score >= 50:
                    high_score_count += 1
                
                logger.debug(
                    f"[Phase 3] Profile @{username} scored: {score} "
                    f"(>=50: {score >= 50})"
                )
                
            except Exception as profile_error:
                logger.error(
                    f"[Phase 3] Error scoring profile {profile_id} "
                    f"(@{username}): {profile_error}"
                )
                try:
                    await update_profile_status(profile_id, "skipped")
                    skipped_count += 1
                except Exception as status_error:
                    logger.error(
                        f"[Phase 3] Failed to update profile {profile_id} "
                        f"status to skipped: {status_error}"
                    )
                # Continue with next profile
                continue
            
            # Rate limiting - equivalent to N8N Node 14 (Wait)
            # Small delay between profile scoring to avoid overwhelming the API
            if i < len(profiles) - 1:  # Don't wait after last profile
                await asyncio.sleep(1)
        
        # =====================================================================
        # Completion
        # Equivalent to N8N Nodes 15-17
        # =====================================================================
        logger.info(
            f"[Complete] Scored {scored_count} profiles, "
            f"{high_score_count} with score >= 50, "
            f"{skipped_count} skipped"
        )
        await update_job_status(job_id, "completed")
        logger.info(f"[Complete] Discovery job {job_id} completed successfully!")
        
    except httpx.HTTPStatusError as e:
        # HTTP error from API
        error_message = f"API error: {e.response.status_code} - {e.response.text}"
        logger.error(f"[Error] Discovery failed: {error_message}")
        
        try:
            await update_job_status(job_id, "failed", error_message=error_message)
        except Exception as status_error:
            logger.error(f"[Error] Failed to update job status: {status_error}")
        
        raise
    
    except Exception as e:
        # =====================================================================
        # Error Handling
        # Equivalent to N8N Nodes 19-21
        # =====================================================================
        error_message = str(e)
        logger.error(f"[Error] Discovery failed: {error_message}", exc_info=True)
        
        try:
            await update_job_status(job_id, "failed", error_message=error_message)
        except Exception as status_error:
            logger.error(f"[Error] Failed to update job status: {status_error}")
        
        raise


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.run_discovery <job_id>")
        print("Example: python -m scripts.run_discovery 11111111-1111-1111-1111-111111111111")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    # Validate UUID format (basic check)
    if len(job_id) != 36 or job_id.count('-') != 4:
        print(f"Error: Invalid job_id format: {job_id}")
        print("Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        sys.exit(1)
    
    # Run the async orchestrator
    try:
        asyncio.run(run_discovery(job_id))
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\n[Interrupted] Discovery cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[Fatal] Discovery failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
