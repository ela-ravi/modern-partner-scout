"""
Custom exception classes for PartnerScout AI.
All exceptions inherit from PartnerScoutException base class.

This module provides a hierarchy of exceptions for different error types:
- Validation errors (400)
- Not found errors (404)
- Authentication errors (401)
- Authorization errors (403)
- LLM/AI provider errors (503)
- Scraping/Apify errors (503)
- Database errors (500)
- Rate limiting errors (429)
"""
from typing import Any, Dict, Optional


class PartnerScoutException(Exception):
    """
    Base exception for all PartnerScout errors.
    
    All custom exceptions in the application should inherit from this class.
    It provides a consistent interface for error handling and API responses.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code for client handling
        status_code: HTTP status code for API responses
        details: Additional structured error details
    """
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error context
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to API response format.
        
        Returns a structured dictionary suitable for JSON API responses,
        following a consistent error response format.
        
        Returns:
            Dict with error code, message, and details
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class ValidationError(PartnerScoutException):
    """
    Raised when input validation fails.
    
    Use this for request body validation, query parameter validation,
    or any business logic validation that fails.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize validation error.
        
        Args:
            message: Description of what validation failed
            details: Field-level error details
        """
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class NotFoundError(PartnerScoutException):
    """
    Raised when a requested resource is not found.
    
    Use this when a database lookup returns no results,
    or when a referenced entity doesn't exist.
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        """
        Initialize not found error.
        
        Args:
            message: Description of what wasn't found
            resource_type: Type of resource (e.g., 'user', 'job', 'profile')
        """
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type} if resource_type else {}
        )


class AuthenticationError(PartnerScoutException):
    """
    Raised when authentication fails.
    
    Use this for invalid tokens, expired sessions, or missing credentials.
    """
    
    def __init__(self, message: str = "Authentication required"):
        """
        Initialize authentication error.
        
        Args:
            message: Description of authentication failure
        """
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationError(PartnerScoutException):
    """
    Raised when user lacks permission for an action.
    
    Use this when a user is authenticated but doesn't have
    the required permissions for the requested operation.
    """
    
    def __init__(self, message: str = "Permission denied"):
        """
        Initialize authorization error.
        
        Args:
            message: Description of the permission issue
        """
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class LLMError(PartnerScoutException):
    """
    Raised when LLM provider encounters an error.
    
    Use this for API errors from OpenAI, Gemini, Ollama, or any
    other AI/LLM service. Includes provider information for debugging.
    """
    
    def __init__(
        self,
        message: str,
        provider: str = "unknown",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize LLM error.
        
        Args:
            message: Description of the LLM failure
            provider: Name of the LLM provider (openai, gemini, ollama)
            details: Additional error context from the provider
        """
        self.provider = provider
        super().__init__(
            message=message,
            code="LLM_ERROR",
            status_code=503,
            details={"provider": provider, **(details or {})}
        )


class ApifyError(PartnerScoutException):
    """
    Raised when Apify scraping encounters an error.
    
    Use this for Instagram scraping failures, actor timeouts,
    or any other Apify-related issues.
    """
    
    def __init__(
        self,
        message: str,
        actor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Apify error.
        
        Args:
            message: Description of the scraping failure
            actor_id: The Apify actor that failed
            details: Additional error context
        """
        self.actor_id = actor_id
        super().__init__(
            message=message,
            code="APIFY_ERROR",
            status_code=503,
            details={"actor_id": actor_id, **(details or {})}
        )


class DatabaseError(PartnerScoutException):
    """
    Raised when database operations fail.
    
    Use this for connection failures, query errors, or
    transaction failures in Supabase or SQLite.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize database error.
        
        Args:
            message: Description of the database failure
            operation: The operation that failed (insert, update, delete, etc.)
        """
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details={"operation": operation} if operation else {}
        )


class RateLimitError(PartnerScoutException):
    """
    Raised when rate limit is exceeded.
    
    Use this when a client exceeds their allowed request quota.
    Includes retry-after information for proper client handling.
    """
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        """
        Initialize rate limit error.
        
        Args:
            message: Description of the rate limit
            retry_after: Seconds until the client can retry
        """
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            status_code=429,
            details={"retry_after": retry_after} if retry_after else {}
        )
