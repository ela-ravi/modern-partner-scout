"""
Unit tests for Supabase client wrapper.
TDD: Write these tests FIRST, then implement supabase_client.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSupabaseClient:
    """Test suite for SupabaseClient wrapper."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = MagicMock()
        settings.supabase_url = "https://test.supabase.co"
        settings.supabase_key = "test-anon-key"
        settings.supabase_service_role_key = "test-service-key"
        settings.use_sqlite_fallback = False
        return settings

    def test_client_initializes_with_settings(self, mock_settings):
        """Client should initialize with provided settings."""
        with patch("app.db.supabase_client.create_client") as mock_create:
            mock_create.return_value = MagicMock()

            from app.db.supabase_client import SupabaseClient
            SupabaseClient(mock_settings)

            mock_create.assert_called_once_with(
                mock_settings.supabase_url,
                mock_settings.supabase_key
            )

    def test_client_provides_table_access(self, mock_settings):
        """Client should provide access to database tables."""
        with patch("app.db.supabase_client.create_client") as mock_create:
            mock_supabase = MagicMock()
            mock_create.return_value = mock_supabase

            from app.db.supabase_client import SupabaseClient
            client = SupabaseClient(mock_settings)

            # Access table
            client.table("discovery_jobs")
            mock_supabase.table.assert_called_with("discovery_jobs")

    def test_client_uses_service_role_for_admin(self, mock_settings):
        """Client should use service role key for admin operations."""
        with patch("app.db.supabase_client.create_client") as mock_create:
            mock_create.return_value = MagicMock()

            from app.db.supabase_client import SupabaseClient
            SupabaseClient(mock_settings, use_service_role=True)

            mock_create.assert_called_with(
                mock_settings.supabase_url,
                mock_settings.supabase_service_role_key
            )


class TestSupabaseClientOperations:
    """Test CRUD operations on Supabase client."""

    @pytest.fixture
    def client(self):
        """Create a mocked client for testing."""
        with patch("app.db.supabase_client.create_client") as mock_create:
            mock_supabase = MagicMock()
            mock_create.return_value = mock_supabase

            settings = MagicMock()
            settings.supabase_url = "https://test.supabase.co"
            settings.supabase_key = "test-key"
            settings.use_sqlite_fallback = False

            from app.db.supabase_client import SupabaseClient
            return SupabaseClient(settings)

    def test_insert_returns_created_record(self, client):
        """Insert should return the created record."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "123", "name": "test"}]
        client._client.table().insert().execute.return_value = mock_response

        result = client.insert("test_table", {"name": "test"})
        assert result["id"] == "123"

    def test_select_returns_records(self, client):
        """Select should return matching records."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "1"}, {"id": "2"}]
        client._client.table().select().execute.return_value = mock_response

        result = client.select("test_table")
        assert len(result) == 2

    def test_select_with_filters(self, client):
        """Select should apply filters correctly."""
        mock_table = client._client.table()
        mock_response = MagicMock()
        mock_response.data = [{"id": "1"}]
        mock_table.select().eq().execute.return_value = mock_response

        client.select("test_table", filters={"status": "active"})
        mock_table.select().eq.assert_called()

    def test_update_modifies_record(self, client):
        """Update should modify existing record."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "123", "name": "updated"}]
        client._client.table().update().eq().execute.return_value = mock_response

        result = client.update("test_table", "123", {"name": "updated"})
        assert result["name"] == "updated"

    def test_delete_removes_record(self, client):
        """Delete should remove record from table."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "123"}]
        client._client.table().delete().eq().execute.return_value = mock_response

        result = client.delete("test_table", "123")
        assert result is True

    def test_handles_supabase_errors(self, client):
        """Client should handle Supabase errors gracefully."""
        from postgrest.exceptions import APIError
        client._client.table().select().execute.side_effect = APIError({
            "message": "Table not found",
            "code": "42P01"
        })

        from app.core.exceptions import DatabaseError
        with pytest.raises(DatabaseError):
            client.select("nonexistent_table")


class TestGetSupabaseClient:
    """Test get_supabase_client factory function."""

    def test_get_client_returns_singleton(self):
        """get_supabase_client should return cached instance."""
        with patch("app.db.supabase_client.create_client"):
            from app.db.supabase_client import get_supabase_client

            client1 = get_supabase_client()
            client2 = get_supabase_client()

            assert client1 is client2

    def test_get_client_respects_sqlite_fallback(self):
        """Should return None when SQLite fallback is enabled."""
        with patch("app.db.supabase_client.get_settings") as mock_settings:
            mock_settings.return_value.use_sqlite_fallback = True

            from app.db.supabase_client import get_supabase_client
            # Clear cache first
            get_supabase_client.cache_clear()

            result = get_supabase_client()
            assert result is None
