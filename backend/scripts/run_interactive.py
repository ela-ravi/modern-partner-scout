"""
Interactive orchestrator wrapper - finds a job and runs with step-by-step approval.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.repositories.job_repo import JobRepository
from scripts.run_discovery_interactive import run_discovery_interactive
from app.core.constants import JobStatus

async def find_and_run_job():
    """Find a pending job and run interactive orchestrator."""
    repo = JobRepository()
    
    # Check if job_id provided as argument
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
        print(f"Using provided job ID: {job_id}")
    else:
        # Find a pending job
        print("Searching for a pending job...")
        jobs = repo.list_all(limit=10)
        
        pending_jobs = [j for j in jobs if j['status'] == JobStatus.PENDING.value]
        
        if pending_jobs:
            job_id = pending_jobs[0]['id']
            print(f"Found pending job: {job_id}")
            print(f"  Name: {pending_jobs[0].get('name', 'N/A')}")
            print(f"  Status: {pending_jobs[0]['status']}")
        else:
            # Use any job
            if jobs:
                job_id = jobs[0]['id']
                print(f"No pending jobs found. Using existing job: {job_id}")
                print(f"  Name: {jobs[0].get('name', 'N/A')}")
                print(f"  Status: {jobs[0]['status']}")
                print(f"  Note: Job status is '{jobs[0]['status']}', not 'pending'")
            else:
                print("Error: No jobs found in database.")
                print("Please create a job first or provide a job_id as argument:")
                print("  python -m scripts.run_interactive <job_id>")
                sys.exit(1)
    
    # Run interactive orchestrator
    await run_discovery_interactive(job_id)

if __name__ == "__main__":
    try:
        asyncio.run(find_and_run_job())
    except KeyboardInterrupt:
        print("\n[Interrupted] Orchestrator cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[Fatal] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
