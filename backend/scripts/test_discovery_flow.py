"""
Test script to verify the discovery flow executes all three agents sequentially
and passes data correctly between them.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.run_discovery import run_discovery
from app.core.config import get_settings
from app.db.supabase import get_supabase_client
from app.repositories.job_repo import JobRepository
from app.core.constants import JobStatus
from uuid import uuid4

async def create_test_job():
    """Create a test job for discovery."""
    settings = get_settings()
    db = get_supabase_client()
    repo = JobRepository()
    
    # Create a test job
    job_data = repo.create(
        user_id=str(uuid4()),  # Test user ID
        brand_description="Sustainable fashion brand focused on eco-friendly materials and ethical production. We target conscious consumers who value quality over quantity.",
        reference_profiles=[
            "https://instagram.com/everlane",
            "https://instagram.com/reformation"
        ],
        name="Test Discovery Flow",
        follower_range_min=10000,
        follower_range_max=500000,
        discovery_limit=5  # Small limit for testing
    )
    
    print(f"Created test job: {job_data['id']}")
    print(f"Status: {job_data['status']}")
    return job_data['id']

async def verify_job_status(job_id: str, expected_status: str):
    """Verify job status matches expected."""
    repo = JobRepository()
    job = repo.get_by_id(job_id)
    actual_status = job['status']
    
    if actual_status == expected_status:
        print(f"✓ Job status verified: {actual_status}")
        return True
    else:
        print(f"✗ Job status mismatch. Expected: {expected_status}, Got: {actual_status}")
        return False

async def main():
    """Main test function."""
    print("=" * 80)
    print("Testing Discovery Flow - Sequential Agent Execution")
    print("=" * 80)
    print()
    
    # Create test job
    print("[Step 1] Creating test job...")
    try:
        job_id = await create_test_job()
    except Exception as e:
        print(f"Error creating test job: {e}")
        print("Using provided job ID from command line or default test ID")
        if len(sys.argv) > 1:
            job_id = sys.argv[1]
        else:
            job_id = "11111111-1111-1111-1111-111111111111"
    
    print(f"Job ID: {job_id}")
    print()
    
    # Verify initial status
    print("[Step 2] Verifying initial job status...")
    await verify_job_status(job_id, JobStatus.PENDING.value)
    print()
    
    # Run discovery
    print("[Step 3] Running discovery flow...")
    print("-" * 80)
    try:
        await run_discovery(job_id)
        print("-" * 80)
        print()
        
        # Verify final status
        print("[Step 4] Verifying final job status...")
        await verify_job_status(job_id, JobStatus.COMPLETED.value)
        print()
        
        print("=" * 80)
        print("✓ Discovery flow completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print("-" * 80)
        print()
        print(f"✗ Discovery flow failed: {e}")
        print()
        
        # Check if job status was updated to failed
        try:
            repo = JobRepository()
            job = repo.get_by_id(job_id)
            print(f"Final job status: {job['status']}")
            if job.get('error_message'):
                print(f"Error message: {job['error_message']}")
        except Exception as check_error:
            print(f"Could not check job status: {check_error}")
        
        print("=" * 80)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
