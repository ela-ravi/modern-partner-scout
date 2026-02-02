"""
PartnerScout AI - Pydantic Models Tests

Unit tests for all Pydantic model validation.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError


# =============================================================================
# Test Job Models
# =============================================================================

class TestCreateJobRequest:
    """Tests for CreateJobRequest model."""
    
    def test_valid_create_job_request(self):
        """Test valid job creation request."""
        from app.models.job import CreateJobRequest
        
        request = CreateJobRequest(
            brand_description="A sustainable fashion brand focusing on eco-friendly materials",
            reference_profiles=[
                "https://instagram.com/everlane",
                "https://instagram.com/reformation"
            ]
        )
        
        assert request.brand_description.startswith("A sustainable")
        assert len(request.reference_profiles) == 2
        assert request.follower_range_min == 5000  # Default
        assert request.discovery_limit == 50  # Default
    
    def test_create_job_request_with_all_fields(self):
        """Test job creation with all optional fields."""
        from app.models.job import CreateJobRequest
        
        request = CreateJobRequest(
            brand_description="Tech startup focused on productivity tools",
            reference_profiles=[
                "https://instagram.com/notion",
                "https://instagram.com/figma",
                "https://instagram.com/linear"
            ],
            name="Q1 2024 Discovery",
            follower_range_min=10000,
            follower_range_max=250000,
            discovery_limit=75
        )
        
        assert request.name == "Q1 2024 Discovery"
        assert request.follower_range_min == 10000
        assert request.follower_range_max == 250000
        assert request.discovery_limit == 75
    
    def test_create_job_request_too_few_profiles(self):
        """Test that fewer than 2 profiles raises validation error."""
        from app.models.job import CreateJobRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateJobRequest(
                brand_description="Test brand description here",
                reference_profiles=["https://instagram.com/test"]  # Only 1 profile
            )
        
        assert "reference_profiles" in str(exc_info.value)
    
    def test_create_job_request_invalid_urls(self):
        """Test that non-Instagram URLs raise validation error."""
        from app.models.job import CreateJobRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateJobRequest(
                brand_description="Test brand description here",
                reference_profiles=[
                    "https://twitter.com/test",
                    "https://facebook.com/test"
                ]
            )
        
        assert "Instagram URL" in str(exc_info.value)
    
    def test_create_job_request_short_description(self):
        """Test that description under 10 chars raises error."""
        from app.models.job import CreateJobRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateJobRequest(
                brand_description="Short",  # Too short
                reference_profiles=[
                    "https://instagram.com/test1",
                    "https://instagram.com/test2"
                ]
            )
        
        assert "brand_description" in str(exc_info.value)
    
    def test_create_job_request_invalid_follower_range(self):
        """Test that min >= max followers raises error."""
        from app.models.job import CreateJobRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateJobRequest(
                brand_description="Valid brand description here",
                reference_profiles=[
                    "https://instagram.com/test1",
                    "https://instagram.com/test2"
                ],
                follower_range_min=100000,
                follower_range_max=50000  # Max < Min
            )
        
        assert "follower_range_min" in str(exc_info.value)


class TestUpdateJobRequest:
    """Tests for UpdateJobRequest model."""
    
    def test_valid_update_name(self):
        """Test updating just the name."""
        from app.models.job import UpdateJobRequest
        
        request = UpdateJobRequest(name="New Job Name")
        assert request.name == "New Job Name"
        assert request.brand_description is None
    
    def test_valid_update_description(self):
        """Test updating just the description."""
        from app.models.job import UpdateJobRequest
        
        request = UpdateJobRequest(
            brand_description="Updated brand description with more details"
        )
        assert request.brand_description is not None
        assert request.name is None
    
    def test_update_requires_at_least_one_field(self):
        """Test that at least one field must be provided."""
        from app.models.job import UpdateJobRequest
        
        with pytest.raises(ValidationError) as exc_info:
            UpdateJobRequest()  # No fields provided
        
        assert "At least one field" in str(exc_info.value)


class TestJobResponseModels:
    """Tests for Job response models."""
    
    def test_job_model_from_dict(self):
        """Test creating Job model from dictionary."""
        from app.models.job import Job
        from app.core.constants import JobStatus
        
        job_data = {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "brand_description": "Test brand",
            "reference_profiles": ["https://instagram.com/test"],
            "follower_range_min": 5000,
            "follower_range_max": 500000,
            "discovery_limit": 50,
            "status": "pending",
            "profiles_discovered": 0,
            "profiles_scored": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        job = Job(**job_data)
        assert job.status == JobStatus.PENDING
        assert isinstance(job.id, UUID)
    
    def test_job_analytics_model(self):
        """Test JobAnalytics model."""
        from app.models.job import JobAnalytics
        
        analytics = JobAnalytics(
            job_id=uuid4(),
            total_profiles=50,
            done_profiles=45,
            avg_score=72,
            max_score=95,
            min_score=35,
            profiles_with_email=30
        )
        
        assert analytics.total_profiles == 50
        assert analytics.avg_score == 72


# =============================================================================
# Test Profile Models
# =============================================================================

class TestProfileModels:
    """Tests for Profile models."""
    
    def test_profile_base_model(self):
        """Test basic profile model."""
        from app.models.profile import ProfileBase
        
        profile = ProfileBase(
            instagram_url="https://instagram.com/testuser",
            username="testuser",
            full_name="Test User",
            followers_count=50000,
            following_count=1000,
            is_verified=True
        )
        
        assert profile.username == "testuser"
        assert profile.followers_count == 50000
        assert profile.is_verified is True
    
    def test_complete_profile_model(self):
        """Test CompleteProfile with all fields."""
        from app.models.profile import CompleteProfile
        from app.core.constants import ProfileStatus
        
        profile = CompleteProfile(
            id=uuid4(),
            job_id=uuid4(),
            instagram_url="https://instagram.com/testuser",
            username="testuser",
            followers_count=75000,
            status=ProfileStatus.SCORED,
            created_at=datetime.now(timezone.utc),
            final_score=85,
            recommendation="highly_recommended",
            contact_email="test@example.com"
        )
        
        assert profile.final_score == 85
        assert profile.contact_email == "test@example.com"


class TestProfileScoreModels:
    """Tests for ProfileScore models."""
    
    def test_valid_profile_score(self):
        """Test valid profile score creation."""
        from app.models.profile import ProfileScore
        
        score = ProfileScore(
            id=uuid4(),
            profile_id=uuid4(),
            visual_aesthetic_match=85,
            content_theme_alignment=90,
            engagement_rate_score=75,
            follower_quality=80,
            business_indicators=70,
            activity_recency=95,
            final_score=82,
            recommendation="recommended",
            reasoning={"overall": "Good match for the brand"},
            created_at=datetime.now(timezone.utc)
        )
        
        assert score.final_score == 82
        assert score.recommendation == "recommended"
    
    def test_score_validation_range(self):
        """Test that scores must be 0-100."""
        from app.models.profile import CreateProfileScoreRequest
        
        with pytest.raises(ValidationError):
            CreateProfileScoreRequest(
                profile_id=uuid4(),
                final_score=150  # Over 100
            )
    
    def test_score_recommendation_validation(self):
        """Test recommendation value validation."""
        from app.models.profile import CreateProfileScoreRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateProfileScoreRequest(
                profile_id=uuid4(),
                final_score=75,
                recommendation="invalid_value"
            )
        
        assert "recommendation" in str(exc_info.value)


class TestProfileContactModels:
    """Tests for ProfileContact models."""
    
    def test_valid_contact(self):
        """Test valid contact creation."""
        from app.models.profile import ProfileContact
        
        contact = ProfileContact(
            id=uuid4(),
            profile_id=uuid4(),
            email="contact@brand.com",
            email_source="business_email",
            website="https://brand.com",
            created_at=datetime.now(timezone.utc)
        )
        
        assert contact.email == "contact@brand.com"
        assert contact.email_source == "business_email"
    
    def test_email_source_validation(self):
        """Test email source must be valid value."""
        from app.models.profile import CreateProfileContactRequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateProfileContactRequest(
                profile_id=uuid4(),
                email="test@test.com",
                email_source="invalid_source"
            )
        
        assert "email_source" in str(exc_info.value)


# =============================================================================
# Test Brand Models
# =============================================================================

class TestBrandDNAModels:
    """Tests for BrandDNA models."""
    
    def test_valid_brand_dna(self):
        """Test valid BrandDNA creation."""
        from app.models.brand import BrandDNA
        
        brand_dna = BrandDNA(
            id=uuid4(),
            job_id=uuid4(),
            hashtags=["#sustainable", "#fashion", "#eco"],
            keywords=["sustainable", "ethical", "organic"],
            visual_themes=["minimalist", "earth tones"],
            content_pillars=["sustainability", "style tips"],
            target_audience_description="Eco-conscious millennials",
            created_at=datetime.now(timezone.utc)
        )
        
        assert len(brand_dna.hashtags) == 3
        assert "sustainable" in brand_dna.keywords
    
    def test_brand_dna_list_normalization(self):
        """Test that lists are normalized (whitespace stripped)."""
        from app.models.brand import CreateBrandDNARequest
        
        request = CreateBrandDNARequest(
            job_id=uuid4(),
            hashtags=["  #test  ", "#hello", "  ", ""],
            keywords=["  keyword1  ", "keyword2"]
        )
        
        assert "#test" in request.hashtags
        assert "" not in request.hashtags  # Empty strings removed
        assert "keyword1" in request.keywords
    
    def test_embedding_vector_validation(self):
        """Test embedding vector must have 1536 dimensions."""
        from app.models.brand import CreateBrandDNARequest
        
        with pytest.raises(ValidationError) as exc_info:
            CreateBrandDNARequest(
                job_id=uuid4(),
                embedding_vector=[0.1] * 100  # Only 100 dims, need 1536
            )
        
        assert "1536" in str(exc_info.value)
    
    def test_valid_embedding_vector(self):
        """Test valid embedding vector passes."""
        from app.models.brand import CreateBrandDNARequest
        
        request = CreateBrandDNARequest(
            job_id=uuid4(),
            hashtags=["#test"],
            embedding_vector=[0.01] * 1536
        )
        
        assert len(request.embedding_vector) == 1536


# =============================================================================
# Test Agent Models
# =============================================================================

class TestAgentModels:
    """Tests for Agent models."""
    
    def test_brand_analyzer_request(self):
        """Test BrandAnalyzerRequest model."""
        from app.models.agent import BrandAnalyzerRequest
        
        request = BrandAnalyzerRequest(job_id=uuid4())
        assert request.max_posts_per_profile == 20  # Default
    
    def test_discovery_request_hashtag_normalization(self):
        """Test hashtags are normalized with # prefix."""
        from app.models.agent import DiscoveryRequest
        
        request = DiscoveryRequest(
            job_id=uuid4(),
            hashtags=["sustainable", "#fashion", "eco"]  # Mixed format
        )
        
        assert all(h.startswith("#") for h in request.hashtags)
        assert "#sustainable" in request.hashtags
    
    def test_discovery_request_requires_hashtags(self):
        """Test that at least one hashtag is required."""
        from app.models.agent import DiscoveryRequest
        
        with pytest.raises(ValidationError):
            DiscoveryRequest(
                job_id=uuid4(),
                hashtags=[]  # Empty
            )
    
    def test_scorer_response_model(self):
        """Test ScorerResponse model."""
        from app.models.agent import ScorerResponse
        
        response = ScorerResponse(
            profile_id=uuid4(),
            job_id=uuid4(),
            visual_aesthetic_match=85,
            content_theme_alignment=90,
            engagement_rate_score=75,
            follower_quality=80,
            business_indicators=70,
            activity_recency=95,
            final_score=82,
            recommendation="recommended"
        )
        
        assert response.final_score == 82


