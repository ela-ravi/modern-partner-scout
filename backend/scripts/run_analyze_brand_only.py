"""
Run only the Brand Analyzer phase through the orchestration layer.

Uses the same flow as run_discovery.py: health check -> status update -> call
POST /api/agent/analyze-brand. Prints the full response so you can verify
hashtags/keywords for the next agent (Discovery).
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.run_discovery import (
    check_server_health,
    update_job_status,
    call_brand_analyzer,
    FASTAPI_BASE_URL,
)
from app.repositories.job_repo import JobRepository

# Optional: find a job if no job_id given
def get_job_id():
    if len(sys.argv) > 1:
        return sys.argv[1]
    repo = JobRepository()
    jobs = repo.list_all(limit=5)
    if not jobs:
        print("No jobs in database. Create a job or pass job_id: python -m scripts.run_analyze_brand_only <job_id>")
        sys.exit(1)
    return jobs[0]["id"]

async def main():
    job_id = get_job_id()
    print(f"Job ID: {job_id}")
    print(f"Backend: {FASTAPI_BASE_URL}")
    print()

    print("[1] Health check...")
    if not await check_server_health():
        print("ERROR: Server not available. Start with: uvicorn app.main:app --port 8001")
        sys.exit(1)
    print("     OK")

    print("[2] Updating job status to 'analyzing'...")
    try:
        await update_job_status(job_id, "analyzing")
        print("     OK")
    except Exception as e:
        print(f"     (skipped: {e})")

    print("[3] Calling Brand Analyzer (POST /api/agent/analyze-brand)...")
    result = await call_brand_analyzer(job_id)
    print("     OK")

    # Full JSON (compact for readability; truncate embedding if present)
    out = dict(result)
    if "embedding_vector" in out and isinstance(out["embedding_vector"], list):
        out["embedding_vector"] = f"[{len(out['embedding_vector'])} floats]"
    print()
    print("=== Full API response (embedding truncated) ===")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print()

    # Summary for next agent (Discovery needs hashtags + keywords)
    hashtags = result.get("hashtags") or []
    keywords = result.get("keywords") or []
    print("=== Summary for next agent (Discovery) ===")
    print(f"  hashtags (count={len(hashtags)}): {hashtags[:15]}{'...' if len(hashtags) > 15 else ''}")
    print(f"  keywords (count={len(keywords)}): {keywords[:15]}{'...' if len(keywords) > 15 else ''}")
    print(f"  visual_themes: {result.get('visual_themes') or []}")
    print(f"  content_pillars: {result.get('content_pillars') or []}")
    print(f"  profiles_analyzed: {result.get('profiles_analyzed', 'N/A')}")
    print(f"  posts_analyzed: {result.get('posts_analyzed', 'N/A')}")
    if not hashtags:
        print()
        print("  WARNING: No hashtags. Discovery Agent requires at least one hashtag.")
    print()
    print("Done. Brand Analyzer ran successfully via orchestration.")

if __name__ == "__main__":
    asyncio.run(main())
