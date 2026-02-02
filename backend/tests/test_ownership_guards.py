"""
Tests for Ownership Guards

Tests for STORY-2.2.2: Implement Ownership Guards
- JobOwnerGuard: Verifies job ownership
- ProfileOwnerGuard: Verifies profile ownership (via job)
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.core.constants import ErrorCodes, HttpStatus
from app.core.exceptions import ForbiddenError, JobNotFoundError, ProfileNotFoundError
from app.guards.auth import UserContext, ServiceContext, create_test_token
from app.guards.ownership import (
    OwnershipGuard,
    JobOwnerGuard,
    ProfileOwnerGuard,
    verify_job_owner,
    verify_job_owner_user_only,
    verify_profile_owner,
    verify_profile_owner_user_only,
    reset_guards,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return str(uuid4())


@pytest.fixture
def other_user_id():
    """Generate a different test user ID."""
    return str(uuid4())


@pytest.fixture
def job_id():
    """Generate a test job ID."""
    return str(uuid4())


@pytest.fixture
def profile_id():
    """Generate a test profile ID."""
    return str(uuid4())


@pytest.fixture
def user_context(user_id):
    """Create a test user context."""
    return UserContext(
        user_id=user_id,
        email="test@example.com",
        role="authenticated",
    )


@pytest.fixture
def other_user_context(other_user_id):
    """Create a different test user context."""
    return UserContext(
        user_id=other_user_id,
        email="other@example.com",
        role="authenticated",
    )


@pytest.fixture
def service_context():
    """Create a test service context."""
    return ServiceContext(
        service_name="n8n",
        is_admin=True,
    )


@pytest.fixture
def sample_job(user_id, job_id):
    """Create a sample job dictionary."""
    return {
        "id": job_id,
        "user_id": user_id,
        "brand_description": "Test brand",
        "reference_profiles": ["https://instagram.com/test1"],
        "status": "pending",
    }


@pytest.fixture
def sample_profile(job_id, profile_id):
    """Create a sample profile dictionary."""
    return {
        "id": profile_id,
        "job_id": job_id,
        "username": "test_user",
        "instagram_url": "https://instagram.com/test_user",
        "followers_count": 10000,
        "status": "new",
    }


@pytest.fixture
def mock_job_repo(sample_job):
    """Create a mock job repository."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = sample_job
    return mock_repo


