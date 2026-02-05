"""
User-related Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.base import BaseEntity


class User(BaseEntity):
    """
    User entity model.

    Represents a user in the system (from Supabase Auth).
    """

    email: EmailStr
    user_metadata: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(BaseModel):
    """
    User registration request.
    """

    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v


class UserLogin(BaseModel):
    """
    User login request.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    User API response (excludes sensitive data).
    """

    id: UUID
    email: EmailStr
    user_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class UserSession(BaseModel):
    """
    User session information.
    """

    user: UserResponse
    access_token: str
    refresh_token: str
    expires_at: datetime


class TokenPayload(BaseModel):
    """
    JWT token payload.
    """

    sub: str  # User ID
    email: Optional[EmailStr] = None
    exp: Optional[datetime] = None
