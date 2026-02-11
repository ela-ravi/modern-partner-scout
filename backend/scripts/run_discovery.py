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

# FastAPI base URL - defaults to localhost:8001 (can be overridden via FASTAPI_BASE_URL env var)
# Default port is 8001 (override with FASTAPI_BASE_URL environment variable if needed)
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")

# Service key for authentication (same as N8N uses)
SERVICE_KEY = settings.n8n.service_key

if not SERVICE_KEY:
    logger.error("N8N_SERVICE_KEY environment variable is required")
    sys.exit(1)


# =============================================================================
# Health Check Function
# =============================================================================

async def check_server_health() -> bool:
    """
    Check if the FastAPI server is available and responding.
    
    Returns:
        True if server is healthy, False otherwise
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FASTAPI_BASE_URL}/api/health",
                timeout=5.0
            )
            response.raise_for_status()
            return True
    except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
        logger.error(
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running. Error: {e}"
        )
        return False
    except Exception as e:
        logger.warning(f"Health check failed: {e}")
        return False


# =============================================================================
# Status Update Functions (calls Status Update APIs)
# =============================================================================

async def update_job_status(
    job_id: str,
    status: str,
    error_message: Optional[str] = None,
    suppress_connection_error: bool = False
) -> Dict:
    """
    Update job status via API.
    
    Calls: PATCH /api/jobs/{job_id}/status (Section 2.1)
    Same endpoint used by N8N nodes: Set Job Analyzing, Set Job Discovering, etc.
    
    Args:
        job_id: UUID of the discovery job
        status: One of: pending, analyzing, discovering, scoring, completed, failed
        error_message: Optional error message (only when status=failed)
        suppress_connection_error: If True, don't raise on connection errors (for error recovery)
    
    Returns:
        Updated job data from API response
        
    Raises:
        httpx.HTTPStatusError: If API call fails with HTTP error
        httpx.ConnectError: If cannot connect to server (unless suppress_connection_error=True)
    """
    try:
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
    except httpx.ConnectError as e:
        if suppress_connection_error:
            logger.warning(
                f"Cannot update job status (server unavailable): {e}. "
                f"This may be expected if the server is down."
            )
            raise
        else:
            port = FASTAPI_BASE_URL.split(':')[-1].rstrip('/')
            error_msg = (
                f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
                f"Please ensure the server is running. "
                f"Start it with: uvicorn app.main:app --reload --port {port}"
            )
            logger.error(error_msg)
            raise httpx.ConnectError(error_msg) from e
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        error_msg = f"Network error while updating job status: {e}"
        logger.error(error_msg)
        raise


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
        httpx.HTTPStatusError: If API call fails with HTTP error
        httpx.ConnectError: If cannot connect to server
    """
    try:
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
    except httpx.ConnectError as e:
        error_msg = (
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running."
        )
        logger.error(error_msg)
        raise httpx.ConnectError(error_msg) from e
    except (httpx.ReadError, httpx.WriteError) as e:
        error_msg = (
            f"Connection interrupted while communicating with server at {FASTAPI_BASE_URL}. "
            f"The server may have closed the connection unexpectedly or there was a network issue."
        )
        if str(e):
            error_msg += f" Error: {e}"
        logger.error(error_msg)
        raise httpx.NetworkError(error_msg) from e
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        error_msg = f"Network error while communicating with server at {FASTAPI_BASE_URL}"
        if str(e):
            error_msg += f": {e}"
        logger.error(error_msg)
        raise


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
        httpx.HTTPStatusError: If API call fails with HTTP error
        httpx.ConnectError: If cannot connect to server
    """
    try:
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
    except httpx.ConnectError as e:
        error_msg = (
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running."
        )
        logger.error(error_msg)
        raise httpx.ConnectError(error_msg) from e
    except (httpx.ReadError, httpx.WriteError) as e:
        error_msg = (
            f"Connection interrupted while communicating with server at {FASTAPI_BASE_URL}. "
            f"The server may have closed the connection unexpectedly or there was a network issue."
        )
        if str(e):
            error_msg += f" Error: {e}"
        logger.error(error_msg)
        raise httpx.NetworkError(error_msg) from e
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        error_msg = f"Network error while communicating with server at {FASTAPI_BASE_URL}"
        if str(e):
            error_msg += f": {e}"
        logger.error(error_msg)
        raise


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
        httpx.HTTPStatusError: If API call fails with HTTP error
        httpx.ConnectError: If cannot connect to server
    """
    try:
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
    except httpx.ConnectError as e:
        error_msg = (
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running."
        )
        logger.error(error_msg)
        raise httpx.ConnectError(error_msg) from e
    except (httpx.ReadError, httpx.WriteError) as e:
        error_msg = (
            f"Connection interrupted while communicating with server at {FASTAPI_BASE_URL}. "
            f"The server may have closed the connection unexpectedly or there was a network issue."
        )
        if str(e):
            error_msg += f" Error: {e}"
        logger.error(error_msg)
        raise httpx.NetworkError(error_msg) from e
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        error_msg = f"Network error while communicating with server at {FASTAPI_BASE_URL}"
        if str(e):
            error_msg += f": {e}"
        logger.error(error_msg)
        raise


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
        httpx.HTTPStatusError: If API call fails with HTTP error
        httpx.ConnectError: If cannot connect to server
    """
    try:
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
    except httpx.ConnectError as e:
        error_msg = (
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running."
        )
        logger.error(error_msg)
        raise httpx.ConnectError(error_msg) from e
    except (httpx.ReadError, httpx.WriteError) as e:
        error_msg = (
            f"Connection interrupted while communicating with server at {FASTAPI_BASE_URL}. "
            f"The server may have closed the connection unexpectedly or there was a network issue."
        )
        if str(e):
            error_msg += f" Error: {e}"
        logger.error(error_msg)
        raise httpx.NetworkError(error_msg) from e
    except (httpx.TimeoutException, httpx.NetworkError) as e:
        error_msg = f"Network error while communicating with server at {FASTAPI_BASE_URL}"
        if str(e):
            error_msg += f": {e}"
        logger.error(error_msg)
        raise


# =============================================================================
# Main Orchestration Function
# =============================================================================

async def run_discovery(job_id: str) -> None:
    """
    Main orchestration function.
    
    Mirrors the N8N workflow exactly, using the same APIs.
    
    Workflow:
    1. Check server health
    2. Set job status to 'analyzing'
    3. Call Brand Analyzer Agent
    4. Set job status to 'discovering'
    5. Call Discovery Agent
    6. Set job status to 'scoring'
    7. For each profile:
       a. Set profile status to 'processing'
       b. Call Scorer Agent
       c. Set profile status to 'done'
    8. Set job status to 'completed'
    
    On any error:
    - Set job status to 'failed' with error message (if server is available)
    
    Args:
        job_id: UUID of the discovery job to process
        
    Raises:
        httpx.ConnectError: If server is not available
        Exception: If any phase fails
    """
    logger.info(f"[Orchestrator] Starting discovery for job: {job_id}")
    
    # Check server health before starting
    logger.info(f"[Orchestrator] Checking server health at {FASTAPI_BASE_URL}...")
    if not await check_server_health():
        error_msg = (
            f"FastAPI server is not available at {FASTAPI_BASE_URL}. "
            f"Please start the server before running discovery. "
            f"Start it with: uvicorn app.main:app --reload --port 8000"
        )
        logger.error(f"[Error] {error_msg}")
        raise httpx.ConnectError(error_msg)
    
    logger.info("[Orchestrator] Server is healthy, proceeding with discovery...")
    
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
            f"[Phase 1] [SUCCESS] Brand Analyzer completed successfully"
        )
        logger.info(
            f"[Phase 1] Extracted {len(hashtags)} hashtags: {hashtags[:5]}{'...' if len(hashtags) > 5 else ''}"
        )
        logger.info(
            f"[Phase 1] Extracted {len(keywords)} keywords: {keywords[:5]}{'...' if len(keywords) > 5 else ''}"
        )
        logger.info(
            f"[Phase 1] [PASS] Passing results to Discovery Agent: {len(hashtags)} hashtags, {len(keywords)} keywords"
        )
        
        # =====================================================================
        # Phase 2: Profile Discovery
        # Equivalent to N8N Nodes 07-08
        # =====================================================================
        logger.info("[Phase 2] Discovering profiles...")
        
        # Check if hashtags are available (Discovery Agent requires at least one)
        if not hashtags:
            error_msg = (
                "Discovery Agent requires at least one hashtag, but Brand Analyzer "
                f"extracted 0 hashtags. Keywords found: {keywords[:5]}{'...' if len(keywords) > 5 else ''}. "
                "Cannot proceed with profile discovery."
            )
            logger.error(f"[Phase 2] [ERROR] {error_msg}")
            await update_job_status(job_id, "failed", error_message=error_msg)
            raise ValueError(error_msg)
        
        await update_job_status(job_id, "discovering")
        
        logger.info(
            f"[Phase 2] [CALL] Calling Discovery Agent with: "
            f"hashtags={hashtags[:3]}{'...' if len(hashtags) > 3 else ''}, "
            f"keywords={keywords[:3]}{'...' if len(keywords) > 3 else ''}, limit=50"
        )
        
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
            f"[Phase 2] ✓ Discovery Agent completed successfully"
        )
        logger.info(
            f"[Phase 2] Discovered {total_discovered} profiles "
            f"({len(profiles)} returned)"
        )
        if profiles:
            logger.info(
                f"[Phase 2] Sample profiles: {[p.get('username', 'unknown') for p in profiles[:3]]}"
            )
        logger.info(
            f"[Phase 2] [PASS] Passing {len(profiles)} profiles to Scorer Agent"
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
                logger.debug(
                    f"[Phase 3] [CALL] Calling Scorer Agent for profile @{username} "
                    f"(profile_id={profile_id}, job_id={job_id})"
                )
                score_result = await call_scorer_agent(profile_id, job_id)
                
                # Extract score from response
                # Response format: {"score": 75, ...} or {"final_score": 75, ...}
                score = score_result.get("score") or score_result.get("final_score", 0)
                
                # Set profile to done (N8N Node 13)
                await update_profile_status(profile_id, "done")
                
                scored_count += 1
                if score >= 50:
                    high_score_count += 1
                
                logger.info(
                    f"[Phase 3] [SUCCESS] Profile @{username} scored: {score} "
                    f"(>=50: {score >= 50})"
                )
                logger.debug(
                    f"[Phase 3] Scorer Agent result: score={score}, "
                    f"recommendation={score_result.get('recommendation', 'N/A')}"
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
        
    except httpx.ConnectError as e:
        # Connection error - server is not available
        port = FASTAPI_BASE_URL.split(':')[-1].rstrip('/')
        error_message = (
            f"Cannot connect to FastAPI server at {FASTAPI_BASE_URL}. "
            f"Please ensure the server is running. "
            f"Start it with: uvicorn app.main:app --reload --port {port}"
        )
        logger.error(f"[Error] {error_message}")
        logger.error(f"[Error] Connection error details: {e}")
        
        # Don't try to update status if server is down
        logger.warning(
            "[Error] Cannot update job status to 'failed' because server is unavailable"
        )
        raise
    
    except (httpx.ReadError, httpx.WriteError) as e:
        # Connection interrupted while reading/writing
        error_message = (
            f"Connection interrupted while communicating with server at {FASTAPI_BASE_URL}. "
            f"The server may have closed the connection unexpectedly or there was a network issue. "
            f"Error: {e}"
        )
        logger.error(f"[Error] {error_message}")
        
        # Try to update status, but handle failures gracefully
        try:
            await update_job_status(
                job_id, 
                "failed", 
                error_message=error_message,
                suppress_connection_error=True
            )
        except httpx.ConnectError:
            logger.warning(
                "[Error] Server became unavailable while updating status. "
                "Job status may not be updated."
            )
        except httpx.HTTPStatusError as status_error:
            # Status update failed (e.g., 422 - invalid transition)
            logger.warning(
                f"[Error] Failed to update job status to 'failed': "
                f"{status_error.response.status_code} - {status_error.response.text}. "
                f"Job may already be in a terminal state."
            )
        except Exception as status_error:
            logger.error(f"[Error] Failed to update job status: {status_error}")
        
        raise httpx.NetworkError(error_message) from e
    
    except httpx.HTTPStatusError as e:
        # HTTP error from API (server is up but returned error)
        error_message = f"API error: {e.response.status_code} - {e.response.text}"
        logger.error(f"[Error] Discovery failed: {error_message}")
        
        try:
            await update_job_status(
                job_id, 
                "failed", 
                error_message=error_message,
                suppress_connection_error=True
            )
        except httpx.ConnectError:
            logger.warning(
                "[Error] Server became unavailable while updating status. "
                "Job status may not be updated."
            )
        except httpx.HTTPStatusError as status_error:
            # Status update failed (e.g., 422 - invalid transition)
            logger.warning(
                f"[Error] Failed to update job status to 'failed': "
                f"{status_error.response.status_code} - {status_error.response.text}. "
                f"Job may already be in a terminal state."
            )
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
            await update_job_status(
                job_id, 
                "failed", 
                error_message=error_message,
                suppress_connection_error=True
            )
        except httpx.ConnectError:
            logger.warning(
                "[Error] Server became unavailable while updating status. "
                "Job status may not be updated."
            )
        except httpx.HTTPStatusError as status_error:
            # Status update failed (e.g., 422 - invalid transition)
            logger.warning(
                f"[Error] Failed to update job status to 'failed': "
                f"{status_error.response.status_code} - {status_error.response.text}. "
                f"Job may already be in a terminal state."
            )
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
