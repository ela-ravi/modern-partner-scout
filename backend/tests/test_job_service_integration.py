"""
Integration Tests for STORY-2.3.1: Implement Job Service

These tests validate the JobService with real database connections
and test the full integration with repositories and Supabase.

Mark tests with @pytest.mark.integration to run only when
database is available.

Note: Tests that require creating new jobs will fail if the database
doesn't have auth.users set up (foreign key constraint). These tests
are skipped automatically when this is the case.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone

from app.services.job_service import JobService, get_job_service
from app.repositories import JobRepository, ProfileRepository
from app.core.constants import JobStatus, ProfileStatus
from app.core.exceptions import (
    BusinessError,
    DailyLimitExceededError,
    InvalidStatusTransitionError,
    JobNotFoundError,
)
from app.db import clear_client_cache


# =============================================================================
# Fixtures for Integration Tests
# =============================================================================

@pytest.fixture(scope="function")
def clear_db_cache():
    """Clear the database client cache before each test."""
    clear_client_cache()
    yield
    clear_client_cache()


@pytest.fixture
def job_service_real():
    """Create a JobService with real repository connections."""
    return JobService()


@pytest.fixture
def sample_user_id():
    """
    Get a valid user ID from the seed data.
    
    Note: The seed data uses NULL for user_id because auth.users
    typically need to be set up separately. For read-only tests,
    we can use any UUID.
    """
    return str(uuid4())


@pytest.fixture
def sample_job_id():
    """Get the sample job ID from seed data."""
    return "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "brand_description": "A sustainable eco-friendly fashion brand focused on minimalist designs and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
            "https://instagram.com/patagonia",
        ],
        "name": f"Integration Test Job {uuid4().hex[:8]}",
        "follower_range_min": 10000,
        "follower_range_max": 250000,
        "discovery_limit": 25,
    }


def _skip_if_fk_violation(exc):
    """Check if exception is a foreign key violation and skip test if so."""
    if "foreign key constraint" in str(exc).lower():
        pytest.skip("Test requires auth.users to be set up in database")
    raise exc


# =============================================================================
# Integration Tests: Read Operations (work with seed data)
# =============================================================================

@pytest.mark.integration
class TestJobServiceReadOperations:
    """Integration tests that only read from database (use seed data)."""
    
    def test_get_job_from_seed_data(self, clear_db_cache, job_service_real, sample_job_id):
        """Test reading the seed data job."""
        try:
            job = job_service_real.get_job(sample_job_id)
            assert job is not None
            assert job["id"] == sample_job_id
            assert "brand_description" in job
            assert job["status"] == JobStatus.COMPLETED.value
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")
    
    def test_get_job_with_profiles_from_seed(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test reading seed job with its profiles."""
        try:
            result = job_service_real.get_job_with_profiles(sample_job_id)
            assert result is not None
            assert result["id"] == sample_job_id
            assert "profiles" in result
            # Seed data has 3 profiles
            assert len(result["profiles"]) == 3
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")
    
    def test_get_analytics_from_seed_job(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test getting analytics for seed job."""
        try:
            analytics = job_service_real.get_analytics(sample_job_id)
            assert analytics is not None
            assert analytics["job_id"] == sample_job_id
            # Seed data has 3 profiles discovered
            assert analytics["profiles_discovered"] >= 0
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")
    
    def test_list_jobs_empty_user(self, clear_db_cache, job_service_real):
        """Test listing jobs for a user with no jobs."""
        random_user_id = str(uuid4())
        result = job_service_real.list_user_jobs(user_id=random_user_id)
        
        assert "jobs" in result
        assert result["jobs"] == []
        assert result["total"] == 0


@pytest.mark.integration
class TestJobServiceQuota:
    """Integration tests for quota/limit checking (read-only)."""
    
    def test_get_remaining_daily_quota_new_user(
        self, clear_db_cache, job_service_real
    ):
        """Test getting remaining quota for a new user."""
        new_user_id = str(uuid4())
        result = job_service_real.get_remaining_daily_quota(new_user_id)
        
        assert result["daily_limit"] == 10
        assert result["used_today"] == 0
        assert result["remaining"] == 10
    
    def test_can_create_job_new_user(self, clear_db_cache, job_service_real):
        """Test can_create_job returns True for new user."""
        new_user_id = str(uuid4())
        assert job_service_real.can_create_job(new_user_id) is True
    
    def test_get_active_jobs_empty(self, clear_db_cache, job_service_real):
        """Test getting active jobs for user with none."""
        random_user_id = str(uuid4())
        result = job_service_real.get_active_jobs(random_user_id)
        
        assert result == []


@pytest.mark.integration  
class TestJobServiceErrorHandling:
    """Integration tests for error handling scenarios."""
    
    def test_get_nonexistent_job(self, clear_db_cache, job_service_real):
        """Test getting a job that doesn't exist."""
        fake_id = str(uuid4())
        
        with pytest.raises(JobNotFoundError):
            job_service_real.get_job(fake_id)
    
    def test_delete_nonexistent_job(self, clear_db_cache, job_service_real):
        """Test deleting a job that doesn't exist."""
        fake_id = str(uuid4())
        
        with pytest.raises(JobNotFoundError):
            job_service_real.delete_job(fake_id)
    
    def test_update_status_nonexistent_job(self, clear_db_cache, job_service_real):
        """Test updating status of a job that doesn't exist."""
        fake_id = str(uuid4())
        
        with pytest.raises(JobNotFoundError):
            job_service_real.update_status(fake_id, JobStatus.ANALYZING)
    
    def test_get_analytics_nonexistent_job(self, clear_db_cache, job_service_real):
        """Test getting analytics for nonexistent job."""
        fake_id = str(uuid4())
        
        with pytest.raises(JobNotFoundError):
            job_service_real.get_analytics(fake_id)


@pytest.mark.integration
class TestJobServiceStatusValidation:
    """Integration tests for status transition validation."""
    
    def test_invalid_status_transition_raises_error(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test that invalid status transition raises error."""
        try:
            # The seed job is 'completed', trying to go to 'analyzing' should fail
            job = job_service_real.get_job(sample_job_id)
            
            if job["status"] == JobStatus.COMPLETED.value:
                with pytest.raises(InvalidStatusTransitionError):
                    job_service_real.update_status(
                        sample_job_id, 
                        JobStatus.ANALYZING
                    )
            else:
                pytest.skip("Seed job status not in expected state")
                
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")


@pytest.mark.integration
class TestJobServiceWithProfileFiltering:
    """Integration tests for profile filtering."""
    
    def test_get_job_with_high_score_filter(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test filtering profiles by minimum score."""
        try:
            result = job_service_real.get_job_with_profiles(
                job_id=sample_job_id,
                min_score=80,  # Only high-scoring profiles
            )
            
            # All returned profiles should have score >= 80
            for profile in result["profiles"]:
                if profile.get("final_score"):
                    assert profile["final_score"] >= 80
                    
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")
    
    def test_get_job_with_limit_filter(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test limiting number of profiles returned."""
        try:
            result = job_service_real.get_job_with_profiles(
                job_id=sample_job_id,
                profile_limit=2,  # Only get 2 profiles
            )
            
            # Should have at most 2 profiles
            assert len(result["profiles"]) <= 2
                
        except JobNotFoundError:
            pytest.skip("Seed data not available in database")


# =============================================================================
# Integration Tests: Write Operations (require auth.users)
# 
# These tests will be skipped if the database doesn't have auth.users
# set up with a test user. In a full test environment, you would
# create a test user before running these.
# =============================================================================

@pytest.mark.integration
class TestJobServiceWriteOperations:
    """
    Integration tests that write to database.
    
    These tests require auth.users to be set up and will be skipped
    if foreign key constraints prevent job creation.
    """
    
    def test_create_job_database_integration(
        self, clear_db_cache, job_service_real, sample_user_id, sample_job_data
    ):
        """Test creating a job persists to database."""
        try:
            job = job_service_real.create_job(
                user_id=sample_user_id,
                **sample_job_data,
            )
            
            # Verify it was created
            assert job is not None
            assert job["id"] is not None
            assert job["status"] == JobStatus.PENDING.value
            
            # Clean up
            job_service_real.delete_job(job["id"])
            
        except BusinessError as e:
            _skip_if_fk_violation(e)
    
    def test_update_status_valid_transition(
        self, clear_db_cache, job_service_real, sample_user_id, sample_job_data
    ):
        """Test valid status transition persists."""
        try:
            # Create a pending job
            job = job_service_real.create_job(
                user_id=sample_user_id,
                **sample_job_data,
            )
            assert job["status"] == JobStatus.PENDING.value
            
            # Update to analyzing (valid)
            updated = job_service_real.update_status(
                job["id"],
                JobStatus.ANALYZING,
            )
            assert updated["status"] == JobStatus.ANALYZING.value
            
            # Verify in database
            retrieved = job_service_real.get_job(job["id"])
            assert retrieved["status"] == JobStatus.ANALYZING.value
            
            # Clean up
            job_service_real.delete_job(job["id"])
            
        except BusinessError as e:
            _skip_if_fk_violation(e)
    
    def test_delete_job_removes_from_database(
        self, clear_db_cache, job_service_real, sample_user_id, sample_job_data
    ):
        """Test deleting a job removes it from database."""
        try:
            job = job_service_real.create_job(
                user_id=sample_user_id,
                **sample_job_data,
            )
            job_id = job["id"]
            
            # Delete it
            result = job_service_real.delete_job(job_id)
            assert result["deleted"] is True
            
            # Verify it's gone
            with pytest.raises(JobNotFoundError):
                job_service_real.get_job(job_id)
                
        except BusinessError as e:
            _skip_if_fk_violation(e)
    
    def test_retry_job_resets_status(
        self, clear_db_cache, job_service_real, sample_user_id, sample_job_data
    ):
        """Test retrying a failed job resets its status."""
        try:
            # Create job
            job = job_service_real.create_job(
                user_id=sample_user_id,
                **sample_job_data,
            )
            
            # Progress to analyzing then fail
            job_service_real.update_status(job["id"], JobStatus.ANALYZING)
            job_service_real.update_status(
                job["id"],
                JobStatus.FAILED,
                error_message="Test failure"
            )
            
            # Retry
            retried = job_service_real.retry_job(job["id"], sample_user_id)
            assert retried["status"] == JobStatus.PENDING.value
            
            # Clean up
            job_service_real.delete_job(job["id"])
            
        except BusinessError as e:
            _skip_if_fk_violation(e)


# =============================================================================
# Performance Tests
# =============================================================================

@pytest.mark.integration
class TestJobServicePerformance:
    """Performance tests for JobService."""
    
    def test_list_jobs_performance(self, clear_db_cache, job_service_real):
        """Test listing jobs performance."""
        import time
        
        random_user_id = str(uuid4())
        
        start_time = time.time()
        result = job_service_real.list_user_jobs(user_id=random_user_id, limit=100)
        elapsed = time.time() - start_time
        
        # Should complete quickly (< 5 seconds)
        assert elapsed < 5
        assert "jobs" in result
    
    def test_get_analytics_performance(
        self, clear_db_cache, job_service_real, sample_job_id
    ):
        """Test analytics calculation performance."""
        import time
        
        try:
            start_time = time.time()
            analytics = job_service_real.get_analytics(sample_job_id)
            elapsed = time.time() - start_time
            
            # Should complete quickly (< 5 seconds)
            assert elapsed < 5
            assert analytics is not None
            
        except JobNotFoundError:
            pytest.skip("Seed data not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