# =============================================================================
# Test Email Models
# =============================================================================

class TestEmailModels:
    """Tests for Email models."""
    
    def test_generate_email_request(self):
        """Test GenerateEmailRequest model."""
        from app.models.email import GenerateEmailRequest, EmailTone
        
        request = GenerateEmailRequest(
            profile_id=uuid4(),
            job_id=uuid4(),
            tone=EmailTone.FRIENDLY
        )
        
        assert request.tone == EmailTone.FRIENDLY
        assert request.include_profile_compliment is True  # Default
    
    def test_email_tone_enum(self):
        """Test EmailTone enum values."""
        from app.models.email import EmailTone
        
        assert EmailTone.PROFESSIONAL.value == "professional"
        assert EmailTone.FRIENDLY.value == "friendly"
        assert EmailTone.CASUAL.value == "casual"
    
    def test_send_email_request_validation(self):
        """Test SendEmailRequest email validation."""
        from app.models.email import SendEmailRequest
        
        # Valid email
        request = SendEmailRequest(
            profile_id=uuid4(),
            job_id=uuid4(),
            recipient_email="valid@email.com",
            subject="Partnership Opportunity",
            body="Hello, I'd like to discuss a partnership..."
        )
        assert request.recipient_email == "valid@email.com"
        
        # Invalid email should fail
        with pytest.raises(ValidationError):
            SendEmailRequest(
                profile_id=uuid4(),
                job_id=uuid4(),
                recipient_email="invalid-email",
                subject="Test",
                body="Test body content here"
            )


