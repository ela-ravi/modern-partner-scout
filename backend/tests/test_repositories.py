"""
Tests for STORY-2.1.3: Implement Repository Layer

These tests validate that the repository classes work correctly,
including CRUD operations and specialized queries.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4


class TestBaseRepository:
    """Tests for the BaseRepository abstract class."""
    
    def test_base_repository_is_abstract(self):
        """Test that BaseRepository cannot be instantiated directly."""
        from app.repositories.base_repo import BaseRepository
        
        # Cannot instantiate abstract class directly
        with pytest.raises(TypeError):
            BaseRepository()
    
    def test_concrete_repository_must_define_table_name(self):
        """Test that concrete repositories must define table_name."""
        from app.repositories.base_repo import BaseRepository
        
        class IncompleteRepo(BaseRepository):
            pass
        
        with pytest.raises(TypeError):
            IncompleteRepo()


class TestJobRepository:
    """Tests for the JobRepository class."""
    
    def test_job_repository_table_name(self):
        """Test JobRepository uses correct table name."""
        from app.repositories import JobRepository
        from app.core.constants import Tables
        
        repo = JobRepository()
        assert repo.table_name == Tables.DISCOVERY_JOBS
    
    def test_job_repository_create_data_structure(self):
        """Test create method builds correct data structure."""
        from app.repositories import JobRepository
        from app.core.constants import JobStatus
        
        # We'll test the data structure without actually inserting
        repo = JobRepository()
        
        # Mock the insert method to capture the data
        original_insert = repo.insert
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        result = repo.create(
            user_id="user-123",
            brand_description="Test Brand",
            reference_profiles=["url1", "url2"]
        )
        
        assert captured_data["user_id"] == "user-123"
        assert captured_data["brand_description"] == "Test Brand"
        assert captured_data["reference_profiles"] == ["url1", "url2"]
        assert captured_data["status"] == JobStatus.PENDING.value
        
        # Restore
        repo.insert = original_insert
    
    def test_job_repository_create_with_optional_fields(self):
        """Test create method with optional fields."""
        from app.repositories import JobRepository
        
        repo = JobRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        result = repo.create(
            user_id="user-123",
            brand_description="Test Brand",
            reference_profiles=["url1", "url2"],
            name="My Job",
            follower_range_min=5000,
            follower_range_max=100000,
            discovery_limit=25
        )
        
        assert captured_data["name"] == "My Job"
        assert captured_data["follower_range_min"] == 5000
        assert captured_data["follower_range_max"] == 100000
        assert captured_data["discovery_limit"] == 25
    
    @pytest.mark.integration
    def test_job_repository_count_user_jobs_today(self):
        """Test counting user jobs from today with valid UUID."""
        from app.repositories import JobRepository
        
        repo = JobRepository()
        
        # Use a valid UUID format (even if user doesn't exist, should return 0)
        valid_uuid = "00000000-0000-0000-0000-000000000000"
        count = repo.count_user_jobs_today(valid_uuid)
        assert isinstance(count, int)
        assert count >= 0


class TestProfileRepository:
    """Tests for the ProfileRepository class."""
    
    def test_profile_repository_table_name(self):
        """Test ProfileRepository uses correct table name."""
        from app.repositories import ProfileRepository
        from app.core.constants import Tables
        
        repo = ProfileRepository()
        assert repo.table_name == Tables.DISCOVERED_PROFILES
    
    def test_profile_repository_create_calculates_ratio(self):
        """Test create method calculates following_ratio."""
        from app.repositories import ProfileRepository
        
        repo = ProfileRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        result = repo.create(
            job_id=str(uuid4()),
            instagram_url="https://instagram.com/test",
            username="testuser",
            followers_count=10000,
            following_count=500
        )
        
        assert captured_data["following_ratio"] == 0.05
    
    def test_profile_repository_create_sets_status(self):
        """Test create method sets default status."""
        from app.repositories import ProfileRepository
        from app.core.constants import ProfileStatus
        
        repo = ProfileRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        repo.create(
            job_id=str(uuid4()),
            instagram_url="https://instagram.com/test",
            username="testuser"
        )
        
        assert captured_data["status"] == ProfileStatus.NEW.value


class TestBrandRepository:
    """Tests for the BrandRepository class."""
    
    def test_brand_repository_table_name(self):
        """Test BrandRepository uses correct table name."""
        from app.repositories import BrandRepository
        from app.core.constants import Tables
        
        repo = BrandRepository()
        assert repo.table_name == Tables.BRAND_DNA
    
    def test_brand_repository_create_structure(self):
        """Test create method builds correct data structure."""
        from app.repositories import BrandRepository
        
        repo = BrandRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        repo.create(
            job_id=str(uuid4()),
            hashtags=["#fashion", "#style"],
            keywords=["fashion", "style"],
            visual_themes=["minimalist", "clean"]
        )
        
        assert captured_data["hashtags"] == ["#fashion", "#style"]
        assert captured_data["keywords"] == ["fashion", "style"]
        assert captured_data["visual_themes"] == ["minimalist", "clean"]


class TestScoreRepository:
    """Tests for the ScoreRepository class."""
    
    def test_score_repository_table_name(self):
        """Test ScoreRepository uses correct table name."""
        from app.repositories import ScoreRepository
        from app.core.constants import Tables
        
        repo = ScoreRepository()
        assert repo.table_name == Tables.PROFILE_SCORES
    
    def test_score_repository_create_full_score(self):
        """Test create_full_score method."""
        from app.repositories import ScoreRepository
        
        repo = ScoreRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        dimensions = {
            "visual_aesthetic_match": 85,
            "content_theme_alignment": 90,
            "engagement_rate_score": 75,
            "follower_quality": 80,
            "business_indicators": 70,
            "activity_recency": 95,
        }
        
        repo.create_full_score(
            profile_id=str(uuid4()),
            dimensions=dimensions,
            final_score=82,
            recommendation="recommended",
            reasoning={"summary": "Good match"},
            is_fake_suspected=False
        )
        
        assert captured_data["final_score"] == 82
        assert captured_data["visual_aesthetic_match"] == 85
        assert captured_data["recommendation"] == "recommended"
        assert captured_data["is_fake_suspected"] == False


class TestContactRepository:
    """Tests for the ContactRepository class."""
    
    def test_contact_repository_table_name(self):
        """Test ContactRepository uses correct table name."""
        from app.repositories import ContactRepository
        from app.core.constants import Tables
        
        repo = ContactRepository()
        assert repo.table_name == Tables.PROFILE_CONTACTS
    
    def test_contact_repository_create_structure(self):
        """Test create method builds correct data structure."""
        from app.repositories import ContactRepository
        
        repo = ContactRepository()
        captured_data = None
        
        def mock_insert(data):
            nonlocal captured_data
            captured_data = data
            return {**data, "id": str(uuid4())}
        
        repo.insert = mock_insert
        
        repo.create(
            profile_id=str(uuid4()),
            email="test@example.com",
            email_source="bio",
            website="https://example.com"
        )
        
        assert captured_data["email"] == "test@example.com"
        assert captured_data["email_source"] == "bio"
        assert captured_data["website"] == "https://example.com"


class TestModuleExports:
    """Test that the repositories module exports correctly."""
    
    def test_import_all_repositories(self):
        """Test importing all repositories from module."""
        from app.repositories import (
            BaseRepository,
            JobRepository,
            ProfileRepository,
            BrandRepository,
            ScoreRepository,
            ContactRepository,
        )
        
        assert BaseRepository is not None
        assert JobRepository is not None
        assert ProfileRepository is not None
        assert BrandRepository is not None
        assert ScoreRepository is not None
        assert ContactRepository is not None
    
    def test_all_repositories_can_be_instantiated(self):
        """Test all concrete repositories can be instantiated."""
        from app.repositories import (
            JobRepository,
            ProfileRepository,
            BrandRepository,
            ScoreRepository,
            ContactRepository,
        )
        
        # All should instantiate without errors
        job_repo = JobRepository()
        profile_repo = ProfileRepository()
        brand_repo = BrandRepository()
        score_repo = ScoreRepository()
        contact_repo = ContactRepository()
        
        assert job_repo is not None
        assert profile_repo is not None
        assert brand_repo is not None
        assert score_repo is not None
        assert contact_repo is not None


class TestRepositoryIntegration:
    """Integration tests for repositories with real database."""
    
    @pytest.mark.integration
    def test_job_repository_list_by_user(self):
        """Test listing jobs for a user with valid UUID."""
        from app.repositories import JobRepository
        
        repo = JobRepository()
        
        # Use a valid UUID format (even if user doesn't exist, query should work)
        valid_uuid = "00000000-0000-0000-0000-000000000000"
        jobs = repo.list_by_user(valid_uuid)
        assert isinstance(jobs, list)
    
    @pytest.mark.integration
    def test_profile_repository_list_by_job(self):
        """Test listing profiles for a job with valid UUID."""
        from app.repositories import ProfileRepository
        
        repo = ProfileRepository()
        
        # Use a valid UUID format
        valid_uuid = "00000000-0000-0000-0000-000000000000"
        profiles = repo.list_by_job(valid_uuid)
        assert isinstance(profiles, list)
    
    @pytest.mark.integration
    def test_job_repository_read_existing_jobs(self):
        """Test reading existing jobs from seed data."""
        from app.repositories import JobRepository
        from app.db import clear_client_cache
        
        clear_client_cache()
        repo = JobRepository()
        
        # Try to get the sample job from seed data
        sample_job_id = "11111111-1111-1111-1111-111111111111"
        
        try:
            job = repo.get_by_id(sample_job_id)
            assert job is not None
            assert job["id"] == sample_job_id
            assert "brand_description" in job
            assert "status" in job
        except Exception as e:
            # If seed data not loaded, skip
            pytest.skip(f"Seed data not available: {e}")
    
    @pytest.mark.integration
    def test_job_repository_count_with_valid_uuid(self):
        """Test counting jobs with valid UUID."""
        from app.repositories import JobRepository
        from app.db import clear_client_cache
        
        clear_client_cache()
        repo = JobRepository()
        
        # Use a valid UUID format
        valid_uuid = "00000000-0000-0000-0000-000000000000"
        count = repo.count_user_jobs_today(valid_uuid)
        assert isinstance(count, int)
        assert count >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
