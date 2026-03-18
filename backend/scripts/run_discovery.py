#!/usr/bin/env python3
"""
PartnerScout AI - Python Orchestrator (Fallback)

Incrementally orchestrates the discovery workflow, calling each agent via HTTP APIs.
Currently supports: Brand Analyzer (Phase 1), Discovery Agent (Phase 2), Scorer Agent (Phase 3)

Usage:
    python -m scripts.run_discovery <job_id>
    python -m scripts.run_discovery <job_id> --phase analyze-only
    python -m scripts.run_discovery <job_id> --phase discover-only
    python -m scripts.run_discovery <job_id> --phase score-only
    python -m scripts.run_discovery <job_id> --phase full
    
Example:
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40 --phase full

Phases:
    analyze-only  : Run only Brand Analyzer (Phase 1)
    discover-only : Run Brand Analyzer + Discovery (Phase 1-2)
    score-only    : Run only Scorer Agent (Phase 3) - assumes profiles exist
    full          : Run complete workflow (Phase 1-3)
"""

import argparse
import asyncio
import sys
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = f"http://localhost:{settings.api_port}"
SERVICE_KEY = settings.n8n.service_key
REQUEST_TIMEOUT = 300  # seconds (agents can take time, discovery can be 3-5 min)


# =============================================================================
# HTTP Client
# =============================================================================

def get_headers() -> Dict[str, str]:
    """Get headers for API requests."""
    return {
        "X-Service-Key": SERVICE_KEY,
        "Content-Type": "application/json",
    }


async def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """
    Make an API request to the FastAPI backend.
    
    Args:
        method: HTTP method (GET, POST, PATCH, etc.)
        endpoint: API endpoint (e.g., /api/jobs/123/status)
        data: Request body data
        timeout: Request timeout in seconds
        
    Returns:
        Response JSON data
        
    Raises:
        Exception: If request fails
    """
    url = f"{API_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=get_headers(),
            json=data,
        )
        
        if response.status_code >= 400:
            error_detail = response.json() if response.text else {"error": response.text}
            raise Exception(f"API Error {response.status_code}: {error_detail}")
        
        return response.json() if response.text else {}


# =============================================================================
# Status Update Functions (Section 2 of Orchestration.md)
# =============================================================================

