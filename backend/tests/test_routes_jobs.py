"""
Tests for STORY-2.4.1: Implement Health & Job Endpoints

Unit tests for the job routes API layer.
Tests route handlers with mocked services and guards.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.jobs import router
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus, Defaults
from app.core.exceptions import (
    BusinessError,
    DailyLimitExceededError,
    ForbiddenError,
    InvalidStatusTransitionError,
    JobAlreadyCompletedError,
    JobNotFoundError,
    JobNotStartableError,
    N8NError,
)
from app.guards.auth import UserContext


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def jwt_secret():
    """Get JWT secret for testing."""
    return settings.supabase.jwt_secret


@pytest.fixture
def valid_user_id():
    """Generate a valid user ID."""
    return str(uuid4())


@pytest.fixture
def valid_token(jwt_secret, valid_user_id):
    """Create a valid JWT token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_job(sample_job_id, valid_user_id):
    """Create a sample job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": valid_user_id,
        "name": "Test Discovery",
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
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
def sample_profiles(sample_job_id):
    """Create sample profile data."""
    return [
        {
            "id": str(uuid4()),
            "job_id": sample_job_id,
            "username": "profile1",
            "full_name": "Profile One",
            "followers_count": 50000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 85,
            "contact_email": "profile1@example.com",
        },
        {
            "id": str(uuid4()),
            "job_id": sample_job_id,
            "username": "profile2",
            "full_name": "Profile Two",
            "followers_count": 75000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 72,
            "contact_email": None,
        },
    ]


@pytest.fixture
def mock_job_service():
    """Create a mock JobService."""
    return Mock()


@pytest.fixture
def mock_job_owner_guard():
    """Create a mock job owner guard."""
    return Mock()


@pytest.fixture
def test_app(mock_job_service, valid_user_id, sample_job):
    """Create a test FastAPI app with job routes and mocked dependencies."""
    from app.main import app
    from app.services.job_service import get_job_service
    from app.guards.auth import get_current_user
    from app.guards.ownership import verify_job_owner_user_only
    
    # Override the JobService dependency
    def override_get_job_service():
        return mock_job_service
    
    # Override the user authentication
    def override_get_current_user():
        return UserContext(
            user_id=valid_user_id,
            email="test@example.com",
            role="authenticated"
        )
    
    # Override the job owner guard
    def override_verify_job_owner():
        return sample_job
    
    app.dependency_overrides[get_job_service] = override_get_job_service
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[verify_job_owner_user_only] = override_verify_job_owner
    
    yield app
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


# =============================================================================
# Test: POST /api/jobs - Create Job
# =============================================================================

class TestCreateJob:
    """Tests for the POST /api/jobs endpoint."""
    
    def test_create_job_success(self, client, mock_job_service, sample_job, valid_token):
        """Test successful job creation."""
        mock_job_service.create_job.return_value = sample_job
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == sample_job["id"]
        assert data["status"] == "pending"
        mock_job_service.create_job.assert_called_once()
    
    def test_create_job_with_all_fields(self, client, mock_job_service, sample_job, valid_token):
        """Test job creation with all optional fields."""
        mock_job_service.create_job.return_value = sample_job
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "name": "My Discovery Session",
                "follower_range_min": 10000,
                "follower_range_max": 100000,
                "discovery_limit": 25,
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        mock_job_service.create_job.assert_called_once()
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert call_kwargs["name"] == "My Discovery Session"
        assert call_kwargs["follower_range_min"] == 10000
        assert call_kwargs["follower_range_max"] == 100000
        assert call_kwargs["discovery_limit"] == 25
    
    def test_create_job_daily_limit_exceeded(self, client, mock_job_service, valid_token):
        """Test job creation when daily limit is exceeded."""
        mock_job_service.create_job.side_effect = DailyLimitExceededError(limit=10)
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["error"]["code"] == "DAILY_LIMIT_EXCEEDED"
    
    def test_create_job_validation_error_short_description(self, client, valid_token):
        """Test validation error for too short brand description."""
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "Short",  # Too short (< 10 chars)
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"
    
    def test_create_job_validation_error_too_few_profiles(self, client, valid_token):
        """Test validation error for too few reference profiles."""
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": ["https://instagram.com/everlane"],  # Only 1
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
    
    def test_create_job_no_auth(self, test_app):
        """Test job creation without authentication."""
        from app.services.job_service import get_job_service
        from app.guards.auth import get_current_user
        
        # Remove the override to test real auth
        del test_app.dependency_overrides[get_current_user]
        
        client = TestClient(test_app)
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            }
        )
        
        assert response.status_code == 401


# =============================================================================
# Test: GET /api/jobs - List Jobs
# =============================================================================

class TestListJobs:
    """Tests for the GET /api/jobs endpoint."""
    
    def test_list_jobs_success(self, client, mock_job_service, sample_job, valid_token):
        """Test successful job listing."""
        mock_job_service.list_user_jobs.return_value = {
            "jobs": [sample_job],
            "total": 1,
            "limit": Defaults.PAGE_SIZE,
            "offset": 0,
        }
        
        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 1
        assert data["total"] == 1
        mock_job_service.list_user_jobs.assert_called_once()
    
    def test_list_jobs_empty(self, client, mock_job_service, valid_token):
        """Test job listing when user has no jobs."""
        mock_job_service.list_user_jobs.return_value = {
            "jobs": [],
            "total": 0,
            "limit": Defaults.PAGE_SIZE,
            "offset": 0,
        }
        
        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 0
        assert data["total"] == 0
    
    def test_list_jobs_with_status_filter(self, client, mock_job_service, valid_token):
        """Test job listing with status filter."""
        mock_job_service.list_user_jobs.return_value = {
            "jobs": [],
            "total": 0,
            "limit": 20,
            "offset": 0,
        }
        
        response = client.get(
            "/api/jobs?status=completed",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        call_kwargs = mock_job_service.list_user_jobs.call_args.kwargs
        assert call_kwargs["status"] == "completed"
    
    def test_list_jobs_with_pagination(self, client, mock_job_service, valid_token):
        """Test job listing with pagination."""
        mock_job_service.list_user_jobs.return_value = {
            "jobs": [],
            "total": 0,
            "limit": 10,
            "offset": 20,
        }
        
        response = client.get(
            "/api/jobs?limit=10&offset=20",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        call_kwargs = mock_job_service.list_user_jobs.call_args.kwargs
        assert call_kwargs["limit"] == 10
        assert call_kwargs["offset"] == 20


# =============================================================================
# Test: GET /api/jobs/{job_id} - Get Job Details
# =============================================================================

class TestGetJob:
    """Tests for the GET /api/jobs/{job_id} endpoint."""
    
    def test_get_job_success(
        self, client, mock_job_service, sample_job, sample_profiles, sample_job_id, valid_token
    ):
        """Test successful job retrieval."""
        mock_job_service.get_job_with_profiles.return_value = {
            **sample_job,
            "profiles": sample_profiles,
            "brand_dna": None,
        }
        
        response = client.get(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_job_id
        assert len(data["profiles"]) == 2
    
    def test_get_job_with_filters(
        self, client, mock_job_service, sample_job, sample_job_id, valid_token
    ):
        """Test job retrieval with profile filters."""
        mock_job_service.get_job_with_profiles.return_value = {
            **sample_job,
            "profiles": [],
            "brand_dna": None,
        }
        
        response = client.get(
            f"/api/jobs/{sample_job_id}?min_score=80&profile_status=scored",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        call_kwargs = mock_job_service.get_job_with_profiles.call_args.kwargs
        assert call_kwargs["min_score"] == 80
        assert call_kwargs["profile_status"] == "scored"
    
    def test_get_job_not_found(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test job retrieval when job doesn't exist."""
        mock_job_service.get_job_with_profiles.side_effect = JobNotFoundError(sample_job_id)
        
        response = client.get(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"


# =============================================================================
# Test: DELETE /api/jobs/{job_id} - Delete Job
# =============================================================================

class TestDeleteJob:
    """Tests for the DELETE /api/jobs/{job_id} endpoint."""
    
    def test_delete_job_success(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test successful job deletion."""
        mock_job_service.delete_job.return_value = {
            "deleted": True,
            "job_id": sample_job_id,
        }
        
        response = client.delete(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] is True
        mock_job_service.delete_job.assert_called_once_with(sample_job_id)
    
    def test_delete_job_not_found(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test job deletion when job doesn't exist."""
        mock_job_service.delete_job.side_effect = JobNotFoundError(sample_job_id)
        
        response = client.delete(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404


# =============================================================================
# Test: PATCH /api/jobs/{job_id} - Update Job
# =============================================================================

class TestUpdateJob:
    """Tests for the PATCH /api/jobs/{job_id} endpoint."""
    
    def test_update_job_success(
        self, client, mock_job_service, sample_job, sample_job_id, valid_token
    ):
        """Test successful job update."""
        updated_job = {**sample_job, "name": "Updated Name"}
        mock_job_service.update_job.return_value = updated_job
        
        response = client.patch(
            f"/api/jobs/{sample_job_id}",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_update_job_description(
        self, client, mock_job_service, sample_job, sample_job_id, valid_token
    ):
        """Test updating job description."""
        new_description = "Updated brand description for testing purposes"
        updated_job = {**sample_job, "brand_description": new_description}
        mock_job_service.update_job.return_value = updated_job
        
        response = client.patch(
            f"/api/jobs/{sample_job_id}",
            json={"brand_description": new_description},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["brand_description"] == new_description
    
    def test_update_job_already_completed(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test updating a completed job returns error."""
        mock_job_service.update_job.side_effect = JobAlreadyCompletedError(sample_job_id)
        
        response = client.patch(
            f"/api/jobs/{sample_job_id}",
            json={"name": "New Name"},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_ALREADY_COMPLETED"
    
    def test_update_job_validation_no_fields(self, client, sample_job_id, valid_token):
        """Test update with no fields provided returns validation error."""
        response = client.patch(
            f"/api/jobs/{sample_job_id}",
            json={},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422


# =============================================================================
# Test: POST /api/jobs/{job_id}/start - Start Discovery
# =============================================================================

class TestStartJob:
    """Tests for the POST /api/jobs/{job_id}/start endpoint."""
    
    def test_start_job_success(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test successful job start."""
        mock_job_service.trigger_discovery.return_value = {
            "status": "accepted",
            "job_id": sample_job_id,
            "message": "Discovery workflow initiated",
        }
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/start",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert data["message"] == "Discovery workflow initiated"
    
    def test_start_job_not_startable(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test starting a job that's not in pending status."""
        mock_job_service.trigger_discovery.side_effect = JobNotStartableError(
            job_id=sample_job_id,
            current_status="analyzing"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/start",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_NOT_STARTABLE"
    
    def test_start_job_n8n_error(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test handling N8N webhook error."""
        mock_job_service.trigger_discovery.side_effect = N8NError(
            message="Webhook failed"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/start",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 502
        data = response.json()
        assert data["detail"]["error"]["code"] == "N8N_ERROR"


# =============================================================================
# Test: POST /api/jobs/{job_id}/retry - Retry Job
# =============================================================================

class TestRetryJob:
    """Tests for the POST /api/jobs/{job_id}/retry endpoint."""
    
    def test_retry_job_success(
        self, client, mock_job_service, sample_job, sample_job_id, valid_token
    ):
        """Test successful job retry."""
        reset_job = {**sample_job, "status": JobStatus.PENDING.value, "error_message": None}
        mock_job_service.retry_job.return_value = reset_job
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/retry",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
    
    def test_retry_job_not_retryable(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test retrying a job that's not in failed status."""
        mock_job_service.retry_job.side_effect = BusinessError(
            message="Job cannot be retried from status 'completed'"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/retry",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 400


# =============================================================================
# Test: GET /api/jobs/{job_id}/analytics - Get Analytics
# =============================================================================

class TestGetJobAnalytics:
    """Tests for the GET /api/jobs/{job_id}/analytics endpoint."""
    
    def test_get_analytics_success(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test successful analytics retrieval."""
        mock_job_service.get_analytics.return_value = {
            "job_id": sample_job_id,
            "total_profiles": 50,
            "new_profiles": 2,
            "processing_profiles": 3,
            "done_profiles": 45,
            "skipped_profiles": 0,
            "avg_score": 72.5,
            "max_score": 95,
            "min_score": 45,
            "profiles_with_email": 30,
        }
        
        response = client.get(
            f"/api/jobs/{sample_job_id}/analytics",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_profiles"] == 50
        assert data["avg_score"] == 72.5
        assert data["profiles_with_email"] == 30
    
    def test_get_analytics_not_found(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test analytics for non-existent job."""
        mock_job_service.get_analytics.side_effect = JobNotFoundError(sample_job_id)
        
        response = client.get(
            f"/api/jobs/{sample_job_id}/analytics",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404


# =============================================================================
# Test: GET /api/jobs/quota - Get Daily Quota
# =============================================================================

class TestGetQuota:
    """Tests for the GET /api/jobs/quota endpoint."""
    
    def test_get_quota_success(self, client, mock_job_service, valid_token):
        """Test successful quota retrieval."""
        mock_job_service.get_remaining_daily_quota.return_value = {
            "daily_limit": 10,
            "used_today": 3,
            "remaining": 7,
        }
        
        response = client.get(
            "/api/jobs/quota",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["daily_limit"] == 10
        assert data["used_today"] == 3
        assert data["remaining"] == 7
    
    def test_get_quota_at_limit(self, client, mock_job_service, valid_token):
        """Test quota when user is at limit."""
        mock_job_service.get_remaining_daily_quota.return_value = {
            "daily_limit": 10,
            "used_today": 10,
            "remaining": 0,
        }
        
        response = client.get(
            "/api/jobs/quota",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["remaining"] == 0


# =============================================================================
# Test: Health Endpoint
# =============================================================================

class TestHealthEndpoint:
    """Tests for the GET /api/health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_detailed_health_check(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data


# =============================================================================
# Test: Error Response Format
# =============================================================================

class TestErrorResponseFormat:
    """Tests for error response formatting."""
    
    def test_not_found_error_format(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test 404 error response format."""
        mock_job_service.get_job_with_profiles.side_effect = JobNotFoundError(sample_job_id)
        
        response = client.get(
            f"/api/jobs/{sample_job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        
        # Verify error structure (HTTPException wraps in 'detail')
        assert "detail" in data
        assert "error" in data["detail"]
        assert "code" in data["detail"]["error"]
        assert "message" in data["detail"]["error"]
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"
    
    def test_validation_error_format(self, client, valid_token):
        """Test validation error response format."""
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "Short",  # Too short
                "reference_profiles": [],  # Too few
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
        data = response.json()
        
        # Verify error structure (wrapped in detail)
        assert "detail" in data
        assert "error" in data["detail"]
        assert "code" in data["detail"]["error"]
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["detail"]["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