# =============================================================================
# Test Status Models
# =============================================================================

class TestStatusModels:
    """Tests for Status models."""
    
    def test_update_job_status_request(self):
        """Test UpdateJobStatusRequest model."""
        from app.models.status import UpdateJobStatusRequest
        from app.core.constants import JobStatus
        
        request = UpdateJobStatusRequest(status=JobStatus.ANALYZING)
        assert request.status == JobStatus.ANALYZING
    
    def test_update_job_status_failed_requires_message(self):
        """Test that failed status requires error message."""
        from app.models.status import UpdateJobStatusRequest
        from app.core.constants import JobStatus
        
        with pytest.raises(ValidationError) as exc_info:
            UpdateJobStatusRequest(status=JobStatus.FAILED)
        
        assert "error_message" in str(exc_info.value)
        
        # With message should work
        request = UpdateJobStatusRequest(
            status=JobStatus.FAILED,
            error_message="Rate limit exceeded"
        )
        assert request.error_message == "Rate limit exceeded"
    
    def test_job_progress_status_calculation(self):
        """Test JobProgressStatus progress calculation."""
        from app.models.status import JobProgressStatus
        from app.core.constants import JobStatus
        
        progress = JobProgressStatus.calculate_progress(
            job_id=uuid4(),
            status=JobStatus.SCORING,
            profiles_discovered=50,
            profiles_scored=25,
            discovery_limit=50
        )
        
        assert progress.current_phase == "scoring"
        assert progress.scoring_progress == 50.0  # 25/50 = 50%
        assert progress.discovery_progress == 100.0  # 50/50 = 100%
    
    def test_batch_update_profile_status(self):
        """Test BatchUpdateProfileStatusRequest model."""
        from app.models.status import BatchUpdateProfileStatusRequest
        from app.core.constants import ProfileStatus
        
        request = BatchUpdateProfileStatusRequest(
            profile_ids=[uuid4() for _ in range(5)],
            status=ProfileStatus.PROCESSING
        )
        
        assert len(request.profile_ids) == 5
        assert request.status == ProfileStatus.PROCESSING


