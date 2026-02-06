"""
Tests for Item 5: Job Creation Enhancements

TDD tests for adding keywords, hashtags, and min_score_threshold fields
to job creation.

These tests should FAIL initially, then pass after implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus, Defaults
from app.guards.auth import UserContext


# =============================================================================
# Test Fixtures
# =============================================================================

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
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_job_with_enhancements(sample_job_id, valid_user_id):
    """Create a sample job with the new enhancement fields."""
    return {
        "id": sample_job_id,
        "user_id": valid_user_id,
        "name": "Enhanced Discovery",
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        # NEW FIELDS
        "keywords": ["sustainable", "eco-friendly", "organic"],
        "hashtags": ["#sustainablefashion", "#ecofriendly"],
        "min_score_threshold": 60,
        # Standard fields
        "status": JobStatus.PENDING.value,
        "profiles_discovered": 0,
        "profiles_scored": 0,
        "error_message": None,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def mock_job_service():
    """Create a mock JobService."""
    return Mock()


@pytest.fixture
def test_app(mock_job_service, valid_user_id, sample_job_with_enhancements):
    """Create a test FastAPI app with mocked dependencies."""
    from app.services.job_service import get_job_service
    from app.guards.auth import get_current_user
    from app.guards.ownership import verify_job_owner_user_only
    
    def override_get_job_service():
        return mock_job_service
    
    def override_get_current_user():
        return UserContext(
            user_id=valid_user_id,
            email="test@example.com",
            role="authenticated"
        )
    
    def override_verify_job_owner():
        return sample_job_with_enhancements
    
    app.dependency_overrides[get_job_service] = override_get_job_service
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[verify_job_owner_user_only] = override_verify_job_owner
    
    yield app
    
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)


# =============================================================================
# Test: POST /api/jobs - Create Job with Enhancement Fields
# =============================================================================

class TestCreateJobWithEnhancements:
    """Tests for creating jobs with keywords, hashtags, and min_score_threshold."""
    
    def test_create_job_with_keywords(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test creating a job with keywords field."""
        mock_job_service.create_job.return_value = sample_job_with_enhancements
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "keywords": ["sustainable", "eco-friendly", "organic"],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify keywords field is in response
        assert "keywords" in data
        assert data["keywords"] == ["sustainable", "eco-friendly", "organic"]
        
        # Verify service was called with keywords
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert "keywords" in call_kwargs
        assert call_kwargs["keywords"] == ["sustainable", "eco-friendly", "organic"]
    
    def test_create_job_with_hashtags(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test creating a job with hashtags field."""
        mock_job_service.create_job.return_value = sample_job_with_enhancements
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "hashtags": ["#sustainablefashion", "#ecofriendly"],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify hashtags field is in response
        assert "hashtags" in data
        assert "#sustainablefashion" in data["hashtags"]
        
        # Verify service was called with hashtags
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert "hashtags" in call_kwargs
    
    def test_create_job_with_min_score_threshold(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test creating a job with min_score_threshold field."""
        mock_job_service.create_job.return_value = sample_job_with_enhancements
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "min_score_threshold": 60,
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify min_score_threshold field is in response
        assert "min_score_threshold" in data
        assert data["min_score_threshold"] == 60
        
        # Verify service was called with min_score_threshold
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert "min_score_threshold" in call_kwargs
        assert call_kwargs["min_score_threshold"] == 60
    
    def test_create_job_with_all_enhancement_fields(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test creating a job with all enhancement fields at once."""
        mock_job_service.create_job.return_value = sample_job_with_enhancements
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "name": "Enhanced Discovery",
                "keywords": ["sustainable", "eco-friendly", "organic"],
                "hashtags": ["#sustainablefashion", "#ecofriendly"],
                "min_score_threshold": 60,
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify all enhancement fields
        assert data["keywords"] == ["sustainable", "eco-friendly", "organic"]
        assert "#sustainablefashion" in data["hashtags"]
        assert data["min_score_threshold"] == 60
    
    def test_create_job_without_enhancement_fields_uses_defaults(
        self, client, mock_job_service, valid_token
    ):
        """Test that enhancement fields have sensible defaults."""
        # Response with default values
        default_job = {
            "id": str(uuid4()),
            "user_id": str(uuid4()),
            "brand_description": "A sustainable fashion brand",
            "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/reformation"],
            "follower_range_min": 5000,
            "follower_range_max": 500000,
            "discovery_limit": 50,
            "keywords": [],  # Default empty
            "hashtags": [],  # Default empty
            "min_score_threshold": 50,  # Default 50
            "status": JobStatus.PENDING.value,
            "profiles_discovered": 0,
            "profiles_scored": 0,
            "error_message": None,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
        }
        mock_job_service.create_job.return_value = default_job
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify defaults are applied
        assert data["keywords"] == []
        assert data["hashtags"] == []
        assert data["min_score_threshold"] == 50


# =============================================================================
# Test: Validation for Enhancement Fields
# =============================================================================

class TestEnhancementFieldValidation:
    """Tests for validation of the new enhancement fields."""
    
    def test_min_score_threshold_must_be_0_to_100(
        self, client, mock_job_service, valid_token
    ):
        """Test that min_score_threshold validates range 0-100."""
        # Test value > 100
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "min_score_threshold": 150,  # Invalid: > 100
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"
    
    def test_min_score_threshold_cannot_be_negative(
        self, client, mock_job_service, valid_token
    ):
        """Test that min_score_threshold cannot be negative."""
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "min_score_threshold": -10,  # Invalid: negative
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 422
    
    def test_keywords_normalized_to_lowercase(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test that keywords are normalized to lowercase."""
        # Return job with lowercase keywords
        normalized_job = {**sample_job_with_enhancements}
        normalized_job["keywords"] = ["sustainable", "eco-friendly"]
        mock_job_service.create_job.return_value = normalized_job
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "keywords": ["SUSTAINABLE", "Eco-Friendly"],  # Mixed case
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        
        # Verify service received lowercase keywords
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert call_kwargs["keywords"] == ["sustainable", "eco-friendly"]
    
    def test_hashtags_auto_prefixed_with_hash(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test that hashtags are auto-prefixed with # if missing."""
        normalized_job = {**sample_job_with_enhancements}
        normalized_job["hashtags"] = ["#sustainable", "#ecofriendly"]
        mock_job_service.create_job.return_value = normalized_job
        
        response = client.post(
            "/api/jobs",
            json={
                "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
                "reference_profiles": [
                    "https://instagram.com/everlane",
                    "https://instagram.com/reformation",
                ],
                "hashtags": ["sustainable", "ecofriendly"],  # Missing #
            },
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 201
        
        # Verify service received prefixed hashtags
        call_kwargs = mock_job_service.create_job.call_args.kwargs
        assert "#sustainable" in call_kwargs["hashtags"]
        assert "#ecofriendly" in call_kwargs["hashtags"]


# =============================================================================
# Test: GET /api/jobs/{job_id} - Job Response Includes Enhancement Fields
# =============================================================================

class TestGetJobWithEnhancements:
    """Tests for retrieving jobs with enhancement fields."""
    
    def test_get_job_includes_enhancement_fields(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test that GET job response includes all enhancement fields."""
        mock_job_service.get_job_with_profiles.return_value = {
            **sample_job_with_enhancements,
            "profiles": [],
            "brand_dna": None,
        }
        
        job_id = sample_job_with_enhancements["id"]
        response = client.get(
            f"/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify enhancement fields are in response
        assert "keywords" in data
        assert "hashtags" in data
        assert "min_score_threshold" in data
        assert data["keywords"] == ["sustainable", "eco-friendly", "organic"]
        assert data["min_score_threshold"] == 60


# =============================================================================
# Test: GET /api/jobs - List Jobs Includes Enhancement Fields
# =============================================================================

class TestListJobsWithEnhancements:
    """Tests for listing jobs with enhancement fields."""
    
    def test_list_jobs_includes_enhancement_fields(
        self, client, mock_job_service, sample_job_with_enhancements, valid_token
    ):
        """Test that list jobs response includes enhancement fields."""
        mock_job_service.list_user_jobs.return_value = {
            "jobs": [sample_job_with_enhancements],
            "total": 1,
            "limit": 20,
            "offset": 0,
        }
        
        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify first job has enhancement fields
        job = data["jobs"][0]
        assert "keywords" in job
        assert "hashtags" in job
        assert "min_score_threshold" in job


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
