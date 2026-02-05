"""
Unit tests for Discovery Job models.
"""
import pytest
from datetime import datetime


class TestDiscoveryJobModels:
    """Test suite for DiscoveryJob Pydantic models."""

    def test_discovery_job_has_required_fields(self):
        """DiscoveryJob should have user_id and status."""
        from app.models.discovery import DiscoveryJob

        job = DiscoveryJob(user_id="test-user-id")
        assert job.user_id == "test-user-id"
        assert job.status == "pending"

    def test_discovery_job_status_validation(self):
        """Status should only accept valid values."""
        from app.models.discovery import DiscoveryJob
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiscoveryJob(user_id="test", status="invalid_status")

    def test_discovery_job_reference_profiles(self):
        """Reference profiles should be a list of URLs."""
        from app.models.discovery import DiscoveryJob

        job = DiscoveryJob(
            user_id="test",
            reference_profiles=["https://instagram.com/profile1"]
        )
        assert len(job.reference_profiles) == 1

    def test_discovery_job_settings(self):
        """Settings should have proper defaults."""
        from app.models.discovery import DiscoveryJob, DiscoverySettings

        job = DiscoveryJob(user_id="test")
        assert job.settings.discovery_limit == 50
        assert job.settings.min_followers == 1000

    def test_discovery_create_request(self):
        """DiscoveryCreate should validate input."""
        from app.models.discovery import DiscoveryCreate

        request = DiscoveryCreate(
            reference_profiles=["https://instagram.com/brand1"],
            settings={"discovery_limit": 100}
        )
        assert len(request.reference_profiles) >= 1

    def test_discovery_create_max_profiles(self):
        """Should enforce max reference profiles limit."""
        from app.models.discovery import DiscoveryCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiscoveryCreate(
                reference_profiles=[f"profile{i}" for i in range(10)]
            )


class TestBrandDNAModels:
    """Test suite for Brand DNA models."""

    def test_brand_dna_has_required_fields(self):
        """BrandDNA should have job_id and analysis data."""
        from app.models.discovery import BrandDNA

        dna = BrandDNA(job_id="job-123")
        assert dna.job_id == "job-123"
        assert dna.hashtags == []

    def test_brand_dna_hashtags_list(self):
        """Hashtags should be a list of strings."""
        from app.models.discovery import BrandDNA

        dna = BrandDNA(
            job_id="job-123",
            hashtags=["fashion", "style", "ootd"]
        )
        assert len(dna.hashtags) == 3

    def test_brand_dna_embedding_vector(self):
        """Embedding should be a list of floats."""
        from app.models.discovery import BrandDNA

        dna = BrandDNA(
            job_id="job-123",
            embedding=[0.1, 0.2, 0.3]
        )
        assert len(dna.embedding) == 3
        assert all(isinstance(x, float) for x in dna.embedding)
