"""
Integration Tests for STORY-2.4.2: Implement Status Update Endpoints

These tests validate the full request/response cycle for status update endpoints,
including authentication, validation, and the complete workflow.

Tests the following endpoints:
- PATCH /api/jobs/{job_id}/status
- PATCH /api/profiles/{profile_id}/status
- PATCH /api/jobs/{job_id}/profiles/status (batch)

Note: These tests use mocked repositories to avoid requiring a running Supabase instance.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus, ErrorCodes, HttpStatus
from app.core.exceptions import JobNotFoundError, ProfileNotFoundError


# =============================================================================
# Pytest Markers
# =============================================================================

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create test client for the full application."""
    return TestClient(app)


@pytest.fixture
def jwt_secret():
    """Get JWT secret for testing."""
    return settings.supabase.jwt_secret


@pytest.fixture
def service_key():
    """Get service key for authentication."""
    return settings.n8n.service_key


@pytest.fixture
def valid_user_id():
    """Generate a valid user ID."""
    return str(uuid4())


@pytest.fixture
def valid_token(jwt_secret, valid_user_id):
    """Create a valid JWT token for user authentication."""
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
def valid_job_id():
    """Generate a valid job UUID."""
    return str(uuid4())


@pytest.fixture
def valid_profile_id():
    """Generate a valid profile UUID."""
    return str(uuid4())