@pytest.fixture
def mock_profile_repo(sample_profile):
    """Create a mock profile repository."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = sample_profile
    return mock_repo


@pytest.fixture(autouse=True)
def reset_guard_singletons():
    """Reset guard singletons before each test."""
    reset_guards()
    yield
    reset_guards()


# =============================================================================
# JobOwnerGuard Unit Tests
# =============================================================================

class TestJobOwnerGuard:
    """Tests for JobOwnerGuard class."""
    
    def test_resource_type(self):
        """Test that resource_type is 'job'."""
        with patch("app.guards.ownership.JobRepository"):
            guard = JobOwnerGuard()
            assert guard.resource_type == "job"
    
    def test_check_ownership_owner(self, user_id, job_id, sample_job):
        """Test check_ownership returns True for owner."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            result = guard.check_ownership(job_id, user_id)
            
            assert result is True
            mock_instance.get_by_id.assert_called_once_with(job_id)
    
    def test_check_ownership_not_owner(self, other_user_id, job_id, sample_job):
        """Test check_ownership returns False for non-owner."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            result = guard.check_ownership(job_id, other_user_id)
            
            assert result is False
    
    def test_check_ownership_job_not_found(self, user_id, job_id):
        """Test check_ownership raises JobNotFoundError when job doesn't exist."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.side_effect = JobNotFoundError(job_id)
            
            guard = JobOwnerGuard()
            
            with pytest.raises(JobNotFoundError) as exc_info:
                guard.check_ownership(job_id, user_id)
            
            assert job_id in str(exc_info.value)
    
    def test_get_job_for_user_success(self, user_context, job_id, sample_job):
        """Test get_job_for_user returns job for owner."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            result = guard.get_job_for_user(job_id, user_context)
            
            assert result == sample_job
    
    def test_get_job_for_user_forbidden(self, other_user_context, job_id, sample_job):
        """Test get_job_for_user raises ForbiddenError for non-owner."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            
            with pytest.raises(ForbiddenError) as exc_info:
                guard.get_job_for_user(job_id, other_user_context)
            
            assert exc_info.value.code == ErrorCodes.FORBIDDEN
            assert "job" in exc_info.value.message.lower()
    
    def test_get_job_for_service_always_allowed(self, service_context, job_id, sample_job):
        """Test get_job_for_user allows service context to access any job."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            result = guard.get_job_for_user(job_id, service_context)
            
            assert result == sample_job


# =============================================================================
# ProfileOwnerGuard Unit Tests
# =============================================================================

class TestProfileOwnerGuard:
    """Tests for ProfileOwnerGuard class."""
    
    def test_resource_type(self):
        """Test that resource_type is 'profile'."""
        with patch("app.guards.ownership.ProfileRepository"), \
             patch("app.guards.ownership.JobRepository"):
            guard = ProfileOwnerGuard()
            assert guard.resource_type == "profile"
    
    def test_check_ownership_owner(self, user_id, profile_id, sample_profile, sample_job):
        """Test check_ownership returns True for owner."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            result = guard.check_ownership(profile_id, user_id)
            
            assert result is True
    
    def test_check_ownership_not_owner(self, other_user_id, profile_id, sample_profile, sample_job):
        """Test check_ownership returns False for non-owner."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            result = guard.check_ownership(profile_id, other_user_id)
            
            assert result is False
    
    def test_check_ownership_profile_not_found(self, user_id, profile_id):
        """Test check_ownership raises ProfileNotFoundError when profile doesn't exist."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository"):
            mock_instance = MockProfileRepo.return_value
            mock_instance.get_by_id.side_effect = ProfileNotFoundError(profile_id)
            
            guard = ProfileOwnerGuard()
            
            with pytest.raises(ProfileNotFoundError) as exc_info:
                guard.check_ownership(profile_id, user_id)
            
            assert profile_id in str(exc_info.value)
    
    def test_get_profile_for_user_success(self, user_context, profile_id, sample_profile, sample_job):
        """Test get_profile_for_user returns profile for owner."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            result = guard.get_profile_for_user(profile_id, user_context)
            
            assert result == sample_profile
    
    def test_get_profile_for_user_forbidden(self, other_user_context, profile_id, sample_profile, sample_job):
        """Test get_profile_for_user raises ForbiddenError for non-owner."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            
            with pytest.raises(ForbiddenError) as exc_info:
                guard.get_profile_for_user(profile_id, other_user_context)
            
            assert exc_info.value.code == ErrorCodes.FORBIDDEN
            assert "profile" in exc_info.value.message.lower()
    
    def test_get_profile_for_service_always_allowed(self, service_context, profile_id, sample_profile):
        """Test get_profile_for_user allows service context to access any profile."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository"):
            mock_instance = MockProfileRepo.return_value
            mock_instance.get_by_id.return_value = sample_profile
            
            guard = ProfileOwnerGuard()
            result = guard.get_profile_for_user(profile_id, service_context)
            
            assert result == sample_profile
    
    def test_check_profile_job_ownership_success(
        self, user_context, profile_id, job_id, sample_profile, sample_job
    ):
        """Test check_profile_job_ownership returns both profile and job."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            profile, job = guard.check_profile_job_ownership(
                profile_id, job_id, user_context
            )
            
            assert profile == sample_profile
            assert job == sample_job
    
    def test_check_profile_job_ownership_mismatch(
        self, user_context, profile_id, sample_profile
    ):
        """Test check_profile_job_ownership raises ForbiddenError for job mismatch."""
        wrong_job_id = str(uuid4())
        
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository"):
            mock_instance = MockProfileRepo.return_value
            mock_instance.get_by_id.return_value = sample_profile
            
            guard = ProfileOwnerGuard()
            
            with pytest.raises(ForbiddenError) as exc_info:
                guard.check_profile_job_ownership(profile_id, wrong_job_id, user_context)
            
            assert "does not belong" in exc_info.value.message


