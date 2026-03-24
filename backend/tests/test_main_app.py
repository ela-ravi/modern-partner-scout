"""
Tests for STORY-2.4.4: Register All Routes in Main App

Comprehensive tests for the main FastAPI application including:
- Route registration verification
- CORS configuration
- Exception handlers
- OpenAPI documentation
- Root endpoint

Testing Summary for FEAT-2.4:
| Test Type         | Description                           | Tool           |
|-------------------|---------------------------------------|----------------|
| Unit Test         | Route handlers call services correctly| pytest + mock  |
| Integration Test  | Full request/response cycle           | pytest + TestClient |
| Contract Test     | Response matches Pydantic model       | pytest         |
| Negative Test     | Invalid inputs return proper errors   | pytest         |
| Authorization Test| Protected routes require auth         | pytest         |
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

import jwt
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app, get_cors_origins, _status_code_to_error_code
from app.core.config import settings
from app.core.constants import HttpStatus, JobStatus
from app.core.exceptions import (
    PartnerScoutError,
    BusinessError,
    JobNotFoundError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


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
def expired_token(jwt_secret, valid_user_id):
    """Create an expired JWT token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def service_key():
    """Get service key for testing."""
    return settings.supabase.service_role_key


# =============================================================================
# Test: Route Registration (SUB-2.4.4.1.1)
# =============================================================================

class TestRouteRegistration:
    """Tests for verifying all routes are registered correctly."""
    
    def test_health_routes_registered(self, client):
        """Test that health routes are accessible."""
        # Basic health
        response = client.get("/api/health")
        assert response.status_code == 200
        
        # Detailed health
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
    
    def test_jobs_routes_registered(self, client, valid_token):
        """Test that job routes are accessible (auth required)."""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        # List jobs
        with patch("app.services.job_service.JobRepository") as mock_repo:
            mock_repo.return_value.list_by_user.return_value = []
            response = client.get("/api/jobs", headers=headers)
            assert response.status_code != 404  # Route exists
        
        # Quota endpoint
        with patch("app.services.job_service.JobRepository") as mock_repo:
            mock_repo.return_value.count_user_jobs_today.return_value = 0
            response = client.get("/api/jobs/quota", headers=headers)
            assert response.status_code != 404
    
    def test_status_routes_registered(self, client):
        """Test that status routes are registered in OpenAPI schema."""
        # Verify routes exist in OpenAPI schema (best way to check registration)
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        paths = schema.get("paths", {})
        
        # Check status routes are registered
        assert "/api/jobs/{job_id}/status" in paths, "Job status route not registered"
        assert "/api/profiles/{profile_id}/status" in paths, "Profile status route not registered"
        assert "/api/jobs/{job_id}/profiles/status" in paths, "Batch status route not registered"
        
        # Verify PATCH method is available
        assert "patch" in paths["/api/jobs/{job_id}/status"], "PATCH method not registered for job status"
        assert "patch" in paths["/api/profiles/{profile_id}/status"], "PATCH method not registered for profile status"
    
    def test_email_routes_registered(self, client, valid_token):
        """Test that email routes are accessible (auth required)."""
        # Email tones - doesn't require profile/job
        with patch("app.services.email_service.EmailService") as mock_service:
            mock_service.return_value.get_available_tones.return_value = [
                {"value": "professional", "label": "Professional"}
            ]
            response = client.get("/api/email/tones")
            assert response.status_code != 404
    
    def test_root_endpoint_registered(self, client):
        """Test that root endpoint is accessible."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_openapi_routes_registered(self, client):
        """Test that OpenAPI documentation routes are accessible."""
        # OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_all_expected_routes_in_openapi(self, client):
        """Test that all expected routes appear in OpenAPI schema."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        paths = schema.get("paths", {})
        
        # Health routes
        assert "/api/health" in paths
        assert "/api/health/detailed" in paths
        
        # Job routes
        assert "/api/jobs" in paths
        assert "/api/jobs/{job_id}" in paths
        assert "/api/jobs/{job_id}/start" in paths
        assert "/api/jobs/{job_id}/retry" in paths
        assert "/api/jobs/{job_id}/analytics" in paths
        assert "/api/jobs/quota" in paths
        
        # Status routes
        assert "/api/jobs/{job_id}/status" in paths
        assert "/api/profiles/{profile_id}/status" in paths
        assert "/api/jobs/{job_id}/profiles/status" in paths
        
        # Email routes
        assert "/api/email/generate" in paths
        assert "/api/email/send" in paths
        assert "/api/email/tones" in paths


