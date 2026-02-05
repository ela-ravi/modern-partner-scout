"""
Integration tests for database layer.
Tests real database operations with SQLite.
"""
import pytest
import tempfile
import os


@pytest.fixture
def sqlite_client():
    """Create SQLite client with temp database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    from app.db.sqlite_client import SQLiteClient
    client = SQLiteClient(path)

    yield client

    os.unlink(path)


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_full_discovery_workflow(self, sqlite_client):
        """Test complete discovery job workflow."""
        from app.repositories.discovery_repository import DiscoveryJobRepository, BrandDNARepository
        from app.repositories.profile_repository import ProfileRepository, ProfileScoreRepository

        job_repo = DiscoveryJobRepository(sqlite_client)
        dna_repo = BrandDNARepository(sqlite_client)
        profile_repo = ProfileRepository(sqlite_client)
        score_repo = ProfileScoreRepository(sqlite_client)

        # 1. Create discovery job
        job = job_repo.create({
            "user_id": "user-123",
            "status": "pending",
            "reference_profiles": '["https://instagram.com/brand"]',
            "settings": "{}"
        })
        assert job.id is not None

        # 2. Add brand DNA
        dna = dna_repo.create({
            "job_id": str(job.id),
            "hashtags": '["fashion", "style"]',
            "keywords": '["trendy", "modern"]',
            "embedding": "[]"
        })
        assert dna.job_id == str(job.id)

        # 3. Discover profiles
        profile = profile_repo.create({
            "job_id": str(job.id),
            "username": "influencer1",
            "follower_count": 50000,
            "status": "new"
        })
        assert profile.username == "influencer1"

        # 4. Score profile
        score = score_repo.create({
            "profile_id": str(profile.id),
            "overall_score": 85,
            "category_scores": '{"brand_alignment": 90}'
        })
        assert score.overall_score == 85

        # 5. Update job status
        updated_job = job_repo.update_status(str(job.id), "completed")
        assert updated_job.status.value == "completed"

        # 6. Query profiles
        profiles = profile_repo.get_by_job(str(job.id))
        assert len(profiles) == 1
