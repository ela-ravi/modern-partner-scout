"""
Tests for STORY-2.3.1: Implement Job Service

These tests validate that the JobService implements all required
business logic correctly, including daily limit enforcement,
status transitions, and N8N webhook integration.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
import httpx

from app.services.job_service import JobService, get_job_service
from app.core.constants import JobStatus, ProfileStatus
from app.core.exceptions import (
    BusinessError,
    DailyLimitExceededError,
    InvalidStatusTransitionError,
    JobNotFoundError,
    JobNotStartableError,
    JobAlreadyCompletedError,
    N8NError,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_job_repo():
    """Create a mock JobRepository."""
    return Mock()


@pytest.fixture
def mock_profile_repo():
    """Create a mock ProfileRepository."""
    return Mock()


@pytest.fixture
def job_service(mock_job_repo, mock_profile_repo):
    """Create a JobService with mocked repositories."""
    return JobService(
        job_repo=mock_job_repo,
        profile_repo=mock_profile_repo,
    )


@pytest.fixture
def sample_job():
    """Create a sample job dictionary."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "Test Job",
        "brand_description": "A sustainable fashion brand",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": JobStatus.PENDING.value,
        "profiles_discovered": 0,
        "profiles_scored": 0,
        "error_message": None,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_profiles():
    """Create sample profile data."""
    return [
        {
            "id": str(uuid4()),
            "job_id": str(uuid4()),
            "username": "profile1",
            "followers_count": 50000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 85,
            "contact_email": "profile1@example.com",
        },
        {
            "id": str(uuid4()),
            "job_id": str(uuid4()),
            "username": "profile2",
            "followers_count": 75000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 72,
            "contact_email": None,
        },
        {
            "id": str(uuid4()),
            "job_id": str(uuid4()),
            "username": "profile3",
            "followers_count": 30000,
            "status": ProfileStatus.NEW.value,
            "final_score": None,
            "contact_email": None,
        },
    ]


# =============================================================================
# Test: create_job() - Daily Limit Enforcement
# =============================================================================