async def update_job_status(
    job_id: str,
    status: str,
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update job status via Status API.
    
    Args:
        job_id: Job UUID
        status: New status (pending, analyzing, discovering, scoring, completed, failed)
        error_message: Error details (only for failed status)
        
    Returns:
        Updated job data
    """
    print(f"  → Updating job status to '{status}'...")
    
    payload = {"status": status}
    if error_message:
        payload["error_message"] = error_message
    
    result = await api_request(
        method="PATCH",
        endpoint=f"/api/jobs/{job_id}/status",
        data=payload,
    )
    
    print(f"  ✓ Job status updated to '{status}'")
    return result


# =============================================================================
# Agent Call Functions
# =============================================================================

async def call_brand_analyzer(job_id: str) -> Dict[str, Any]:
    """
    Call the Brand Analyzer Agent API.
    
    Args:
        job_id: Job UUID to analyze
        
    Returns:
        Brand analysis result with hashtags, keywords, etc.
    """
    print(f"  → Calling Brand Analyzer Agent...")
    start_time = datetime.now()
    
    result = await api_request(
        method="POST",
        endpoint="/api/agent/analyze-brand",
        data={"job_id": job_id},
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log results
    hashtags = result.get("hashtags", [])
    keywords = result.get("keywords", [])
    profiles_analyzed = result.get("profiles_analyzed", 0)
    
    print(f"  ✓ Brand analysis completed in {duration:.1f}s")
    print(f"    - Hashtags: {len(hashtags)}")
    print(f"    - Keywords: {len(keywords)}")
    print(f"    - Profiles analyzed: {profiles_analyzed}")
    
    return result


async def call_discovery_agent(
    job_id: str,
    hashtags: list,
    keywords: list,
    limit: int = 50,
    follower_min: int = 5000,
    follower_max: int = 500000
) -> Dict[str, Any]:
    """
    Call the Discovery Agent API.
    
    Args:
        job_id: Job UUID
        hashtags: List of hashtags to search (from brand analysis)
        keywords: List of keywords to filter by
        limit: Maximum profiles to discover
        follower_min: Minimum follower count
        follower_max: Maximum follower count
        
    Returns:
        Discovery result with profiles list
    """
    print(f"  → Calling Discovery Agent...")
    print(f"    - Hashtags: {len(hashtags)} (using top 5)")
    print(f"    - Keywords: {len(keywords)}")
    print(f"    - Limit: {limit}")
    start_time = datetime.now()
    
    # Use top 5 hashtags to avoid rate limits
    top_hashtags = hashtags[:5] if len(hashtags) > 5 else hashtags
    
    result = await api_request(
        method="POST",
        endpoint="/api/agent/discover",
        data={
            "job_id": job_id,
            "hashtags": top_hashtags,
            "keywords": keywords[:10] if len(keywords) > 10 else keywords,
            "limit": limit,
            "follower_min": follower_min,
            "follower_max": follower_max,
        },
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log results
    profiles = result.get("profiles", [])
    filtered_out = result.get("filtered_out", 0)
    
    print(f"  ✓ Discovery completed in {duration:.1f}s")
    print(f"    - Profiles found: {len(profiles)}")
    print(f"    - Filtered out: {filtered_out}")
    
    return result


async def call_scorer_agent(job_id: str, profile_id: str) -> Dict[str, Any]:
    """
    Call the Scorer Agent API.
    
    Args:
        job_id: Job UUID
        profile_id: Profile UUID to score
        
    Returns:
        Scoring result with final_score, recommendation, reasoning, etc.
    """
    result = await api_request(
        method="POST",
        endpoint="/api/agent/score",
        data={
            "job_id": job_id,
            "profile_id": profile_id,
        },
    )
    
    return result


async def get_profiles_for_scoring(job_id: str) -> list:
    """
    Get discovered profiles that need scoring.
    
    Args:
        job_id: Job UUID
        
    Returns:
        List of profiles with id, username, status
    """
    from app.db.supabase import get_supabase_admin_client
    
    db = get_supabase_admin_client()
    
    # Get profiles with status 'new' (not yet scored)
    response = db.table("discovered_profiles").select(
        "id,username,status"
    ).eq("job_id", job_id).eq("status", "new").execute()
    
    return response.data or []


# =============================================================================
# Orchestration Phases
# =============================================================================

async def run_phase_1_analyze(job_id: str) -> Dict[str, Any]:
    """
    Phase 1: Brand Analysis
    
    Updates job status to 'analyzing' and calls Brand Analyzer Agent.
    
    Args:
        job_id: Job UUID
        
    Returns:
        Brand analysis result
    """
    print("\n" + "=" * 60)
    print("PHASE 1: Brand Analysis")
    print("=" * 60)
    
    # Update status to analyzing
    await update_job_status(job_id, "analyzing")
    
    # Call Brand Analyzer Agent
    result = await call_brand_analyzer(job_id)
    
    print("\n✓ Phase 1 Complete!")
    return result


async def run_phase_2_discover(job_id: str, brand_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 2: Profile Discovery
    
    Uses brand DNA to discover similar profiles.
    
    Args:
        job_id: Job UUID
        brand_result: Result from Phase 1 (brand analysis)
        
    Returns:
        Discovery result with profiles
    """
    print("\n" + "=" * 60)
    print("PHASE 2: Profile Discovery")
    print("=" * 60)
    
    # Update status to discovering
    await update_job_status(job_id, "discovering")
    
    # Call Discovery Agent with brand DNA
    result = await call_discovery_agent(
        job_id=job_id,
        hashtags=brand_result.get("hashtags", []),
        keywords=brand_result.get("keywords", []),
        limit=50
    )
    
    print(f"\n✓ Phase 2 Complete! Discovered {len(result.get('profiles', []))} profiles")
    return result


async def run_phase_3_score(job_id: str) -> Dict[str, Any]:
    """
    Phase 3: Profile Scoring
    
    Scores each discovered profile against brand DNA.
    
    Args:
        job_id: Job UUID
        
    Returns:
        Summary of scoring results
    """
    print("\n" + "=" * 60)
    print("PHASE 3: Profile Scoring")
    print("=" * 60)
    
    # Update status to scoring
    await update_job_status(job_id, "scoring")
    
    # Get profiles that need scoring
    profiles = await get_profiles_for_scoring(job_id)
    total = len(profiles)
    
    print(f"  → Found {total} profiles to score")
    
    if total == 0:
        print("  ⚠ No profiles found for scoring")
        return {"scored": 0, "skipped": 0, "failed": 0, "results": []}
    
    scored = 0
    skipped = 0
    failed = 0
    results = []
    
    for i, profile in enumerate(profiles, 1):
        username = profile.get("username", "unknown")
        profile_id = profile["id"]
        
        print(f"  [{i}/{total}] Scoring @{username}...", end=" ", flush=True)
        
        try:
            result = await call_scorer_agent(job_id, profile_id)
            final_score = result.get("final_score", 0)
            recommendation = result.get("recommendation", "unknown")
            
            results.append({
                "profile_id": profile_id,
                "username": username,
                "score": final_score,
                "recommendation": recommendation,
            })
            
            # Visual indicator based on score
            if final_score >= 70:
                indicator = "✓"
            elif final_score >= 50:
                indicator = "○"
            else:
                indicator = "·"
            
            print(f"{indicator} Score: {final_score} ({recommendation})")
            scored += 1
            
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"✗ Failed: {error_msg}")
            failed += 1
    
    # Summary
    print(f"\n  ✓ Scoring complete:")
    print(f"    - Scored: {scored}")
    print(f"    - Failed: {failed}")
    
    if results:
        # Show top 5 recommendations
        top_5 = sorted(results, key=lambda x: x["score"], reverse=True)[:5]
        print(f"\n  Top 5 Recommendations:")
        for r in top_5:
            print(f"    @{r['username']}: {r['score']} ({r['recommendation']})")
    
    return {
        "scored": scored,
        "skipped": skipped,
        "failed": failed,
        "results": results,
    }


