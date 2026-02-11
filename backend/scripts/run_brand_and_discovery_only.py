"""
Run Brand Analyzer then Discovery Agent through the orchestration layer.
Uses Brand Analyzer output (hashtags, keywords) as input to Discovery.
Prints Discovery results and stops before running the Scorer.
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from app.core.config import get_settings
from scripts.run_discovery import (
    check_server_health,
    update_job_status,
    call_brand_analyzer,
    FASTAPI_BASE_URL,
)
from app.repositories.job_repo import JobRepository
from app.repositories.brand_repo import BrandRepository


def get_job_id():
    if len(sys.argv) > 1:
        return sys.argv[1]
    repo = JobRepository()
    jobs = repo.list_all(limit=5)
    if not jobs:
        print("No jobs in database. Pass job_id: python -m scripts.run_brand_and_discovery_only <job_id>")
        sys.exit(1)
    return jobs[0]["id"]


async def main():
    job_id = get_job_id()
    print(f"Job ID: {job_id}")
    print(f"Backend: {FASTAPI_BASE_URL}")
    print()

    # --- Phase 1: Brand Analyzer (get hashtags/keywords for Discovery) ---
    print("[1] Health check...")
    if not await check_server_health():
        print("ERROR: Server not available. Start with: uvicorn app.main:app --port 8001")
        sys.exit(1)
    print("     OK")

    print("[2] Getting hashtags/keywords (from brand_dna or Brand Analyzer)...")
    brand_repo = BrandRepository()
    brand_dna = brand_repo.get_by_job_id_optional(job_id)
    if brand_dna and (brand_dna.get("hashtags") or brand_dna.get("keywords")):
        hashtags = brand_dna.get("hashtags") or []
        keywords = brand_dna.get("keywords") or []
        print(f"     Using existing brand_dna -> {len(hashtags)} hashtags, {len(keywords)} keywords")
    else:
        try:
            await update_job_status(job_id, "analyzing")
        except Exception:
            pass
        brand_result = await call_brand_analyzer(job_id)
        hashtags = brand_result.get("hashtags") or []
        keywords = brand_result.get("keywords") or []
        print(f"     OK (Brand Analyzer) -> {len(hashtags)} hashtags, {len(keywords)} keywords")

    if not hashtags:
        print("ERROR: Discovery requires at least one hashtag. Aborting.")
        sys.exit(1)

    # --- Phase 2: Discovery Agent ---
    print("[3] Updating job status to 'discovering'...")
    try:
        await update_job_status(job_id, "discovering")
        print("     OK")
    except Exception as e:
        print(f"     (skipped: {e})")

    print("[4] Discovery Agent (POST /api/agent/discover) [timeout=600s]...")
    service_key = get_settings().n8n.service_key
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FASTAPI_BASE_URL}/api/agent/discover",
            headers={
                "X-Service-Key": service_key,
                "Content-Type": "application/json",
            },
            json={
                "job_id": job_id,
                "hashtags": hashtags,
                "keywords": keywords,
                "limit": 50,
            },
            timeout=600.0,
        )
        response.raise_for_status()
        discovery_result = response.json()
    print("     OK")

    # --- Output full response and summary ---
    print()
    print("=== Full Discovery API response ===")
    print(json.dumps(discovery_result, indent=2, ensure_ascii=False, default=str))
    print()

    profiles = discovery_result.get("profiles") or []
    total = discovery_result.get("total_discovered", len(profiles))
    dedup = discovery_result.get("deduplicated", 0)
    filtered = discovery_result.get("filtered_out", 0)

    print("=== Summary (for Scorer - not run yet) ===")
    print(f"  total_discovered: {total}")
    print(f"  profiles returned: {len(profiles)}")
    print(f"  deduplicated: {dedup}")
    print(f"  filtered_out: {filtered}")
    if profiles:
        print()
        print("  Discovered profiles (profile_id needed for Scorer):")
        for i, p in enumerate(profiles[:20], 1):
            pid = p.get("profile_id") or p.get("id") or "N/A"
            username = p.get("username", "N/A")
            followers = p.get("follower_count", p.get("followersCount", "N/A"))
            print(f"    {i}. {username}  profile_id={pid}  followers={followers}")
        if len(profiles) > 20:
            print(f"    ... and {len(profiles) - 20} more")
    print()
    print("Done. Discovery ran successfully via orchestration. Scorer not executed.")


if __name__ == "__main__":
    asyncio.run(main())
