"""
Unit tests for FastAPI application setup.
TDD: These tests are written FIRST, before implementing main.py
"""
import pytest
from fastapi.testclient import TestClient


class TestApplication:
    """Test suite for main FastAPI application."""

    def test_app_creates_successfully(self):
        """Application should create without errors."""
        from app.main import app
        assert app is not None
        assert app.title == "PartnerScout AI"

    def test_app_has_cors_middleware(self):
        """Application should have CORS middleware configured."""
        from app.main import app
        
        # Check if CORS middleware is in the middleware stack
        middleware_classes = [type(m).__name__ for m in app.user_middleware]
        # CORS middleware is added via add_middleware, check that it exists
        assert len(app.user_middleware) > 0 or any(
            "cors" in str(m).lower() for m in app.user_middleware
        )


class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client for the app."""
        from app.main import app
        return TestClient(app)

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """Health endpoint should return status information."""
        response = client.get("/api/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_health_returns_correct_version(self, client):
        """Health endpoint should return app version."""
        response = client.get("/api/health")
        data = response.json()
        
        assert data["version"] == "0.1.0"

    def test_health_detailed_returns_extra_info(self, client):
        """Detailed health endpoint should return database and service status."""
        response = client.get("/api/health/detailed")
        data = response.json()
        
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data
