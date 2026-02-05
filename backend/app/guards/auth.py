"""
PartnerScout AI - Authentication Guards

Implements authentication guards for securing API endpoints.
- UserGuard: JWT-based authentication for user requests
- ServiceKeyGuard: Service key authentication for N8N/internal services
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.constants import ErrorCodes, HttpStatus
from app.core.exceptions import (
    ExpiredTokenError,
    ForbiddenError,
    InvalidServiceKeyError,
    InvalidTokenError,
    UnauthorizedError,
)


# =============================================================================
# Security Schemes
# =============================================================================

# Optional Bearer token scheme (doesn't auto-raise 403)
# scheme_name must match the security scheme name in OpenAPI spec
oauth2_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth")


# =============================================================================
# User Context Model
# =============================================================================

class UserContext:
    """
    Represents an authenticated user context.
    
    Extracted from a validated JWT token.
    """
    
    def __init__(
        self,
        user_id: str,
        email: Optional[str] = None,
        role: str = "authenticated",
        exp: Optional[datetime] = None,
        raw_token: Optional[str] = None,
        claims: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.exp = exp
        self.raw_token = raw_token
        self.claims = claims or {}
    
    def __repr__(self) -> str:
        return f"UserContext(user_id={self.user_id}, email={self.email}, role={self.role})"
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return bool(self.user_id)
    
    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if self.exp is None:
            return False
        return datetime.now(timezone.utc) > self.exp


class ServiceContext:
    """
    Represents a service authentication context.
    
    Used for N8N and internal service calls.
    """
    
    def __init__(
        self,
        service_name: str = "n8n",
        is_admin: bool = True,
    ):
        self.service_name = service_name
        self.is_admin = is_admin
    
    def __repr__(self) -> str:
        return f"ServiceContext(service_name={self.service_name}, is_admin={self.is_admin})"


# =============================================================================
# Base Guard Class
# =============================================================================

class AuthGuard(ABC):
    """
    Abstract base class for authentication guards.
    
    Provides common interface for all authentication mechanisms.
    """
    
    @abstractmethod
    def authenticate(self, request: Request) -> Any:
        """
        Authenticate the request and return the context.
        
        Args:
            request: The incoming FastAPI request
            
        Returns:
            Authentication context (UserContext or ServiceContext)
            
        Raises:
            UnauthorizedError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_auth_header(self, request: Request) -> Optional[str]:
        """
        Extract the authentication header from the request.
        
        Args:
            request: The incoming FastAPI request
            
        Returns:
            The authentication header value or None
        """
        pass


# =============================================================================
# User Guard (JWT Authentication)
# =============================================================================

