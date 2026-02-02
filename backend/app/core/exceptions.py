"""
PartnerScout AI - Custom Exceptions

Hierarchical exception classes for consistent error handling across the application.
All exceptions include error codes for client-side handling.
"""

from typing import Any, Dict, Optional

from app.core.constants import ErrorCodes, HttpStatus


class PartnerScoutError(Exception):
    """
    Base exception for all PartnerScout application errors.
    
    All custom exceptions should inherit from this class to ensure
    consistent error handling and response formatting.
    """
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCodes.INTERNAL_ERROR,
        status_code: int = HttpStatus.INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            code: Machine-readable error code from ErrorCodes
            status_code: HTTP status code for the response
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to a dictionary for JSON serialization.
        
        Returns:
            Dict with error information
        """
        error_dict = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if self.details:
            error_dict["error"]["details"] = self.details
        return error_dict
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# =============================================================================
# Business Logic Errors
# =============================================================================

class BusinessError(PartnerScoutError):
    """
    Base class for business logic errors.
    
    Use this for errors related to business rules, validation,
    and application-specific constraints.
    """
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCodes.VALIDATION_ERROR,
        status_code: int = HttpStatus.BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code, details)


class DailyLimitExceededError(BusinessError):
    """Raised when a user exceeds their daily job creation limit."""
    
    def __init__(
        self,
        limit: int,
        message: str = "Daily job limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.DAILY_LIMIT_EXCEEDED,
            status_code=HttpStatus.TOO_MANY_REQUESTS,
            details=details or {"limit": limit},
        )


class ProfileLimitExceededError(BusinessError):
    """Raised when a job exceeds the maximum profile limit."""
    
    def __init__(
        self,
        limit: int,
        message: str = "Profile limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.PROFILE_LIMIT_EXCEEDED,
            status_code=HttpStatus.BAD_REQUEST,
            details=details or {"limit": limit},
        )


class InvalidStatusTransitionError(BusinessError):
    """Raised when an invalid status transition is attempted."""
    
    def __init__(
        self,
        from_status: str,
        to_status: str,
        entity_type: str = "job",
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Cannot transition {entity_type} from '{from_status}' to '{to_status}'"
        super().__init__(
            message=message,
            code=ErrorCodes.INVALID_TRANSITION,
            status_code=HttpStatus.BAD_REQUEST,
            details={
                "entity_type": entity_type,
                "from_status": from_status,
                "to_status": to_status,
            },
        )


class JobNotStartableError(BusinessError):
    """Raised when attempting to start a job that cannot be started."""
    
    def __init__(
        self,
        job_id: str,
        current_status: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Job cannot be started (current status: {current_status})"
        super().__init__(
            message=message,
            code=ErrorCodes.JOB_NOT_STARTABLE,
            status_code=HttpStatus.CONFLICT,
            details={"job_id": job_id, "current_status": current_status},
        )


class JobAlreadyCompletedError(BusinessError):
    """Raised when attempting to modify a completed job."""
    
    def __init__(
        self,
        job_id: str,
        message: str = "Job has already been completed and cannot be modified",
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.JOB_ALREADY_COMPLETED,
            status_code=HttpStatus.CONFLICT,
            details={"job_id": job_id},
        )


# =============================================================================
# Authentication & Authorization Errors
# =============================================================================

class UnauthorizedError(PartnerScoutError):
    """
    Raised when authentication fails or is missing.
    
    Use for cases where the user is not authenticated at all.
    """
    
    def __init__(
        self,
        message: str = "Authentication required",
        code: str = ErrorCodes.UNAUTHORIZED,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=HttpStatus.UNAUTHORIZED,
            details=details,
        )


class InvalidTokenError(UnauthorizedError):
    """Raised when a JWT token is invalid."""
    
    def __init__(
        self,
        message: str = "Invalid or malformed token",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.INVALID_TOKEN,
            details=details,
        )


class ExpiredTokenError(UnauthorizedError):
    """Raised when a JWT token has expired."""
    
    def __init__(
        self,
        message: str = "Token has expired",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.EXPIRED_TOKEN,
            details=details,
        )


class InvalidServiceKeyError(UnauthorizedError):
    """Raised when a service key is invalid."""
    
    def __init__(
        self,
        message: str = "Invalid service key",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.INVALID_SERVICE_KEY,
            details=details,
        )


class ForbiddenError(PartnerScoutError):
    """
    Raised when access to a resource is denied.
    
    Use for cases where the user is authenticated but lacks permission.
    """
    
    def __init__(
        self,
        message: str = "Access denied",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            code=ErrorCodes.FORBIDDEN,
            status_code=HttpStatus.FORBIDDEN,
            details=error_details,
        )


# =============================================================================
# Resource Not Found Errors
# =============================================================================

class NotFoundError(PartnerScoutError):
    """
    Base class for resource not found errors.
    
    Use when a requested resource does not exist.
    """
    
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = ErrorCodes.NOT_FOUND,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            code=code,
            status_code=HttpStatus.NOT_FOUND,
            details=error_details,
        )


class JobNotFoundError(NotFoundError):
    """Raised when a discovery job is not found."""
    
    def __init__(
        self,
        job_id: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Discovery job not found: {job_id}"
        super().__init__(
            message=message,
            code=ErrorCodes.JOB_NOT_FOUND,
            resource_type="job",
            resource_id=job_id,
        )


class ProfileNotFoundError(NotFoundError):
    """Raised when a discovered profile is not found."""
    
    def __init__(
        self,
        profile_id: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Profile not found: {profile_id}"
        super().__init__(
            message=message,
            code=ErrorCodes.PROFILE_NOT_FOUND,
            resource_type="profile",
            resource_id=profile_id,
        )


class BrandDNANotFoundError(NotFoundError):
    """Raised when brand DNA is not found for a job."""
    
    def __init__(
        self,
        job_id: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Brand DNA not found for job: {job_id}"
        super().__init__(
            message=message,
            code=ErrorCodes.BRAND_DNA_NOT_FOUND,
            resource_type="brand_dna",
            resource_id=job_id,
        )


# =============================================================================
# AI Agent Errors
# =============================================================================

class AgentError(PartnerScoutError):
    """
    Base class for AI agent errors.
    
    Use for errors that occur during AI agent operations.
    """
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCodes.AGENT_ERROR,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if agent_name:
            error_details["agent"] = agent_name
        
        super().__init__(
            message=message,
            code=code,
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            details=error_details,
        )


class LLMError(AgentError):
    """Raised when an LLM call fails."""
    
    def __init__(
        self,
        message: str = "LLM request failed",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if provider:
            error_details["provider"] = provider
        if model:
            error_details["model"] = model
        
        super().__init__(
            message=message,
            code=ErrorCodes.LLM_ERROR,
            details=error_details,
        )


class ScrapingError(AgentError):
    """Raised when web scraping fails."""
    
    def __init__(
        self,
        message: str = "Scraping operation failed",
        target: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if target:
            error_details["target"] = target
        
        super().__init__(
            message=message,
            code=ErrorCodes.SCRAPING_ERROR,
            agent_name="scraper",
            details=error_details,
        )


class ScoringError(AgentError):
    """Raised when profile scoring fails."""
    
    def __init__(
        self,
        message: str = "Profile scoring failed",
        profile_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if profile_id:
            error_details["profile_id"] = profile_id
        
        super().__init__(
            message=message,
            code=ErrorCodes.SCORING_ERROR,
            agent_name="scorer",
            details=error_details,
        )


class EmailGenerationError(AgentError):
    """Raised when email generation fails."""
    
    def __init__(
        self,
        message: str = "Email generation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCodes.EMAIL_GENERATION_ERROR,
            agent_name="email_composer",
            details=details,
        )


# =============================================================================
# External Service Errors
# =============================================================================

class ExternalServiceError(PartnerScoutError):
    """
    Base class for external service errors.
    
    Use for errors from third-party services (Supabase, Apify, N8N, etc.).
    """
    
    def __init__(
        self,
        message: str,
        service_name: str,
        code: str = ErrorCodes.EXTERNAL_SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["service"] = service_name
        
        super().__init__(
            message=message,
            code=code,
            status_code=HttpStatus.BAD_GATEWAY,
            details=error_details,
        )


class SupabaseError(ExternalServiceError):
    """Raised when a Supabase operation fails."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            service_name="supabase",
            code=ErrorCodes.SUPABASE_ERROR,
            details=details,
        )


