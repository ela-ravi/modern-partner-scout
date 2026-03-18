#!/usr/bin/env python3
"""
PartnerScout AI - Mock Orchestration Demo

Demonstrates the full 3-phase orchestration pipeline using mock data.
No external services required (no LLM, no Apify, no Supabase).

Usage:
    python -m scripts.mock_orchestration
"""

import asyncio
import random
import sys
import os
import io
import time
from datetime import datetime
from typing import Any, Dict, List

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.demo_seed import DEMO_BRAND_DESCRIPTION, DEMO_BRAND_DNA, DEMO_PROFILES


# =============================================================================
# Mock Job State
# =============================================================================

class MockJobState:
    """Simulates database state for a discovery job."""

    def __init__(self):
        self.job_id = "mock-0001-aaaa-bbbb-cccc-ddddeeee"
        self.status = "pending"
        self.brand_dna = None
        self.discovered_profiles = []
        self.scored_profiles = []
        self.start_time = None

    def set_status(self, status: str):
        self.status = status
        elapsed = f" [{self._elapsed()}]" if self.start_time else ""
        print(f"  -> Job status: {status}{elapsed}")

    def _elapsed(self) -> str:
        if not self.start_time:
            return "0.0s"
        return f"{time.time() - self.start_time:.1f}s"


# =============================================================================
# Phase 1: Brand Analysis (Mock)
# =============================================================================

async def phase_1_brand_analysis(state: MockJobState) -> Dict[str, Any]:
    """
    Simulate the Brand Analyzer Agent.

    In production, this calls POST /api/agent/analyze-brand which:
    1. Loads reference profiles from the job
    2. Scrapes each profile using Apify
    3. Analyzes visual aesthetics, content themes, engagement patterns
    4. Extracts hashtags, keywords, and generates an embedding vector
    5. Stores the brand DNA in the database
    """
    print("\n" + "=" * 70)
    print("  PHASE 1: BRAND ANALYSIS")
    print("  Agent: BrandAnalyzerAgent")
    print("  API:   POST /api/agent/analyze-brand")
    print("=" * 70)

    state.set_status("analyzing")

    # Simulate LLM processing time
    print("\n  [1/4] Loading reference profiles...")
    await asyncio.sleep(0.5)
    print("        - https://instagram.com/ecolife_brand")
    print("        - https://instagram.com/sustainable_co")

    print("  [2/4] Scraping profile data via Apify...")
    await asyncio.sleep(0.8)
    print("        - Fetched bio, posts, metrics for 2 profiles")

    print("  [3/4] Analyzing brand DNA with LLM (Gemini)...")
    await asyncio.sleep(1.0)

    brand_dna = DEMO_BRAND_DNA.copy()
    brand_dna["embedding_vector"] = [round(random.uniform(-1, 1), 4) for _ in range(10)]

    print("  [4/4] Storing brand DNA in database...")
    await asyncio.sleep(0.3)

    state.brand_dna = brand_dna

    # Display results
    print(f"\n  [OK] Brand Analysis Complete!")
    print(f"    Hashtags:  {', '.join(brand_dna['hashtags'])}")
    print(f"    Keywords:  {', '.join(brand_dna['keywords'])}")
    print(f"    Themes:    {', '.join(brand_dna['visual_themes'])}")
    print(f"    Pillars:   {', '.join(brand_dna['content_pillars'])}")
    print(f"    Audience:  {brand_dna['target_audience_description']}")
    print(f"    Embedding: [{brand_dna['embedding_vector'][0]}, {brand_dna['embedding_vector'][1]}, ... ] (1536 dims)")

    return brand_dna


# =============================================================================
# Phase 2: Profile Discovery (Mock)
# =============================================================================

