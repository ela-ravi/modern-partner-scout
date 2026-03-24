"""
PartnerScout AI - Authentication Guards Tests

Unit and integration tests for authentication guards.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import jwt
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.core.config import settings


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def jwt_secret():
    """Get JWT secret for testing."""
    return settings.supabase.jwt_secret


@pytest.fixture
def service_key():
    """Get service key for testing."""
    return settings.supabase.service_role_key


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
def expired_token(jwt_secret, valid_user_id):
    """Create an expired JWT token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),  # Expired 1 hour ago
        "aud": "authenticated",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def invalid_signature_token(valid_user_id):
    """Create a token signed with wrong secret."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    return jwt.encode(payload, "wrong-secret", algorithm="HS256")


# =============================================================================
# Test UserContext Model
# =============================================================================

class TestUserContext:
    """Tests for UserContext model."""
    
    def test_user_context_creation(self):
        """Test creating a UserContext."""
        from app.guards.auth import UserContext
        
        user = UserContext(
            user_id="test-user-id",
            email="test@example.com",
            role="authenticated"
        )
        
        assert user.user_id == "test-user-id"
        assert user.email == "test@example.com"
        assert user.role == "authenticated"
        assert user.is_authenticated is True
    
    def test_user_context_is_expired(self):
        """Test expiration check."""
        from app.guards.auth import UserContext
        
        # Not expired
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        user = UserContext(user_id="test", exp=future)
        assert user.is_expired is False
        
        # Expired
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        user = UserContext(user_id="test", exp=past)
        assert user.is_expired is True
    
    def test_user_context_repr(self):
        """Test string representation."""
        from app.guards.auth import UserContext
        
        user = UserContext(
            user_id="test-id",
            email="test@test.com",
            role="admin"
        )
        
        assert "test-id" in repr(user)
        assert "test@test.com" in repr(user)


class TestServiceContext:
    """Tests for ServiceContext model."""
    
    def test_service_context_creation(self):
        """Test creating a ServiceContext."""
        from app.guards.auth import ServiceContext
        
        service = ServiceContext(service_name="internal", is_admin=True)
        
        assert service.service_name == "internal"
        assert service.is_admin is True
    
    def test_service_context_repr(self):
        """Test string representation."""
        from app.guards.auth import ServiceContext
        
        service = ServiceContext(service_name="test-service")
        assert "test-service" in repr(service)


# =============================================================================
# Test UserGuard
# =============================================================================

class TestUserGuard:
    """Tests for UserGuard authentication."""
    
    def test_validate_valid_token(self, valid_token, valid_user_id, jwt_secret):
        """Test validating a valid JWT token."""
        from app.guards.auth import UserGuard
        
        guard = UserGuard(jwt_secret=jwt_secret)
        user = guard.validate_token(valid_token)
        
        assert user.user_id == valid_user_id
        assert user.email == "test@example.com"
        assert user.role == "authenticated"
        assert user.is_authenticated is True
    
    def test_validate_expired_token(self, expired_token, jwt_secret):
        """Test that expired tokens are rejected."""
        from app.guards.auth import UserGuard
        from app.core.exceptions import ExpiredTokenError
        
        guard = UserGuard(jwt_secret=jwt_secret)
        
        with pytest.raises(ExpiredTokenError) as exc_info:
            guard.validate_token(expired_token)
        
        assert "expired" in str(exc_info.value.message).lower()
    
    def test_validate_invalid_signature(self, invalid_signature_token, jwt_secret):
        """Test that tokens with invalid signature are rejected."""
        from app.guards.auth import UserGuard
        from app.core.exceptions import InvalidTokenError
        
        guard = UserGuard(jwt_secret=jwt_secret)
        
        with pytest.raises(InvalidTokenError):
            guard.validate_token(invalid_signature_token)
    
    def test_validate_malformed_token(self, jwt_secret):
        """Test that malformed tokens are rejected."""
        from app.guards.auth import UserGuard
        from app.core.exceptions import InvalidTokenError
        
        guard = UserGuard(jwt_secret=jwt_secret)
        
        with pytest.raises(InvalidTokenError):
            guard.validate_token("not-a-valid-jwt-token")
    
    def test_get_auth_header_with_bearer(self):
        """Test extracting token from Authorization header."""
        from app.guards.auth import UserGuard
        
        guard = UserGuard()
        request = MagicMock()
        request.headers.get.return_value = "Bearer test-token-123"
        
        token = guard.get_auth_header(request)
        assert token == "test-token-123"
    
    def test_get_auth_header_missing(self):
        """Test handling missing Authorization header."""
        from app.guards.auth import UserGuard
        
        guard = UserGuard()
        request = MagicMock()
        request.headers.get.return_value = None
        
        token = guard.get_auth_header(request)
        assert token is None
    
    def test_authenticate_no_token(self):
        """Test authentication fails without token."""
        from app.guards.auth import UserGuard
        from app.core.exceptions import UnauthorizedError
        
        guard = UserGuard()
        request = MagicMock()
        request.headers.get.return_value = None
        
        with pytest.raises(UnauthorizedError) as exc_info:
            guard.authenticate(request)
        
        assert "Authorization header required" in str(exc_info.value.message)


# =============================================================================
# Test ServiceKeyGuard
# =============================================================================

class TestServiceKeyGuard:
    """Tests for ServiceKeyGuard authentication."""
    
    def test_validate_valid_key(self, service_key):
        """Test validating a valid service key."""
        from app.guards.auth import ServiceKeyGuard
        
        guard = ServiceKeyGuard(service_key=service_key)
        context = guard.validate_key(service_key)
        
        assert context.service_name == "internal"
        assert context.is_admin is True
    
    def test_validate_invalid_key(self, service_key):
        """Test that invalid keys are rejected."""
        from app.guards.auth import ServiceKeyGuard
        from app.core.exceptions import InvalidServiceKeyError
        
        guard = ServiceKeyGuard(service_key=service_key)
        
        with pytest.raises(InvalidServiceKeyError):
            guard.validate_key("wrong-service-key")
    
    def test_get_auth_header(self):
        """Test extracting service key from header."""
        from app.guards.auth import ServiceKeyGuard
        
        guard = ServiceKeyGuard()
        request = MagicMock()
        request.headers.get.return_value = "my-service-key"
        
        key = guard.get_auth_header(request)
        assert key == "my-service-key"
    
    def test_authenticate_no_key(self):
        """Test authentication fails without service key."""
        from app.guards.auth import ServiceKeyGuard
        from app.core.exceptions import UnauthorizedError
        
        guard = ServiceKeyGuard()
        request = MagicMock()
        request.headers.get.return_value = None
        
        with pytest.raises(UnauthorizedError) as exc_info:
            guard.authenticate(request)
        
        assert "Service key required" in str(exc_info.value.message)
    
    def test_secure_compare_timing_safe(self):
        """Test that comparison is timing-safe."""
        from app.guards.auth import ServiceKeyGuard
        
        # Same strings should return True
        assert ServiceKeyGuard._secure_compare("abc123", "abc123") is True
        
        # Different strings should return False
        assert ServiceKeyGuard._secure_compare("abc123", "xyz789") is False
        
        # Different lengths should return False
        assert ServiceKeyGuard._secure_compare("short", "longer-string") is False


# =============================================================================
# Test CombinedAuthGuard
# =============================================================================

class TestCombinedAuthGuard:
    """Tests for CombinedAuthGuard."""
    
    def test_authenticate_with_service_key(self, service_key, jwt_secret):
        """Test authentication with service key."""
        from app.guards.auth import CombinedAuthGuard, UserGuard, ServiceKeyGuard
        
        user_guard = UserGuard(jwt_secret=jwt_secret)
        service_guard = ServiceKeyGuard(service_key=service_key)
        guard = CombinedAuthGuard(user_guard=user_guard, service_guard=service_guard)
        
        request = MagicMock()
        request.headers.get = lambda key: service_key if key == "X-Service-Key" else None
        
        context, auth_type = guard.authenticate(request)
        
        assert auth_type == "service"
        assert context.service_name == "internal"
    
    def test_authenticate_with_user_token(self, valid_token, jwt_secret, service_key):
        """Test authentication with user JWT."""
        from app.guards.auth import CombinedAuthGuard, UserGuard, ServiceKeyGuard
        
        user_guard = UserGuard(jwt_secret=jwt_secret)
        service_guard = ServiceKeyGuard(service_key=service_key)
        guard = CombinedAuthGuard(user_guard=user_guard, service_guard=service_guard)
        
        request = MagicMock()
        request.headers.get = lambda key: f"Bearer {valid_token}" if key == "Authorization" else None
        
        context, auth_type = guard.authenticate(request)
        
        assert auth_type == "user"
        assert context.is_authenticated is True
    
    def test_authenticate_neither_provided(self, jwt_secret, service_key):
        """Test authentication fails when neither auth method provided."""
        from app.guards.auth import CombinedAuthGuard, UserGuard, ServiceKeyGuard
        from app.core.exceptions import UnauthorizedError
        
        user_guard = UserGuard(jwt_secret=jwt_secret)
        service_guard = ServiceKeyGuard(service_key=service_key)
        guard = CombinedAuthGuard(user_guard=user_guard, service_guard=service_guard)
        
        request = MagicMock()
        request.headers.get.return_value = None
        
        with pytest.raises(UnauthorizedError) as exc_info:
            guard.authenticate(request)
        
        assert "Authentication required" in str(exc_info.value.message)


# =============================================================================
# Test FastAPI Integration
# =============================================================================

class TestFastAPIIntegration:
    """Integration tests with FastAPI."""
    
    @pytest.fixture
    def test_app(self):
        """Create a test FastAPI app with guarded routes."""
        from app.guards.auth import get_current_user, get_service_context, UserContext, ServiceContext
        
        app = FastAPI()
        
        @app.get("/user-protected")
        async def user_protected(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.user_id, "email": user.email}
        
        @app.get("/service-protected")
        async def service_protected(service: ServiceContext = Depends(get_service_context)):
            return {"service": service.service_name}
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create a test client."""
        return TestClient(test_app)
    
    def test_user_protected_no_auth(self, client):
        """Test user-protected route without auth returns 401."""
        response = client.get("/user-protected")
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"
    
    def test_user_protected_with_valid_token(self, client, valid_token, valid_user_id):
        """Test user-protected route with valid token."""
        response = client.get(
            "/user-protected",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == valid_user_id
        assert data["email"] == "test@example.com"
    
    def test_user_protected_with_expired_token(self, client, expired_token):
        """Test user-protected route with expired token returns 401."""
        response = client.get(
            "/user-protected",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "EXPIRED_TOKEN"
    
    def test_user_protected_with_invalid_token(self, client):
        """Test user-protected route with invalid token returns 401."""
        response = client.get(
            "/user-protected",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "INVALID_TOKEN"
    
    def test_service_protected_no_key(self, client):
        """Test service-protected route without key returns 401."""
        response = client.get("/service-protected")
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "UNAUTHORIZED"
    
    def test_service_protected_with_valid_key(self, client, service_key):
        """Test service-protected route with valid key."""
        response = client.get(
            "/service-protected",
            headers={"X-Service-Key": service_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "internal"
    
    def test_service_protected_with_invalid_key(self, client):
        """Test service-protected route with invalid key returns 401."""
        response = client.get(
            "/service-protected",
            headers={"X-Service-Key": "wrong-key"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["error"]["code"] == "INVALID_SERVICE_KEY"


# =============================================================================
# Test Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_create_test_token(self, jwt_secret):
        """Test creating a test token."""
        from app.guards.auth import create_test_token, UserGuard
        
        user_id = str(uuid4())
        token = create_test_token(
            user_id=user_id,
            email="test@test.com",
            role="admin"
        )
        
        # Validate the token
        guard = UserGuard(jwt_secret=jwt_secret)
        user = guard.validate_token(token)
        
        assert user.user_id == user_id
        assert user.email == "test@test.com"
        assert user.role == "admin"


# =============================================================================
# Test Module Exports
# =============================================================================

class TestModuleExports:
    """Tests for module exports."""
    
    def test_all_guards_exported(self):
        """Test that all guards are exported from __init__."""
        from app.guards import (
            UserContext,
            ServiceContext,
            AuthGuard,
            UserGuard,
            ServiceKeyGuard,
            CombinedAuthGuard,
            get_current_user,
            get_service_context,
            get_optional_user,
            get_user_or_service,
            create_test_token,
        )
        
        assert UserContext is not None
        assert ServiceContext is not None
        assert UserGuard is not None
        assert ServiceKeyGuard is not None
        assert get_current_user is not None
