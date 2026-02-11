"""
Reset a job to pending status and run discovery flow.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.supabase import get_supabase_client
from app.repositories.job_repo import JobRepository
from app.core.constants import JobStatus
import httpx
from app.core.config import get_settings

async def reset_job_status(job_id: str):
    """Reset job status to pending."""
    settings = get_settings()
    FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8001")
    SERVICE_KEY = settings.n8n.service_key
    
    async with httpx.AsyncClient() as client:
        # First, try to set to pending directly
        try:
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
                print(f"✓ Reset job {job_id} to pending status")
                return True
        except Exception as e:
            print(f"Could not reset via API: {e}")
    
    # Fallback: Update directly in database
    try:
        repo = JobRepository()
        repo.update_status(id=job_id, status=JobStatus.PENDING)
        print(f"✓ Reset job {job_id} to pending status (via DB)")
        return True
    except Exception as e:
        print(f"Could not reset via DB: {e}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("Usage: python reset_and_run_discovery.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    
    print(f"Resetting job {job_id} to pending status...")
    await reset_job_status(job_id)
    
    print(f"\nRunning discovery for job {job_id}...")
    from scripts.run_discovery import run_discovery
    await run_discovery(job_id)

if __name__ == "__main__":
    asyncio.run(main())
