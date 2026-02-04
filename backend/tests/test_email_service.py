"""
Tests for STORY-2.3.2: Implement Email Service

These tests validate that the EmailService implements all required
email generation and sending logic correctly, including personalization,
tone selection, and mock sending functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.services.email_service import EmailService, get_email_service
from app.models.email import EmailTone, GeneratedEmail
from app.core.exceptions import BusinessError, ProfileNotFoundError, NotFoundError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_profile_repo():
    """Create a mock ProfileRepository."""
    return Mock()


@pytest.fixture
def mock_contact_repo():
    """Create a mock ContactRepository."""
    return Mock()


@pytest.fixture
def mock_brand_repo():
    """Create a mock BrandRepository."""
    return Mock()


@pytest.fixture
def mock_job_repo():
    """Create a mock JobRepository."""
    return Mock()


@pytest.fixture
def email_service(mock_profile_repo, mock_contact_repo, mock_brand_repo, mock_job_repo):
    """Create an EmailService with mocked repositories."""
    return EmailService(
        profile_repo=mock_profile_repo,
        contact_repo=mock_contact_repo,
        brand_repo=mock_brand_repo,
        job_repo=mock_job_repo,
    )


@pytest.fixture
def sample_profile():
    """Create a sample profile dictionary."""
    return {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "username": "fashion_influencer",
        "full_name": "Jane Smith",
        "bio": "Fashion enthusiast | Style blogger | NYC",
        "followers_count": 75000,
        "following_count": 1200,
        "posts_count": 450,
        "engagement_rate": 3.5,
        "is_verified": False,
        "is_business_account": True,
        "profile_picture_url": "https://example.com/pic.jpg",
        "external_url": "https://janesmithfashion.com",
    }


@pytest.fixture
def sample_job():
    """Create a sample job dictionary."""
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "Sustainable Fashion Discovery",
        "brand_description": "Eco-friendly sustainable fashion brand focused on ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "status": "completed",
    }


@pytest.fixture
def sample_brand_dna():
    """Create sample brand DNA dictionary."""
    return {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "hashtags": ["#sustainablefashion", "#ethicalfashion", "#slowfashion"],
        "keywords": ["sustainable", "ethical", "eco-friendly"],
        "visual_themes": ["minimalist", "natural", "clean"],
        "content_pillars": ["sustainability", "fashion", "lifestyle"],
    }


# =============================================================================
# Test: generate_email()
# =============================================================================

class TestGenerateEmail:
    """Tests for the generate_email method."""
    
    def test_generate_email_success(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job, sample_brand_dna
    ):
        """Test successful email generation."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = sample_brand_dna
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.FRIENDLY,
        )
        
        assert isinstance(result, GeneratedEmail)
        assert result.subject != ""
        assert result.body != ""
        assert result.tone == EmailTone.FRIENDLY
    
    def test_generate_email_includes_profile_name(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that email includes profile's name."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
        )
        
        # First name should be in the greeting
        assert "Jane" in result.body
    
    def test_generate_email_includes_username(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that email includes profile's username."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None

        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            use_ai=False,  # Use templates for deterministic test
        )

        assert "@fashion_influencer" in result.body
    
    def test_generate_email_profile_not_found(
        self, email_service, mock_profile_repo
    ):
        """Test error when profile is not found."""
        mock_profile_repo.get_by_id.side_effect = NotFoundError(
            "Profile not found",
            resource_type="profile",
            resource_id="test-id"
        )
        
        with pytest.raises(ProfileNotFoundError):
            email_service.generate_email(
                profile_id="test-id",
                job_id=str(uuid4()),
            )
    
    def test_generate_email_job_not_found(
        self, email_service, mock_profile_repo, mock_job_repo, sample_profile
    ):
        """Test error when job is not found."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.side_effect = NotFoundError(
            "Job not found",
            resource_type="job",
            resource_id="test-id"
        )
        
        with pytest.raises(BusinessError) as exc_info:
            email_service.generate_email(
                profile_id=sample_profile["id"],
                job_id="test-id",
            )
        
        assert "Job not found" in str(exc_info.value.message)
    
    def test_generate_email_with_custom_context(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test email generation with custom context."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        custom_context = "We loved your recent collaboration with Brand X!"
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            custom_context=custom_context,
        )
        
        assert custom_context in result.body
    
    def test_generate_email_with_sender_info(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test email generation with sender information."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None

        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            sender_name="John Doe",
            sender_company="Acme Inc",
            use_ai=False,  # Use templates for deterministic test
        )

        assert "John Doe" in result.body
        assert "Acme Inc" in result.body
    
    def test_generate_email_has_personalization_points(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that email tracks personalization points."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            include_profile_compliment=True,
        )
        
        assert len(result.personalization_points) > 0
    
    def test_generate_email_creates_html_body(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that email includes HTML body."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
        )
        
        assert result.html_body is not None
        assert "<p>" in result.html_body or "<br>" in result.html_body


# =============================================================================
# Test: Email Tones
# =============================================================================

class TestEmailTones:
    """Tests for different email tones."""
    
    def test_professional_tone(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test professional tone email."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.PROFESSIONAL,
        )
        
        assert result.tone == EmailTone.PROFESSIONAL
        # Professional tone uses "Dear" greeting
        assert "Dear" in result.body or "Best regards" in result.body
    
    def test_friendly_tone(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test friendly tone email."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.FRIENDLY,
        )
        
        assert result.tone == EmailTone.FRIENDLY
        # Friendly tone uses "Hi" greeting
        assert "Hi" in result.body or "Cheers" in result.body
    
    def test_casual_tone(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test casual tone email."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.CASUAL,
        )
        
        assert result.tone == EmailTone.CASUAL
        # Casual tone uses "Hey" greeting
        assert "Hey" in result.body or "Talk soon" in result.body
    
    def test_subject_varies_by_tone(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that subject line varies by tone."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        professional = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.PROFESSIONAL,
        )
        
        casual = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            tone=EmailTone.CASUAL,
        )
        
        assert professional.subject != casual.subject


# =============================================================================
# Test: send_email_mock()
# =============================================================================

class TestSendEmailMock:
    """Tests for the send_email_mock method."""
    
    def test_send_email_success(self, email_service):
        """Test successful mock email sending."""
        profile_id = str(uuid4())
        job_id = str(uuid4())
        
        result = email_service.send_email_mock(
            profile_id=profile_id,
            job_id=job_id,
            recipient_email="test@example.com",
            subject="Test Subject",
            body="Test body content",
        )
        
        assert result.success is True
        assert result.message_id is not None
        assert result.sent_at is not None
        assert result.recipient_email == "test@example.com"
    
    def test_send_email_invalid_email_fails(self, email_service):
        """Test that invalid email format fails."""
        result = email_service.send_email_mock(
            profile_id=str(uuid4()),
            job_id=str(uuid4()),
            recipient_email="not-an-email",
            subject="Test",
            body="Test",
        )
        
        assert result.success is False
        assert result.error is not None
        assert "Invalid email" in result.error
    
    def test_send_email_stores_in_history(self, email_service):
        """Test that sent emails are stored in mock history."""
        email_service.clear_sent_emails()
        
        profile_id = str(uuid4())
        job_id = str(uuid4())
        
        email_service.send_email_mock(
            profile_id=profile_id,
            job_id=job_id,
            recipient_email="test@example.com",
            subject="Test Subject",
            body="Test body",
        )
        
        sent = email_service.get_sent_emails()
        assert len(sent) == 1
        assert sent[0]["recipient_email"] == "test@example.com"
    
    def test_get_sent_emails_filters_by_profile(self, email_service):
        """Test filtering sent emails by profile."""
        email_service.clear_sent_emails()
        
        profile_id_1 = str(uuid4())
        profile_id_2 = str(uuid4())
        job_id = str(uuid4())
        
        email_service.send_email_mock(
            profile_id=profile_id_1,
            job_id=job_id,
            recipient_email="test1@example.com",
            subject="Test 1",
            body="Test 1",
        )
        
        email_service.send_email_mock(
            profile_id=profile_id_2,
            job_id=job_id,
            recipient_email="test2@example.com",
            subject="Test 2",
            body="Test 2",
        )
        
        filtered = email_service.get_sent_emails(profile_id=profile_id_1)
        assert len(filtered) == 1
        assert filtered[0]["profile_id"] == profile_id_1
    
    def test_clear_sent_emails(self, email_service):
        """Test clearing sent emails history."""
        email_service.send_email_mock(
            profile_id=str(uuid4()),
            job_id=str(uuid4()),
            recipient_email="test@example.com",
            subject="Test",
            body="Test",
        )
        
        assert len(email_service.get_sent_emails()) > 0
        
        email_service.clear_sent_emails()
        
        assert len(email_service.get_sent_emails()) == 0


# =============================================================================
# Test: Email Validation
# =============================================================================

class TestEmailValidation:
    """Tests for email validation."""
    
    @pytest.mark.parametrize("email,expected_valid", [
        ("test@example.com", True),
        ("user.name@domain.co.uk", True),
        ("user+tag@example.org", True),
        ("not-an-email", False),
        ("missing@domain", False),
        ("@nodomain.com", False),
        ("spaces in@email.com", False),
        ("", False),
    ])
    def test_email_validation(self, email_service, email, expected_valid):
        """Test email validation with various formats."""
        assert email_service._is_valid_email(email) == expected_valid


# =============================================================================
# Test: get_available_tones()
# =============================================================================

class TestGetAvailableTones:
    """Tests for the get_available_tones method."""
    
    def test_returns_all_tones(self, email_service):
        """Test that all tones are returned."""
        tones = email_service.get_available_tones()
        
        assert len(tones) == 3
        
        values = [t["value"] for t in tones]
        assert "professional" in values
        assert "friendly" in values
        assert "casual" in values
    
    def test_tone_has_required_fields(self, email_service):
        """Test that each tone has required fields."""
        tones = email_service.get_available_tones()
        
        for tone in tones:
            assert "value" in tone
            assert "label" in tone
            assert "description" in tone


# =============================================================================
# Test: estimate_email_effectiveness()
# =============================================================================

class TestEstimateEmailEffectiveness:
    """Tests for the estimate_email_effectiveness method."""
    
    def test_effectiveness_score_returned(self, email_service, sample_profile):
        """Test that effectiveness estimate is returned."""
        email = GeneratedEmail(
            subject="Test Subject Line Here",
            body="This is the email body content " * 20,  # ~100 words
            tone=EmailTone.FRIENDLY,
            profile_id=uuid4(),
            job_id=uuid4(),
            personalization_points=["Referenced profile"],
        )
        
        result = email_service.estimate_email_effectiveness(
            profile=sample_profile,
            email=email,
        )
        
        assert "effectiveness_score" in result
        assert "factors" in result
        assert "recommendation" in result
    
    def test_personalization_increases_score(self, email_service, sample_profile):
        """Test that personalization increases effectiveness score."""
        email_no_personalization = GeneratedEmail(
            subject="Test",
            body="Test body",
            tone=EmailTone.FRIENDLY,
            profile_id=uuid4(),
            job_id=uuid4(),
            personalization_points=[],
        )
        
        email_with_personalization = GeneratedEmail(
            subject="Test",
            body="Test body",
            tone=EmailTone.FRIENDLY,
            profile_id=uuid4(),
            job_id=uuid4(),
            personalization_points=["Referenced profile", "Mentioned content"],
        )
        
        result_no_pers = email_service.estimate_email_effectiveness(
            sample_profile, email_no_personalization
        )
        result_with_pers = email_service.estimate_email_effectiveness(
            sample_profile, email_with_personalization
        )
        
        assert result_with_pers["effectiveness_score"] > result_no_pers["effectiveness_score"]


# =============================================================================
# Test: regenerate_email()
# =============================================================================

class TestRegenerateEmail:
    """Tests for the regenerate_email method."""
    
    def test_regenerate_email_returns_new_email(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that regenerate returns a new email."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.regenerate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            previous_subject="Old Subject",
            feedback="Make it more casual",
            tone=EmailTone.CASUAL,
        )
        
        assert isinstance(result, GeneratedEmail)
        assert result.tone == EmailTone.CASUAL
    
    def test_regenerate_email_includes_feedback(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that regenerated email incorporates feedback."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        feedback = "Mention our sustainability commitment"
        
        result = email_service.regenerate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            previous_subject="Old Subject",
            feedback=feedback,
        )
        
        # Feedback is passed as custom context
        assert feedback in result.body


# =============================================================================
# Test: get_email_service Factory
# =============================================================================

class TestGetEmailServiceFactory:
    """Tests for the get_email_service factory function."""
    
    def test_get_email_service_returns_instance(self):
        """Test factory returns EmailService instance."""
        service = get_email_service()
        
        assert isinstance(service, EmailService)
        assert service.profile_repo is not None
        assert service.contact_repo is not None


# =============================================================================
# Test: Module Exports
# =============================================================================

class TestModuleExports:
    """Test module exports correctly."""
    
    def test_import_from_services(self):
        """Test importing EmailService from services module."""
        from app.services import EmailService, get_email_service
        
        assert EmailService is not None
        assert get_email_service is not None


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_profile_without_full_name(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test email generation when profile has no full name."""
        sample_profile["full_name"] = None
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
        )
        
        # Should fall back to username
        assert "fashion_influencer" in result.body
    
    def test_profile_with_low_followers(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test email generation for profile with low followers."""
        sample_profile["followers_count"] = 1000
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
        )
        
        # Should still generate email without errors
        assert result.subject != ""
        assert result.body != ""
    
    def test_profile_without_engagement_rate(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test email generation when engagement rate is missing."""
        sample_profile["engagement_rate"] = None
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        result = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            include_profile_compliment=True,
        )
        
        # Should still generate email
        assert result is not None
    
    def test_no_compliment_when_disabled(
        self, email_service, mock_profile_repo, mock_job_repo, mock_brand_repo,
        sample_profile, sample_job
    ):
        """Test that compliment is not included when disabled."""
        mock_profile_repo.get_by_id.return_value = sample_profile
        mock_job_repo.get_by_id.return_value = sample_job
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        with_compliment = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            include_profile_compliment=True,
        )
        
        without_compliment = email_service.generate_email(
            profile_id=sample_profile["id"],
            job_id=sample_job["id"],
            include_profile_compliment=False,
        )
        
        # Email without compliment should be shorter or different
        # (they won't be exactly equal due to generation variation)
        assert with_compliment.body != without_compliment.body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
