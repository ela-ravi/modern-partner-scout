"""
Unit tests for User models.
"""
import pytest


class TestUserModels:
    """Test suite for User Pydantic models."""

    def test_user_model_has_required_fields(self):
        """User should have email and id."""
        from app.models.user import User

        user = User(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.id is not None

    def test_user_email_validation(self):
        """User email should be validated."""
        from app.models.user import User
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            User(email="invalid-email")

    def test_user_metadata_defaults_empty(self):
        """User metadata should default to empty dict."""
        from app.models.user import User

        user = User(email="test@example.com")
        assert user.user_metadata == {}

    def test_user_create_request(self):
        """UserCreate should validate registration data."""
        from app.models.user import UserCreate

        user = UserCreate(
            email="test@example.com",
            password="SecurePass123!"
        )
        assert user.email == "test@example.com"
        assert user.password == "SecurePass123!"

    def test_user_create_password_min_length(self):
        """Password should have minimum length."""
        from app.models.user import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="short")

    def test_user_response_excludes_sensitive(self):
        """UserResponse should not include password."""
        from app.models.user import UserResponse

        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="test@example.com"
        )

        assert not hasattr(user, "password")
        assert not hasattr(user, "password_hash")
