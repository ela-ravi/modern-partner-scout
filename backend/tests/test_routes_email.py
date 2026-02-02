"""
PartnerScout AI - Email Routes Unit Tests

Tests for STORY-2.4.3: Implement Email Endpoints

Unit tests for email routes:
- POST /api/email/generate
- POST /api/email/send
- GET /api/email/tones
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.email import router, get_profile_repository, get_job_repository
from app.core.config import settings
from app.core.constants import HttpStatus, ErrorCodes, JobStatus, ProfileStatus
from app.core.exceptions import (
    JobNotFoundError,
    ProfileNotFoundError,
    ForbiddenError,
    BusinessError,
)
from app.guards.auth import get_current_user, UserContext
from app.models.email import EmailTone, GeneratedEmail
from app.services.email_service import EmailService, get_email_service


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Create test FastAPI application with email routes."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api")
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user_context():
    """Create a mock user context."""
    return UserContext(
        user_id=str(uuid4()),
        email="test@example.com",
        role="authenticated",
    )


@pytest.fixture
def valid_job_id():
    """Generate a valid job UUID."""
    return str(uuid4())


@pytest.fixture
def valid_profile_id():
    """Generate a valid profile UUID."""
    return str(uuid4())


@pytest.fixture
def mock_job(valid_job_id, mock_user_context):
    """Create a mock job dictionary."""
    return {
        "id": valid_job_id,
        "user_id": mock_user_context.user_id,
        "status": JobStatus.COMPLETED.value,
        "brand_description": "Sustainable fashion brand",
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
        "username": "fashion_influencer",
        "full_name": "Jane Smith",
        "instagram_url": "https://instagram.com/fashion_influencer",
        "bio": "Fashion enthusiast | NYC",
        "followers_count": 75000,
        "status": ProfileStatus.SCORED.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_generated_email(valid_profile_id, valid_job_id):
    """Create a mock GeneratedEmail object."""
    return GeneratedEmail(
        subject="Hey Jane! Let's collaborate?",
        body="Hi Jane,\n\nI've been following your content...",
        html_body="<p>Hi Jane,</p><p>I've been following your content...</p>",
        tone=EmailTone.FRIENDLY,
        profile_id=valid_profile_id,
        job_id=valid_job_id,
        personalization_points=["Referenced @fashion_influencer"],
    )


# =============================================================================
# Generate Email Tests
# =============================================================================

class TestGenerateEmail:
    """Tests for POST /api/email/generate endpoint."""
    
    def test_generate_email_success(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile, mock_generated_email
    ):
        """Test successful email generation."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["email"]["subject"] == mock_generated_email.subject
        assert data["email"]["tone"] == "friendly"
        assert data["profile_username"] == "fashion_influencer"
        assert data["profile_name"] == "Jane Smith"
        assert "generation_duration_seconds" in data
        
        # Cleanup
        app.dependency_overrides.clear()
    
    def test_generate_email_with_custom_context(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile, mock_generated_email
    ):
        """Test email generation with custom context."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        custom_context = "We loved your recent post about sustainability!"
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "professional",
                "custom_context": custom_context,
                "sender_name": "John Doe",
                "sender_company": "Eco Fashion Co",
            },
        )
        
        assert response.status_code == 200
        
        # Verify the service was called with correct arguments
        mock_email_service.generate_email.assert_called_once()
        call_kwargs = mock_email_service.generate_email.call_args.kwargs
        assert call_kwargs["custom_context"] == custom_context
        assert call_kwargs["sender_name"] == "John Doe"
        assert call_kwargs["sender_company"] == "Eco Fashion Co"
        
        app.dependency_overrides.clear()
    
    def test_generate_email_professional_tone(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile, mock_generated_email
    ):
        """Test email generation with professional tone."""
        mock_generated_email.tone = EmailTone.PROFESSIONAL
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "professional",
            },
        )
        
        assert response.status_code == 200
        
        # Verify tone was passed correctly
        call_kwargs = mock_email_service.generate_email.call_args.kwargs
        assert call_kwargs["tone"] == EmailTone.PROFESSIONAL
        
        app.dependency_overrides.clear()
    
    def test_generate_email_profile_not_found(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id
    ):
        """Test email generation with non-existent profile returns 404."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.side_effect = ProfileNotFoundError(valid_profile_id)
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.PROFILE_NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_generate_email_job_not_found(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id, mock_profile
    ):
        """Test email generation with non-existent job returns 404."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.NOT_FOUND
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.JOB_NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_generate_email_user_not_owner(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test email generation when user doesn't own the job returns 403."""
        # Modify job to have different user_id
        mock_job["user_id"] = str(uuid4())  # Different user
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.FORBIDDEN
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.FORBIDDEN
        
        app.dependency_overrides.clear()
    
    def test_generate_email_profile_wrong_job(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test email generation when profile doesn't belong to job returns 403."""
        # Modify profile to have different job_id
        mock_profile["job_id"] = str(uuid4())  # Different job
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.FORBIDDEN
        data = response.json()
        assert data["detail"]["error"]["code"] == ErrorCodes.FORBIDDEN
        
        app.dependency_overrides.clear()
    
    def test_generate_email_no_auth(self, client, valid_job_id, valid_profile_id):
        """Test email generation without authentication returns 401."""
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        # Without the dependency override, it will attempt real auth
        assert response.status_code == HttpStatus.UNAUTHORIZED
    
    def test_generate_email_invalid_tone(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id
    ):
        """Test email generation with invalid tone returns 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "invalid_tone",
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_generate_email_missing_required_fields(self, app, client, mock_user_context):
        """Test email generation with missing required fields returns 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Missing profile_id
        response = client.post(
            "/api/email/generate",
            json={
                "job_id": str(uuid4()),
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# =============================================================================
# Send Email Tests
# =============================================================================

class TestSendEmail:
    """Tests for POST /api/email/send endpoint."""
    
    def test_send_email_success(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test successful email sending."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        from app.models.email import SendEmailResponse
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=True,
            message_id="mock_12345",
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            sent_at=datetime.now(timezone.utc),
        )
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "recipient_email": "jane@example.com",
                "subject": "Partnership Opportunity",
                "body": "Hi Jane, I'd love to discuss a partnership...",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message_id"] == "mock_12345"
        assert data["recipient_email"] == "jane@example.com"
        
        app.dependency_overrides.clear()
    
    def test_send_email_with_optional_fields(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test email sending with all optional fields."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        from app.models.email import SendEmailResponse
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=True,
            message_id="mock_12345",
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            sent_at=datetime.now(timezone.utc),
        )
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "recipient_email": "jane@example.com",
                "subject": "Partnership Opportunity",
                "body": "Hi Jane, I'd love to discuss a partnership...",
                "html_body": "<p>Hi Jane, I'd love to discuss a partnership...</p>",
                "from_name": "John Doe",
                "from_email": "john@ecofashion.com",
                "reply_to": "partnerships@ecofashion.com",
                "track_opens": True,
                "track_clicks": False,
            },
        )
        
        assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    def test_send_email_invalid_recipient(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test email sending with invalid recipient email."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        from app.models.email import SendEmailResponse
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=False,
            profile_id=valid_profile_id,
            recipient_email="invalid-email",
            error="Invalid email format",
        )
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "recipient_email": "invalid-email",
                "subject": "Test",
                "body": "Test body content",
            },
        )
        
        # Pydantic validation should catch invalid email format
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_send_email_profile_not_found(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id
    ):
        """Test email sending with non-existent profile returns 404."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.side_effect = ProfileNotFoundError(valid_profile_id)
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        
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
        
        assert response.status_code == HttpStatus.NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_send_email_job_not_found(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id, mock_profile
    ):
        """Test email sending with non-existent job returns 404."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.side_effect = JobNotFoundError(valid_job_id)
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        
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
        
        assert response.status_code == HttpStatus.NOT_FOUND
        
        app.dependency_overrides.clear()
    
    def test_send_email_user_not_owner(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test email sending when user doesn't own the job returns 403."""
        mock_job["user_id"] = str(uuid4())  # Different user
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        
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
        
        assert response.status_code == HttpStatus.FORBIDDEN
        
        app.dependency_overrides.clear()
    
    def test_send_email_no_auth(self, client, valid_job_id, valid_profile_id):
        """Test email sending without authentication returns 401."""
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
    
    def test_send_email_missing_required_fields(self, app, client, mock_user_context):
        """Test email sending with missing required fields returns 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Missing body
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": str(uuid4()),
                "job_id": str(uuid4()),
                "recipient_email": "jane@example.com",
                "subject": "Test",
                # missing body
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# =============================================================================
# Get Available Tones Tests
# =============================================================================

class TestGetAvailableTones:
    """Tests for GET /api/email/tones endpoint."""
    
    def test_get_tones_success(self, app, client):
        """Test successful retrieval of available tones."""
        mock_email_service = MagicMock()
        mock_email_service.get_available_tones.return_value = [
            {"value": "professional", "label": "Professional", "description": "Formal"},
            {"value": "friendly", "label": "Friendly", "description": "Warm"},
            {"value": "casual", "label": "Casual", "description": "Relaxed"},
        ]
        
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.get("/api/email/tones")
        
        assert response.status_code == 200
        data = response.json()
        assert "tones" in data
        assert len(data["tones"]) == 3
        
        values = [t["value"] for t in data["tones"]]
        assert "professional" in values
        assert "friendly" in values
        assert "casual" in values
        
        app.dependency_overrides.clear()
    
    def test_get_tones_no_auth_required(self, app, client):
        """Test that getting tones doesn't require authentication."""
        mock_email_service = MagicMock()
        mock_email_service.get_available_tones.return_value = [
            {"value": "professional", "label": "Professional", "description": "Formal"},
        ]
        
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.get("/api/email/tones")
        
        # Should not return 401
        assert response.status_code == 200
        
        app.dependency_overrides.clear()


# =============================================================================
# Validation Tests
# =============================================================================

class TestEmailRoutesValidation:
    """Tests for input validation on email routes."""
    
    def test_generate_email_invalid_uuid(self, app, client, mock_user_context):
        """Test email generation with invalid UUID format."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": "not-a-uuid",
                "job_id": str(uuid4()),
                "tone": "friendly",
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_generate_email_custom_context_too_long(self, app, client, mock_user_context):
        """Test email generation with custom context exceeding limit."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Custom context has max_length=1000
        long_context = "a" * 1001
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": str(uuid4()),
                "job_id": str(uuid4()),
                "tone": "friendly",
                "custom_context": long_context,
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_send_email_subject_too_long(self, app, client, mock_user_context):
        """Test email sending with subject exceeding limit."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Subject has max_length=200
        long_subject = "a" * 201
        
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": str(uuid4()),
                "job_id": str(uuid4()),
                "recipient_email": "jane@example.com",
                "subject": long_subject,
                "body": "Test body content",
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()
    
    def test_send_email_body_too_short(self, app, client, mock_user_context):
        """Test email sending with body too short."""
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        
        # Body has min_length=10
        response = client.post(
            "/api/email/send",
            json={
                "profile_id": str(uuid4()),
                "job_id": str(uuid4()),
                "recipient_email": "jane@example.com",
                "subject": "Test Subject",
                "body": "Short",  # Too short
            },
        )
        
        assert response.status_code == HttpStatus.UNPROCESSABLE_ENTITY
        
        app.dependency_overrides.clear()


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestEmailRoutesEdgeCases:
    """Tests for edge cases in email routes."""
    
    def test_generate_email_profile_without_name(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile, mock_generated_email
    ):
        """Test email generation when profile has no full name."""
        mock_profile["full_name"] = None
        
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "friendly",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["profile_name"] is None
        assert data["profile_username"] == "fashion_influencer"
        
        app.dependency_overrides.clear()
    
    def test_generate_email_without_compliment(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile, mock_generated_email
    ):
        """Test email generation with compliment disabled."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        mock_email_service.generate_email.return_value = mock_generated_email
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
        response = client.post(
            "/api/email/generate",
            json={
                "profile_id": valid_profile_id,
                "job_id": valid_job_id,
                "tone": "casual",
                "include_profile_compliment": False,
            },
        )
        
        assert response.status_code == 200
        
        # Verify the service was called with compliment disabled
        call_kwargs = mock_email_service.generate_email.call_args.kwargs
        assert call_kwargs["include_profile_compliment"] is False
        
        app.dependency_overrides.clear()
    
    def test_send_email_fails_gracefully(
        self, app, client, mock_user_context, valid_job_id, valid_profile_id,
        mock_job, mock_profile
    ):
        """Test that email send failure returns proper response."""
        mock_profile_repo = MagicMock()
        mock_profile_repo.get_by_id.return_value = mock_profile
        
        mock_job_repo = MagicMock()
        mock_job_repo.get_by_id.return_value = mock_job
        
        mock_email_service = MagicMock()
        from app.models.email import SendEmailResponse
        mock_email_service.send_email_mock.return_value = SendEmailResponse(
            success=False,
            profile_id=valid_profile_id,
            recipient_email="jane@example.com",
            error="Email service temporarily unavailable",
        )
        
        app.dependency_overrides[get_current_user] = lambda: mock_user_context
        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service
        
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
        
        # Should still return 200 but with success=False
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
        
        app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
