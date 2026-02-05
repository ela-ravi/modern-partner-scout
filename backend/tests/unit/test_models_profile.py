"""
Unit tests for Profile models.
"""
import pytest


class TestDiscoveredProfileModels:
    """Test suite for DiscoveredProfile models."""

    def test_profile_has_required_fields(self):
        """Profile should have job_id and username."""
        from app.models.profile import DiscoveredProfile

        profile = DiscoveredProfile(
            job_id="job-123",
            username="testuser"
        )
        assert profile.username == "testuser"
        assert profile.status == "new"

    def test_profile_url_generated(self):
        """Profile URL should be generated from username."""
        from app.models.profile import DiscoveredProfile

        profile = DiscoveredProfile(
            job_id="job-123",
            username="testuser"
        )
        assert "instagram.com" in profile.profile_url

    def test_profile_stats_defaults(self):
        """Profile stats should have sensible defaults."""
        from app.models.profile import DiscoveredProfile

        profile = DiscoveredProfile(
            job_id="job-123",
            username="testuser"
        )
        assert profile.follower_count == 0
        assert profile.following_count == 0
        assert profile.post_count == 0

    def test_profile_engagement_rate(self):
        """Profile should calculate engagement rate."""
        from app.models.profile import DiscoveredProfile

        profile = DiscoveredProfile(
            job_id="job-123",
            username="testuser",
            follower_count=10000,
            avg_likes=500,
            avg_comments=50
        )
        # Engagement = (likes + comments) / followers * 100
        assert profile.engagement_rate == 5.5


class TestProfileScoreModels:
    """Test suite for ProfileScore models."""

    def test_score_has_required_fields(self):
        """Score should have profile_id and overall_score."""
        from app.models.profile import ProfileScore

        score = ProfileScore(
            profile_id="profile-123",
            overall_score=85
        )
        assert score.overall_score == 85

    def test_score_range_validation(self):
        """Score should be between 0 and 100."""
        from app.models.profile import ProfileScore
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileScore(profile_id="123", overall_score=150)

    def test_score_category_breakdown(self):
        """Score should include category breakdown."""
        from app.models.profile import ProfileScore

        score = ProfileScore(
            profile_id="profile-123",
            overall_score=85,
            category_scores={
                "brand_alignment": 90,
                "audience_fit": 80,
                "engagement_quality": 85
            }
        )
        assert score.category_scores["brand_alignment"] == 90


class TestProfileContactModels:
    """Test suite for ProfileContact models."""

    def test_contact_has_email(self):
        """Contact should have email field."""
        from app.models.profile import ProfileContact

        contact = ProfileContact(
            profile_id="profile-123",
            email="creator@example.com"
        )
        assert contact.email == "creator@example.com"

    def test_contact_confidence_range(self):
        """Confidence should be between 0 and 1."""
        from app.models.profile import ProfileContact
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileContact(
                profile_id="123",
                email="test@test.com",
                confidence=1.5
            )

    def test_contact_source_tracking(self):
        """Contact should track extraction source."""
        from app.models.profile import ProfileContact

        contact = ProfileContact(
            profile_id="profile-123",
            email="creator@example.com",
            source="bio"
        )
        assert contact.source == "bio"