class TestCreateJob:
    """Tests for the create_job method."""
    
    def test_create_job_success(self, job_service, mock_job_repo, sample_job):
        """Test successful job creation when under daily limit."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 0
        mock_job_repo.create.return_value = sample_job
        
        result = job_service.create_job(
            user_id=user_id,
            brand_description="Test brand",
            reference_profiles=["url1", "url2"],
        )
        
        assert result == sample_job
        mock_job_repo.count_user_jobs_today.assert_called_once_with(user_id)
        mock_job_repo.create.assert_called_once()
    
    def test_create_job_with_optional_fields(self, job_service, mock_job_repo, sample_job):
        """Test job creation with all optional fields."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 0
        mock_job_repo.create.return_value = sample_job
        
        result = job_service.create_job(
            user_id=user_id,
            brand_description="Test brand",
            reference_profiles=["url1", "url2"],
            name="My Discovery",
            follower_range_min=10000,
            follower_range_max=100000,
            discovery_limit=25,
        )
        
        mock_job_repo.create.assert_called_once_with(
            user_id=user_id,
            brand_description="Test brand",
            reference_profiles=["url1", "url2"],
            name="My Discovery",
            follower_range_min=10000,
            follower_range_max=100000,
            discovery_limit=25,
            keywords=[],
            hashtags=[],
            min_score_threshold=50,
        )
    
    def test_create_job_daily_limit_exceeded(self, job_service, mock_job_repo):
        """Test that daily limit is enforced."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 10  # At limit
        
        with pytest.raises(DailyLimitExceededError) as exc_info:
            job_service.create_job(
                user_id=user_id,
                brand_description="Test brand",
                reference_profiles=["url1", "url2"],
            )
        
        assert exc_info.value.code == "DAILY_LIMIT_EXCEEDED"
        assert "10" in str(exc_info.value.message)
        mock_job_repo.create.assert_not_called()
    
    def test_create_job_at_limit_minus_one(self, job_service, mock_job_repo, sample_job):
        """Test job creation when at limit-1 (should succeed)."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 9  # One below limit
        mock_job_repo.create.return_value = sample_job
        
        result = job_service.create_job(
            user_id=user_id,
            brand_description="Test brand",
            reference_profiles=["url1", "url2"],
        )
        
        assert result == sample_job
        mock_job_repo.create.assert_called_once()
    
    def test_create_job_repo_error(self, job_service, mock_job_repo):
        """Test handling of repository errors during creation."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 0
        mock_job_repo.create.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessError) as exc_info:
            job_service.create_job(
                user_id=user_id,
                brand_description="Test brand",
                reference_profiles=["url1", "url2"],
            )
        
        assert "Failed to create discovery job" in str(exc_info.value.message)


# =============================================================================
# Test: list_user_jobs()
# =============================================================================

class TestListUserJobs:
    """Tests for the list_user_jobs method."""
    
    def test_list_user_jobs_success(self, job_service, mock_job_repo, sample_job):
        """Test listing jobs for a user."""
        user_id = str(uuid4())
        mock_job_repo.list_by_user.return_value = [sample_job]
        
        result = job_service.list_user_jobs(user_id=user_id)
        
        assert "jobs" in result
        assert result["jobs"] == [sample_job]
        assert result["total"] == 1
        mock_job_repo.list_by_user.assert_called_once_with(
            user_id=user_id,
            status=None,
            limit=50,
            offset=0,
        )
    
    def test_list_user_jobs_with_filters(self, job_service, mock_job_repo):
        """Test listing jobs with status filter."""
        user_id = str(uuid4())
        mock_job_repo.list_by_user.return_value = []
        
        result = job_service.list_user_jobs(
            user_id=user_id,
            status="completed",
            limit=10,
            offset=5,
        )
        
        mock_job_repo.list_by_user.assert_called_once_with(
            user_id=user_id,
            status="completed",
            limit=10,
            offset=5,
        )
    
    def test_list_user_jobs_empty(self, job_service, mock_job_repo):
        """Test listing jobs when user has none."""
        user_id = str(uuid4())
        mock_job_repo.list_by_user.return_value = []
        
        result = job_service.list_user_jobs(user_id=user_id)
        
        assert result["jobs"] == []
        assert result["total"] == 0


# =============================================================================
# Test: get_job_with_profiles()
# =============================================================================

class TestGetJobWithProfiles:
    """Tests for the get_job_with_profiles method."""
    
    def test_get_job_with_profiles_success(
        self, job_service, mock_job_repo, mock_profile_repo, sample_job, sample_profiles
    ):
        """Test getting a job with its profiles."""
        job_id = sample_job["id"]
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.get_with_brand_dna.return_value = {**sample_job, "brand_dna": None}
        mock_profile_repo.list_by_job_with_scores.return_value = sample_profiles
        
        result = job_service.get_job_with_profiles(job_id=job_id)
        
        assert result["id"] == job_id
        assert result["profiles"] == sample_profiles
        assert "brand_dna" in result
    
    def test_get_job_with_profiles_with_filters(
        self, job_service, mock_job_repo, mock_profile_repo, sample_job
    ):
        """Test getting a job with profile filters."""
        job_id = sample_job["id"]
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.get_with_brand_dna.return_value = sample_job
        mock_profile_repo.list_by_job_with_scores.return_value = []
        
        result = job_service.get_job_with_profiles(
            job_id=job_id,
            min_score=80,
            profile_status="scored",
            profile_limit=10,
            profile_offset=5,
        )
        
        mock_profile_repo.list_by_job_with_scores.assert_called_once_with(
            job_id=job_id,
            min_score=80,
            status="scored",
            limit=10,
            offset=5,
        )
    
    def test_get_job_with_profiles_not_found(self, job_service, mock_job_repo):
        """Test error when job is not found."""
        mock_job_repo.get_by_id.side_effect = JobNotFoundError("test-id")
        
        with pytest.raises(JobNotFoundError):
            job_service.get_job_with_profiles(job_id="test-id")


# =============================================================================
# Test: update_status()
# =============================================================================

class TestUpdateStatus:
    """Tests for the update_status method."""
    
    def test_update_status_valid_transition(self, job_service, mock_job_repo, sample_job):
        """Test valid status transition."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.update_status.return_value = {
            **sample_job,
            "status": JobStatus.ANALYZING.value,
        }
        
        result = job_service.update_status(
            job_id=job_id,
            new_status=JobStatus.ANALYZING,
        )
        
        assert result["status"] == JobStatus.ANALYZING.value
        mock_job_repo.update_status.assert_called_once()
    
    def test_update_status_invalid_transition(self, job_service, mock_job_repo, sample_job):
        """Test invalid status transition raises error."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job
        
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            job_service.update_status(
                job_id=job_id,
                new_status=JobStatus.COMPLETED,  # Can't go directly from pending to completed
            )
        
        assert exc_info.value.code == "INVALID_TRANSITION"
        mock_job_repo.update_status.assert_not_called()
    
    def test_update_status_skip_validation(self, job_service, mock_job_repo, sample_job):
        """Test status update with validation skipped."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.update_status.return_value = {
            **sample_job,
            "status": JobStatus.COMPLETED.value,
        }
        
        result = job_service.update_status(
            job_id=job_id,
            new_status=JobStatus.COMPLETED,
            validate_transition=False,
        )
        
        assert result["status"] == JobStatus.COMPLETED.value
    
    def test_update_status_with_error_message(self, job_service, mock_job_repo, sample_job):
        """Test status update with error message."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.ANALYZING.value
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.update_status.return_value = {
            **sample_job,
            "status": JobStatus.FAILED.value,
            "error_message": "LLM timeout",
        }
        
        result = job_service.update_status(
            job_id=job_id,
            new_status=JobStatus.FAILED,
            error_message="LLM timeout",
        )
        
        mock_job_repo.update_status.assert_called_once_with(
            id=job_id,
            status=JobStatus.FAILED,
            error_message="LLM timeout",
        )
    
    @pytest.mark.parametrize("from_status,to_status,should_succeed", [
        (JobStatus.PENDING, JobStatus.ANALYZING, True),
        (JobStatus.PENDING, JobStatus.CANCELLED, True),
        (JobStatus.ANALYZING, JobStatus.DISCOVERING, True),
        (JobStatus.ANALYZING, JobStatus.FAILED, True),
        (JobStatus.DISCOVERING, JobStatus.SCORING, True),
        (JobStatus.SCORING, JobStatus.COMPLETED, True),
        (JobStatus.FAILED, JobStatus.PENDING, True),  # Retry
        (JobStatus.PENDING, JobStatus.COMPLETED, False),
        (JobStatus.PENDING, JobStatus.SCORING, False),
        (JobStatus.COMPLETED, JobStatus.PENDING, False),
        (JobStatus.CANCELLED, JobStatus.PENDING, False),
    ])
    def test_status_transition_matrix(
        self, job_service, mock_job_repo, sample_job, from_status, to_status, should_succeed
    ):
        """Test all valid and invalid status transitions."""
        job_id = sample_job["id"]
        sample_job["status"] = from_status.value
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.update_status.return_value = {**sample_job, "status": to_status.value}
        
        if should_succeed:
            result = job_service.update_status(job_id=job_id, new_status=to_status)
            assert result is not None
        else:
            with pytest.raises(InvalidStatusTransitionError):
                job_service.update_status(job_id=job_id, new_status=to_status)


# =============================================================================
# Test: trigger_discovery()
# =============================================================================

class TestTriggerDiscovery:
    """Tests for the trigger_discovery method."""
    
    @patch("app.services.job_service.httpx.Client")
    def test_trigger_discovery_success(
        self, mock_httpx_client, job_service, mock_job_repo, sample_job
    ):
        """Test successful discovery trigger."""
        job_id = sample_job["id"]
        user_id = sample_job["user_id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job
        
        # Mock httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'
        mock_response.json.return_value = {"status": "ok"}
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_httpx_client.return_value = mock_client_instance
        
        result = job_service.trigger_discovery(job_id=job_id, user_id=user_id)
        
        assert result["status"] == "accepted"
        assert result["job_id"] == job_id
        mock_client_instance.post.assert_called_once()
    
    def test_trigger_discovery_not_startable(self, job_service, mock_job_repo, sample_job):
        """Test error when job is not in startable status."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.ANALYZING.value  # Not startable
        mock_job_repo.get_by_id.return_value = sample_job
        
        with pytest.raises(JobNotStartableError) as exc_info:
            job_service.trigger_discovery(job_id=job_id, user_id="user-123")
        
        assert exc_info.value.code == "JOB_NOT_STARTABLE"
        assert "analyzing" in str(exc_info.value.message).lower()
    
    @patch("app.services.job_service.httpx.Client")
    def test_trigger_discovery_webhook_error(
        self, mock_httpx_client, job_service, mock_job_repo, sample_job
    ):
        """Test error when N8N webhook fails."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job
        
        # Mock httpx error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_httpx_client.return_value = mock_client_instance
        
        result = job_service.trigger_discovery(job_id=job_id, user_id="user-123")

        # N8N failure now falls back to internal orchestration instead of raising
        assert result is not None

    @patch("app.services.job_service.httpx.Client")
    def test_trigger_discovery_network_error(
        self, mock_httpx_client, job_service, mock_job_repo, sample_job
    ):
        """Test network error falls back to internal orchestration."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.PENDING.value
        mock_job_repo.get_by_id.return_value = sample_job

        mock_client_instance = MagicMock()
        mock_client_instance.post.side_effect = httpx.RequestError("Connection refused")
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_httpx_client.return_value = mock_client_instance

        # N8N failure now falls back to internal orchestration instead of raising
        result = job_service.trigger_discovery(job_id=job_id, user_id="user-123")
        assert result is not None