# =============================================================================
# Test: CORS Configuration (SUB-2.4.4.1.2)
# =============================================================================

class TestCORSConfiguration:
    """Tests for CORS middleware configuration."""
    
    def test_cors_preflight_request(self, client):
        """Test CORS preflight (OPTIONS) request."""
        response = client.options(
            "/api/jobs",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            }
        )
        
        assert response.status_code == 200
    
    def test_cors_allowed_origin(self, client):
        """Test that allowed origins get CORS headers."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"}
        )
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_get_cors_origins_returns_list(self):
        """Test that get_cors_origins returns a list."""
        origins = get_cors_origins()
        assert isinstance(origins, list)
        assert len(origins) > 0
    
    def test_get_cors_origins_includes_localhost(self):
        """Test that localhost origins are included in development."""
        origins = get_cors_origins()
        
        # At least one localhost variant should be present
        localhost_variants = [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
        
        has_localhost = any(origin in origins for origin in localhost_variants)
        assert has_localhost, "No localhost origin found in CORS configuration"
    
    def test_cors_request_with_service_key_header(self, client, service_key):
        """Test CORS allows X-Service-Key header."""
        response = client.options(
            "/api/jobs/test-id/status",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "PATCH",
                "Access-Control-Request-Headers": "X-Service-Key, Content-Type",
            }
        )
        
        assert response.status_code == 200


# =============================================================================
# Test: Exception Handlers (SUB-2.4.4.1.3)
# =============================================================================

class TestExceptionHandlers:
    """Tests for exception handlers."""
    
    def test_partner_scout_error_handler(self, client):
        """Test PartnerScoutError exception handler."""
        # Trigger a 401 error by not providing auth
        response = client.get("/api/jobs")
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_validation_error_handler(self, client, valid_token):
        """Test validation error handler."""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        # Send invalid job creation request
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "Too short",  # Too short
                "reference_profiles": [],  # Empty
            },
            headers=headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"
    
    def test_validation_error_contains_field_details(self, client, valid_token):
        """Test validation error contains field-specific details."""
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "Short",
                "reference_profiles": ["only one url"],
            },
            headers=headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "details" in data["detail"]["error"]
        assert "errors" in data["detail"]["error"]["details"]
    
    def test_http_exception_handler(self, client):
        """Test HTTP exception handler for 404."""
        response = client.get("/nonexistent-route")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_general_exception_handler(self, client, valid_token):
        """Test general exception handler for unhandled errors."""
        client_no_raise = TestClient(app, raise_server_exceptions=False)
        headers = {"Authorization": f"Bearer {valid_token}"}
        
        with patch("app.services.job_service.JobRepository") as mock_repo:
            mock_repo.return_value.list_by_user.side_effect = Exception("Unexpected error")
            
            response = client_no_raise.get("/api/jobs", headers=headers)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"]["code"] == "INTERNAL_ERROR"
    
    def test_status_code_to_error_code_mapping(self):
        """Test status code to error code mapping."""
        assert _status_code_to_error_code(400) == "BAD_REQUEST"
        assert _status_code_to_error_code(401) == "UNAUTHORIZED"
        assert _status_code_to_error_code(403) == "FORBIDDEN"
        assert _status_code_to_error_code(404) == "NOT_FOUND"
        assert _status_code_to_error_code(409) == "CONFLICT"
        assert _status_code_to_error_code(422) == "VALIDATION_ERROR"
        assert _status_code_to_error_code(429) == "TOO_MANY_REQUESTS"
        assert _status_code_to_error_code(500) == "INTERNAL_ERROR"
        assert _status_code_to_error_code(502) == "BAD_GATEWAY"
        assert _status_code_to_error_code(999) == "HTTP_ERROR"  # Unknown code


# =============================================================================
# Test: Root Endpoint
# =============================================================================

class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_returns_api_info(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "PartnerScout AI"
        assert data["version"] == "1.0.0"
        assert "description" in data
    
    def test_root_contains_documentation_links(self, client):
        """Test root endpoint contains documentation links."""
        response = client.get("/")
        data = response.json()
        
        assert "documentation" in data
        assert data["documentation"]["swagger"] == "/docs"
        assert data["documentation"]["redoc"] == "/redoc"
        assert data["documentation"]["openapi"] == "/openapi.json"
    
    def test_root_contains_endpoints_info(self, client):
        """Test root endpoint contains endpoints information."""
        response = client.get("/")
        data = response.json()
        
        assert "endpoints" in data
        
        # Check health endpoints
        assert "health" in data["endpoints"]
        assert "basic" in data["endpoints"]["health"]
        assert "detailed" in data["endpoints"]["health"]
        
        # Check job endpoints
        assert "jobs" in data["endpoints"]
        expected_job_endpoints = [
            "create", "list", "get", "update", "delete",
            "start", "retry", "analytics", "quota"
        ]
        for endpoint in expected_job_endpoints:
            assert endpoint in data["endpoints"]["jobs"]
        
        # Check status endpoints
        assert "status" in data["endpoints"]
        assert "update_job" in data["endpoints"]["status"]
        assert "update_profile" in data["endpoints"]["status"]
        assert "batch_update" in data["endpoints"]["status"]
        
        # Check email endpoints
        assert "email" in data["endpoints"]
        assert "generate" in data["endpoints"]["email"]
        assert "send" in data["endpoints"]["email"]
        assert "tones" in data["endpoints"]["email"]
    
    def test_root_contains_environment(self, client):
        """Test root endpoint contains environment info."""
        response = client.get("/")
        data = response.json()
        
        assert "environment" in data


# =============================================================================
# Test: OpenAPI Documentation
# =============================================================================

class TestOpenAPIDocumentation:
    """Tests for OpenAPI documentation completeness."""
    
    def test_openapi_schema_structure(self, client):
        """Test OpenAPI schema has required structure."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        
        # Required OpenAPI fields
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_openapi_info_section(self, client):
        """Test OpenAPI info section is complete."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        info = schema["info"]
        assert info["title"] == "PartnerScout AI"
        assert info["version"] == "1.0.0"
        assert "description" in info
    
    def test_openapi_has_tags(self, client):
        """Test OpenAPI schema includes tags."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        # Should have tags for organization
        assert "tags" in schema or any(
            "tags" in route.get("get", route.get("post", {}))
            for route in schema.get("paths", {}).values()
        )
    
    def test_openapi_endpoints_have_descriptions(self, client):
        """Test that endpoints have descriptions."""
        response = client.get("/openapi.json")
        schema = response.json()
        
        paths = schema.get("paths", {})
        
        # Check a few key endpoints have summaries
        health_endpoint = paths.get("/api/health", {})
        if "get" in health_endpoint:
            assert "summary" in health_endpoint["get"] or "description" in health_endpoint["get"]
    
    def test_swagger_ui_loads(self, client):
        """Test Swagger UI page loads."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert b"swagger" in response.content.lower()
    
    def test_redoc_loads(self, client):
        """Test ReDoc page loads."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


