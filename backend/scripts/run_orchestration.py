#!/usr/bin/env python3
"""
PartnerScout AI - Real Orchestration Runner (Python Fallback)

Replaces N8N workflow by calling backend API endpoints directly.
Runs the full 3-phase pipeline: Brand Analysis -> Discovery -> Scoring.

Usage:
    # Make sure backend server is running on port 8001 first
    cd backend
    python -m scripts.run_orchestration
"""

import io
import json
import sys
import time
from datetime import datetime, timezone, timedelta

import httpx
import jwt

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# =============================================================================
# Configuration (reads from .env via hardcoded values for standalone script)
# =============================================================================

BASE_URL = "http://localhost:8001/api"
SERVICE_KEY = "ks-partnerscout-n8n-2026-secure"
JWT_SECRET = "0adc5126-ba10-4b62-ba00-dbb55b6bd01e"
TEST_USER_ID = "13db01c0-19f8-4538-a807-16f5a24b1828"

# Cost-optimized discovery settings
DISCOVERY_LIMIT = 10
MAX_POSTS_PER_PROFILE = 12

# Brand to discover partners for
BRAND_DESCRIPTION = """
EcoLife is a sustainable lifestyle brand focused on eco-friendly products,
zero-waste living, and minimalist design. We target environmentally conscious
millennials and Gen-Z consumers who value quality over quantity.
Our aesthetic is clean, natural, and earth-toned with an emphasis on
organic materials and ethical sourcing.
"""

REFERENCE_PROFILES = [
    "https://instagram.com/patagonia",
    "https://instagram.com/tentree",
]

# Request timeout (agent calls can take a while with Apify)
TIMEOUT = 600  # 10 minutes


# =============================================================================
# Helpers
# =============================================================================

def generate_jwt_token() -> str:
    """Generate a test JWT token for job creation."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": TEST_USER_ID,
        "email": "orchestrator@partnerscout.ai",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def user_headers(token: str) -> dict:
    """Headers for user-authenticated endpoints."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def service_headers() -> dict:
    """Headers for service-authenticated endpoints."""
    return {
        "X-Service-Key": SERVICE_KEY,
        "Content-Type": "application/json",
    }


def print_phase(phase_num: int, title: str):
    print(f"\n{'=' * 70}")
    print(f"  PHASE {phase_num}: {title}")
    print(f"{'=' * 70}")


def print_step(step: str):
    print(f"\n  >> {step}")


def print_result(label: str, value):
    print(f"     {label}: {value}")


def update_job_status(client: httpx.Client, job_id: str, status: str, error_msg: str = None):
    """Update job status via API."""
    payload = {"status": status}
    if error_msg:
        payload["error_message"] = error_msg

    resp = client.patch(
        f"{BASE_URL}/jobs/{job_id}/status",
        json=payload,
        headers=service_headers(),
    )
    if resp.status_code == 200:
        print(f"     Job status -> {status}")
    else:
        print(f"     WARNING: Status update failed ({resp.status_code}): {resp.text[:200]}")


# =============================================================================
# Main Orchestration
# =============================================================================

