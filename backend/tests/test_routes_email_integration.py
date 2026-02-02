"""
Integration Tests for STORY-2.4.3: Implement Email Endpoints

These tests validate the full request/response cycle for email endpoints,
including authentication, validation, and the complete workflow.

Tests the following endpoints:
- POST /api/email/generate
- POST /api/email/send
- GET /api/email/tones

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
from app.models.email import EmailTone, GeneratedEmail


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
def expired_token(jwt_secret, valid_user_id):
    """Create an expired JWT token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),  # Expired
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
        "name": "Sustainable Fashion Discovery",
        "brand_description": "Eco-friendly sustainable fashion brand focused on ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 10000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": JobStatus.COMPLETED.value,
        "profiles_discovered": 25,
        "profiles_scored": 25,
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
        "username": "fashion_influencer",
        "instagram_url": "https://instagram.com/fashion_influencer",
        "full_name": "Jane Smith",
        "bio": "Fashion enthusiast | Style blogger | NYC based",
        "followers_count": 75000,
        "following_count": 1200,
        "posts_count": 450,
        "engagement_rate": 3.5,
        "is_verified": False,
        "is_business_account": True,
        "status": ProfileStatus.SCORED.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_generated_email(valid_profile_id, valid_job_id):
    """Create a mock GeneratedEmail object."""
    return GeneratedEmail(
        subject="Hey Jane! Let's collaborate?",
        body="Hi Jane,\n\nI've been following your content at @fashion_influencer and love what you're doing! I work with Eco-friendly sustainable fashion brand focused on ethical production and couldn't help but reach out.\n\nI have to say, Your engagement rate is impressive – it's clear you've built a really connected community.\n\nWe're all about finding authentic partnerships, not just one-off posts. We'd love to explore what a collaboration could look like – whether that's sponsored content, product seeding, or something completely unique!\n\nWould love to hop on a quick call or chat to explore this further! No pressure at all – just let me know if you're interested.\n\nCheers,\nThe Team",
        html_body="<p>Hi Jane,</p><p>I've been following your content...</p>",
        tone=EmailTone.FRIENDLY,
        profile_id=valid_profile_id,
        job_id=valid_job_id,
        personalization_points=["Referenced @fashion_influencer", "Included profile-specific compliment"],
    )


# =============================================================================
# Integration Test: Email Generation Workflow
# =============================================================================

class TestEmailGenerationWorkflow:
    """Integration tests for email generation workflow."""
    
    def test_generate_email_complete_workflow(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile, mock_generated_email
    ):
        """Test complete email generation workflow with all parameters."""
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        # Use dependency overrides (more reliable than patching)
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/generate",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "tone": "friendly",
                    "include_profile_compliment": True,
                    "custom_context": "We loved your recent sustainability post!",
                    "sender_name": "John Doe",
                    "sender_company": "Eco Fashion Co",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "email" in data
            assert "profile_name" in data
            assert "profile_username" in data
            assert "generation_duration_seconds" in data
            
            # Verify email content
            assert data["email"]["subject"] == mock_generated_email.subject
            assert data["email"]["tone"] == "friendly"
            assert data["profile_username"] == "fashion_influencer"
            assert data["profile_name"] == "Jane Smith"
        finally:
            app.dependency_overrides.clear()
    
    def test_generate_email_with_different_tones(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile
    ):
        """Test email generation with all available tones."""
        tones = ["professional", "friendly", "casual"]
        
        for tone in tones:
            mock_email = GeneratedEmail(
                subject=f"Subject for {tone}",
                body=f"Body for {tone}",
                tone=EmailTone(tone),
                profile_id=valid_profile_id,
                job_id=valid_job_id,
            )
            
            mock_profile_repo = Mock()
            mock_profile_repo.get_by_id.return_value = mock_profile
            
            mock_job_repo = Mock()
            mock_job_repo.get_by_id.return_value = mock_job
            
            mock_email_service = Mock()
            mock_email_service.generate_email.return_value = mock_email
            
            from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
            app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
            app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
            app.dependency_overrides[get_email_service] = lambda: mock_email_service
            
            try:
                response = client.post(
                    "/api/email/generate",
                    json={
                        "profile_id": valid_profile_id,
                        "job_id": valid_job_id,
                        "tone": tone,
                    },
                    headers={"Authorization": f"Bearer {valid_token}"},
                )
                
                assert response.status_code == 200, f"Failed for tone: {tone}"
                data = response.json()
                assert data["email"]["tone"] == tone
            finally:
                app.dependency_overrides.clear()