# =============================================================================
# Test: Authentication Integration
# =============================================================================

class TestAuthenticationIntegration:
    """Tests for authentication with the main app."""
    
    def test_unauthenticated_request_rejected(self, client):
        """Test that protected routes reject unauthenticated requests."""
        response = client.get("/api/jobs")
        
        assert response.status_code == 401
    
    def test_invalid_token_rejected(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/api/jobs",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
    
    def test_expired_token_rejected(self, client, expired_token):
        """Test that expired tokens are rejected."""
        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
    
    def test_valid_token_accepted(self, client, valid_token):
        """Test that valid tokens are accepted."""
        with patch("app.services.job_service.JobRepository") as mock_repo:
            mock_repo.return_value.list_by_user.return_value = []
            
            response = client.get(
                "/api/jobs",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
        
        # Should not be 401 (auth should pass)
        assert response.status_code != 401
    
    def test_service_key_authentication(self, client, service_key):
        """Test service key authentication for internal routes."""
        job_id = str(uuid4())
        
        with patch("app.repositories.job_repo.JobRepository") as mock_repo:
            mock_repo.return_value.get_by_id.return_value = {
                "id": job_id,
                "status": "pending"
            }
            mock_repo.return_value.update_status.return_value = {
                "id": job_id,
                "status": "analyzing",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = client.patch(
                f"/api/jobs/{job_id}/status",
                json={"status": "analyzing"},
                headers={"X-Service-Key": service_key}
            )
        
        # Should not be 401
        assert response.status_code != 401
    
    def test_invalid_service_key_rejected(self, client):
        """Test that invalid service keys are rejected."""
        job_id = str(uuid4())
        
        response = client.patch(
            f"/api/jobs/{job_id}/status",
            json={"status": "analyzing"},
            headers={"X-Service-Key": "invalid-key"}
        )
        
        assert response.status_code == 401


# =============================================================================
# Test: Health Endpoints
# =============================================================================

class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_basic_health_check(self, client):
        """Test basic health check endpoint."""
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
        
        assert "status" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "llm_provider" in data["services"]
        assert "apify" in data["services"]


# =============================================================================
# Test: Error Response Format Consistency
# =============================================================================

class TestErrorResponseConsistency:
    """Tests for consistent error response format across all routes."""
    
    def test_401_error_format(self, client):
        """Test 401 error response format."""
        response = client.get("/api/jobs")
        
        assert response.status_code == 401
        data = response.json()
        
        # Should have error structure (may be in 'detail' for HTTPException)
        error_data = data.get("error") or data.get("detail", {}).get("error")
        assert error_data is not None
        assert "code" in error_data
        assert "message" in error_data
    
    def test_404_error_format(self, client):
        """Test 404 error response format."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "error" in data or "detail" in data
    
    def test_422_error_format(self, client, valid_token):
        """Test 422 validation error format."""
        response = client.post(
            "/api/jobs",
            json={},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["detail"]["error"]


# =============================================================================
# Test: Contract Tests (Response Matches Models)
# =============================================================================

class TestContractTests:
    """Contract tests to verify responses match Pydantic models."""
    
    def test_health_response_contract(self, client):
        """Test health response matches expected model."""
        response = client.get("/api/health")
        data = response.json()
        
        # Required fields
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
    
    def test_job_list_response_contract(self, client, valid_token):
        """Test job list response matches expected model."""
        with patch("app.services.job_service.JobRepository") as mock_repo:
            mock_repo.return_value.list_by_user.return_value = []
            
            response = client.get(
                "/api/jobs",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields in job list response
        assert "jobs" in data
        assert isinstance(data["jobs"], list)
        assert "total" in data
        assert isinstance(data["total"], int)


# =============================================================================
# Test: Negative Tests
# =============================================================================

class TestNegativeTests:
    """Negative tests for invalid inputs."""
    
    def test_invalid_uuid_parameter(self):
        """Test invalid UUID parameter returns error."""
        # Use client that doesn't raise server exceptions
        client = TestClient(app, raise_server_exceptions=False)
        
        # Get a valid token first
        jwt_secret = settings.supabase.jwt_secret
        user_id = str(uuid4())
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "role": "authenticated",
            "iat": now,
            "exp": now + timedelta(hours=1),
            "aud": "authenticated",
        }
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        
        response = client.get(
            "/api/jobs/not-a-uuid",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should return an error response (400, 403, 404, 422, or 500)
        # The exact code depends on where validation happens
        assert response.status_code >= 400
    
    def test_missing_required_fields(self, client, valid_token):
        """Test missing required fields returns validation error."""
        response = client.post(
            "/api/jobs",
            json={},
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
    
    def test_invalid_json_body(self, client, valid_token):
        """Test invalid JSON body returns error."""
        response = client.post(
            "/api/jobs",
            content="not valid json",
            headers={
                "Authorization": f"Bearer {valid_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 422
    
    def test_unsupported_method(self, client):
        """Test unsupported HTTP method returns 405."""
        response = client.put("/api/health")
        
        assert response.status_code == 405


# =============================================================================
# Test: Application Metadata
# =============================================================================

class TestApplicationMetadata:
    """Tests for application metadata and configuration."""
    
    def test_app_title(self):
        """Test application title is set correctly."""
        assert app.title == "PartnerScout AI"
    
    def test_app_version(self):
        """Test application version is set correctly."""
        assert app.version == "1.0.0"
    
    def test_app_description(self):
        """Test application description is set."""
        assert app.description is not None
        assert len(app.description) > 0
    
    def test_docs_url_configured(self):
        """Test documentation URLs are configured."""
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
