"""
Unit tests for base Pydantic models.
TDD: Write these tests FIRST, then implement models.
"""
import pytest
from datetime import datetime
from uuid import UUID


class TestBaseModel:
    """Test suite for base model functionality."""

    def test_base_model_has_id(self):
        """Base model should have optional UUID id field."""
        from app.models.base import BaseDBModel

        model = BaseDBModel()
        assert hasattr(model, "id")

    def test_base_model_generates_uuid(self):
        """Base model should auto-generate UUID if not provided."""
        from app.models.base import BaseDBModel

        model = BaseDBModel()
        assert model.id is not None
        assert isinstance(model.id, UUID)

    def test_base_model_accepts_uuid_string(self):
        """Base model should accept UUID as string."""
        from app.models.base import BaseDBModel

        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        model = BaseDBModel(id=uuid_str)
        assert str(model.id) == uuid_str

    def test_base_model_has_timestamps(self):
        """Base model should have created_at and updated_at."""
        from app.models.base import TimestampMixin

        class TestModel(TimestampMixin):
            pass

        model = TestModel()
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")

    def test_timestamps_auto_generated(self):
        """Timestamps should be auto-generated."""
        from app.models.base import TimestampMixin

        class TestModel(TimestampMixin):
            pass

        model = TestModel()
        assert model.created_at is not None
        assert isinstance(model.created_at, datetime)


class TestResponseModel:
    """Test API response model patterns."""

    def test_api_response_has_data_field(self):
        """API response should wrap data."""
        from app.models.base import APIResponse

        response = APIResponse(data={"key": "value"})
        assert response.data == {"key": "value"}

    def test_api_response_has_meta_field(self):
        """API response should have optional meta."""
        from app.models.base import APIResponse

        response = APIResponse(data={}, meta={"total": 100})
        assert response.meta["total"] == 100

    def test_paginated_response(self):
        """Paginated response should include pagination info."""
        from app.models.base import PaginatedResponse

        response = PaginatedResponse(
            data=[{"id": 1}, {"id": 2}],
            total=100,
            page=1,
            page_size=20
        )

        assert response.total == 100
        assert response.page == 1
        assert response.page_size == 20
        assert response.total_pages == 5