# =============================================================================
# Integration Test: Email Sending Workflow
# =============================================================================

class TestEmailSendingWorkflow:
    """Integration tests for email sending workflow."""
    
    def test_send_email_complete_workflow(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile
    ):
        """Test complete email sending workflow."""
        from app.models.email import SendEmailResponse
        
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=True,
            message_id="mock_abc123def456",
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            sent_at=datetime.now(timezone.utc),
        )
        
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/send",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "recipient_email": "jane@example.com",
                    "subject": "Partnership Opportunity",
                    "body": "Hi Jane, I'd love to discuss a potential partnership...",
                    "html_body": "<p>Hi Jane,</p><p>I'd love to discuss...</p>",
                    "from_name": "John Doe",
                    "from_email": "john@ecofashion.com",
                    "track_opens": True,
                    "track_clicks": True,
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["message_id"] == "mock_abc123def456"
            assert data["recipient_email"] == "jane@example.com"
            assert "sent_at" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_send_email_with_send_failure(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile
    ):
        """Test email sending when service returns failure."""
        from app.models.email import SendEmailResponse
        
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=False,
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            error="Email service temporarily unavailable",
        )
        
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/send",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "recipient_email": "jane@example.com",
                    "subject": "Test Subject",
                    "body": "Test body content for email",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            
            assert response.status_code == 200  # Still 200, but success=False
            data = response.json()
            
            assert data["success"] is False
            assert data["error"] == "Email service temporarily unavailable"
        finally:
            app.dependency_overrides.clear()


# =============================================================================
# Integration Test: Authentication
# =============================================================================

class TestEmailAuthenticationIntegration:
    """Integration tests for email endpoint authentication."""
    
    def test_generate_email_requires_auth(self, client, valid_job_id, valid_profile_id):
        """Test that email generation requires authentication."""
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_send_email_requires_auth(self, client, valid_job_id, valid_profile_id):
        """Test that email sending requires authentication."""
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "recipient_email": "jane@example.com",
                "subject": "Test",
                "body": "Test body content",
            },
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_expired_token_rejected(
        self, client, expired_token, valid_job_id, valid_profile_id
    ):
        """Test that expired token is rejected."""
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_invalid_token_rejected(self, client, valid_job_id, valid_profile_id):
        """Test that invalid token is rejected."""
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
            headers={"Authorization": "Bearer invalid-token-12345"},
        )
        
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_get_tones_no_auth_required(self, client):
        """Test that getting tones does not require authentication."""
        with patch("app.api.routes.email.EmailService") as mock_email_service_class:
            mock_email_service = Mock()
            mock_email_service.get_available_tones.return_value = [
                {"value": "professional", "label": "Professional", "description": "Formal"},
                {"value": "friendly", "label": "Friendly", "description": "Warm"},
                {"value": "casual", "label": "Casual", "description": "Relaxed"},
            ]
            mock_email_service_class.return_value = mock_email_service
            
            response = client.get("/api/email/tones")
        
        assert response.status_code == 200


# =============================================================================
# Integration Test: Authorization
# =============================================================================

