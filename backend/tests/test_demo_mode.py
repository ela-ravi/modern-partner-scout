"""
Tests for Item 8: Demo Mode Endpoint

TDD tests for POST /api/demo/start endpoint.

These tests should FAIL initially, then pass after implementation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.constants import JobStatus, ProfileStatus
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
def sample_demo_job_id():
    """Generate a sample demo job ID."""
    return str(uuid4())


@pytest.fixture
def demo_job_response(sample_demo_job_id):
    """Create a sample demo job response."""
    return {
        "job_id": sample_demo_job_id,
        "status": "completed",
        "message": "Demo job created with 10 sample profiles",
        "profiles_count": 10,
        "redirect_url": f"/jobs/{sample_demo_job_id}",
        "is_demo": True,
    }


@pytest.fixture
def mock_demo_service():
    """Create a mock DemoService."""
    return Mock()


# =============================================================================
# Test: POST /api/demo/start - Demo Mode Endpoint
# =============================================================================

class TestDemoModeEndpoint:
    """Tests for the POST /api/demo/start endpoint."""
    
    @patch('app.services.demo_service.DemoService')
    def test_start_demo_success_authenticated(self, mock_demo_service_class, valid_token, sample_demo_job_id):
        """Test successfully starting a demo as authenticated user."""
        # Mock the service to return a demo response
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created with 10 sample profiles",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        # Override dependency
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/demo/start",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "job_id" in data
            assert data["status"] == "completed"
            assert "profiles_count" in data
            assert data["profiles_count"] > 0
            assert "redirect_url" in data
            assert data["is_demo"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('app.services.demo_service.DemoService')
    def test_start_demo_success_anonymous(self, mock_demo_service_class, sample_demo_job_id):
        """Test successfully starting a demo as anonymous user."""
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created with 10 sample profiles",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post("/api/demo/start")
            
            assert response.status_code == 201
            data = response.json()
            
            assert "job_id" in data
            assert data["status"] == "completed"
            assert data["is_demo"] is True
        finally:
            app.dependency_overrides.clear()
    
    @patch('app.services.demo_service.DemoService')
    def test_demo_creates_completed_job(self, mock_demo_service_class, valid_token, sample_demo_job_id):
        """Test that demo creates a job in completed status."""
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/demo/start",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "completed"
        finally:
            app.dependency_overrides.clear()
    
    @patch('app.services.demo_service.DemoService')
    def test_demo_creates_profiles_with_scores(self, mock_demo_service_class, valid_token, sample_demo_job_id):
        """Test that demo job has pre-scored profiles."""
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created with 10 sample profiles",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/demo/start",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["profiles_count"] >= 3
        finally:
            app.dependency_overrides.clear()
    
    @patch('app.services.demo_service.DemoService')
    def test_demo_returns_redirect_url(self, mock_demo_service_class, valid_token, sample_demo_job_id):
        """Test that demo response includes redirect URL."""
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/demo/start",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "redirect_url" in data
            assert sample_demo_job_id in data["redirect_url"]
        finally:
            app.dependency_overrides.clear()


# =============================================================================
# Test: Demo Service Unit Tests
# =============================================================================

class TestDemoServiceUnit:
    """Unit tests for DemoService."""
    
    def test_demo_service_creates_job(self):
        """Test that DemoService.create_demo_job creates a job."""
        from app.services.demo_service import DemoService
        
        # Create mocks
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        mock_brand_repo = Mock()
        mock_score_repo = Mock()
        mock_contact_repo = Mock()
        
        # Mock job creation
        job_id = str(uuid4())
        mock_job_repo.create.return_value = {"id": job_id}
        mock_job_repo.update_status.return_value = {"id": job_id, "status": "completed"}
        
        # Mock profile creation
        profile_id = str(uuid4())
        mock_profile_repo.create.return_value = {"id": profile_id}
        mock_profile_repo.update_status.return_value = {"id": profile_id}
        
        service = DemoService(
            job_repo=mock_job_repo,
            profile_repo=mock_profile_repo,
            brand_dna_repo=mock_brand_repo,
            score_repo=mock_score_repo,
            contact_repo=mock_contact_repo,
        )
        
        result = service.create_demo_job(user_id=str(uuid4()))
        
        assert result["job_id"] == job_id
        assert result["status"] == "completed"
        assert result["is_demo"] is True
        mock_job_repo.create.assert_called_once()
    
    def test_demo_service_creates_profiles(self):
        """Test that DemoService creates profiles with scores."""
        from app.services.demo_service import DemoService
        
        mock_job_repo = Mock()
        mock_profile_repo = Mock()
        mock_brand_repo = Mock()
        mock_score_repo = Mock()
        mock_contact_repo = Mock()
        
        job_id = str(uuid4())
        mock_job_repo.create.return_value = {"id": job_id}
        mock_job_repo.update_status.return_value = {"id": job_id}
        
        profile_id = str(uuid4())
        mock_profile_repo.create.return_value = {"id": profile_id}
        mock_profile_repo.update_status.return_value = {"id": profile_id}
        
        service = DemoService(
            job_repo=mock_job_repo,
            profile_repo=mock_profile_repo,
            brand_dna_repo=mock_brand_repo,
            score_repo=mock_score_repo,
            contact_repo=mock_contact_repo,
        )
        
        result = service.create_demo_job(user_id=str(uuid4()))
        
        # Should have created profiles
        assert result["profiles_count"] > 0
        assert mock_profile_repo.create.call_count > 0


# =============================================================================
# Test: Demo Seed Data Structure
# =============================================================================

class TestDemoSeedData:
    """Tests for demo seed data structure."""
    
    def test_demo_seed_data_has_required_profiles(self):
        """Test that demo seed data has the required structure."""
        from app.data.demo_seed import DEMO_PROFILES, DEMO_BRAND_DNA, DEMO_BRAND_DESCRIPTION
        
        # Check we have profiles
        assert len(DEMO_PROFILES) >= 3
        
        # Check profile structure
        for profile in DEMO_PROFILES:
            assert "username" in profile
            assert "followers_count" in profile
            assert "score" in profile
            assert "bio" in profile
    
    def test_demo_brand_dna_has_required_fields(self):
        """Test that demo brand DNA has required fields."""
        from app.data.demo_seed import DEMO_BRAND_DNA
        
        assert "hashtags" in DEMO_BRAND_DNA
        assert "keywords" in DEMO_BRAND_DNA
        assert len(DEMO_BRAND_DNA["hashtags"]) > 0
        assert len(DEMO_BRAND_DNA["keywords"]) > 0


# =============================================================================
# Test: Response Model
# =============================================================================

class TestDemoResponseModel:
    """Tests for demo response model."""
    
    @patch('app.services.demo_service.DemoService')
    def test_demo_response_has_all_required_fields(self, mock_demo_service_class, valid_token, sample_demo_job_id):
        """Test that demo response includes all required fields."""
        mock_service = Mock()
        mock_service.create_demo_job.return_value = {
            "job_id": sample_demo_job_id,
            "status": "completed",
            "message": "Demo job created with 10 sample profiles",
            "profiles_count": 10,
            "redirect_url": f"/jobs/{sample_demo_job_id}",
            "is_demo": True,
        }
        
        from app.services.demo_service import get_demo_service
        app.dependency_overrides[get_demo_service] = lambda: mock_service
        
        try:
            client = TestClient(app)
            response = client.post(
                "/api/demo/start",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # All required fields
            required_fields = ["job_id", "status", "message", "profiles_count", "redirect_url", "is_demo"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