@pytest.fixture
def mock_job(valid_job_id, valid_user_id):
    """Create a mock job dictionary."""
    return {
        "id": valid_job_id,
        "user_id": valid_user_id,
        "name": "Test Discovery Job",
        "brand_description": "A test brand for integration tests",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 10000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": JobStatus.PENDING.value,
        "profiles_discovered": 0,
        "profiles_scored": 0,
        "error_message": None,
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
        "full_name": "Test User",
        "bio": "A test profile for integration tests",
        "followers_count": 50000,
        "following_count": 1000,
        "posts_count": 250,
        "status": ProfileStatus.NEW.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# Integration Test: Job Status Update Workflow
# =============================================================================

class TestJobStatusUpdateWorkflow:
    """Integration tests for job status update workflow."""
    
    def test_complete_job_workflow_status_transitions(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test complete job status workflow: pending -> analyzing -> discovering -> scoring -> completed."""
        job_states = [
            (JobStatus.PENDING.value, JobStatus.ANALYZING.value),
            (JobStatus.ANALYZING.value, JobStatus.DISCOVERING.value),
            (JobStatus.DISCOVERING.value, JobStatus.SCORING.value),
            (JobStatus.SCORING.value, JobStatus.COMPLETED.value),
        ]
        
        for current_status, next_status in job_states:
            mock_job = {
                "id": valid_job_id,
                "user_id": valid_user_id,
                "status": current_status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            with patch("app.api.routes.status.JobRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.get_by_id.return_value = mock_job
                mock_repo.update_status.return_value = {
                    **mock_job,
                    "status": next_status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                mock_repo_class.return_value = mock_repo
                
                response = client.patch(
                    f"/api/jobs/{valid_job_id}/status",
                    json={"status": next_status},
                    headers={"X-Service-Key": service_key},
                )
            
            assert response.status_code == 200, f"Failed transition {current_status} -> {next_status}"
            data = response.json()
            assert data["status"] == next_status
            assert data["previous_status"] == current_status
    
    def test_job_failure_and_retry_workflow(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test job failure and retry workflow: analyzing -> failed -> pending."""
        # Step 1: Transition to failed
        mock_job_analyzing = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.ANALYZING.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_job_analyzing
            mock_repo.update_status.return_value = {
                **mock_job_analyzing,
                "status": JobStatus.FAILED.value,
                "error_message": "LLM service unavailable",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/jobs/{valid_job_id}/status",
                json={
                    "status": "failed",
                    "error_message": "LLM service unavailable",
                },
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error_message"] == "LLM service unavailable"
        
        # Step 2: Retry - transition back to pending
        mock_job_failed = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.FAILED.value,
            "error_message": "LLM service unavailable",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_job_failed
            mock_repo.update_status.return_value = {
                **mock_job_failed,
                "status": JobStatus.PENDING.value,
                "error_message": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/jobs/{valid_job_id}/status",
                json={"status": "pending"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["previous_status"] == "failed"


# =============================================================================
# Integration Test: Profile Status Update Workflow
# =============================================================================

class TestProfileStatusUpdateWorkflow:
    """Integration tests for profile status update workflow."""
    
    def test_complete_profile_scoring_workflow(
        self, client, service_key, valid_profile_id, valid_job_id
    ):
        """Test complete profile scoring workflow: new -> processing -> scored."""
        profile_states = [
            (ProfileStatus.NEW.value, ProfileStatus.PROCESSING.value),
            (ProfileStatus.PROCESSING.value, ProfileStatus.SCORED.value),
        ]
        
        for current_status, next_status in profile_states:
            mock_profile = {
                "id": valid_profile_id,
                "job_id": valid_job_id,
                "username": "testuser",
                "status": current_status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            
            with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
                mock_repo = Mock()
                mock_repo.get_by_id.return_value = mock_profile
                mock_repo.update_status.return_value = {
                    **mock_profile,
                    "status": next_status,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                mock_repo_class.return_value = mock_repo
                
                response = client.patch(
                    f"/api/profiles/{valid_profile_id}/status",
                    json={"status": next_status},
                    headers={"X-Service-Key": service_key},
                )
            
            assert response.status_code == 200, f"Failed transition {current_status} -> {next_status}"
            data = response.json()
            assert data["status"] == next_status
    
    def test_profile_skip_workflow(
        self, client, service_key, valid_profile_id, valid_job_id
    ):
        """Test skipping a profile: new -> skipped."""
        mock_profile = {
            "id": valid_profile_id,
            "job_id": valid_job_id,
            "username": "duplicateuser",
            "status": ProfileStatus.NEW.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_profile
            mock_repo.update_status.return_value = {
                **mock_profile,
                "status": ProfileStatus.SKIPPED.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/profiles/{valid_profile_id}/status",
                json={"status": "skipped"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"
    
    def test_profile_failure_and_retry_workflow(
        self, client, service_key, valid_profile_id, valid_job_id
    ):
        """Test profile failure and retry: processing -> failed -> processing."""
        # Step 1: Fail during processing
        mock_profile_processing = {
            "id": valid_profile_id,
            "job_id": valid_job_id,
            "username": "testuser",
            "status": ProfileStatus.PROCESSING.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_profile_processing
            mock_repo.update_status.return_value = {
                **mock_profile_processing,
                "status": ProfileStatus.FAILED.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/profiles/{valid_profile_id}/status",
                json={"status": "failed"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        
        # Step 2: Retry processing
        mock_profile_failed = {
            "id": valid_profile_id,
            "job_id": valid_job_id,
            "username": "testuser",
            "status": ProfileStatus.FAILED.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_profile_failed
            mock_repo.update_status.return_value = {
                **mock_profile_failed,
                "status": ProfileStatus.PROCESSING.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/profiles/{valid_profile_id}/status",
                json={"status": "processing"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        assert response.json()["status"] == "processing"


# =============================================================================
# Integration Test: Batch Update Workflow
# =============================================================================

class TestBatchUpdateWorkflow:
    """Integration tests for batch profile status updates."""
    
    def test_batch_mark_profiles_processing(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test batch marking profiles as processing."""
        profile_ids = [str(uuid4()) for _ in range(5)]
        
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.SCORING.value,
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_job_repo_class:
            mock_job_repo = Mock()
            mock_job_repo.get_by_id.return_value = mock_job
            mock_job_repo_class.return_value = mock_job_repo
            
            with patch("app.api.routes.status.ProfileRepository") as mock_profile_repo_class:
                mock_profile_repo = Mock()
                
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
                mock_profile_repo_class.return_value = mock_profile_repo
                
                response = client.patch(
                    f"/api/jobs/{valid_job_id}/profiles/status",
                    json={
                        "profile_ids": profile_ids,
                        "status": "processing",
                    },
                    headers={"X-Service-Key": service_key},
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 5
        assert data["failed"] == 0
        assert len(data["results"]) == 5
        for result in data["results"]:
            assert result["status"] == "processing"
    
    def test_batch_update_handles_partial_failures(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test batch update gracefully handles partial failures."""
        profile_ids = [str(uuid4()) for _ in range(5)]
        
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.SCORING.value,
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_job_repo_class:
            mock_job_repo = Mock()
            mock_job_repo.get_by_id.return_value = mock_job
            mock_job_repo_class.return_value = mock_job_repo
            
            with patch("app.api.routes.status.ProfileRepository") as mock_profile_repo_class:
                mock_profile_repo = Mock()
                
                call_count = [0]
                
                def get_profile(profile_id):
                    call_count[0] += 1
                    # Fail for 2nd and 4th profiles
                    if call_count[0] in [2, 4]:
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
                        "status": status.value if hasattr(status, 'value') else status,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                
                mock_profile_repo.get_by_id.side_effect = get_profile
                mock_profile_repo.update_status.side_effect = update_status
                mock_profile_repo_class.return_value = mock_profile_repo
                
                response = client.patch(
                    f"/api/jobs/{valid_job_id}/profiles/status",
                    json={
                        "profile_ids": profile_ids,
                        "status": "processing",
                    },
                    headers={"X-Service-Key": service_key},
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 3
        assert data["failed"] == 2
        assert len(data["errors"]) == 2


# =============================================================================
# Integration Test: Authentication & Authorization
# =============================================================================

class TestStatusAuthenticationIntegration:
    """Integration tests for status endpoint authentication."""
    
    def test_job_status_requires_service_key(self, client, valid_job_id):
        """Test that job status update requires service key."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.UNAUTHORIZED
    
    def test_profile_status_requires_service_key(self, client, valid_profile_id):
        """Test that profile status update requires service key."""
        response = client.patch(
            f"/api/profiles/{valid_profile_id}/status",
            json={"status": "processing"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_batch_status_requires_service_key(self, client, valid_job_id):
        """Test that batch status update requires service key."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/profiles/status",
            json={
                "profile_ids": [str(uuid4())],
                "status": "processing",
            },
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_invalid_service_key_rejected(self, client, valid_job_id):
        """Test that invalid service key is rejected."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
            headers={"X-Service-Key": "invalid-service-key-123"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.INVALID_SERVICE_KEY
    
    def test_user_token_not_accepted_for_status_update(
        self, client, valid_token, valid_job_id
    ):
        """Test that user JWT token is not accepted for status updates."""
        # Status updates should only accept service key, not user tokens
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "analyzing"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        
        # Should fail because Authorization header is used instead of X-Service-Key
        assert response.status_code == HttpStatus.UNAUTHORIZED


# =============================================================================
# Integration Test: Error Responses
# =============================================================================

class TestStatusErrorResponses:
    """Integration tests for error responses in status endpoints."""
    
    def test_job_not_found_error(self, client, service_key, valid_job_id):
        """Test 404 response when job not found."""
        with patch("app.api.routes.status.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/jobs/{valid_job_id}/status",
                json={"status": "analyzing"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.JOB_NOT_FOUND
    
    def test_profile_not_found_error(self, client, service_key, valid_profile_id):
        """Test 404 response when profile not found."""
        with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.side_effect = ProfileNotFoundError(valid_profile_id)
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/profiles/{valid_profile_id}/status",
                json={"status": "processing"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.PROFILE_NOT_FOUND
    
    def test_invalid_job_transition_error(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test 400 response for invalid job status transition."""
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.PENDING.value,  # Can't go directly to completed
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_job
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/jobs/{valid_job_id}/status",
                json={"status": "completed"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == HttpStatus.BAD_REQUEST
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.INVALID_TRANSITION
        assert "pending" in data["detail"]["error"]["message"]
        assert "completed" in data["detail"]["error"]["message"]
    
    def test_invalid_profile_transition_error(
        self, client, service_key, valid_profile_id, valid_job_id
    ):
        """Test 400 response for invalid profile status transition."""
        mock_profile = {
            "id": valid_profile_id,
            "job_id": valid_job_id,
            "status": ProfileStatus.NEW.value,  # Can't go directly to scored
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.ProfileRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_profile
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/profiles/{valid_profile_id}/status",
                json={"status": "scored"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == HttpStatus.BAD_REQUEST
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.INVALID_TRANSITION
    
    def test_invalid_status_value_error(self, client, service_key, valid_job_id):
        """Test 422 response for invalid status value."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "invalid_status_value"},
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
    
    def test_failed_status_missing_error_message(
        self, client, service_key, valid_job_id
    ):
        """Test validation error when failed status has no error message."""
        response = client.patch(
            f"/api/jobs/{valid_job_id}/status",
            json={"status": "failed"},  # Missing required error_message
            headers={"X-Service-Key": service_key},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY


# =============================================================================
# Integration Test: OpenAPI Schema
# =============================================================================

class TestStatusOpenAPISchema:
    """Integration tests for status routes in OpenAPI schema."""
    
    def test_status_routes_in_openapi(self, client):
        """Test that status routes are documented in OpenAPI."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data.get("paths", {})
        
        # Check job status endpoint is documented
        assert "/api/jobs/{job_id}/status" in paths
        assert "patch" in paths["/api/jobs/{job_id}/status"]
        
        # Check profile status endpoint is documented
        assert "/api/profiles/{profile_id}/status" in paths
        assert "patch" in paths["/api/profiles/{profile_id}/status"]
        
        # Check batch profile status endpoint is documented
        assert "/api/jobs/{job_id}/profiles/status" in paths
        assert "patch" in paths["/api/jobs/{job_id}/profiles/status"]
    
    def test_status_routes_have_tags(self, client):
        """Test that status routes have proper tags."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check Status tag exists
        tags = [tag.get("name") for tag in data.get("tags", [])]
        # Tags may be auto-generated, so just verify routes have tags
        job_status_route = data["paths"]["/api/jobs/{job_id}/status"]["patch"]
        assert "tags" in job_status_route


# =============================================================================
# Integration Test: Response Structure
# =============================================================================

class TestStatusResponseStructure:
    """Integration tests for response structure compliance."""
    
    def test_job_status_response_structure(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test that job status response has correct structure."""
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.PENDING.value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_id.return_value = mock_job
            mock_repo.update_status.return_value = {
                **mock_job,
                "status": JobStatus.ANALYZING.value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_repo_class.return_value = mock_repo
            
            response = client.patch(
                f"/api/jobs/{valid_job_id}/status",
                json={"status": "analyzing"},
                headers={"X-Service-Key": service_key},
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "id" in data
        assert "status" in data
        assert "previous_status" in data
        assert "updated_at" in data
        
        # Verify field types
        assert data["id"] == valid_job_id
        assert data["status"] == "analyzing"
        assert data["previous_status"] == "pending"
    
    def test_batch_update_response_structure(
        self, client, service_key, valid_job_id, valid_user_id
    ):
        """Test that batch update response has correct structure."""
        profile_id = str(uuid4())
        
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.SCORING.value,
        }
        
        with patch("app.api.routes.status.JobRepository") as mock_job_repo_class:
            mock_job_repo = Mock()
            mock_job_repo.get_by_id.return_value = mock_job
            mock_job_repo_class.return_value = mock_job_repo
            
            with patch("app.api.routes.status.ProfileRepository") as mock_profile_repo_class:
                mock_profile_repo = Mock()
                mock_profile_repo.get_by_id.return_value = {
                    "id": profile_id,
                    "job_id": valid_job_id,
                    "status": ProfileStatus.NEW.value,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                mock_profile_repo.update_status.return_value = {
                    "id": profile_id,
                    "job_id": valid_job_id,
                    "status": ProfileStatus.PROCESSING.value,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                mock_profile_repo_class.return_value = mock_profile_repo
                
                response = client.patch(
                    f"/api/jobs/{valid_job_id}/profiles/status",
                    json={
                        "profile_ids": [profile_id],
                        "status": "processing",
                    },
                    headers={"X-Service-Key": service_key},
                )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "updated" in data
        assert "failed" in data
        assert "results" in data
        assert "errors" in data
        
        # Verify field types
        assert isinstance(data["updated"], int)
        assert isinstance(data["failed"], int)
        assert isinstance(data["results"], list)
        assert isinstance(data["errors"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