class TestEmailAuthorizationIntegration:
    """Integration tests for email endpoint authorization."""
    
    def test_user_cannot_access_other_users_job(
        self, client, valid_token, valid_job_id, valid_profile_id, mock_profile
    ):
        """Test that user cannot generate email for another user's job."""
        other_user_id = str(uuid4())  # Different user
        mock_job = {
            "id": valid_job_id,
            "user_id": other_user_id,  # Different user owns this job
            "status": JobStatus.COMPLETED.value,
            "brand_description": "Test brand",
        }
        
        with patch("app.api.routes.email.ProfileRepository") as mock_profile_repo_class:
            mock_profile_repo = Mock()
            mock_profile_repo.get_by_id.return_value = mock_profile
            mock_profile_repo_class.return_value = mock_profile_repo
            
            with patch("app.api.routes.email.JobRepository") as mock_job_repo_class:
                mock_job_repo = Mock()
                mock_job_repo.get_by_id.return_value = mock_job
                mock_job_repo_class.return_value = mock_job_repo
                
                response = client.post(
                    "/api/email/generate",
                    json={
                        "profile_id": valid_profile_id,
                        "job_id": valid_job_id,
                        "tone": "friendly",
                    },
                    headers={"Authorization": f"Bearer {valid_token}"},
                )
        
        assert response.status_code == HttpStatus.FORBIDDEN
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.FORBIDDEN
    
    def test_profile_must_belong_to_job(
        self, client, valid_token, valid_job_id, valid_profile_id, valid_user_id
    ):
        """Test that profile must belong to the specified job."""
        other_job_id = str(uuid4())  # Different job
        
        mock_job = {
            "id": valid_job_id,
            "user_id": valid_user_id,
            "status": JobStatus.COMPLETED.value,
        }
        
        mock_profile = {
            "id": valid_profile_id,
            "job_id": other_job_id,  # Profile belongs to different job
            "username": "test",
            "status": ProfileStatus.SCORED.value,
        }
        
        with patch("app.api.routes.email.ProfileRepository") as mock_profile_repo_class:
            mock_profile_repo = Mock()
            mock_profile_repo.get_by_id.return_value = mock_profile
            mock_profile_repo_class.return_value = mock_profile_repo
            
            with patch("app.api.routes.email.JobRepository") as mock_job_repo_class:
                mock_job_repo = Mock()
                mock_job_repo.get_by_id.return_value = mock_job
                mock_job_repo_class.return_value = mock_job_repo
                
                response = client.post(
                    "/api/email/generate",
                    json={
                        "profile_id": valid_profile_id,
                        "job_id": valid_job_id,
                        "tone": "friendly",
                    },
                    headers={"Authorization": f"Bearer {valid_token}"},
                )
        
        assert response.status_code == HttpStatus.FORBIDDEN


# =============================================================================
# Integration Test: Error Responses
# =============================================================================