async def phase_2_discovery(state: MockJobState, brand_dna: Dict) -> List[Dict]:
    """
    Simulate the Discovery Agent.

    In production, this calls POST /api/agent/discover which:
    1. Takes hashtags and keywords from brand DNA
    2. Searches Instagram via Apify hashtag scraper
    3. Fetches full profile data for matching accounts
    4. Deduplicates and filters (follower range, engagement)
    5. Inserts discovered profiles into the database
    """
    print("\n" + "=" * 70)
    print("  PHASE 2: PROFILE DISCOVERY")
    print("  Agent: DiscoveryAgent")
    print("  API:   POST /api/agent/discover")
    print("=" * 70)

    state.set_status("discovering")

    hashtags = brand_dna["hashtags"][:5]

    print(f"\n  [1/4] Searching hashtags: {', '.join(hashtags)}")
    await asyncio.sleep(0.8)
    print(f"        Found 47 posts from #sustainable")
    print(f"        Found 35 posts from #ecofriendly")
    print(f"        Found 28 posts from #minimalist")
    print(f"        Found 22 posts from #zerowaste")
    print(f"        Found 18 posts from #organic")

    print(f"  [2/4] Extracting unique profiles...")
    await asyncio.sleep(0.5)
    print(f"        Extracted 23 unique usernames")

    print(f"  [3/4] Fetching full profile data via Apify...")
    await asyncio.sleep(1.0)

    # Use demo profiles as discovered profiles
    profiles = []
    for i, p in enumerate(DEMO_PROFILES):
        profile = {
            "id": f"profile-{i+1:04d}",
            "username": p["username"],
            "full_name": p["full_name"],
            "bio": p["bio"],
            "followers_count": p["followers_count"],
            "following_count": p["following_count"],
            "posts_count": p["posts_count"],
            "engagement_rate": p["engagement_rate"],
            "is_verified": p["is_verified"],
            "is_business_account": p["is_business_account"],
            "status": "new",
        }
        profiles.append(profile)
        marker = "V" if p["is_verified"] else " "
        biz = "BIZ" if p["is_business_account"] else "   "
        print(f"        [{marker}] @{p['username']:25s} {biz}  {p['followers_count']:>7,} followers  ER: {p['engagement_rate']}%")
        await asyncio.sleep(0.15)

    print(f"  [4/4] Filtering by follower range (5K-500K)...")
    await asyncio.sleep(0.3)
    print(f"        Filtered out: 0 (all within range)")

    state.discovered_profiles = profiles

    print(f"\n  [OK] Discovery Complete!")
    print(f"    Profiles found:    {len(profiles)}")
    print(f"    Business accounts: {sum(1 for p in profiles if p['is_business_account'])}")
    print(f"    Verified:          {sum(1 for p in profiles if p['is_verified'])}")
    print(f"    Avg followers:     {sum(p['followers_count'] for p in profiles) // len(profiles):,}")

    return profiles


# =============================================================================
# Phase 3: Profile Scoring (Mock)
# =============================================================================

async def phase_3_scoring(state: MockJobState, profiles: List[Dict]) -> List[Dict]:
    """
    Simulate the Scorer Agent.

    In production, this calls POST /api/agent/score for each profile which:
    1. Loads the profile data and brand DNA
    2. Evaluates 6 scoring dimensions using LLM
    3. Detects fake/bot accounts
    4. Extracts contact email
    5. Stores scores and contacts in the database

    The orchestrator processes profiles in batches of 5 with 1-second delays.
    """
    print("\n" + "=" * 70)
    print("  PHASE 3: PROFILE SCORING")
    print("  Agent: ScorerAgent")
    print("  API:   POST /api/agent/score (per profile)")
    print("=" * 70)

    state.set_status("scoring")

    total = len(profiles)
    batch_size = 5
    scored = []

    print(f"\n  Scoring {total} profiles in batches of {batch_size}...")
    print(f"  {'=' * 68}")
    print(f"  {'#':>3}  {'Username':25s}  {'Score':>5}  {'Recommendation':16s}  {'Email'}")
    print(f"  {'-' * 68}")

    for i, profile in enumerate(profiles):
        demo = DEMO_PROFILES[i]
        dims = demo["dimension_scores"]

        await asyncio.sleep(0.3)

        profile["status"] = "processing"

        score = demo["score"]
        recommendation = demo["recommendation"]
        email = demo.get("contact_email", "---")

        scored_profile = {
            **profile,
            "final_score": score,
            "recommendation": recommendation,
            "contact_email": email,
            "dimensions": dims,
            "status": "done",
        }
        scored.append(scored_profile)

        if score >= 80:
            icon = "***"
        elif score >= 60:
            icon = " * "
        else:
            icon = " . "

        rec_display = recommendation.replace("_", " ").title()
        email_display = email if email else "---"

        print(f"  {i+1:>3}  @{profile['username']:25s}  {score:>3}  {icon} {rec_display:14s}  {email_display}")

        if (i + 1) % batch_size == 0 and i + 1 < total:
            print(f"  {'':>3}  --- batch complete, 1s cooldown ---")
            await asyncio.sleep(0.5)

    state.scored_profiles = scored

    high_score = [p for p in scored if p["final_score"] >= 80]
    recommended = [p for p in scored if p["final_score"] >= 50]
    with_email = [p for p in scored if p.get("contact_email")]

    print(f"  {'-' * 68}")
    print(f"\n  [OK] Scoring Complete!")
    print(f"    Total scored:       {len(scored)}")
    print(f"    High score (80+):   {len(high_score)}")
    print(f"    Recommended (50+):  {len(recommended)}")
    print(f"    With email:         {len(with_email)}")
    print(f"    Average score:      {sum(p['final_score'] for p in scored) / len(scored):.1f}")

    return scored


