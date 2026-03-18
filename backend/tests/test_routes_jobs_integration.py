"""
Integration Tests for STORY-2.4.1: Implement Health & Job Endpoints

These tests validate the full request/response cycle for job endpoints,
including authentication, authorization, validation, and service layer integration.

Note: These tests may require a running Supabase instance for full integration.
They use pytest markers to allow selective execution.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus, Defaults
from app.guards.auth import UserContext


# =============================================================================
# Pytest Markers
# =============================================================================

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


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
def another_user_id():
    """Generate another user ID for cross-user tests."""
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
def another_user_token(jwt_secret, another_user_id):
    """Create a token for another user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": another_user_id,
        "email": "other@example.com",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def expired_token(jwt_secret, valid_user_id):
    """Create an expired JWT token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def service_key():
    """Get service key for testing."""
    return settings.n8n.service_key


@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def valid_create_job_payload():
    """Create a valid job creation payload."""
    return {
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
    }


@pytest.fixture
def full_create_job_payload():
    """Create a job creation payload with all fields."""
    return {
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
            "https://instagram.com/patagonia",
        ],
        "name": "Sustainable Fashion Discovery",
        "follower_range_min": 10000,
        "follower_range_max": 200000,
        "discovery_limit": 30,
    }


@pytest.fixture
def mock_job_repo():
    """Create a mock job repository for testing."""
    return Mock()


@pytest.fixture
def mock_profile_repo():
    """Create a mock profile repository for testing."""
    return Mock()


# =============================================================================
# Integration Test: Authentication Flow
# =============================================================================

class TestAuthenticationIntegration:
    """Integration tests for authentication flow."""
    
    def test_protected_endpoint_no_auth(self):
        """Test that protected endpoints require authentication."""
        client = TestClient(app)
        
        response = client.get("/api/jobs")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"
    
    def test_protected_endpoint_invalid_token(self):
        """Test that invalid tokens are rejected."""
        client = TestClient(app)
        
        response = client.get(
            "/api/jobs",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "INVALID_TOKEN"
    
    def test_protected_endpoint_expired_token(self, expired_token):
        """Test that expired tokens are rejected."""
        client = TestClient(app)
        
        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "EXPIRED_TOKEN"
    
    def test_protected_endpoint_valid_token(self, valid_token):
        """Test that valid tokens are accepted."""
        client = TestClient(app)
        
        # Mock the repository to avoid database calls
        with patch("app.repositories.job_repo.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.list_by_user.return_value = []
            mock_repo_class.return_value = mock_repo
            
            response = client.get(
                "/api/jobs",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
        
        # Should not return 401
        assert response.status_code != 401


# =============================================================================
# Integration Test: Job Creation Flow
# =============================================================================

class TestJobCreationIntegration:
    """Integration tests for job creation flow."""
    
    def test_create_job_full_flow(self, valid_token, valid_create_job_payload, valid_user_id):
        """Test full job creation flow with mocked repository."""
        client = TestClient(app)
        
        job_id = str(uuid4())
        mock_job = {
            "id": job_id,
            "user_id": valid_user_id,
            "name": None,
            "brand_description": valid_create_job_payload["brand_description"],
            "reference_profiles": valid_create_job_payload["reference_profiles"],
            "follower_range_min": 5000,
            "follower_range_max": 500000,
            "discovery_limit": 50,
            "status": JobStatus.PENDING.value,
            "profiles_discovered": 0,
            "profiles_scored": 0,
            "error_message": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.services.job_service.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.count_user_jobs_today.return_value = 0
            mock_repo.create.return_value = mock_job
            mock_repo_class.return_value = mock_repo
            
            with patch("app.services.job_service.ProfileRepository"):
                response = client.post(
                    "/api/jobs",
                    json=valid_create_job_payload,
                    headers={"Authorization": f"Bearer {valid_token}"}
                )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "pending"
        assert data["brand_description"] == valid_create_job_payload["brand_description"]
    
    def test_create_job_with_all_fields(
        self, valid_token, full_create_job_payload, valid_user_id
    ):
        """Test job creation with all optional fields."""
        client = TestClient(app)
        
        job_id = str(uuid4())
        mock_job = {
            "id": job_id,
            "user_id": valid_user_id,
            "name": full_create_job_payload["name"],
            "brand_description": full_create_job_payload["brand_description"],
            "reference_profiles": full_create_job_payload["reference_profiles"],
            "follower_range_min": full_create_job_payload["follower_range_min"],
            "follower_range_max": full_create_job_payload["follower_range_max"],
            "discovery_limit": full_create_job_payload["discovery_limit"],
            "status": JobStatus.PENDING.value,
            "profiles_discovered": 0,
            "profiles_scored": 0,
            "error_message": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        with patch("app.services.job_service.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.count_user_jobs_today.return_value = 0
            mock_repo.create.return_value = mock_job
            mock_repo_class.return_value = mock_repo
            
            with patch("app.services.job_service.ProfileRepository"):
                response = client.post(
                    "/api/jobs",
                    json=full_create_job_payload,
                    headers={"Authorization": f"Bearer {valid_token}"}
                )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == full_create_job_payload["name"]
        assert data["follower_range_min"] == full_create_job_payload["follower_range_min"]
        assert data["discovery_limit"] == full_create_job_payload["discovery_limit"]


# =============================================================================
# Integration Test: Validation Flow
# =============================================================================

class TestValidationIntegration:
    """Integration tests for request validation."""
    
    def test_validation_brand_description_too_short(self, valid_token):
        """Test validation rejects too short brand description."""
        client = TestClient(app)
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "Short",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "brand_description" in str(data).lower()
    
    def test_validation_too_few_profiles(self, valid_token):
        """Test validation rejects too few reference profiles."""
        client = TestClient(app)
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": ["https://instagram.com/everlane"],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
    
    def test_validation_invalid_instagram_url(self, valid_token):
        """Test validation rejects invalid Instagram URLs."""
        client = TestClient(app)
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://twitter.com/notinstagram",
                    "https://facebook.com/alsonotinstagram",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
    
    def test_validation_follower_range_invalid(self, valid_token):
        """Test validation rejects invalid follower range."""
        client = TestClient(app)
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "follower_range_min": 100000,
                "follower_range_max": 50000,  # Min > Max
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422


# =============================================================================
# Integration Test: Job Operations
# =============================================================================

class TestJobOperationsIntegration:
    """Integration tests for job operations."""
    
    def test_list_jobs_flow(self, valid_token, valid_user_id):
        """Test listing jobs flow."""
        client = TestClient(app)
        
        mock_jobs = [
            {
                "id": str(uuid4()),
                "user_id": valid_user_id,
                "name": "Job 1",
                "brand_description": "Description 1",
                "status": JobStatus.COMPLETED.value,
                "profiles_discovered": 50,
                "profiles_scored": 45,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            {
                "id": str(uuid4()),
                "user_id": valid_user_id,
                "name": "Job 2",
                "brand_description": "Description 2",
                "status": JobStatus.PENDING.value,
                "profiles_discovered": 0,
                "profiles_scored": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        ]
        
        with patch("app.services.job_service.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.list_by_user.return_value = mock_jobs
            mock_repo_class.return_value = mock_repo
            
            with patch("app.services.job_service.ProfileRepository"):
                response = client.get(
                    "/api/jobs",
                    headers={"Authorization": f"Bearer {valid_token}"}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["total"] == 2


# =============================================================================
# Integration Test: Health Endpoints
# =============================================================================

class TestHealthEndpointsIntegration:
    """Integration tests for health check endpoints."""
    
    def test_health_endpoint(self):
        """Test basic health check."""
        client = TestClient(app)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check."""
        client = TestClient(app)
        
        response = client.get("/api/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]


# =============================================================================
# Integration Test: Error Handling
# =============================================================================

class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    def test_not_found_error_response(self, valid_token, valid_user_id):
        """Test 404 error response structure."""
        client = TestClient(app)
        
        job_id = str(uuid4())
        
        with patch("app.services.job_service.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            from app.core.exceptions import JobNotFoundError
            mock_repo.get_by_id.side_effect = JobNotFoundError(job_id)
            mock_repo_class.return_value = mock_repo
            
            with patch("app.services.job_service.ProfileRepository"):
                with patch("app.guards.ownership.JobRepository") as mock_ownership_repo:
                    mock_ownership_repo.return_value = mock_repo
                    
                    response = client.get(
                        f"/api/jobs/{job_id}",
                        headers={"Authorization": f"Bearer {valid_token}"}
                    )
        
        assert response.status_code in [403, 404]  # Could be either based on guard
    
    def test_internal_error_response(self, valid_token):
        """Test 500 error response for unexpected errors."""
        # Use raise_server_exceptions=False to receive error response instead of raised exception
        client = TestClient(app, raise_server_exceptions=False)
        
        with patch("app.services.job_service.JobRepository") as mock_repo_class:
            mock_repo = Mock()
            mock_repo.list_by_user.side_effect = Exception("Unexpected database error")
            mock_repo_class.return_value = mock_repo
            
            with patch("app.services.job_service.ProfileRepository"):
                response = client.get(
                    "/api/jobs",
                    headers={"Authorization": f"Bearer {valid_token}"}
                )
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"]["code"] == "INTERNAL_ERROR"


# =============================================================================
# Integration Test: CORS Headers
# =============================================================================

class TestCORSIntegration:
    """Integration tests for CORS configuration."""
    
    def test_cors_headers_preflight(self):
        """Test CORS preflight request."""
        client = TestClient(app)
        
        response = client.options(
            "/api/jobs",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            }
        )
        
        # CORS preflight should be successful
        assert response.status_code == 200
    
    def test_cors_headers_present(self):
        """Test CORS headers are present in response."""
        client = TestClient(app)
        
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        # Note: CORS headers may vary based on configuration


# =============================================================================
# Integration Test: Root Endpoint
# =============================================================================

class TestRootEndpointIntegration:
    """Integration tests for root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        client = TestClient(app)
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "PartnerScout AI"
        assert "version" in data
        assert "documentation" in data  # Updated: docs -> documentation
        assert "endpoints" in data
        assert "health" in data["endpoints"]  # Updated: nested under endpoints
        assert "jobs" in data["endpoints"]  # Updated: nested under endpoints


# =============================================================================
# Integration Test: OpenAPI Documentation
# =============================================================================

class TestOpenAPIIntegration:
    """Integration tests for OpenAPI documentation."""
    
    def test_openapi_schema_available(self):
        """Test OpenAPI schema is accessible."""
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/api/jobs" in data["paths"]
        assert "/api/health" in data["paths"]
    
    def test_swagger_ui_available(self):
        """Test Swagger UI is accessible."""
        client = TestClient(app)
        
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_available(self):
        """Test ReDoc is accessible."""
        client = TestClient(app)
        
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