class TestEmailErrorResponses:
    """Integration tests for error responses in email endpoints."""
    
    def test_profile_not_found_error(
        self, client, valid_token, valid_job_id, valid_profile_id
    ):
        """Test 404 response when profile not found."""
        with patch("app.api.routes.email.ProfileRepository") as mock_profile_repo_class:
            mock_profile_repo = Mock()
            mock_profile_repo.get_by_id.side_effect = ProfileNotFoundError(valid_profile_id)
            mock_profile_repo_class.return_value = mock_profile_repo
            
            response = client.post(
                "/api/email/generate",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "tone": "friendly",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.PROFILE_NOT_FOUND
    
    def test_job_not_found_error(
        self, client, valid_token, valid_job_id, valid_profile_id, mock_profile
    ):
        """Test 404 response when job not found."""
        with patch("app.api.routes.email.ProfileRepository") as mock_profile_repo_class:
            mock_profile_repo = Mock()
            mock_profile_repo.get_by_id.return_value = mock_profile
            mock_profile_repo_class.return_value = mock_profile_repo
            
            with patch("app.api.routes.email.JobRepository") as mock_job_repo_class:
                mock_job_repo = Mock()
                mock_job_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
                mock_job_repo_class.return_value = mock_job_repo
                
                response = client.post(
                    "/api/email/generate",
                    json={
                        "profile_id": valid_profile_id,
                        "job_id": valid_job_id,
                        "tone": "friendly",
                    },
                    headers={"Authorization": f"Bearer {valid_token}"},
                )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.JOB_NOT_FOUND
    
    def test_invalid_tone_error(self, client, valid_token, valid_job_id, valid_profile_id):
        """Test 422 response for invalid tone."""
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "super_casual",  # Invalid tone
            },
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
    
    def test_invalid_email_format_error(
        self, client, valid_token, valid_job_id, valid_profile_id
    ):
        """Test 422 response for invalid email format."""
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "recipient_email": "not-a-valid-email",
                "subject": "Test",
                "body": "Test body content",
            },
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
    
    def test_missing_required_fields_error(self, client, valid_token):
        """Test 422 response for missing required fields."""
        # Missing profile_id
        response = client.post(
            "/api/email/generate",
            json={
                "job_id": str(uuid4()),
                "tone": "friendly",
            },
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY


# =============================================================================
# Integration Test: OpenAPI Schema
# =============================================================================

class TestEmailOpenAPISchema:
    """Integration tests for email routes in OpenAPI schema."""
    
    def test_email_routes_in_openapi(self, client):
        """Test that email routes are documented in OpenAPI."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data.get("paths", {})
        
        # Check email endpoints are documented
        assert "/api/email/generate" in paths
        assert "post" in paths["/api/email/generate"]
        
        assert "/api/email/send" in paths
        assert "post" in paths["/api/email/send"]
        
        assert "/api/email/tones" in paths
        assert "get" in paths["/api/email/tones"]
    
    def test_email_routes_have_tags(self, client):
        """Test that email routes have proper tags."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        generate_route = data["paths"]["/api/email/generate"]["post"]
        assert "tags" in generate_route
        
        send_route = data["paths"]["/api/email/send"]["post"]
        assert "tags" in send_route
    
    def test_email_routes_have_descriptions(self, client):
        """Test that email routes have descriptions."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        generate_route = data["paths"]["/api/email/generate"]["post"]
        assert "summary" in generate_route
        assert "description" in generate_route
        
        send_route = data["paths"]["/api/email/send"]["post"]
        assert "summary" in send_route
        assert "description" in send_route


# =============================================================================
# Integration Test: Response Structure
# =============================================================================

class TestEmailResponseStructure:
    """Integration tests for response structure compliance."""
    
    def test_generate_email_response_structure(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile, mock_generated_email
    ):
        """Test that generate email response has correct structure."""
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/generate",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "tone": "friendly",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify required fields
            assert "email" in data
            assert "profile_name" in data
            assert "profile_username" in data
            assert "generation_duration_seconds" in data
            
            # Verify email structure
            email = data["email"]
            assert "subject" in email
            assert "body" in email
            assert "tone" in email
            assert "profile_id" in email
            assert "job_id" in email
        finally:
            app.dependency_overrides.clear()
    
    def test_send_email_response_structure(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile
    ):
        """Test that send email response has correct structure."""
        from app.models.email import SendEmailResponse
        
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=True,
            message_id="mock_123",
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            sent_at=datetime.now(timezone.utc),
        )
        
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/send",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "recipient_email": "jane@example.com",
                    "subject": "Test",
                    "body": "Test body content here",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify required fields
            assert "success" in data
            assert "profile_id" in data
            assert "recipient_email" in data
            
            # For successful send
            assert "message_id" in data
            assert "sent_at" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_get_tones_response_structure(self, client):
        """Test that get tones response has correct structure."""
        with patch("app.api.routes.email.EmailService") as mock_email_service_class:
            mock_email_service = Mock()
            mock_email_service.get_available_tones.return_value = [
                {"value": "professional", "label": "Professional", "description": "Formal"},
                {"value": "friendly", "label": "Friendly", "description": "Warm"},
                {"value": "casual", "label": "Casual", "description": "Relaxed"},
            ]
            mock_email_service_class.return_value = mock_email_service
            
            response = client.get("/api/email/tones")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tones" in data
        assert isinstance(data["tones"], list)
        assert len(data["tones"]) == 3
        
        for tone in data["tones"]:
            assert "value" in tone
            assert "label" in tone
            assert "description" in tone


# =============================================================================
# Integration Test: Curl Validation (as per STORY-2.4.3)
# =============================================================================

class TestEmailCurlValidation:
    """Integration tests matching the curl commands from STORY-2.4.3."""
    
    def test_curl_generate_email(
        self, client, valid_token, valid_job_id, valid_profile_id,
        valid_user_id, mock_job, mock_profile, mock_generated_email
    ):
        """
        Test matching the curl validation command:
        curl -X POST http://localhost:8000/api/email/generate \
          -H "Authorization: Bearer $USER_TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"profile_id": "'$PROFILE_ID'", "job_id": "'$JOB_ID'", "tone": "friendly"}'
        # Expected: {"subject": "...", "body": "...", "metadata": {...}}
        """
        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = Mock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        from app.api.routes.email import get_profile_repository, get_job_repository, get_email_service
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        try:
            response = client.post(
                "/api/email/generate",
                json={
                    "profile_id": valid_profile_id,
                    "job_id": valid_job_id,
                    "tone": "friendly",
                },
                headers={
                    "Authorization": f"Bearer {valid_token}",
                    "Content-Type": "application/json",
                },
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Expected response structure per STORY-2.4.3
            assert "email" in data
            assert "subject" in data["email"]
            assert "body" in data["email"]
            # metadata is in the form of profile_name, profile_username, generation_duration_seconds
            assert data["email"]["subject"] is not None
            assert data["email"]["body"] is not None
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
