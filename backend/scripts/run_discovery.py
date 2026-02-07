"""
Python Fallback Orchestrator for PartnerScout AI.

This script manages the end-to-end partner discovery workflow:
1. Brand Analysis (Extracts DNA)
2. Discovery (Finds profiles)
3. Scoring (Evaluates profiles)

Usage:
    cd backend
    python -m scripts.run_discovery <job_id>
"""

import asyncio
import sys
import os
import httpx
import json
from typing import Optional, Dict, Any, List

# Configuration
FASTAPI_BASE_URL = os.getenv("API_URL", "http://localhost:8001")
SERVICE_KEY = os.getenv("N8N_SERVICE_KEY", "ks-partnerscout-n8n-2026-secure")

# =============================================================================
# Status Update Functions
# =============================================================================

async def update_job_status(
    job_id: str, 
    status: str, 
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update job status via API.
    Calls: PATCH /api/jobs/{job_id}/status
    """
    async with httpx.AsyncClient() as client:
        payload = {"status": status}
        if error_message:
            payload["error_message"] = error_message
        
        try:
            response = await client.patch(
                f"{FASTAPI_BASE_URL}/api/jobs/{job_id}/status",
                headers={
                    "X-Service-Key": SERVICE_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"[Error] API Status Error: {e.response.text}")
            raise
        except Exception as e:
            print(f"[Error] Connection Error updating job status: {str(e)}")
            raise

async def update_profile_status(profile_id: str, status: str) -> Dict[str, Any]:
    """
    Update profile status via API.
    Calls: PATCH /api/profiles/{profile_id}/status
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{FASTAPI_BASE_URL}/api/profiles/{profile_id}/status",
                headers={
                    "X-Service-Key": SERVICE_KEY,
                    "Content-Type": "application/json"
                },
                json={"status": status},
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log but don't crash whole workflow for one profile status update
            print(f"[Warning] Failed to update profile {profile_id} status to {status}: {str(e)}")
            return {}

# =============================================================================
# Agent Call Functions
# =============================================================================

async def call_brand_analyzer(job_id: str) -> Dict[str, Any]:
    """
    Call Brand Analyzer Agent API.
    Calls: POST /api/agent/analyze-brand
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FASTAPI_BASE_URL}/api/agent/analyze-brand",
            headers={
                "X-Service-Key": SERVICE_KEY,
                "Content-Type": "application/json"
            },
            json={"job_id": job_id},
            timeout=120.0
        )
        response.raise_for_status()
        return response.json()

async def call_discovery_agent(
    job_id: str, 
    hashtags: List[str], 
    keywords: List[str],
    limit: int = 50
) -> Dict[str, Any]:
    """
    Call Discovery Agent API.
    Calls: POST /api/agent/discover
    """
    async with httpx.AsyncClient() as client:
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
            timeout=300.0
        )
        response.raise_for_status()
        return response.json()

async def call_scorer_agent(profile_id: str, job_id: str) -> Dict[str, Any]:
    """
    Call Scorer Agent API.
    Calls: POST /api/agent/score
    """
    async with httpx.AsyncClient() as client:
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
            timeout=120.0
        )
        response.raise_for_status()
        return response.json()

# =============================================================================
# Main Orchestration Logic
# =============================================================================

async def run_discovery(job_id: str) -> None:
    """
    Main orchestration function.
    Executes the full discovery pipeline.
    """
    print(f"\n[Orchestrator] Starting partner discovery for job: {job_id}")
    print(f"[Config] API: {FASTAPI_BASE_URL}")
    
    try:
        # 1. ANALYZE BRAND
        print("\n[Phase 1] Analyzing brand DNA...")
        await update_job_status(job_id, "analyzing")
        
        # Call Brand Analyzer
        brand_result = await call_brand_analyzer(job_id)
        
        # Handle different response structures if necessary, but assuming exact API spec
        # The API can return flattened keys or nested 'brand_dna'. 
        # API Response Example in PRD: {"hashtags": [...], "keywords": [...], ...} (flattened)
        # But docs method `call_brand_analyzer` used `brand_result["brand_dna"]`.
        # Let's check the API response example in USER REQUEST.
        # User Request says: 
        # Response: { "job_id": "...", "hashtags": [...], "keywords": [...], ... }
        # So it is flattened, NOT inside 'brand_dna' key.
        # I will use the flattened response structure.
        
        hashtags = brand_result.get("hashtags", [])
        keywords = brand_result.get("keywords", [])
        
        print(f"[Phase 1] Success! Extracted {len(hashtags)} hashtags, {len(keywords)} keywords")
        
        # 2. DISCOVER PROFILES
        print("\n[Phase 2] Discovering profiles via Instagram...")
        await update_job_status(job_id, "discovering")
        
        print(f"[Phase 2] Debug: Calling discovery with {len(hashtags)} hashtags and {len(keywords)} keywords")
        
        discovery_result = await call_discovery_agent(
            job_id=job_id,
            hashtags=hashtags,
            keywords=keywords,
            limit=50
        )
        
        profiles = discovery_result.get("profiles", [])
        print(f"[Phase 2] Success! Discovered {len(profiles)} profiles")
        
        if not profiles:
            print("[Warning] No profiles found. Proceeding to completion sequence.")
            # Must transition through 'scoring' even if empty to satisfy state machine
            await update_job_status(job_id, "scoring")
            await update_job_status(job_id, "completed")
            print("Job marked as COMPLETED (0 profiles).")
            return

        # 3. SCORE PROFILES
        print("\n[Phase 3] Scoring profiles...")
        await update_job_status(job_id, "scoring")
        
        scored_count = 0
        high_score_count = 0
        
        for i, profile in enumerate(profiles):
            profile_id = profile.get("id")
            username = profile.get("username", "unknown")
            
            if not profile_id:
                continue
                
            print(f"[{i+1}/{len(profiles)}] Scoring @{username}...")
            
            # Set to processing
            await update_profile_status(profile_id, "processing")
            
            try:
                # Call Scorer
                score_result = await call_scorer_agent(profile_id, job_id)
                final_score = score_result.get("final_score", 0) # API example says "final_score" or "score"
                # API Example in Request: "final_score": 74
                # Docs example: "score": 92. 
                # I'll check both just in case.
                final_score = score_result.get("final_score", score_result.get("score", 0))
                
                print(f"   -> Score: {final_score}/100")
                
                if final_score >= 50:
                    high_score_count += 1
                scored_count += 1
                
                # Set to done
                await update_profile_status(profile_id, "done")
                
            except Exception as e:
                print(f"   -> Failed to score: {e}")
                # We don't fail the job if one profile fails, just mark it? 
                # Maybe mark as skipped or error? 'skipped' is a valid status.
                await update_profile_status(profile_id, "skipped")
            
            # Rate limiting to be safe (avoid overwhelming local server or ext APIs if they don't handle it)
            await asyncio.sleep(1) 
            
        # 4. COMPLETION
        print(f"\n[Complete] Scored {scored_count} profiles. {high_score_count} high potential (>50).")
        await update_job_status(job_id, "completed")
        print("Job marked as COMPLETED.")

    except Exception as e:
        error_msg = str(e)
        print(f"\n[CRITICAL ERROR] Workflow failed: {error_msg}")
        try:
            # Try to update job status to failed
            # Ensure error_message is passed clearly
            print(f"[Error Handler] Attempting to set job status to 'failed' with message...")
            result = await update_job_status(job_id, "failed", error_message=error_msg)
            print(f"[Error Handler] Job successfully marked as FAILED. Response: {result}")
        except Exception as status_error:
            print(f"[CRITICAL] Could not update job status to failed. Error: {str(status_error)}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_discovery <job_id>")
        sys.exit(1)
        
    job_id = sys.argv[1]
    
    # Simple validation
    if len(job_id) < 30:
        print("Error: Invalid Job ID format")
        sys.exit(1)
        
    # Run async loop
    try:
        asyncio.run(run_discovery(job_id))
    except KeyboardInterrupt:
        print("\n[Aborted] Operation cancelled by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()
