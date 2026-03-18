"""
Tests for Item 1: Cancel Job Endpoint

TDD tests for POST /api/jobs/{job_id}/cancel endpoint.

These tests should FAIL initially, then pass after implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus
from app.core.exceptions import BusinessError, JobNotFoundError
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
def pending_job(sample_job_id, valid_user_id):
    """Create a sample job in pending status."""
    return {
        "id": sample_job_id,
        "user_id": valid_user_id,
        "name": "Test Discovery",
        "brand_description": "A sustainable fashion brand",
        "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/reformation"],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "keywords": [],
        "hashtags": [],
        "min_score_threshold": 50,
        "status": JobStatus.PENDING.value,
        "profiles_discovered": 0,
        "profiles_scored": 0,
        "error_message": None,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def analyzing_job(pending_job):
    """Create a sample job in analyzing status."""
    return {**pending_job, "status": JobStatus.ANALYZING.value}


@pytest.fixture
def completed_job(pending_job):
    """Create a sample job in completed status."""
    return {**pending_job, "status": JobStatus.COMPLETED.value}


@pytest.fixture
def cancelled_job(pending_job):
    """Create a sample job in cancelled status."""
    return {**pending_job, "status": JobStatus.CANCELLED.value}


@pytest.fixture
def mock_job_service():
    """Create a mock JobService."""
    return Mock()


@pytest.fixture
def test_app(mock_job_service, valid_user_id, pending_job):
    """Create a test FastAPI app with mocked dependencies."""
    from app.services.job_service import get_job_service
    from app.guards.auth import get_current_user
    from app.guards.ownership import verify_job_owner_user_only
    
    def override_get_job_service():
        return mock_job_service
    
    def override_get_current_user():
        return UserContext(
            user_id=valid_user_id,
            email="test@example.com",
            role="authenticated"
        )
    
    def override_verify_job_owner():
        return pending_job
    
    app.dependency_overrides[get_job_service] = override_get_job_service
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[verify_job_owner_user_only] = override_verify_job_owner
    
    yield app
    
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


# =============================================================================
# Test: POST /api/jobs/{job_id}/cancel - Cancel Job Endpoint
# =============================================================================

class TestCancelJobEndpoint:
    """Tests for the POST /api/jobs/{job_id}/cancel endpoint."""
    
    def test_cancel_pending_job_success(
        self, client, mock_job_service, sample_job_id, cancelled_job, valid_token
    ):
        """Test successfully cancelling a pending job."""
        mock_job_service.cancel_job.return_value = {
            "status": "cancelled",
            "job_id": sample_job_id,
            "cancelled_at": "2026-02-06T12:00:00Z",
            "message": "Discovery job cancelled successfully",
        }
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["job_id"] == sample_job_id
        assert "cancelled_at" in data
        assert data["message"] == "Discovery job cancelled successfully"
        
        # Verify service was called
        mock_job_service.cancel_job.assert_called_once()
    
    def test_cancel_analyzing_job_success(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test successfully cancelling a job that's currently analyzing."""
        mock_job_service.cancel_job.return_value = {
            "status": "cancelled",
            "job_id": sample_job_id,
            "cancelled_at": "2026-02-06T12:00:00Z",
            "message": "Discovery job cancelled successfully",
        }
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    def test_cancel_job_not_found(
        self, client, mock_job_service, valid_token
    ):
        """Test cancelling a non-existent job returns 404."""
        non_existent_id = str(uuid4())
        mock_job_service.cancel_job.side_effect = JobNotFoundError(non_existent_id)
        
        response = client.post(
            f"/api/jobs/{non_existent_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "JOB_NOT_FOUND"
    
    def test_cancel_completed_job_fails(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test that cancelling a completed job returns error."""
        mock_job_service.cancel_job.side_effect = BusinessError(
            message="Job cannot be cancelled from status 'completed'"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 400
    
    def test_cancel_already_cancelled_job_fails(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test that cancelling an already cancelled job returns error."""
        mock_job_service.cancel_job.side_effect = BusinessError(
            message="Job cannot be cancelled from status 'cancelled'"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 400
    
    def test_cancel_failed_job_fails(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test that cancelling a failed job returns error."""
        mock_job_service.cancel_job.side_effect = BusinessError(
            message="Job cannot be cancelled from status 'failed'"
        )
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 400
    
    def test_cancel_job_requires_authentication(self, test_app, sample_job_id):
        """Test that cancel endpoint requires authentication."""
        from app.guards.auth import get_current_user
        
        # Remove the auth override
        del test_app.dependency_overrides[get_current_user]
        
        client = TestClient(test_app)
        response = client.post(f"/api/jobs/{sample_job_id}/cancel")
        
        assert response.status_code == 401


# =============================================================================
# Test: JobService.cancel_job() method
# =============================================================================

class TestCancelJobService:
    """Tests for the JobService.cancel_job() method."""
    
    def test_cancel_job_updates_status_to_cancelled(self):
        """Test that cancel_job updates job status to cancelled."""
        from app.services.job_service import JobService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        
        job_id = str(uuid4())
        user_id = str(uuid4())
        
        # Mock the current job state
        mock_job_repo.get_by_id.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.PENDING.value,
        }
        
        # Mock the update status
        mock_job_repo.update_status.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.CANCELLED.value,
        }
        
        service = JobService(job_repo=mock_job_repo, profile_repo=mock_profile_repo)
        result = service.cancel_job(job_id, user_id)
        
        assert result["status"] == "cancelled"
        assert result["job_id"] == job_id
        assert "cancelled_at" in result
    
    def test_cancel_job_from_analyzing_status(self):
        """Test cancelling a job that is currently analyzing."""
        from app.services.job_service import JobService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        
        job_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_job_repo.get_by_id.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.ANALYZING.value,
        }
        
        mock_job_repo.update_status.return_value = {
            "id": job_id,
            "status": JobStatus.CANCELLED.value,
        }
        
        service = JobService(job_repo=mock_job_repo, profile_repo=mock_profile_repo)
        result = service.cancel_job(job_id, user_id)
        
        assert result["status"] == "cancelled"
    
    def test_cancel_job_from_discovering_status(self):
        """Test cancelling a job that is currently discovering."""
        from app.services.job_service import JobService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        
        job_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_job_repo.get_by_id.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.DISCOVERING.value,
        }
        
        mock_job_repo.update_status.return_value = {
            "id": job_id,
            "status": JobStatus.CANCELLED.value,
        }
        
        service = JobService(job_repo=mock_job_repo, profile_repo=mock_profile_repo)
        result = service.cancel_job(job_id, user_id)
        
        assert result["status"] == "cancelled"
    
    def test_cancel_job_from_scoring_status(self):
        """Test cancelling a job that is currently scoring."""
        from app.services.job_service import JobService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        
        job_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_job_repo.get_by_id.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.SCORING.value,
        }
        
        mock_job_repo.update_status.return_value = {
            "id": job_id,
            "status": JobStatus.CANCELLED.value,
        }
        
        service = JobService(job_repo=mock_job_repo, profile_repo=mock_profile_repo)
        result = service.cancel_job(job_id, user_id)
        
        assert result["status"] == "cancelled"
    
    def test_cancel_completed_job_raises_error(self):
        """Test that cancelling a completed job raises BusinessError."""
        from app.services.job_service import JobService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        
        job_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_job_repo.get_by_id.return_value = {
            "id": job_id,
            "user_id": user_id,
            "status": JobStatus.COMPLETED.value,
        }
        
        service = JobService(job_repo=mock_job_repo, profile_repo=mock_profile_repo)
        
        with pytest.raises(BusinessError) as exc_info:
            service.cancel_job(job_id, user_id)
        
        assert "cannot be cancelled" in str(exc_info.value.message).lower()


# =============================================================================
# Test: Response Model
# =============================================================================

class TestCancelJobResponseModel:
    """Tests for the cancel job response model."""
    
    def test_cancel_response_has_required_fields(
        self, client, mock_job_service, sample_job_id, valid_token
    ):
        """Test that cancel response has all required fields."""
        mock_job_service.cancel_job.return_value = {
            "status": "cancelled",
            "job_id": sample_job_id,
            "cancelled_at": "2026-02-06T12:00:00Z",
            "message": "Discovery job cancelled successfully",
        }
        
        response = client.post(
            f"/api/jobs/{sample_job_id}/cancel",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "status" in data
        assert "job_id" in data
        assert "cancelled_at" in data
        assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