class ApifyError(ExternalServiceError):
    """Raised when an Apify operation fails."""
    
    def __init__(
        self,
        message: str = "Scraping service operation failed",
        actor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if actor_id:
            error_details["actor_id"] = actor_id
        
        super().__init__(
            message=message,
            service_name="apify",
            code=ErrorCodes.APIFY_ERROR,
            details=error_details,
        )


class N8NError(ExternalServiceError):
    """Raised when an N8N operation fails."""
    
    def __init__(
        self,
        message: str = "Workflow orchestration failed",
        workflow_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if workflow_id:
            error_details["workflow_id"] = workflow_id
        
        super().__init__(
            message=message,
            service_name="n8n",
            code=ErrorCodes.N8N_ERROR,
            details=error_details,
        )


# =============================================================================
# Validation Errors
# =============================================================================

class ValidationError(BusinessError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)
        
        super().__init__(
            message=message,
            code=ErrorCodes.VALIDATION_ERROR,
            status_code=HttpStatus.UNPROCESSABLE_ENTITY,
            details=error_details,
        )


class InvalidURLError(ValidationError):
    """Raised when a URL is invalid."""
    
    def __init__(
        self,
        url: str,
        message: Optional[str] = None,
    ):
        if message is None:
            message = f"Invalid URL format: {url}"
        super().__init__(
            message=message,
            field="url",
            value=url,
        )
        self.code = ErrorCodes.INVALID_URL