# =============================================================================
# FastAPI Integration Tests
# =============================================================================

class TestOwnershipGuardsFastAPI:
    """Integration tests for ownership guards with FastAPI."""
    
    @pytest.fixture
    def app(self, user_id, job_id, profile_id, sample_job, sample_profile):
        """Create a test FastAPI application."""
        app = FastAPI()
        
        # Mock the repositories
        with patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.ProfileRepository") as MockProfileRepo:
            
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance.get_by_id.return_value = sample_job
            mock_profile_instance.get_by_id.return_value = sample_profile
            
            @app.get("/api/jobs/{job_id}")
            async def get_job(job: dict = Depends(verify_job_owner)):
                return {"job": job}
            
            @app.get("/api/jobs/{job_id}/user-only")
            async def get_job_user_only(job: dict = Depends(verify_job_owner_user_only)):
                return {"job": job}
            
            @app.get("/api/profiles/{profile_id}")
            async def get_profile(profile: dict = Depends(verify_profile_owner)):
                return {"profile": profile}
            
            @app.get("/api/profiles/{profile_id}/user-only")
            async def get_profile_user_only(profile: dict = Depends(verify_profile_owner_user_only)):
                return {"profile": profile}
            
            yield app
    
    def test_verify_job_owner_with_valid_token(
        self, user_id, job_id, sample_job
    ):
        """Test accessing job with valid owner token."""
        app = FastAPI()
        
        with patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_job_instance = MockJobRepo.return_value
            mock_job_instance.get_by_id.return_value = sample_job
            
            user_context = UserContext(user_id=user_id, email="test@example.com")
            mock_auth.return_value = (user_context, "user")
            
            @app.get("/api/jobs/{job_id}")
            async def get_job(job: dict = Depends(verify_job_owner)):
                return {"job": job}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(user_id)
            
            response = client.get(
                f"/api/jobs/{job_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
    
    def test_verify_job_owner_with_different_user(
        self, user_id, other_user_id, job_id, sample_job
    ):
        """Test accessing job with different user token returns 403."""
        app = FastAPI()
        
        with patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_job_instance = MockJobRepo.return_value
            mock_job_instance.get_by_id.return_value = sample_job
            
            # Different user trying to access
            other_context = UserContext(user_id=other_user_id, email="other@example.com")
            mock_auth.return_value = (other_context, "user")
            
            @app.get("/api/jobs/{job_id}")
            async def get_job(job: dict = Depends(verify_job_owner)):
                return {"job": job}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(other_user_id)
            
            response = client.get(
                f"/api/jobs/{job_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == HttpStatus.FORBIDDEN
            assert response.json()["detail"]["error"]["code"] == ErrorCodes.FORBIDDEN
    
    def test_verify_job_owner_job_not_found(self, user_id, job_id):
        """Test accessing non-existent job returns 404."""
        app = FastAPI()
        
        with patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_job_instance = MockJobRepo.return_value
            mock_job_instance.get_by_id.side_effect = JobNotFoundError(job_id)
            
            user_context = UserContext(user_id=user_id, email="test@example.com")
            mock_auth.return_value = (user_context, "user")
            
            @app.get("/api/jobs/{job_id}")
            async def get_job(job: dict = Depends(verify_job_owner)):
                return {"job": job}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(user_id)
            
            response = client.get(
                f"/api/jobs/{job_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == HttpStatus.NOT_FOUND
    
    def test_verify_job_owner_with_service_key(
        self, user_id, job_id, sample_job
    ):
        """Test accessing job with service key always succeeds."""
        from app.guards.auth import get_user_or_service
        
        app = FastAPI()
        
        # Override the dependency at FastAPI level
        service_context = ServiceContext(service_name="n8n", is_admin=True)
        
        async def mock_get_user_or_service():
            return (service_context, "service")
        
        app.dependency_overrides[get_user_or_service] = mock_get_user_or_service
        
        with patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_job_instance = MockJobRepo.return_value
            mock_job_instance.get_by_id.return_value = sample_job
            
            @app.get("/api/jobs/{job_id}")
            async def get_job(job: dict = Depends(verify_job_owner)):
                return {"job": job}
            
            reset_guards()
            client = TestClient(app)
            
            response = client.get(
                f"/api/jobs/{job_id}",
                headers={"X-Service-Key": "test-service-key"}
            )
            
            assert response.status_code == 200
    
    def test_verify_profile_owner_with_valid_token(
        self, user_id, job_id, profile_id, sample_job, sample_profile
    ):
        """Test accessing profile with valid owner token."""
        app = FastAPI()
        
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            user_context = UserContext(user_id=user_id, email="test@example.com")
            mock_auth.return_value = (user_context, "user")
            
            @app.get("/api/profiles/{profile_id}")
            async def get_profile(profile: dict = Depends(verify_profile_owner)):
                return {"profile": profile}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(user_id)
            
            response = client.get(
                f"/api/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
    
    def test_verify_profile_owner_with_different_user(
        self, user_id, other_user_id, job_id, profile_id, sample_job, sample_profile
    ):
        """Test accessing profile with different user token returns 403."""
        app = FastAPI()
        
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo, \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            # Different user trying to access
            other_context = UserContext(user_id=other_user_id, email="other@example.com")
            mock_auth.return_value = (other_context, "user")
            
            @app.get("/api/profiles/{profile_id}")
            async def get_profile(profile: dict = Depends(verify_profile_owner)):
                return {"profile": profile}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(other_user_id)
            
            response = client.get(
                f"/api/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == HttpStatus.FORBIDDEN
    
    def test_verify_profile_owner_profile_not_found(self, user_id, profile_id):
        """Test accessing non-existent profile returns 404."""
        app = FastAPI()
        
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository"), \
             patch("app.guards.ownership.get_user_or_service") as mock_auth:
            
            mock_profile_instance = MockProfileRepo.return_value
            mock_profile_instance.get_by_id.side_effect = ProfileNotFoundError(profile_id)
            
            user_context = UserContext(user_id=user_id, email="test@example.com")
            mock_auth.return_value = (user_context, "user")
            
            @app.get("/api/profiles/{profile_id}")
            async def get_profile(profile: dict = Depends(verify_profile_owner)):
                return {"profile": profile}
            
            reset_guards()
            client = TestClient(app)
            token = create_test_token(user_id)
            
            response = client.get(
                f"/api/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == HttpStatus.NOT_FOUND


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestOwnershipGuardsEdgeCases:
    """Edge case tests for ownership guards."""
    
    def test_profile_with_missing_job_id(self, user_id, profile_id):
        """Test profile without job_id returns False for ownership check."""
        profile_without_job = {
            "id": profile_id,
            "job_id": None,
            "username": "test_user",
        }
        
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository"):
            mock_instance = MockProfileRepo.return_value
            mock_instance.get_by_id.return_value = profile_without_job
            
            guard = ProfileOwnerGuard()
            result = guard.check_ownership(profile_id, user_id)
            
            assert result is False
    
    def test_verify_ownership_uses_correct_resource_type(self, user_id, job_id, sample_job):
        """Test that error messages include correct resource type."""
        other_user_id = str(uuid4())
        
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            user_context = UserContext(user_id=other_user_id, email="other@example.com")
            
            with pytest.raises(ForbiddenError) as exc_info:
                guard.verify_ownership(job_id, user_context)
            
            assert exc_info.value.details.get("resource_type") == "job"
            assert exc_info.value.details.get("resource_id") == job_id
    
    def test_reset_guards_clears_singletons(self):
        """Test that reset_guards clears the singleton instances."""
        from app.guards.ownership import (
            _job_owner_guard,
            _profile_owner_guard,
            _get_job_owner_guard,
            _get_profile_owner_guard,
        )
        
        with patch("app.guards.ownership.JobRepository"), \
             patch("app.guards.ownership.ProfileRepository"):
            # Create singletons
            guard1 = _get_job_owner_guard()
            guard2 = _get_profile_owner_guard()
            
            # Reset
            reset_guards()
            
            # Get new instances
            guard3 = _get_job_owner_guard()
            guard4 = _get_profile_owner_guard()
            
            # They should be different instances
            assert guard1 is not guard3
            assert guard2 is not guard4


# =============================================================================
# Security Tests
# =============================================================================

class TestOwnershipGuardsSecurity:
    """Security tests for ownership guards."""
    
    def test_cannot_access_other_users_job(
        self, user_id, other_user_id, job_id, sample_job
    ):
        """Test that users cannot access other users' jobs."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            other_context = UserContext(user_id=other_user_id, email="other@example.com")
            
            with pytest.raises(ForbiddenError):
                guard.get_job_for_user(job_id, other_context)
    
    def test_cannot_access_other_users_profile(
        self, user_id, other_user_id, job_id, profile_id, sample_job, sample_profile
    ):
        """Test that users cannot access profiles from other users' jobs."""
        with patch("app.guards.ownership.ProfileRepository") as MockProfileRepo, \
             patch("app.guards.ownership.JobRepository") as MockJobRepo:
            mock_profile_instance = MockProfileRepo.return_value
            mock_job_instance = MockJobRepo.return_value
            mock_profile_instance.get_by_id.return_value = sample_profile
            mock_job_instance.get_by_id.return_value = sample_job
            
            guard = ProfileOwnerGuard()
            other_context = UserContext(user_id=other_user_id, email="other@example.com")
            
            with pytest.raises(ForbiddenError):
                guard.get_profile_for_user(profile_id, other_context)
    
    def test_service_can_access_any_job(
        self, user_id, job_id, sample_job, service_context
    ):
        """Test that service context can access any job."""
        with patch("app.guards.ownership.JobRepository") as MockRepo:
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_job
            
            guard = JobOwnerGuard()
            result = guard.get_job_for_user(job_id, service_context)
            
            assert result == sample_job
    
    def test_service_can_access_any_profile(
        self, profile_id, sample_profile, service_context
    ):
        """Test that service context can access any profile."""
        with patch("app.guards.ownership.ProfileRepository") as MockRepo, \
             patch("app.guards.ownership.JobRepository"):
            mock_instance = MockRepo.return_value
            mock_instance.get_by_id.return_value = sample_profile
            
            guard = ProfileOwnerGuard()
            result = guard.get_profile_for_user(profile_id, service_context)
            
            assert result == sample_profile


# =============================================================================
# Export Tests
# =============================================================================

class TestOwnershipGuardsExports:
    """Test that all ownership guard components are properly exported."""
    
    def test_guards_package_exports(self):
        """Test that guards package exports ownership components."""
        from app.guards import (
            OwnershipGuard,
            JobOwnerGuard,
            ProfileOwnerGuard,
            verify_job_owner,
            verify_job_owner_user_only,
            verify_profile_owner,
            verify_profile_owner_user_only,
            reset_guards,
        )
        
        assert OwnershipGuard is not None
        assert JobOwnerGuard is not None
        assert ProfileOwnerGuard is not None
        assert verify_job_owner is not None
        assert verify_job_owner_user_only is not None
        assert verify_profile_owner is not None
        assert verify_profile_owner_user_only is not None
        assert reset_guards is not None
