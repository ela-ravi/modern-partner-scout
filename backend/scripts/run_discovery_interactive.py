"""
Interactive Python Fallback Orchestrator with Step-by-Step Approval

This script runs the discovery workflow but pauses after each agent execution
to show results and wait for user approval before proceeding to the next step.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.run_discovery import (
    check_server_health,
    update_job_status,
    call_brand_analyzer,
    call_discovery_agent,
    call_scorer_agent,
    FASTAPI_BASE_URL,
    SERVICE_KEY
)
from app.core.config import get_settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_section(title: str, char: str = "="):
    """Print a formatted section header."""
    print("\n" + char * 80)
    print(f"  {title}")
    print(char * 80 + "\n")


def print_json(data: Dict[str, Any], title: str = "Result"):
    """Pretty print JSON data."""
    print(f"\n{title}:")
    print("-" * 80)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("-" * 80)


def wait_for_approval(phase_name: str) -> bool:
    """Wait for user approval before proceeding."""
    print_section(f"Phase Complete: {phase_name}", "=")
    response = input("\n[APPROVAL] Do you want to proceed to the next phase? (yes/no/y/n): ").strip().lower()
    return response in ['yes', 'y']


async def run_discovery_interactive(job_id: str) -> None:
    """
    Run discovery workflow with interactive approval at each step.
    
    Args:
        job_id: UUID of the discovery job to process
    """
    print_section("Python Fallback Orchestrator - Interactive Mode", "=")
    print(f"Job ID: {job_id}")
    print(f"Backend URL: {FASTAPI_BASE_URL}")
    print()
    
    try:
        # Health check
        print_section("Step 0: Server Health Check", "-")
        if not await check_server_health():
            raise ConnectionError("Server health check failed")
        print("[OK] Server is healthy")
        
        # =====================================================================
        # Phase 1: Brand Analysis
        # =====================================================================
        print_section("Phase 1: Brand Analyzer", "=")
        logger.info("[Phase 1] Starting Brand Analyzer...")
        
        await update_job_status(job_id, "analyzing")
        print("[OK] Job status updated to 'analyzing'")
        
        print("\n[Calling Brand Analyzer API...]")
        brand_result = await call_brand_analyzer(job_id)
        
        print_section("Brand Analyzer Results", "-")
        print_json(brand_result, "Full Brand Analyzer Response")
        
        # Extract key information
        hashtags = brand_result.get("hashtags", [])
        keywords = brand_result.get("keywords", [])
        brand_dna_id = brand_result.get("brand_dna_id")
        
        print("\n[SUMMARY]")
        print(f"  - Brand DNA ID: {brand_dna_id}")
        print(f"  - Hashtags extracted: {len(hashtags)}")
        if hashtags:
            print(f"    * {', '.join(hashtags[:10])}{'...' if len(hashtags) > 10 else ''}")
        else:
            print("    * [WARNING] No hashtags found!")
        print(f"  - Keywords extracted: {len(keywords)}")
        if keywords:
            print(f"    * {', '.join(keywords[:10])}{'...' if len(keywords) > 10 else ''}")
        
        # Check if hashtags are available
        if not hashtags:
            print("\n[WARNING] Discovery Agent requires at least one hashtag!")
            print("   The Discovery Agent will fail if no hashtags are provided.")
        
        # Wait for approval
        if not wait_for_approval("Brand Analyzer"):
            print("\n[STOPPED] User chose not to proceed. Exiting.")
            return
        
        # =====================================================================
        # Phase 2: Profile Discovery
        # =====================================================================
        print_section("Phase 2: Discovery Agent", "=")
        
        if not hashtags:
            error_msg = (
                "Discovery Agent requires at least one hashtag, but Brand Analyzer "
                f"extracted 0 hashtags. Keywords found: {keywords[:5]}{'...' if len(keywords) > 5 else ''}. "
                "Cannot proceed with profile discovery."
            )
            logger.error(f"[Phase 2] [ERROR] {error_msg}")
            await update_job_status(job_id, "failed", error_message=error_msg)
            raise ValueError(error_msg)
        
        logger.info("[Phase 2] Starting Discovery Agent...")
        await update_job_status(job_id, "discovering")
        print("[OK] Job status updated to 'discovering'")
        
        print(f"\n[Calling Discovery Agent API...]")
        print(f"  • Hashtags: {hashtags[:5]}{'...' if len(hashtags) > 5 else ''}")
        print(f"  • Keywords: {keywords[:5]}{'...' if len(keywords) > 5 else ''}")
        print(f"  • Limit: 50")
        
        discovery_result = await call_discovery_agent(
            job_id=job_id,
            hashtags=hashtags,
            keywords=keywords,
            limit=50
        )
        
        print_section("Discovery Agent Results", "-")
        print_json(discovery_result, "Full Discovery Agent Response")
        
        # Extract profiles
        profiles = discovery_result.get("profiles", [])
        total_discovered = discovery_result.get("total_discovered", len(profiles))
        deduplicated = discovery_result.get("deduplicated", 0)
        filtered_out = discovery_result.get("filtered_out", 0)
        
        print("\n[SUMMARY]")
        print(f"  - Total profiles discovered: {total_discovered}")
        print(f"  - Profiles returned: {len(profiles)}")
        print(f"  - Deduplicated: {deduplicated}")
        print(f"  - Filtered out: {filtered_out}")
        
        if profiles:
            print(f"\n[SAMPLE PROFILES] (first 3):")
            for i, profile in enumerate(profiles[:3], 1):
                print(f"\n  Profile {i}:")
                print(f"    * Username: {profile.get('username', 'N/A')}")
                print(f"    * Profile ID: {profile.get('profile_id', 'N/A')}")
                print(f"    * Followers: {profile.get('follower_count', 'N/A'):,}" if profile.get('follower_count') else "    * Followers: N/A")
                print(f"    * Bio: {profile.get('bio', 'N/A')[:80]}...")
        
        if not profiles:
            print("\n[WARNING] No profiles discovered!")
            print("   The workflow will complete without scoring.")
        
        # Wait for approval
        if not wait_for_approval("Discovery Agent"):
            print("\n[STOPPED] User chose not to proceed. Exiting.")
            return
        
        # =====================================================================
        # Phase 3: Profile Scoring
        # =====================================================================
        if not profiles:
            print_section("Phase 3: Skipped (No Profiles)", "=")
            print("No profiles to score. Completing job...")
            await update_job_status(job_id, "completed")
            logger.info(f"[Complete] Discovery job {job_id} completed (no profiles)")
            return
        
        print_section("Phase 3: Scorer Agent", "=")
        logger.info("[Phase 3] Starting Scorer Agent...")
        await update_job_status(job_id, "scoring")
        print("[OK] Job status updated to 'scoring'")
        
        print(f"\n[Scoring {len(profiles)} profiles...]")
        
        scored_profiles = []
        failed_profiles = []
        
        for idx, profile in enumerate(profiles, 1):
            profile_id = profile.get("profile_id") or profile.get("id")
            username = profile.get("username", "unknown")
            
            if not profile_id:
                logger.warning(f"[Phase 3] Skipping profile {idx}: No profile_id found")
                failed_profiles.append({"profile": profile, "error": "No profile_id"})
                continue
            
            print(f"\n  [{idx}/{len(profiles)}] Scoring profile: {username} (ID: {profile_id})")
            
            try:
                score_result = await call_scorer_agent(profile_id, job_id)
                
                print(f"    [OK] Score calculated successfully")
                
                # Extract score details
                score_data = score_result.get("score", {})
                overall_score = score_data.get("overall_score", 0)
                dimension_scores = score_data.get("dimension_scores", {})
                
                print(f"    * Overall Score: {overall_score:.2f}/100")
                if dimension_scores:
                    print(f"    * Dimension Scores:")
                    for dim, score in dimension_scores.items():
                        print(f"      - {dim}: {score:.2f}")
                
                scored_profiles.append({
                    "profile": profile,
                    "score_result": score_result
                })
                
            except Exception as e:
                logger.error(f"[Phase 3] Failed to score profile {username}: {e}")
                failed_profiles.append({"profile": profile, "error": str(e)})
                print(f"    [ERROR] Failed: {e}")
        
        print_section("Scorer Agent Results", "-")
        print(f"\n[SUMMARY]")
        print(f"  - Profiles scored successfully: {len(scored_profiles)}")
        print(f"  - Profiles failed: {len(failed_profiles)}")
        
        if scored_profiles:
            print(f"\n[SCORED PROFILES]")
            for item in scored_profiles[:5]:  # Show first 5
                profile = item["profile"]
                score_result = item["score_result"]
                score_data = score_result.get("score", {})
                overall_score = score_data.get("overall_score", 0)
                username = profile.get("username", "unknown")
                print(f"\n  - {username}:")
                print(f"    * Overall Score: {overall_score:.2f}/100")
                print(f"    * Profile ID: {profile.get('profile_id', 'N/A')}")
        
        if failed_profiles:
            print(f"\n[FAILED PROFILES]")
            for item in failed_profiles:
                profile = item["profile"]
                username = profile.get("username", "unknown")
                print(f"  - {username}: {item['error']}")
        
        # Wait for approval (optional - just to show final results)
        print_section("All Phases Complete", "=")
        print("[SUCCESS] Discovery workflow completed successfully!")
        print(f"  - Brand analyzed: [OK]")
        print(f"  - Profiles discovered: {len(profiles)}")
        print(f"  - Profiles scored: {len(scored_profiles)}")
        
        await update_job_status(job_id, "completed")
        logger.info(f"[Complete] Discovery job {job_id} completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n[Interrupted] Discovery cancelled by user")
        await update_job_status(job_id, "failed", error_message="Cancelled by user")
        raise
    except Exception as e:
        logger.error(f"[Fatal] Discovery failed: {e}")
        error_message = str(e)
        try:
            await update_job_status(job_id, "failed", error_message=error_message)
        except Exception as update_error:
            logger.warning(f"Failed to update job status: {update_error}")
        raise


def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.run_discovery_interactive <job_id>")
        print("Example: python -m scripts.run_discovery_interactive 11111111-1111-1111-1111-111111111111")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    # Validate UUID format (basic check)
    if len(job_id) != 36 or job_id.count('-') != 4:
        print(f"Error: Invalid job_id format: {job_id}")
        print("Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        sys.exit(1)
    
    # Run the async orchestrator
    try:
        asyncio.run(run_discovery_interactive(job_id))
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\n[Interrupted] Discovery cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"[Fatal] Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
