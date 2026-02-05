"""
Unit tests for custom exceptions.
TDD: These tests are written FIRST, before implementing exceptions.py
"""
import pytest


class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_partner_scout_exception_base(self):
        """PartnerScoutException should be base for all custom exceptions."""
        from app.core.exceptions import PartnerScoutException
        
        exc = PartnerScoutException("Test error", code="TEST_ERROR")
        assert str(exc) == "Test error"
        assert exc.code == "TEST_ERROR"
        assert exc.status_code == 500

    def test_validation_error(self):
        """ValidationError should have 400 status code."""
        from app.core.exceptions import ValidationError
        
        exc = ValidationError("Invalid input")
        assert exc.status_code == 400
        assert exc.code == "VALIDATION_ERROR"

    def test_not_found_error(self):
        """NotFoundError should have 404 status code."""
        from app.core.exceptions import NotFoundError
        
        exc = NotFoundError("Resource not found")
        assert exc.status_code == 404
        assert exc.code == "NOT_FOUND"

    def test_authentication_error(self):
        """AuthenticationError should have 401 status code."""
        from app.core.exceptions import AuthenticationError
        
        exc = AuthenticationError("Invalid token")
        assert exc.status_code == 401
        assert exc.code == "AUTHENTICATION_ERROR"

    def test_authorization_error(self):
        """AuthorizationError should have 403 status code."""
        from app.core.exceptions import AuthorizationError
        
        exc = AuthorizationError("Permission denied")
        assert exc.status_code == 403
        assert exc.code == "AUTHORIZATION_ERROR"

    def test_llm_error(self):
        """LLMError should handle AI/LLM failures."""
        from app.core.exceptions import LLMError
        
        exc = LLMError("OpenAI rate limited", provider="openai")
        assert exc.status_code == 503
        assert exc.provider == "openai"

    def test_apify_error(self):
        """ApifyError should handle scraping failures."""
        from app.core.exceptions import ApifyError
        
        exc = ApifyError("Actor failed", actor_id="test-actor")
        assert exc.status_code == 503
        assert exc.actor_id == "test-actor"

    def test_database_error(self):
        """DatabaseError should handle database failures."""
        from app.core.exceptions import DatabaseError
        
        exc = DatabaseError("Connection failed", operation="insert")
        assert exc.status_code == 500
        assert exc.code == "DATABASE_ERROR"

    def test_rate_limit_error(self):
        """RateLimitError should have 429 status code."""
        from app.core.exceptions import RateLimitError
        
        exc = RateLimitError("Rate limit exceeded", retry_after=60)
        assert exc.status_code == 429
        assert exc.code == "RATE_LIMIT_ERROR"

    def test_exception_to_dict(self):
        """Exceptions should serialize to dict for API responses."""
        from app.core.exceptions import ValidationError
        
        exc = ValidationError("Invalid email", details={"field": "email"})
        result = exc.to_dict()
        
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert result["error"]["message"] == "Invalid email"
        assert result["error"]["details"]["field"] == "email"


class TestExceptionInheritance:
    """Test that all exceptions inherit from PartnerScoutException."""

    def test_all_exceptions_are_partner_scout_exceptions(self):
        """All custom exceptions should inherit from PartnerScoutException."""
        from app.core.exceptions import (
            PartnerScoutException,
            ValidationError,
            NotFoundError,
            AuthenticationError,
            AuthorizationError,
            LLMError,
            ApifyError,
            DatabaseError,
            RateLimitError,
        )
        
        exception_classes = [
            ValidationError,
            NotFoundError,
            AuthenticationError,
            AuthorizationError,
            LLMError,
            ApifyError,
            DatabaseError,
            RateLimitError,
        ]
        
        for exc_class in exception_classes:
            assert issubclass(exc_class, PartnerScoutException), \
                f"{exc_class.__name__} should inherit from PartnerScoutException"
