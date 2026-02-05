"""
Base Pydantic models for the application.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class BaseDBModel(BaseModel):
    """
    Base model for database entities.

    Provides UUID id field with auto-generation.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID | str = Field(default_factory=uuid4)


class TimestampMixin(BaseModel):
    """
    Mixin for models with timestamps.
    """

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class BaseEntity(BaseDBModel, TimestampMixin):
    """
    Base entity with ID and timestamps.

    Use as base class for all database entities.
    """
    pass


# Type variable for generic responses
T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.

    Attributes:
        data: Response payload
        meta: Optional metadata
    """

    data: T
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """
    Standard API error response.

    Matches the error format from exceptions.
    """

    error: Dict[str, Any] = Field(
        ...,
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "details": {}
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated API response.

    Attributes:
        data: List of items
        total: Total number of items
        page: Current page number
        page_size: Items per page
        total_pages: Calculated total pages
    """

    data: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class PaginationParams(BaseModel):
    """
    Pagination query parameters.
    """

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