# =============================================================================
# Results Summary
# =============================================================================

def print_results_summary(state: MockJobState, scored_profiles: List[Dict]):
    """Print a detailed results summary similar to what the dashboard shows."""

    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY - TOP PARTNER RECOMMENDATIONS")
    print("=" * 70)

    sorted_profiles = sorted(scored_profiles, key=lambda p: p["final_score"], reverse=True)

    for p in sorted_profiles:
        score = p["final_score"]
        dims = p["dimensions"]

        bar_len = score // 5
        bar = "#" * bar_len + "." * (20 - bar_len)

        rec = p["recommendation"]
        if rec == "highly_recommended":
            badge = "[HIGHLY REC]"
        elif rec == "recommended":
            badge = "[RECOMMEND] "
        elif rec == "consider":
            badge = "[CONSIDER]  "
        else:
            badge = "[NOT REC]   "

        verified = " (Verified)" if p["is_verified"] else ""
        email = p.get("contact_email", "")

        print(f"\n  @{p['username']:25s} {badge}  Score: {score}/100{verified}")
        print(f"  [{bar}]  {p['full_name']}")
        print(f"  VIS:{dims['visual_aesthetic_match']:>3}  CNT:{dims['content_theme_alignment']:>3}  ENG:{dims['engagement_rate_score']:>3}  FLW:{dims['follower_quality']:>3}  BIZ:{dims['business_indicators']:>3}  ACT:{dims['activity_recency']:>3}")
        if email:
            print(f"  Contact: {email}")
        print(f"  {'-' * 68}")

    print(f"\n  Scoring Dimensions:")
    print(f"    VIS = Visual Aesthetic Match (15%)")
    print(f"    CNT = Content Theme Alignment (20%)")
    print(f"    ENG = Engagement Rate Score (25%)")
    print(f"    FLW = Follower Quality (15%)")
    print(f"    BIZ = Business Indicators (15%)")
    print(f"    ACT = Activity Recency (10%)")


# =============================================================================
# Main Orchestration
# =============================================================================

async def run_mock_orchestration():
    """Run the complete mock orchestration pipeline."""

    state = MockJobState()
    state.start_time = time.time()

    print("\n" + "=" * 70)
    print("  PARTNERSCOUT AI - ORCHESTRATION PIPELINE")
    print("  Mode: Mock Demo (No external services required)")
    print("=" * 70)
    print(f"  Job ID:    {state.job_id}")
    print(f"  Brand:     EcoLife - Sustainable Lifestyle")
    print(f"  Profiles:  2 reference -> discover -> score")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  LLM:       Gemini (gemini-2.5-flash-lite) [MOCK]")
    print(f"  Scraper:   Apify Instagram [MOCK]")
    print("=" * 70)

    print(f"\n  Brand Description:")
    desc = DEMO_BRAND_DESCRIPTION.strip()
    for line in desc.split("\n"):
        print(f"    {line.strip()}")

    # Phase 1: Brand Analysis
    brand_dna = await phase_1_brand_analysis(state)

    # Phase 2: Profile Discovery
    profiles = await phase_2_discovery(state, brand_dna)

    # Phase 3: Profile Scoring
    scored = await phase_3_scoring(state, profiles)

    # Complete
    state.set_status("completed")
    elapsed = time.time() - state.start_time

    # Results
    print_results_summary(state, scored)

    # Final summary
    print("\n" + "=" * 70)
    print("  ORCHESTRATION COMPLETE")
    print("=" * 70)
    print(f"  Status:          completed")
    print(f"  Total time:      {elapsed:.1f}s")
    print(f"  Profiles found:  {len(profiles)}")
    print(f"  Profiles scored: {len(scored)}")
    print(f"  High matches:    {sum(1 for p in scored if p['final_score'] >= 80)}")
    print(f"  With email:      {sum(1 for p in scored if p.get('contact_email'))}")
    print("=" * 70)

    print(f"\n  In production, this pipeline:")
    print(f"    1. N8N webhook triggers at POST /webhook/start-discovery")
    print(f"    2. Brand Analyzer calls POST /api/agent/analyze-brand")
    print(f"    3. Discovery Agent calls POST /api/agent/discover")
    print(f"    4. Scorer Agent calls POST /api/agent/score (per profile)")
    print(f"    5. Status updates via PATCH /api/jobs/{{job_id}}/status")
    print(f"    6. Frontend polls for real-time updates")
    print(f"    7. Dashboard shows profiles as they are scored")
    print()


if __name__ == "__main__":
    asyncio.run(run_mock_orchestration())
