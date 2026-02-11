"""
Run Discovery Agent in-process using brand_dna from DB (same data as orchestration).
Use when the backend server is not running or when you want to avoid HTTP timeouts.
Prints full Discovery results; does not run Scorer.
"""

import asyncio
import json
import sys
import os
from uuid import UUID

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.repositories.brand_repo import BrandRepository
from app.repositories.job_repo import JobRepository
from app.agents.discovery import get_discovery_agent
from app.models.agent import DiscoveryRequest


def get_job_id():
    if len(sys.argv) > 1:
        return sys.argv[1]
    repo = JobRepository()
    jobs = repo.list_all(limit=5)
    if not jobs:
        print("No jobs. Usage: python -m scripts.run_discovery_inprocess <job_id>")
        sys.exit(1)
    return jobs[0]["id"]


async def main():
    job_id = get_job_id()
    print(f"Job ID: {job_id}")
    print("(Running Discovery in-process using brand_dna from DB)")
    print()

    brand_repo = BrandRepository()
    brand_dna = brand_repo.get_by_job_id_optional(job_id)
    if not brand_dna:
        print("ERROR: No brand_dna for this job. Run Brand Analyzer first.")
        sys.exit(1)

    hashtags = brand_dna.get("hashtags") or []
    keywords = brand_dna.get("keywords") or []
    if not hashtags:
        print("ERROR: No hashtags in brand_dna. Discovery requires at least one.")
        sys.exit(1)

    print(f"Using brand_dna: {len(hashtags)} hashtags, {len(keywords)} keywords")
    print("Calling Discovery Agent...")
    print()

    request = DiscoveryRequest(
        job_id=UUID(job_id),
        hashtags=hashtags,
        keywords=keywords,
        limit=50,
    )
    agent = get_discovery_agent()
    response = await agent.run(request)

    # Convert to dict for JSON (Pydantic model)
    out = response.model_dump() if hasattr(response, "model_dump") else response.dict()
    print("=== Full Discovery result ===")
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    print()

    profiles = out.get("profiles") or []
    total = out.get("total_discovered", len(profiles))
    print("=== Summary (for Scorer - not run) ===")
    print(f"  total_discovered: {total}")
    print(f"  profiles returned: {len(profiles)}")
    print(f"  deduplicated: {out.get('deduplicated', 0)}")
    print(f"  filtered_out: {out.get('filtered_out', 0)}")
    if profiles:
        print()
        print("  Discovered profiles (profile_id for Scorer):")
        for i, p in enumerate(profiles[:20], 1):
            pid = p.get("profile_id") or p.get("id") or "N/A"
            username = p.get("username", "N/A")
            followers = p.get("follower_count", p.get("followersCount", "N/A"))
            print(f"    {i}. {username}  profile_id={pid}  followers={followers}")
        if len(profiles) > 20:
            print(f"    ... and {len(profiles) - 20} more")
    print()
    print("Done. Discovery ran in-process. Scorer not executed.")


if __name__ == "__main__":
    asyncio.run(main())
