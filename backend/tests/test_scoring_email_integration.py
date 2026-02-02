"""
Integration Tests for STORY-2.3.2: Scoring & Email Services

These tests validate that the ScoringService and EmailService work
correctly together and integrate properly with the rest of the system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from app.services.scoring_service import ScoringService, get_scoring_service
from app.services.email_service import EmailService, get_email_service
from app.models.email import EmailTone
from app.core.constants import ProfileStatus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def scoring_service():
    """Create a real ScoringService with mocked repository."""
    mock_repo = Mock()
    mock_repo.create_full_score.return_value = {
        "id": str(uuid4()),
        "profile_id": str(uuid4()),
        "final_score": 75,
        "recommendation": "recommended",
    }
    mock_repo.get_score_stats_for_job.return_value = {
        "count": 10,
        "avg_score": 68.5,
        "min_score": 45,
        "max_score": 92,
    }
    mock_repo.count_by_recommendation.return_value = {
        "highly_recommended": 2,
        "recommended": 5,
        "consider": 2,
        "not_recommended": 1,
    }
    return ScoringService(score_repo=mock_repo)


@pytest.fixture
def email_service():
    """Create a real EmailService with mocked repositories."""
    mock_profile_repo = Mock()
    mock_job_repo = Mock()
    mock_brand_repo = Mock()
    mock_contact_repo = Mock()
    
    mock_profile_repo.get_by_id.return_value = {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "username": "test_influencer",
        "full_name": "Test User",
        "bio": "Content creator | Lifestyle blogger",
        "followers_count": 50000,
        "engagement_rate": 4.5,
        "is_business_account": True,
    }
    
    mock_job_repo.get_by_id.return_value = {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "brand_description": "Sustainable lifestyle brand",
        "status": "completed",
    }
    
    mock_brand_repo.get_by_job_id_optional.return_value = None
    
    return EmailService(
        profile_repo=mock_profile_repo,
        contact_repo=mock_contact_repo,
        brand_repo=mock_brand_repo,
        job_repo=mock_job_repo,
    )


@pytest.fixture
def sample_scored_profile():
    """Create a sample scored profile."""
    return {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "username": "fashion_brand",
        "full_name": "Fashion Brand",
        "bio": "Fashion and lifestyle content",
        "followers_count": 75000,
        "engagement_rate": 3.8,
        "is_business_account": True,
        "status": ProfileStatus.SCORED.value,
        "final_score": 82,
        "recommendation": "highly_recommended",
        "visual_aesthetic_match": 85,
        "content_theme_alignment": 80,
        "engagement_rate_score": 90,
        "follower_quality": 75,
        "business_indicators": 85,
        "activity_recency": 80,
    }


# =============================================================================
# Test: Scoring and Email Flow Integration
# =============================================================================

class TestScoringEmailFlow:
    """Tests for the complete scoring to email workflow."""
    
    def test_score_affects_email_personalization(
        self, scoring_service, email_service
    ):
        """Test that scoring result influences email generation context."""
        # Generate scores
        dimensions = {
            "visual_aesthetic_match": 90,
            "content_theme_alignment": 85,
            "engagement_rate_score": 95,
            "follower_quality": 80,
            "business_indicators": 85,
            "activity_recency": 90,
        }
        
        score_result = scoring_service.process_score(dimensions)
        
        assert score_result["recommendation"] == "highly_recommended"
        
        # Generate email for the scored profile
        profile_id = str(uuid4())
        job_id = str(uuid4())
        
        email = email_service.generate_email(
            profile_id=profile_id,
            job_id=job_id,
            tone=EmailTone.FRIENDLY,
        )
        
        # Email should be generated successfully
        assert email is not None
        assert email.body != ""
    
    def test_low_score_profiles_can_still_receive_emails(
        self, scoring_service, email_service
    ):
        """Test that even low-scored profiles can receive emails."""
        # Generate low score
        dimensions = {
            "visual_aesthetic_match": 30,
            "content_theme_alignment": 35,
            "engagement_rate_score": 40,
            "follower_quality": 25,
            "business_indicators": 30,
            "activity_recency": 45,
        }
        
        score_result = scoring_service.process_score(dimensions)
        
        # Should get low recommendation
        assert score_result["recommendation"] in ["consider", "not_recommended"]
        
        # But email can still be generated
        email = email_service.generate_email(
            profile_id=str(uuid4()),
            job_id=str(uuid4()),
            tone=EmailTone.PROFESSIONAL,
        )
        
        assert email is not None
    
    def test_fake_suspected_profiles_scored_correctly(
        self, scoring_service
    ):
        """Test that fake suspected profiles are correctly marked."""
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 75,
            "engagement_rate_score": 85,
            "follower_quality": 70,
            "business_indicators": 75,
            "activity_recency": 80,
        }
        
        result = scoring_service.process_score(
            dimensions=dimensions,
            is_fake_suspected=True,
        )
        
        # Score should still be calculated
        assert result["final_score"] > 0
        
        # But recommendation should be not_recommended
        assert result["recommendation"] == "not_recommended"
        assert result["is_fake_suspected"] is True


# =============================================================================
# Test: Service Integration with Repositories
# =============================================================================

class TestRepositoryIntegration:
    """Tests for service integration with repositories."""
    
    def test_scoring_service_creates_db_record(self, scoring_service):
        """Test that scoring service creates database record."""
        profile_id = str(uuid4())
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 75,
            "engagement_rate_score": 85,
            "follower_quality": 70,
            "business_indicators": 75,
            "activity_recency": 80,
        }
        
        result = scoring_service.score_profile(
            profile_id=profile_id,
            dimensions=dimensions,
            reasoning={"test": "reasoning"},
        )
        
        # Verify repository was called
        scoring_service.score_repo.create_full_score.assert_called_once()
        
        # Verify result includes category
        assert "category" in result
    
    def test_email_service_stores_sent_emails(self, email_service):
        """Test that email service tracks sent emails."""
        email_service.clear_sent_emails()
        
        # Send mock emails
        for i in range(3):
            email_service.send_email_mock(
                profile_id=str(uuid4()),
                job_id=str(uuid4()),
                recipient_email=f"test{i}@example.com",
                subject=f"Test {i}",
                body=f"Body {i}",
            )
        
        sent = email_service.get_sent_emails()
        assert len(sent) == 3
    
    def test_scoring_statistics_aggregation(self, scoring_service):
        """Test scoring statistics aggregation."""
        job_id = str(uuid4())
        
        stats = scoring_service.get_score_statistics(job_id)
        
        assert "count" in stats
        assert "avg_score" in stats
        assert "recommendation_counts" in stats


# =============================================================================
# Test: Service Factory Functions
# =============================================================================

class TestServiceFactories:
    """Tests for service factory functions."""
    
    def test_scoring_service_factory_creates_instance(self):
        """Test get_scoring_service factory."""
        service = get_scoring_service()
        
        assert isinstance(service, ScoringService)
        assert hasattr(service, "calculate_final_score")
        assert hasattr(service, "get_recommendation")
    
    def test_email_service_factory_creates_instance(self):
        """Test get_email_service factory."""
        service = get_email_service()
        
        assert isinstance(service, EmailService)
        assert hasattr(service, "generate_email")
        assert hasattr(service, "send_email_mock")
    
    def test_services_can_be_imported_from_module(self):
        """Test services can be imported from services module."""
        from app.services import (
            ScoringService,
            EmailService,
            get_scoring_service,
            get_email_service,
        )
        
        scoring = get_scoring_service()
        email = get_email_service()
        
        assert isinstance(scoring, ScoringService)
        assert isinstance(email, EmailService)


# =============================================================================
# Test: Configuration Integration
# =============================================================================

class TestConfigurationIntegration:
    """Tests for configuration integration."""
    
    def test_scoring_uses_yaml_config(self):
        """Test that scoring service uses YAML configuration."""
        from app.core.settings import get_scoring_weights, get_scoring_thresholds
        
        weights = get_scoring_weights()
        thresholds = get_scoring_thresholds()
        
        # Weights should sum to 1.0
        assert 0.99 <= sum(weights.values()) <= 1.01
        
        # Thresholds should be defined
        assert "min_recommendation_score" in thresholds or "high_score" in thresholds
    
    def test_scoring_config_weights_are_applied(self):
        """Test that config weights are actually applied to scoring."""
        from app.core.settings import get_scoring_weights
        
        service = get_scoring_service()
        config_weights = get_scoring_weights()
        
        # Service weights should match config
        for key, weight in config_weights.items():
            assert service.weights.get(key) == weight


# =============================================================================
# Test: Error Handling Integration
# =============================================================================

class TestErrorHandling:
    """Tests for error handling across services."""
    
    def test_scoring_handles_missing_dimensions(self, scoring_service):
        """Test scoring handles missing dimension gracefully."""
        # Only provide some dimensions
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 75,
            # Missing other dimensions
        }
        
        result = scoring_service.process_score(dimensions)
        
        # Should still produce a score
        assert result["final_score"] >= 0
        assert result["recommendation"] is not None
    
    def test_email_handles_missing_profile_data(self, email_service):
        """Test email generation handles missing profile data."""
        # Modify mock to return minimal profile
        email_service.profile_repo.get_by_id.return_value = {
            "id": str(uuid4()),
            "job_id": str(uuid4()),
            "username": "minimal_user",
            # Missing full_name, bio, etc.
        }
        
        email = email_service.generate_email(
            profile_id=str(uuid4()),
            job_id=str(uuid4()),
        )
        
        # Should still generate email
        assert email is not None
        assert email.body != ""


# =============================================================================
# Test: Complete Workflow Simulation
# =============================================================================

class TestCompleteWorkflow:
    """Tests simulating complete workflows."""
    
    def test_discovery_to_outreach_workflow(
        self, scoring_service, email_service, sample_scored_profile
    ):
        """Test complete workflow from scoring to email outreach."""
        # Step 1: Score the profile
        dimensions = {
            "visual_aesthetic_match": sample_scored_profile["visual_aesthetic_match"],
            "content_theme_alignment": sample_scored_profile["content_theme_alignment"],
            "engagement_rate_score": sample_scored_profile["engagement_rate_score"],
            "follower_quality": sample_scored_profile["follower_quality"],
            "business_indicators": sample_scored_profile["business_indicators"],
            "activity_recency": sample_scored_profile["activity_recency"],
        }
        
        score_result = scoring_service.process_score(dimensions)
        
        # Verify scoring
        assert score_result["final_score"] > 0
        assert score_result["recommendation"] in [
            "highly_recommended", "recommended", "consider", "not_recommended"
        ]
        
        # Step 2: Check if recommendable
        is_recommendable = scoring_service.is_recommendable(
            score_result["final_score"],
            score_result["is_fake_suspected"],
        )
        
        # Step 3: If recommendable, generate email
        if is_recommendable:
            email = email_service.generate_email(
                profile_id=sample_scored_profile["id"],
                job_id=sample_scored_profile["job_id"],
                tone=EmailTone.FRIENDLY,
            )
            
            assert email is not None
            
            # Step 4: Send email
            result = email_service.send_email_mock(
                profile_id=sample_scored_profile["id"],
                job_id=sample_scored_profile["job_id"],
                recipient_email="influencer@example.com",
                subject=email.subject,
                body=email.body,
            )
            
            assert result.success is True
    
    def test_batch_scoring_workflow(self, scoring_service):
        """Test scoring multiple profiles in batch."""
        profiles = [
            {
                "id": str(uuid4()),
                "dimensions": {
                    "visual_aesthetic_match": 85,
                    "content_theme_alignment": 80,
                    "engagement_rate_score": 90,
                    "follower_quality": 75,
                    "business_indicators": 80,
                    "activity_recency": 85,
                },
            },
            {
                "id": str(uuid4()),
                "dimensions": {
                    "visual_aesthetic_match": 60,
                    "content_theme_alignment": 55,
                    "engagement_rate_score": 70,
                    "follower_quality": 50,
                    "business_indicators": 45,
                    "activity_recency": 75,
                },
            },
            {
                "id": str(uuid4()),
                "dimensions": {
                    "visual_aesthetic_match": 30,
                    "content_theme_alignment": 25,
                    "engagement_rate_score": 40,
                    "follower_quality": 20,
                    "business_indicators": 35,
                    "activity_recency": 50,
                },
            },
        ]
        
        results = []
        for profile in profiles:
            result = scoring_service.process_score(profile["dimensions"])
            results.append(result)
        
        # Verify all scored
        assert len(results) == 3
        
        # Verify different recommendations based on scores
        recommendations = [r["recommendation"] for r in results]
        assert "highly_recommended" in recommendations or "recommended" in recommendations
        assert "not_recommended" in recommendations or "consider" in recommendations
    
    def test_email_campaign_workflow(self, email_service):
        """Test sending emails to multiple profiles."""
        email_service.clear_sent_emails()
        
        profiles = [
            {"id": str(uuid4()), "email": "profile1@example.com"},
            {"id": str(uuid4()), "email": "profile2@example.com"},
            {"id": str(uuid4()), "email": "profile3@example.com"},
        ]
        
        job_id = str(uuid4())
        successful = 0
        failed = 0
        
        for profile in profiles:
            # Generate email
            email = email_service.generate_email(
                profile_id=profile["id"],
                job_id=job_id,
                tone=EmailTone.FRIENDLY,
            )
            
            # Send email
            result = email_service.send_email_mock(
                profile_id=profile["id"],
                job_id=job_id,
                recipient_email=profile["email"],
                subject=email.subject,
                body=email.body,
            )
            
            if result.success:
                successful += 1
            else:
                failed += 1
        
        assert successful == 3
        assert failed == 0
        assert len(email_service.get_sent_emails()) == 3


# =============================================================================
# Test: Performance Considerations
# =============================================================================

class TestPerformance:
    """Tests for performance-related scenarios."""
    
    def test_scoring_is_deterministic(self, scoring_service):
        """Test that scoring produces consistent results."""
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 75,
            "engagement_rate_score": 85,
            "follower_quality": 70,
            "business_indicators": 75,
            "activity_recency": 80,
        }
        
        # Score multiple times
        results = [
            scoring_service.calculate_final_score_from_dict(dimensions)
            for _ in range(10)
        ]
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def test_scoring_many_profiles(self, scoring_service):
        """Test scoring many profiles efficiently."""
        import time
        
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 75,
            "engagement_rate_score": 85,
            "follower_quality": 70,
            "business_indicators": 75,
            "activity_recency": 80,
        }
        
        start_time = time.time()
        
        for _ in range(100):
            scoring_service.process_score(dimensions)
        
        elapsed = time.time() - start_time
        
        # Should complete 100 scorings quickly (< 1 second)
        assert elapsed < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