# =============================================================================
# Test: retry_job()
# =============================================================================

class TestRetryJob:
    """Tests for the retry_job method."""
    
    def test_retry_job_success(self, job_service, mock_job_repo, sample_job):
        """Test successful job retry."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.FAILED.value
        sample_job["error_message"] = "Previous error"
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.update_status.return_value = {
            **sample_job,
            "status": JobStatus.PENDING.value,
            "error_message": None,
        }
        
        result = job_service.retry_job(job_id=job_id, user_id="user-123")
        
        assert result["status"] == JobStatus.PENDING.value
        mock_job_repo.update_status.assert_called_once()
    
    def test_retry_job_not_retryable(self, job_service, mock_job_repo, sample_job):
        """Test error when job is not in retryable status."""
        job_id = sample_job["id"]
        sample_job["status"] = JobStatus.COMPLETED.value  # Not retryable
        mock_job_repo.get_by_id.return_value = sample_job
        
        with pytest.raises(BusinessError) as exc_info:
            job_service.retry_job(job_id=job_id, user_id="user-123")
        
        assert "cannot be retried" in str(exc_info.value.message).lower()


# =============================================================================
# Test: delete_job()
# =============================================================================

class TestDeleteJob:
    """Tests for the delete_job method."""
    
    def test_delete_job_success(self, job_service, mock_job_repo, sample_job):
        """Test successful job deletion."""
        job_id = sample_job["id"]
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.delete_job.return_value = True
        
        result = job_service.delete_job(job_id=job_id)
        
        assert result["deleted"] is True
        assert result["job_id"] == job_id
        mock_job_repo.delete_job.assert_called_once_with(job_id)
    
    def test_delete_job_not_found(self, job_service, mock_job_repo):
        """Test error when job is not found."""
        mock_job_repo.get_by_id.side_effect = JobNotFoundError("test-id")
        
        with pytest.raises(JobNotFoundError):
            job_service.delete_job(job_id="test-id")


# =============================================================================
# Test: get_analytics()
# =============================================================================

class TestGetAnalytics:
    """Tests for the get_analytics method."""
    
    def test_get_analytics_with_summary_view(
        self, job_service, mock_job_repo, sample_job
    ):
        """Test analytics using summary view."""
        job_id = sample_job["id"]
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.get_job_summary.return_value = {
            "total_profiles": 50,
            "scored_profiles": 45,
            "new_profiles": 2,
            "processing_profiles": 3,
            "done_profiles": 45,
            "skipped_profiles": 0,
            "avg_score": 72.5,
            "max_score": 95,
            "min_score": 45,
            "profiles_with_email": 30,
            "high_score_count": 12,
        }
        
        result = job_service.get_analytics(job_id=job_id)
        
        assert result["job_id"] == job_id
        assert result["total_profiles"] == 50
        assert result["avg_score"] == 72.5
        assert result["profiles_with_email"] == 30
    
    def test_get_analytics_fallback_calculation(
        self, job_service, mock_job_repo, mock_profile_repo, sample_job, sample_profiles
    ):
        """Test analytics with fallback calculation when view not available."""
        job_id = sample_job["id"]
        mock_job_repo.get_by_id.return_value = sample_job
        mock_job_repo.get_job_summary.return_value = None
        mock_profile_repo.list_by_job_with_scores.return_value = sample_profiles
        
        result = job_service.get_analytics(job_id=job_id)
        
        assert result["job_id"] == job_id
        assert result["total_profiles"] == 3
        assert result["profiles_with_email"] == 1
        # Two profiles have scores (85 and 72)
        assert result["avg_score"] == 78.5


# =============================================================================
# Test: Utility Methods
# =============================================================================

class TestUtilityMethods:
    """Tests for utility methods."""
    
    def test_get_remaining_daily_quota(self, job_service, mock_job_repo):
        """Test getting remaining daily quota."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 3
        
        result = job_service.get_remaining_daily_quota(user_id=user_id)
        
        assert result["daily_limit"] == 10
        assert result["used_today"] == 3
        assert result["remaining"] == 7
    
    def test_can_create_job_true(self, job_service, mock_job_repo):
        """Test can_create_job returns True when under limit."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 5
        
        result = job_service.can_create_job(user_id=user_id)
        
        assert result is True
    
    def test_can_create_job_false(self, job_service, mock_job_repo):
        """Test can_create_job returns False when at limit."""
        user_id = str(uuid4())
        mock_job_repo.count_user_jobs_today.return_value = 10
        
        result = job_service.can_create_job(user_id=user_id)
        
        assert result is False
    
    def test_get_active_jobs(self, job_service, mock_job_repo, sample_job):
        """Test getting active jobs."""
        user_id = str(uuid4())
        sample_job["status"] = JobStatus.ANALYZING.value
        mock_job_repo.get_active_jobs_for_user.return_value = [sample_job]
        
        result = job_service.get_active_jobs(user_id=user_id)
        
        assert len(result) == 1
        assert result[0]["status"] == JobStatus.ANALYZING.value


# =============================================================================
# Test: get_job_service factory
# =============================================================================

class TestGetJobServiceFactory:
    """Tests for the get_job_service factory function."""
    
    def test_get_job_service_returns_instance(self):
        """Test factory returns JobService instance."""
        service = get_job_service()
        
        assert isinstance(service, JobService)
        assert service.job_repo is not None
        assert service.profile_repo is not None


# =============================================================================
# Test: Module Exports
# =============================================================================

class TestModuleExports:
    """Test module exports correctly."""
    
    def test_import_from_services(self):
        """Test importing JobService from services module."""
        from app.services import JobService, get_job_service
        
        assert JobService is not None
        assert get_job_service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