class UserGuard(AuthGuard):
    """
    Guard for user authentication via Supabase JWT tokens.
    
    Validates JWT tokens and extracts user information.
    """
    
    def __init__(self, jwt_secret: Optional[str] = None, algorithms: list = None):
        """
        Initialize the user guard.
        
        Args:
            jwt_secret: JWT secret for validation (defaults to settings)
            algorithms: List of allowed algorithms (defaults to HS256)
        """
        self.jwt_secret = jwt_secret or settings.supabase.jwt_secret
        self.algorithms = algorithms or ["HS256"]
    
    def get_auth_header(self, request: Request) -> Optional[str]:
        """Extract Bearer token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # Handle "Bearer <token>" format
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        
        return None
    
    def authenticate(self, request: Request) -> UserContext:
        """
        Authenticate the request using JWT token.
        
        Args:
            request: The incoming FastAPI request
            
        Returns:
            UserContext with authenticated user information
            
        Raises:
            UnauthorizedError: If no token provided
            InvalidTokenError: If token is malformed or invalid
            ExpiredTokenError: If token has expired
        """
        token = self.get_auth_header(request)
        
        if not token:
            raise UnauthorizedError(
                message="Authorization header required",
                details={"hint": "Include 'Authorization: Bearer <token>' header"}
            )
        
        return self.validate_token(token)
    
    def validate_token(self, token: str) -> UserContext:
        """
        Validate a JWT token and extract user context.
        
        Args:
            token: The JWT token string
            
        Returns:
            UserContext with user information
            
        Raises:
            InvalidTokenError: If token is invalid
            ExpiredTokenError: If token has expired
        """
        try:
            # Decode and validate the token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=self.algorithms,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": False,  # Skip audience verification
                    "require": ["sub", "exp"],
                }
            )
            
            # Extract user information from Supabase JWT structure
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role", "authenticated")
            
            # Parse expiration
            exp_timestamp = payload.get("exp")
            exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) if exp_timestamp else None
            
            return UserContext(
                user_id=user_id,
                email=email,
                role=role,
                exp=exp,
                raw_token=token,
                claims=payload,
            )
        
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError(
                message="Token has expired",
                details={"hint": "Please refresh your authentication token"}
            )
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(
                message="Invalid authentication token",
                details={"error": str(e)}
            )


# =============================================================================
# Service Key Guard (N8N/Internal Services)
# =============================================================================

class ServiceKeyGuard(AuthGuard):
    """
    Guard for service-to-service authentication using API keys.
    
    Used for N8N workflows and internal service calls.
    """
    
    HEADER_NAME = "X-Service-Key"
    
    def __init__(self, service_key: Optional[str] = None):
        """
        Initialize the service key guard.
        
        Args:
            service_key: Expected service key (defaults to settings)
        """
        self.service_key = service_key or settings.n8n.service_key
    
    def get_auth_header(self, request: Request) -> Optional[str]:
        """Extract service key from X-Service-Key header."""
        return request.headers.get(self.HEADER_NAME)
    
    def authenticate(self, request: Request) -> ServiceContext:
        """
        Authenticate the request using service key.
        
        Args:
            request: The incoming FastAPI request
            
        Returns:
            ServiceContext for the authenticated service
            
        Raises:
            UnauthorizedError: If no service key provided
            InvalidServiceKeyError: If service key is invalid
        """
        key = self.get_auth_header(request)
        
        if not key:
            raise UnauthorizedError(
                message="Service key required",
                details={"hint": f"Include '{self.HEADER_NAME}: <key>' header"}
            )
        
        return self.validate_key(key)
    
    def validate_key(self, key: str) -> ServiceContext:
        """
        Validate a service key.
        
        Args:
            key: The service key to validate
            
        Returns:
            ServiceContext for the service
            
        Raises:
            InvalidServiceKeyError: If key is invalid
        """
        # Constant-time comparison to prevent timing attacks
        if not self._secure_compare(key, self.service_key):
            raise InvalidServiceKeyError(
                message="Invalid service key",
                details={"hint": "Check your N8N_SERVICE_KEY configuration"}
            )
        
        return ServiceContext(
            service_name="n8n",
            is_admin=True,
        )
    
    @staticmethod
    def _secure_compare(a: str, b: str) -> bool:
        """
        Perform constant-time string comparison.
        
        Prevents timing attacks by always comparing all characters.
        """
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a.encode(), b.encode()):
            result |= x ^ y
        
        return result == 0


# =============================================================================
# Combined Guard (User OR Service)
# =============================================================================

class CombinedAuthGuard:
    """
    Guard that accepts either user JWT or service key authentication.
    
    Useful for endpoints that can be called by both users and services.
    """
    
    def __init__(
        self,
        user_guard: Optional[UserGuard] = None,
        service_guard: Optional[ServiceKeyGuard] = None,
    ):
        self.user_guard = user_guard or UserGuard()
        self.service_guard = service_guard or ServiceKeyGuard()
    
    def authenticate(self, request: Request) -> tuple:
        """
        Attempt authentication via user JWT or service key.
        
        Args:
            request: The incoming FastAPI request
            
        Returns:
            Tuple of (context, auth_type) where auth_type is 'user' or 'service'
            
        Raises:
            UnauthorizedError: If neither authentication method succeeds
        """
        # Try service key first (faster check)
        service_key = self.service_guard.get_auth_header(request)
        if service_key:
            try:
                context = self.service_guard.validate_key(service_key)
                return context, "service"
            except InvalidServiceKeyError:
                pass  # Fall through to try user auth
        
        # Try user JWT
        token = self.user_guard.get_auth_header(request)
        if token:
            context = self.user_guard.validate_token(token)
            return context, "user"
        
        # Neither provided
        raise UnauthorizedError(
            message="Authentication required",
            details={
                "hint": "Provide either 'Authorization: Bearer <token>' or 'X-Service-Key: <key>'"
            }
        )


# =============================================================================
# FastAPI Dependencies
# =============================================================================

# Guard instances (singletons)
_user_guard = UserGuard()
_service_guard = ServiceKeyGuard()
_combined_guard = CombinedAuthGuard()


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(oauth2_scheme),
) -> UserContext:
    """
    FastAPI dependency for user authentication.
    
    Usage:
        @app.get("/api/jobs")
        async def list_jobs(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.user_id}
    
    Args:
        request: The FastAPI request object
        credentials: Optional bearer credentials
        
    Returns:
        UserContext with authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        return _user_guard.authenticate(request)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except (InvalidTokenError, ExpiredTokenError) as e:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def get_service_context(
    request: Request,
    x_service_key: Optional[str] = Header(None, alias="X-Service-Key"),
) -> ServiceContext:
    """
    FastAPI dependency for service key authentication.
    
    Usage:
        @app.patch("/api/jobs/{job_id}/status")
        async def update_status(service: ServiceContext = Depends(get_service_context)):
            return {"service": service.service_name}
    
    Args:
        request: The FastAPI request object
        x_service_key: Service key from header
        
    Returns:
        ServiceContext for authenticated service
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        return _service_guard.authenticate(request)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )
    except InvalidServiceKeyError as e:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(oauth2_scheme),
) -> Optional[UserContext]:
    """
    FastAPI dependency for optional user authentication.
    
    Returns None if no authentication provided, otherwise validates the token.
    
    Usage:
        @app.get("/api/public")
        async def public_endpoint(user: Optional[UserContext] = Depends(get_optional_user)):
            if user:
                return {"authenticated": True, "user_id": user.user_id}
            return {"authenticated": False}
    """
    token = _user_guard.get_auth_header(request)
    if not token:
        return None
    
    try:
        return _user_guard.validate_token(token)
    except (InvalidTokenError, ExpiredTokenError):
        return None


async def get_user_or_service(
    request: Request,
) -> tuple:
    """
    FastAPI dependency that accepts either user or service authentication.
    
    Returns:
        Tuple of (context, auth_type) where auth_type is 'user' or 'service'
    
    Usage:
        @app.get("/api/resource")
        async def get_resource(auth: tuple = Depends(get_user_or_service)):
            context, auth_type = auth
            if auth_type == 'user':
                # Handle user request
                pass
            else:
                # Handle service request
                pass
    """
    try:
        return _combined_guard.authenticate(request)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=HttpStatus.UNAUTHORIZED,
            detail={"error": {"code": e.code, "message": e.message, "details": e.details}}
        )


# =============================================================================
# Utility Functions
# =============================================================================

def create_test_token(
    user_id: str,
    email: str = "test@example.com",
    role: str = "authenticated",
    exp_hours: int = 1,
) -> str:
    """
    Create a test JWT token for development/testing.
    
    WARNING: Only use in development/testing environments!
    
    Args:
        user_id: User ID to include in token
        email: User email
        role: User role
        exp_hours: Hours until expiration
        
    Returns:
        Encoded JWT token string
    """
    from datetime import timedelta
    
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=exp_hours),
        "aud": "authenticated",
    }
    
    return jwt.encode(payload, settings.supabase.jwt_secret, algorithm="HS256")
