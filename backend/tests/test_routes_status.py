"""
PartnerScout AI - Status Routes Unit Tests

Tests for STORY-2.4.2: Implement Status Update Endpoints

Unit tests for status update routes:
- PATCH /api/jobs/{job_id}/status
- PATCH /api/profiles/{profile_id}/status
- PATCH /api/jobs/{job_id}/profiles/status (batch)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.status import router, get_job_repository, get_profile_repository
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus, ErrorCodes, HttpStatus
from app.core.exceptions import (
    JobNotFoundError,
    ProfileNotFoundError,
    InvalidStatusTransitionError,
)
from app.guards.auth import get_service_context, ServiceContext


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Create test FastAPI application with status routes."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api")
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def service_key():
    """Get service key for authentication."""
    return settings.supabase.service_role_key


@pytest.fixture
def mock_service_context():
    """Create a mock service context."""
    return ServiceContext(service_name="internal", is_admin=True)


@pytest.fixture
def valid_job_id():
    """Generate a valid job UUID."""
    return str(uuid4())


@pytest.fixture
def valid_profile_id():
    """Generate a valid profile UUID."""
    return str(uuid4())


@pytest.fixture
def mock_job(valid_job_id):
    """Create a mock job dictionary."""
    return {
        "id": valid_job_id,
        "user_id": str(uuid4()),
        "status": JobStatus.PENDING.value,
        "brand_description": "Test brand",
        "reference_profiles": ["https://instagram.com/test"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_profile(valid_profile_id, valid_job_id):
    """Create a mock profile dictionary."""
    return {
        "id": valid_profile_id,
        "job_id": valid_job_id,
        "username": "testuser",
        "instagram_url": "https://instagram.com/testuser",
        "status": ProfileStatus.NEW.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# Update Job Status Tests
# =============================================================================

class TestUpdateJobStatus:
    """Tests for PATCH /api/jobs/{job_id}/status endpoint."""
    
    def test_update_job_status_pending_to_analyzing(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test valid transition from pending to analyzing."""
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        mock_job_repo.update_status.return_value = {
            **mock_job,
            "status": JobStatus.ANALYZING.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Override dependencies
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == valid_job_id
        assert data["status"] == "analyzing"
        assert data["previous_status"] == "pending"
        
        # Cleanup
        app.dependency_overrides.clear()
    
    def test_update_job_status_scoring_to_completed(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test valid transition from scoring to completed."""
        mock_job["status"] = JobStatus.SCORING.value
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        mock_job_repo.update_status.return_value = {
            **mock_job,
            "status": JobStatus.COMPLETED.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "completed"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["previous_status"] == "scoring"
        
        app.dependency_overrides.clear()
    
    def test_update_job_status_with_error_message(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test updating to failed status with error message."""
        mock_job["status"] = JobStatus.ANALYZING.value
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        mock_job_repo.update_status.return_value = {
            **mock_job,
            "status": JobStatus.FAILED.value,
            "error_message": "Brand analysis failed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "failed", "error_message": "Brand analysis failed"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "Brand analysis failed"
        
        app.dependency_overrides.clear()
    
    def test_update_job_status_invalid_transition(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test invalid transition from pending to completed."""
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "completed"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.BAD_REQUEST
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.INVALID_TRANSITION
        
        app.dependency_overrides.clear()
    
    def test_update_job_status_job_not_found(
        self, app, client, service_key, valid_job_id
    ):
        """Test updating non-existent job returns 404."""
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.JOB_NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_update_job_status_invalid_status_value(
        self, app, client, service_key, valid_job_id
    ):
        """Test invalid status value returns 422."""
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "invalid_status"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_update_job_status_no_service_key(self, client, valid_job_id):
        """Test request without service key returns 401."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_update_job_status_retry_failed_job(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test retrying a failed job (failed -> pending)."""
        mock_job["status"] = JobStatus.FAILED.value
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        mock_job_repo.update_status.return_value = {
            **mock_job,
            "status": JobStatus.PENDING.value,
            "error_message": None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "pending"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["previous_status"] == "failed"
        
        app.dependency_overrides.clear()


# =============================================================================
# Update Profile Status Tests
# =============================================================================

class TestUpdateProfileStatus:
    """Tests for PATCH /api/profiles/{profile_id}/status endpoint."""
    
    def test_update_profile_status_new_to_processing(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test valid transition from new to processing."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        mock_profile_repo.update_status.return_value = {
            **mock_profile,
            "status": ProfileStatus.PROCESSING.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == valid_profile_id
        assert data["status"] == "processing"
        assert data["previous_status"] == "new"
        
        app.dependency_overrides.clear()
    
    def test_update_profile_status_processing_to_scored(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test valid transition from processing to scored."""
        mock_profile["status"] = ProfileStatus.PROCESSING.value
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        mock_profile_repo.update_status.return_value = {
            **mock_profile,
            "status": ProfileStatus.SCORED.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "done"},
            headers={"X-Service-Key": service_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"
        assert data["previous_status"] == "processing"

        app.dependency_overrides.clear()

    def test_update_profile_status_processing_to_skipped(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test valid transition from processing to skipped."""
        mock_profile["status"] = ProfileStatus.PROCESSING.value

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        mock_profile_repo.update_status.return_value = {
            **mock_profile,
            "status": ProfileStatus.SKIPPED.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )

        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "skipped"},
            headers={"X-Service-Key": service_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"

        app.dependency_overrides.clear()
    
    def test_update_profile_status_invalid_transition(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test invalid transition from new to scored."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "done"},  # Invalid: new -> done
            headers={"X-Service-Key": service_key},
        )

        assert response.status_code == HttpStatus.BAD_REQUEST
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.INVALID_TRANSITION
        
        app.dependency_overrides.clear()
    
    def test_update_profile_status_not_found(
        self, app, client, service_key, valid_profile_id
    ):
        """Test updating non-existent profile returns 404."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.side_effect = ProfileNotFoundError(valid_profile_id)
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.PROFILE_NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_update_profile_status_retry_processing_profile(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test retrying a processing profile (processing -> new)."""
        mock_profile["status"] = ProfileStatus.PROCESSING.value

        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        mock_profile_repo.update_status.return_value = {
            **mock_profile,
            "status": ProfileStatus.NEW.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "new"},
            headers={"X-Service-Key": service_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "new"
        assert data["previous_status"] == "processing"

        app.dependency_overrides.clear()


# =============================================================================
# Batch Update Profile Statuses Tests
# =============================================================================

class TestBatchUpdateProfileStatuses:
    """Tests for PATCH /api/jobs/{job_id}/profiles/status endpoint."""
    
    def test_batch_update_all_success(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test batch update with all profiles succeeding."""
        profile_ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_profile_repo = MagicMock()
        
        def get_profile(profile_id):
            return {
                "id": profile_id,
                "job_id": valid_job_id,
                "username": f"user_{profile_id[:8]}",
                "status": ProfileStatus.NEW.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        def update_status(id, status):
            return {
                "id": id,
                "job_id": valid_job_id,
                "username": f"user_{id[:8]}",
                "status": status.value if hasattr(status, 'value') else status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        mock_profile_repo.get_by_id.side_effect = get_profile
        mock_profile_repo.update_status.side_effect = update_status
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": profile_ids, "status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 3
        assert data["failed"] == 0
        assert len(data["results"]) == 3
        assert len(data["errors"]) == 0
        
        app.dependency_overrides.clear()
    
    def test_batch_update_partial_failure(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test batch update with some profiles failing."""
        profile_ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_profile_repo = MagicMock()
        
        call_count = [0]
        
        def get_profile(profile_id):
            call_count[0] += 1
            if call_count[0] == 2:
                raise ProfileNotFoundError(profile_id)
            return {
                "id": profile_id,
                "job_id": valid_job_id,
                "username": f"user_{profile_id[:8]}",
                "status": ProfileStatus.NEW.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        def update_status(id, status):
            return {
                "id": id,
                "job_id": valid_job_id,
                "username": f"user_{id[:8]}",
                "status": status.value if hasattr(status, 'value') else status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        mock_profile_repo.get_by_id.side_effect = get_profile
        mock_profile_repo.update_status.side_effect = update_status
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": profile_ids, "status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 2
        assert data["failed"] == 1
        assert len(data["results"]) == 2
        assert len(data["errors"]) == 1
        
        app.dependency_overrides.clear()
    
    def test_batch_update_job_not_found(
        self, app, client, service_key, valid_job_id
    ):
        """Test batch update with non-existent job returns 404."""
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": [str(uuid4())], "status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_batch_update_profile_wrong_job(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test batch update with profile belonging to different job."""
        profile_id = str(uuid4())
        other_job_id = str(uuid4())
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = {
            "id": profile_id,
            "job_id": other_job_id,  # Different job
            "username": "testuser",
            "status": ProfileStatus.NEW.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": [profile_id], "status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 0
        assert data["failed"] == 1
        assert data["errors"][0]["code"] == ErrorCodes.FORBIDDEN
        
        app.dependency_overrides.clear()
    
    def test_batch_update_invalid_transition(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test batch update with invalid status transition."""
        profile_id = str(uuid4())
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = {
            "id": profile_id,
            "job_id": valid_job_id,
            "username": "testuser",
            "status": ProfileStatus.NEW.value,  # new -> done is invalid
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": [profile_id], "status": "done"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 0
        assert data["failed"] == 1
        assert data["errors"][0]["code"] == ErrorCodes.INVALID_TRANSITION
        
        app.dependency_overrides.clear()
    
    def test_batch_update_empty_profile_list(
        self, app, client, service_key, valid_job_id
    ):
        """Test batch update with empty profile list."""
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": [], "status": "processing"},
            headers={"X-Service-Key": service_key},
        )
        
        # Should fail validation - min 1 profile required
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# =============================================================================
# Authentication Tests
# =============================================================================

class TestStatusRoutesAuthentication:
    """Tests for authentication requirements on status routes."""
    
    def test_job_status_no_auth(self, client, valid_job_id):
        """Test job status update without auth returns 401."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_job_status_invalid_service_key(self, client, valid_job_id):
        """Test job status update with invalid key returns 401."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
            headers={"X-Service-Key": "invalid-key"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_profile_status_no_auth(self, client, valid_profile_id):
        """Test profile status update without auth returns 401."""
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "processing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_batch_status_no_auth(self, client, valid_job_id):
        """Test batch status update without auth returns 401."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={"profile_ids": [str(uuid4())], "status": "processing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestStatusRoutesEdgeCases:
    """Tests for edge cases in status routes."""
    
    def test_update_job_status_terminal_state(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test cannot transition from terminal state (completed)."""
        mock_job["status"] = JobStatus.COMPLETED.value
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "pending"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.BAD_REQUEST
        
        app.dependency_overrides.clear()
    
    def test_update_profile_status_terminal_state(
        self, app, client, service_key, valid_profile_id, mock_profile
    ):
        """Test cannot transition from terminal state (scored)."""
        mock_profile["status"] = ProfileStatus.SCORED.value
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "new"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.BAD_REQUEST
        
        app.dependency_overrides.clear()
    
    def test_failed_status_requires_error_message(
        self, app, client, service_key, valid_job_id, mock_job
    ):
        """Test that failed status requires error_message."""
        mock_job["status"] = JobStatus.ANALYZING.value
        
        app.dependency_overrides[get_service_context] = lambda: ServiceContext(
            service_name="internal", is_admin=True
        )
        
        # Request without error_message should fail validation
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "failed"},  # Missing error_message
            headers={"X-Service-Key": service_key},
        )
        
        # Pydantic model validation should fail
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