# =============================================================================
# Main Orchestration Function
# =============================================================================

async def run_discovery(job_id: str, phase: str = "analyze-only") -> None:
    """
    Main orchestration function.
    
    Supports:
    - analyze-only: Run Phase 1 (Brand Analysis) only
    - discover-only: Phase 1 + 2
    - score-only: Phase 3 only (assumes profiles exist)
    - full: Phase 1 + 2 + 3
    
    Args:
        job_id: Job UUID to process
        phase: Which phases to run
    """
    print("\n" + "=" * 60)
    print("PARTNERSCOUT AI - PYTHON ORCHESTRATOR")
    print("=" * 60)
    print(f"Job ID: {job_id}")
    print(f"Phase:  {phase}")
    print(f"API:    {API_BASE_URL}")
    print("=" * 60)
    
    try:
        # Score-only phase: Skip to Phase 3 directly
        if phase == "score-only":
            scoring_result = await run_phase_3_score(job_id)
            
            # Mark job as completed
            await update_job_status(job_id, "completed")
            
            print("\n" + "=" * 60)
            print("ORCHESTRATION COMPLETE (score-only)")
            print("=" * 60)
            print(f"Profiles scored: {scoring_result.get('scored', 0)}")
            print(f"Profiles failed: {scoring_result.get('failed', 0)}")
            return
        
        # Phase 1: Brand Analysis (IMPLEMENTED)
        brand_result = await run_phase_1_analyze(job_id)
        
        if phase == "analyze-only":
            # Stop here - we're only testing brand analysis
            print("\n" + "=" * 60)
            print("ORCHESTRATION COMPLETE (analyze-only)")
            print("=" * 60)
            print("Note: Job status remains 'analyzing'")
            print("      Run with --phase discover-only or --phase full for more")
            return
        
        # Phase 2: Profile Discovery (IMPLEMENTED)
        if phase in ["discover-only", "full"]:
            discovery_result = await run_phase_2_discover(job_id, brand_result)
            
            if phase == "discover-only":
                print("\n" + "=" * 60)
                print("ORCHESTRATION COMPLETE (discover-only)")
                print("=" * 60)
                print("Note: Job status is 'discovering'")
                print("      Run with --phase full to score profiles")
                return
            
            # Phase 3: Profile Scoring (IMPLEMENTED)
            scoring_result = await run_phase_3_score(job_id)
            
            # Mark job as completed
            await update_job_status(job_id, "completed")
            
            print("\n" + "=" * 60)
            print("ORCHESTRATION COMPLETE (full)")
            print("=" * 60)
            print(f"Profiles analyzed: {brand_result.get('profiles_analyzed', 0)}")
            print(f"Profiles discovered: {len(discovery_result.get('profiles', []))}")
            print(f"Profiles scored: {scoring_result.get('scored', 0)}")
        
    except Exception as e:
        error_msg = str(e) if str(e) else type(e).__name__
        print(f"\n❌ ERROR: {error_msg}")
        
        try:
            await update_job_status(job_id, "failed", error_message=error_msg)
            print("  → Job status set to 'failed'")
        except Exception as status_error:
            print(f"  → Failed to update job status: {status_error}")
        
        raise


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PartnerScout AI - Python Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run brand analysis only
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40

    # Run discovery (Phase 1 + 2)
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40 --phase discover-only
    
    # Run scoring only (Phase 3, assumes profiles exist)
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40 --phase score-only
    
    # Run full workflow (Phase 1 + 2 + 3)
    python -m scripts.run_discovery ab322126-7df1-4400-8012-ea9e586aba40 --phase full
        """
    )
    
    parser.add_argument(
        "job_id",
        help="Job UUID to process"
    )
    
    parser.add_argument(
        "--phase",
        choices=["analyze-only", "discover-only", "score-only", "full"],
        default="analyze-only",
        help="Which phases to run (default: analyze-only)"
    )
    
    args = parser.parse_args()
    
    # Validate UUID format
    job_id = args.job_id
    if len(job_id) != 36 or job_id.count('-') != 4:
        print(f"Error: Invalid job_id format: {job_id}")
        print("Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        sys.exit(1)
    
    # Run the orchestrator
    try:
        asyncio.run(run_discovery(job_id, args.phase))
        print("\n✓ Orchestration completed successfully!")
    except Exception as e:
        print(f"\n✗ Orchestration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
