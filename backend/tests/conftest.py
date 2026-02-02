"""
PartnerScout AI - Pytest Configuration and Shared Fixtures

This module provides shared fixtures used across all test modules.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus


# =============================================================================
# Application Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def client_no_raise():
    """Create a test client that doesn't raise server exceptions."""
    return TestClient(app, raise_server_exceptions=False)


# =============================================================================
# Authentication Fixtures
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
def another_user_id():
    """Generate another user ID for cross-user tests."""
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
def another_user_token(jwt_secret, another_user_id):
    """Create a token for another user (cross-user testing)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": another_user_id,
        "email": "other@example.com",
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
        "exp": now - timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def service_key():
    """Get service key for internal API authentication."""
    return settings.n8n.service_key


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_profile_id():
    """Generate a sample profile ID."""
    return str(uuid4())


@pytest.fixture
def sample_job(sample_job_id, valid_user_id):
    """Create a sample job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": valid_user_id,
        "name": "Test Discovery",
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": JobStatus.PENDING.value,
        "profiles_discovered": 0,
        "profiles_scored": 0,
        "error_message": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_profile(sample_profile_id, sample_job_id):
    """Create a sample profile dictionary."""
    return {
        "id": sample_profile_id,
        "job_id": sample_job_id,
        "username": "sample_influencer",
        "full_name": "Sample Influencer",
        "bio": "Fashion enthusiast and sustainable living advocate",
        "followers_count": 75000,
        "following_count": 500,
        "posts_count": 850,
        "is_verified": False,
        "is_business_account": True,
        "profile_pic_url": "https://example.com/pic.jpg",
        "status": ProfileStatus.NEW.value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_profiles(sample_job_id):
    """Create sample profile data list."""
    return [
        {
            "id": str(uuid4()),
            "job_id": sample_job_id,
            "username": "profile1",
            "full_name": "Profile One",
            "followers_count": 50000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 85,
            "contact_email": "profile1@example.com",
        },
        {
            "id": str(uuid4()),
            "job_id": sample_job_id,
            "username": "profile2",
            "full_name": "Profile Two",
            "followers_count": 75000,
            "status": ProfileStatus.SCORED.value,
            "final_score": 72,
            "contact_email": None,
        },
    ]


@pytest.fixture
def valid_create_job_payload():
    """Create a valid job creation payload."""
    return {
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
    }


@pytest.fixture
def full_create_job_payload():
    """Create a job creation payload with all fields."""
    return {
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
            "https://instagram.com/patagonia",
        ],
        "name": "Sustainable Fashion Discovery",
        "follower_range_min": 10000,
        "follower_range_max": 200000,
        "discovery_limit": 30,
    }


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_job_repo():
    """Create a mock job repository."""
    return Mock()


@pytest.fixture
def mock_profile_repo():
    """Create a mock profile repository."""
    return Mock()


@pytest.fixture
def mock_job_service():
    """Create a mock job service."""
    return Mock()


@pytest.fixture
def mock_email_service():
    """Create a mock email service."""
    return Mock()


# =============================================================================
# Helper Functions
# =============================================================================

def auth_headers(token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {token}"}


def service_headers(key: str) -> dict:
    """Create service key headers."""
    return {"X-Service-Key": key}