class TestHealthModels:
    """Tests for Health status models."""
    
    def test_health_status(self):
        """Test HealthStatus model."""
        from app.models.status import HealthStatus
        
        health = HealthStatus(
            status="healthy",
            database="connected",
            llm_service="ready",
            active_jobs=5
        )
        
        assert health.status == "healthy"
        assert health.active_jobs == 5
    
    def test_detailed_health_status(self):
        """Test DetailedHealthStatus model."""
        from app.models.status import DetailedHealthStatus
        
        health = DetailedHealthStatus(
            status="healthy",
            uptime_seconds=3600.5,
            memory_usage_mb=512.0,
            jobs_completed_24h=25,
            profiles_scored_24h=500
        )
        
        assert health.uptime_seconds == 3600.5
        assert health.jobs_completed_24h == 25


# =============================================================================
# Test Module Exports
# =============================================================================

class TestModuleExports:
    """Tests for module exports."""
    
    def test_all_job_models_exported(self):
        """Test all job models are exported from __init__."""
        from app.models import (
            CreateJobRequest,
            UpdateJobRequest,
            Job,
            JobSummary,
            JobWithProfiles,
            JobAnalytics,
        )
        
        assert CreateJobRequest is not None
        assert Job is not None
    
    def test_all_profile_models_exported(self):
        """Test all profile models are exported from __init__."""
        from app.models import (
            Profile,
            ProfileScore,
            ProfileContact,
            CompleteProfile,
        )
        
        assert Profile is not None
        assert CompleteProfile is not None
    
    def test_all_brand_models_exported(self):
        """Test all brand models are exported from __init__."""
        from app.models import BrandDNA, CreateBrandDNARequest
        
        assert BrandDNA is not None
    
    def test_all_agent_models_exported(self):
        """Test all agent models are exported from __init__."""
        from app.models import (
            BrandAnalyzerRequest,
            DiscoveryRequest,
            ScorerRequest,
            ScorerResponse,
        )
        
        assert BrandAnalyzerRequest is not None
        assert ScorerResponse is not None
    
    def test_all_email_models_exported(self):
        """Test all email models are exported from __init__."""
        from app.models import (
            EmailTone,
            GenerateEmailRequest,
            SendEmailRequest,
        )
        
        assert EmailTone is not None
    
    def test_all_status_models_exported(self):
        """Test all status models are exported from __init__."""
        from app.models import (
            UpdateJobStatusRequest,
            JobProgressStatus,
            HealthStatus,
        )
        
        assert UpdateJobStatusRequest is not None
        assert HealthStatus is not None
