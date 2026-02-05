"""
Unit tests for base repository pattern.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock


class TestBaseRepository:
    """Test suite for BaseRepository class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock database client."""
        client = MagicMock()
        client.insert = MagicMock(return_value={"id": "123", "name": "test"})
        client.select = MagicMock(return_value=[{"id": "123"}])
        client.select_one = MagicMock(return_value={"id": "123"})
        client.update = MagicMock(return_value={"id": "123", "name": "updated"})
        client.delete = MagicMock(return_value=True)
        client.count = MagicMock(return_value=5)
        return client

    def test_repository_requires_table_name(self, mock_client):
        """Repository should have table name defined."""
        from app.repositories.base import BaseRepository

        class TestRepo(BaseRepository):
            table_name = "test_table"

        repo = TestRepo(MagicMock())
        assert repo.table_name == "test_table"

    def test_create_inserts_record(self, mock_client):
        """Create should insert record and return entity."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        result = repo.create({"name": "test"})

        mock_client.insert.assert_called_once()
        assert result is not None

    def test_get_by_id_returns_entity(self, mock_client):
        """Get by ID should return entity or None."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        repo.get_by_id("123")

        mock_client.select_one.assert_called_with("test_table", "123", "*")

    def test_get_all_returns_list(self, mock_client):
        """Get all should return list of entities."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        result = repo.get_all()

        assert isinstance(result, list)

    def test_update_modifies_entity(self, mock_client):
        """Update should modify and return entity."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        repo.update("123", {"name": "updated"})

        mock_client.update.assert_called_once()

    def test_delete_removes_entity(self, mock_client):
        """Delete should remove entity."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        result = repo.delete("123")

        mock_client.delete.assert_called_with("test_table", "123")
        assert result is True

    def test_count_returns_integer(self, mock_client):
        """Count should return number of records."""
        from app.repositories.base import BaseRepository
        from app.models.base import BaseDBModel

        class TestRepo(BaseRepository):
            table_name = "test_table"
            model_class = BaseDBModel

        repo = TestRepo(mock_client)
        result = repo.count()

        assert result == 5