def run():
    start_time = time.time()

    print("\n" + "=" * 70)
    print("  PARTNERSCOUT AI - REAL ORCHESTRATION")
    print("  Mode: Python Fallback (calling backend API directly)")
    print("=" * 70)
    print(f"  Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  API Base:        {BASE_URL}")
    print(f"  Discovery Limit: {DISCOVERY_LIMIT}")
    print(f"  Posts/Profile:   {MAX_POSTS_PER_PROFILE}")
    print(f"  Reference:       {', '.join(REFERENCE_PROFILES)}")
    print("=" * 70)

    # Generate JWT for job creation
    token = generate_jwt_token()
    print_step("Generated JWT token for authentication")

    client = httpx.Client(timeout=TIMEOUT)

    try:
        # =================================================================
        # Step 1: Create Discovery Job
        # =================================================================
        print_phase(0, "CREATE DISCOVERY JOB")

        job_payload = {
            "brand_description": BRAND_DESCRIPTION.strip(),
            "reference_profiles": REFERENCE_PROFILES,
            "name": "Real Orchestration Test",
            "follower_range_min": 5000,
            "follower_range_max": 500000,
            "discovery_limit": DISCOVERY_LIMIT,
            "min_score_threshold": 50,
        }

        print_step("POST /api/jobs")
        resp = client.post(
            f"{BASE_URL}/jobs",
            json=job_payload,
            headers=user_headers(token),
        )

        if resp.status_code not in (200, 201):
            print(f"  FAILED to create job: {resp.status_code}")
            print(f"  Response: {resp.text[:500]}")
            return

        job = resp.json()
        job_id = job["id"]
        print_result("Job ID", job_id)
        print_result("Status", job["status"])

        # =================================================================
        # Phase 1: Brand Analysis
        # =================================================================
        print_phase(1, "BRAND ANALYSIS")

        update_job_status(client, job_id, "analyzing")

        print_step("POST /api/agent/analyze-brand")
        print(f"     Analyzing reference profiles via Apify + Gemini LLM...")
        print(f"     (This may take 1-3 minutes)")

        phase1_start = time.time()
        resp = client.post(
            f"{BASE_URL}/agent/analyze-brand",
            json={
                "job_id": job_id,
                "max_posts_per_profile": MAX_POSTS_PER_PROFILE,
            },
            headers=service_headers(),
        )

        if resp.status_code != 200:
            error_msg = f"Brand analysis failed: {resp.status_code} - {resp.text[:300]}"
            print(f"  FAILED: {error_msg}")
            update_job_status(client, job_id, "failed", error_msg)
            return

        brand_dna = resp.json()
        phase1_time = time.time() - phase1_start

        hashtags = brand_dna.get("hashtags", [])
        keywords = brand_dna.get("keywords", [])
        themes = brand_dna.get("visual_themes", [])
        pillars = brand_dna.get("content_pillars", [])

        print_result("Duration", f"{phase1_time:.1f}s")
        print_result("Hashtags", ", ".join(hashtags[:8]))
        print_result("Keywords", ", ".join(keywords[:8]))
        print_result("Themes", ", ".join(themes[:5]))
        print_result("Pillars", ", ".join(pillars[:5]))
        print_result("Profiles analyzed", brand_dna.get("profiles_analyzed", "?"))
        print_result("Posts analyzed", brand_dna.get("posts_analyzed", "?"))

        # =================================================================
        # Phase 2: Profile Discovery
        # =================================================================
        print_phase(2, "PROFILE DISCOVERY")

        update_job_status(client, job_id, "discovering")

        # Use hashtags from brand DNA, limit to top 5
        discovery_hashtags = hashtags[:5] if hashtags else ["#sustainable", "#ecofriendly"]

        print_step("POST /api/agent/discover")
        print(f"     Searching hashtags: {', '.join(discovery_hashtags)}")
        print(f"     Fetching profiles via Apify...")
        print(f"     (This may take 2-5 minutes)")

        phase2_start = time.time()
        resp = client.post(
            f"{BASE_URL}/agent/discover",
            json={
                "job_id": job_id,
                "hashtags": discovery_hashtags,
                "keywords": keywords[:5] if keywords else [],
                "limit": DISCOVERY_LIMIT,
                "follower_min": 5000,
                "follower_max": 500000,
            },
            headers=service_headers(),
        )

        if resp.status_code != 200:
            error_msg = f"Discovery failed: {resp.status_code} - {resp.text[:300]}"
            print(f"  FAILED: {error_msg}")
            update_job_status(client, job_id, "failed", error_msg)
            return

        discovery = resp.json()
        phase2_time = time.time() - phase2_start

        profiles = discovery.get("profiles", [])
        total_discovered = discovery.get("total_discovered", len(profiles))
        deduplicated = discovery.get("deduplicated", 0)
        filtered_out = discovery.get("filtered_out", 0)

        print_result("Duration", f"{phase2_time:.1f}s")
        print_result("Profiles discovered", total_discovered)
        print_result("Deduplicated", deduplicated)
        print_result("Filtered out", filtered_out)

        if profiles:
            print(f"\n     Discovered profiles:")
            for i, p in enumerate(profiles):
                username = p.get("username", "unknown")
                followers = p.get("followers_count", 0)
                print(f"       {i+1:>2}. @{username:<25s} {followers:>8,} followers")

        if not profiles:
            print("  WARNING: No profiles discovered. Check Apify credits and hashtags.")
            update_job_status(client, job_id, "completed")
            return

        # =================================================================
        # Phase 3: Profile Scoring
        # =================================================================
        print_phase(3, "PROFILE SCORING")

        update_job_status(client, job_id, "scoring")

        print_step(f"Scoring {len(profiles)} profiles via Gemini LLM...")
        print(f"     {'#':>3}  {'Username':25s}  {'Score':>5}  {'Recommendation'}")
        print(f"     {'-' * 60}")

        phase3_start = time.time()
        scored_profiles = []

        for i, profile in enumerate(profiles):
            profile_id = profile.get("id")
            username = profile.get("username", "unknown")

            if not profile_id:
                print(f"     {i+1:>3}  @{username:<25s}  SKIP  (no profile ID)")
                continue

            resp = client.post(
                f"{BASE_URL}/agent/score",
                json={
                    "profile_id": profile_id,
                    "job_id": job_id,
                },
                headers=service_headers(),
            )

            if resp.status_code == 200:
                score_data = resp.json()
                final_score = score_data.get("final_score", 0)
                recommendation = score_data.get("recommendation", "unknown")
                rec_display = recommendation.replace("_", " ").title()

                icon = "***" if final_score >= 80 else " * " if final_score >= 60 else " . "

                print(f"     {i+1:>3}  @{username:<25s}  {final_score:>3}  {icon} {rec_display}")

                scored_profiles.append({
                    "username": username,
                    "score": final_score,
                    "recommendation": recommendation,
                    "profile_id": profile_id,
                })
            else:
                print(f"     {i+1:>3}  @{username:<25s}  ERR   ({resp.status_code})")

        phase3_time = time.time() - phase3_start

        print(f"\n     Scoring duration: {phase3_time:.1f}s")

        # =================================================================
        # Complete
        # =================================================================
        update_job_status(client, job_id, "completed")

        total_time = time.time() - start_time

        print("\n" + "=" * 70)
        print("  ORCHESTRATION COMPLETE")
        print("=" * 70)
        print(f"  Job ID:            {job_id}")
        print(f"  Status:            completed")
        print(f"  Total time:        {total_time:.1f}s")
        print(f"  Phase 1 (Brand):   {phase1_time:.1f}s")
        print(f"  Phase 2 (Discover):{phase2_time:.1f}s")
        print(f"  Phase 3 (Score):   {phase3_time:.1f}s")
        print(f"  Profiles found:    {total_discovered}")
        print(f"  Profiles scored:   {len(scored_profiles)}")

        if scored_profiles:
            high = [p for p in scored_profiles if p["score"] >= 80]
            recommended = [p for p in scored_profiles if p["score"] >= 50]
            avg_score = sum(p["score"] for p in scored_profiles) / len(scored_profiles)

            print(f"  High score (80+):  {len(high)}")
            print(f"  Recommended (50+): {len(recommended)}")
            print(f"  Average score:     {avg_score:.1f}")

            print(f"\n  TOP MATCHES:")
            for p in sorted(scored_profiles, key=lambda x: x["score"], reverse=True)[:5]:
                rec = p["recommendation"].replace("_", " ").title()
                print(f"    @{p['username']:<25s}  Score: {p['score']:>3}/100  [{rec}]")

        print("=" * 70)
        print(f"\n  View results: GET {BASE_URL}/jobs/{job_id}")
        print()

    except httpx.ConnectError:
        print("\n  ERROR: Cannot connect to backend server!")
        print(f"  Make sure the server is running on {BASE_URL}")
        print("  Run: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001")
    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()


if __name__ == "__main__":
    run()
