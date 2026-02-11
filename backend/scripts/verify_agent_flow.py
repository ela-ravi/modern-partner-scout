"""
Comprehensive test to verify all three agents execute sequentially
and pass results correctly between them.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.run_discovery import (
    run_discovery,
    call_brand_analyzer,
    call_discovery_agent,
    call_scorer_agent,
    update_job_status,
    update_profile_status
)
from app.db.supabase import get_supabase_client
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository
from app.core.constants import JobStatus, ProfileStatus
from uuid import uuid4
import httpx
from app.core.config import get_settings

class FlowVerifier:
    """Verifies the sequential execution and data flow between agents."""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.verification_results = {
            "phase1_brand_analyzer": {},
            "phase2_discovery_agent": {},
            "phase3_scorer_agent": {},
            "data_flow": {}
        }
        self.errors = []
    
    async def verify_phase1_brand_analyzer(self):
        """Verify Brand Analyzer executes and returns data."""
        print("\n" + "="*80)
        print("PHASE 1: Brand Analyzer Agent")
        print("="*80)
        
        try:
            # Call Brand Analyzer
            print("[Step 1.1] Calling Brand Analyzer Agent...")
            brand_result = await call_brand_analyzer(self.job_id)
            
            # Extract brand DNA
            if "brand_dna" in brand_result:
                brand_dna = brand_result["brand_dna"]
            else:
                brand_dna = brand_result
            
            hashtags = brand_dna.get("hashtags", [])
            keywords = brand_dna.get("keywords", [])
            
            print(f"[Step 1.2] [SUCCESS] Brand Analyzer completed")
            print(f"  - Hashtags extracted: {len(hashtags)}")
            print(f"  - Keywords extracted: {len(keywords)}")
            print(f"  - Sample hashtags: {hashtags[:3]}")
            print(f"  - Sample keywords: {keywords[:3]}")
            
            # Store for next phase
            self.verification_results["phase1_brand_analyzer"] = {
                "status": "success",
                "hashtags": hashtags,
                "keywords": keywords,
                "hashtag_count": len(hashtags),
                "keyword_count": len(keywords)
            }
            
            self.verification_results["data_flow"]["brand_to_discovery"] = {
                "hashtags": hashtags,
                "keywords": keywords
            }
            
            return hashtags, keywords
            
        except Exception as e:
            print(f"[Step 1.2] [FAILED] Brand Analyzer failed: {e}")
            self.verification_results["phase1_brand_analyzer"]["status"] = "failed"
            self.verification_results["phase1_brand_analyzer"]["error"] = str(e)
            self.errors.append(f"Phase 1 failed: {e}")
            raise
    
    async def verify_phase2_discovery_agent(self, hashtags: list, keywords: list):
        """Verify Discovery Agent receives data from Brand Analyzer and discovers profiles."""
        print("\n" + "="*80)
        print("PHASE 2: Discovery Agent")
        print("="*80)
        
        try:
            # Verify data received from Phase 1
            print(f"[Step 2.1] Verifying data received from Brand Analyzer...")
            print(f"  - Received {len(hashtags)} hashtags: {hashtags[:3]}...")
            print(f"  - Received {len(keywords)} keywords: {keywords[:3]}...")
            
            if not hashtags or not keywords:
                raise ValueError("Missing hashtags or keywords from Brand Analyzer")
            
            print(f"[Step 2.2] [SUCCESS] Data verification passed")
            
            # Call Discovery Agent with data from Phase 1
            print(f"[Step 2.3] Calling Discovery Agent with Phase 1 data...")
            discovery_result = await call_discovery_agent(
                job_id=self.job_id,
                hashtags=hashtags,
                keywords=keywords,
                limit=5  # Small limit for testing
            )
            
            profiles = discovery_result.get("profiles", [])
            total_discovered = discovery_result.get("total_discovered", len(profiles))
            
            print(f"[Step 2.4] [SUCCESS] Discovery Agent completed")
            print(f"  - Profiles discovered: {total_discovered}")
            print(f"  - Profiles returned: {len(profiles)}")
            if profiles:
                print(f"  - Sample profiles: {[p.get('username', 'unknown') for p in profiles[:3]]}")
            
            # Store for next phase
            self.verification_results["phase2_discovery_agent"] = {
                "status": "success",
                "profiles": profiles,
                "total_discovered": total_discovered,
                "profile_count": len(profiles)
            }
            
            self.verification_results["data_flow"]["discovery_to_scorer"] = {
                "profiles": [{"id": p.get("id"), "username": p.get("username")} for p in profiles]
            }
            
            return profiles
            
        except Exception as e:
            print(f"[Step 2.4] [FAILED] Discovery Agent failed: {e}")
            self.verification_results["phase2_discovery_agent"]["status"] = "failed"
            self.verification_results["phase2_discovery_agent"]["error"] = str(e)
            self.errors.append(f"Phase 2 failed: {e}")
            raise
    
    async def verify_phase3_scorer_agent(self, profiles: list):
        """Verify Scorer Agent receives profiles from Discovery Agent."""
        print("\n" + "="*80)
        print("PHASE 3: Scorer Agent")
        print("="*80)
        
        if not profiles:
            print("[Step 3.1] ⚠ No profiles to score")
            return
        
        scored_count = 0
        scores = []
        
        try:
            print(f"[Step 3.1] Verifying data received from Discovery Agent...")
            print(f"  - Received {len(profiles)} profiles to score")
            print(f"  - Profile IDs: {[p.get('id', 'unknown')[:8] + '...' for p in profiles[:3]]}")
            
            # Score first 2 profiles (for testing)
            test_profiles = profiles[:2]
            print(f"[Step 3.2] Scoring {len(test_profiles)} profiles...")
            
            for i, profile in enumerate(test_profiles, 1):
                profile_id = profile.get("id")
                username = profile.get("username", "unknown")
                
                if not profile_id:
                    print(f"  [WARNING] Profile {i} missing ID, skipping")
                    continue
                
                print(f"\n[Step 3.3.{i}] Scoring profile @{username} (ID: {profile_id[:8]}...)")
                
                # Update profile status
                await update_profile_status(profile_id, "processing")
                
                # Call Scorer Agent
                score_result = await call_scorer_agent(profile_id, self.job_id)
                
                # Extract score
                score = score_result.get("score") or score_result.get("final_score", 0)
                recommendation = score_result.get("recommendation", "N/A")
                
                print(f"  [SUCCESS] Profile @{username} scored: {score}")
                print(f"    - Recommendation: {recommendation}")
                
                # Update profile status
                await update_profile_status(profile_id, "done")
                
                scored_count += 1
                scores.append({
                    "profile_id": profile_id,
                    "username": username,
                    "score": score,
                    "recommendation": recommendation
                })
            
            print(f"\n[Step 3.4] [SUCCESS] Scorer Agent completed")
            print(f"  - Profiles scored: {scored_count}/{len(test_profiles)}")
            print(f"  - Average score: {sum(s['score'] for s in scores) / len(scores) if scores else 0:.1f}")
            
            # Store results
            self.verification_results["phase3_scorer_agent"] = {
                "status": "success",
                "scored_count": scored_count,
                "scores": scores
            }
            
        except Exception as e:
            print(f"[Step 3.4] [FAILED] Scorer Agent failed: {e}")
            self.verification_results["phase3_scorer_agent"]["status"] = "failed"
            self.verification_results["phase3_scorer_agent"]["error"] = str(e)
            self.errors.append(f"Phase 3 failed: {e}")
            raise
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY")
        print("="*80)
        
        # Phase 1
        p1 = self.verification_results["phase1_brand_analyzer"]
        status1 = "[PASS]" if p1.get("status") == "success" else "[FAIL]"
        print(f"\nPhase 1 - Brand Analyzer: {status1}")
        if p1.get("status") == "success":
            print(f"  - Hashtags: {p1.get('hashtag_count', 0)}")
            print(f"  - Keywords: {p1.get('keyword_count', 0)}")
        
        # Phase 2
        p2 = self.verification_results["phase2_discovery_agent"]
        status2 = "[PASS]" if p2.get("status") == "success" else "[FAIL]"
        print(f"\nPhase 2 - Discovery Agent: {status2}")
        if p2.get("status") == "success":
            print(f"  - Profiles discovered: {p2.get('profile_count', 0)}")
        
        # Phase 3
        p3 = self.verification_results["phase3_scorer_agent"]
        status3 = "[PASS]" if p3.get("status") == "success" else "[FAIL]"
        print(f"\nPhase 3 - Scorer Agent: {status3}")
        if p3.get("status") == "success":
            print(f"  - Profiles scored: {p3.get('scored_count', 0)}")
        
        # Data Flow
        print(f"\nData Flow Verification:")
        df = self.verification_results["data_flow"]
        if "brand_to_discovery" in df:
            bd = df["brand_to_discovery"]
            print(f"  [PASS] Brand Analyzer → Discovery Agent:")
            print(f"    - Hashtags passed: {len(bd.get('hashtags', []))}")
            print(f"    - Keywords passed: {len(bd.get('keywords', []))}")
        
        if "discovery_to_scorer" in df:
            ds = df["discovery_to_scorer"]
            print(f"  [PASS] Discovery Agent -> Scorer Agent:")
            print(f"    - Profiles passed: {len(ds.get('profiles', []))}")
        
        # Overall
        all_passed = (
            p1.get("status") == "success" and
            p2.get("status") == "success" and
            p3.get("status") == "success"
        )
        
        print(f"\n{'='*80}")
        if all_passed:
            print("[SUCCESS] ALL PHASES PASSED - Sequential execution verified!")
        else:
            print("[FAILED] SOME PHASES FAILED - Check errors above")
        print(f"{'='*80}")
        
        return all_passed

async def reset_job_to_pending(job_id: str):
    """Reset job status to pending."""
    settings = get_settings()
    FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")
    SERVICE_KEY = settings.n8n.service_key
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{FASTAPI_BASE_URL}/api/jobs/{job_id}/status",
                headers={
                    "X-Service-Key": SERVICE_KEY,
                    "Content-Type": "application/json"
                },
                json={"status": "pending"},
                timeout=30.0
            )
            if response.status_code == 200:
                print(f"[SUCCESS] Reset job {job_id} to pending status")
                return True
    except Exception as e:
        print(f"[WARNING] Could not reset via API: {e}")
    
    # Try direct DB update
    try:
        repo = JobRepository()
        repo.update_status(id=job_id, status=JobStatus.PENDING)
        print(f"[SUCCESS] Reset job {job_id} to pending status (via DB)")
        return True
    except Exception as e:
        print(f"[WARNING] Could not reset via DB: {e}")
        return False

async def main():
    """Main test function."""
    print("="*80)
    print("AGENT FLOW VERIFICATION TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Get job ID
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        job_id = "11111111-1111-1111-1111-111111111111"
    
    print(f"\nJob ID: {job_id}")
    
    # Reset job to pending
    print("\n[Setup] Resetting job to pending status...")
    await reset_job_to_pending(job_id)
    
    # Create verifier
    verifier = FlowVerifier(job_id)
    
    try:
        # Update job status to analyzing
        await update_job_status(job_id, "analyzing")
        
        # Phase 1: Brand Analyzer
        hashtags, keywords = await verifier.verify_phase1_brand_analyzer()
        
        # Update job status to discovering
        await update_job_status(job_id, "discovering")
        
        # Phase 2: Discovery Agent
        profiles = await verifier.verify_phase2_discovery_agent(hashtags, keywords)
        
        # Update job status to scoring
        await update_job_status(job_id, "scoring")
        
        # Phase 3: Scorer Agent
        await verifier.verify_phase3_scorer_agent(profiles)
        
        # Update job status to completed
        await update_job_status(job_id, "completed")
        
        # Print summary
        all_passed = verifier.print_summary()
        
        if all_passed:
            print("\n[SUCCESS] VERIFICATION COMPLETE - All agents executed sequentially!")
            return 0
        else:
            print("\n[FAILED] VERIFICATION FAILED - Some phases did not complete")
            return 1
            
    except Exception as e:
        print(f"\n[FAILED] VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to update job status to failed
        try:
            await update_job_status(job_id, "failed", error_message=str(e))
        except:
            pass
        
        verifier.print_summary()
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
