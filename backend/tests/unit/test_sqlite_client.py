"""
Unit tests for SQLite fallback client.
TDD: Write these tests FIRST, then implement sqlite_client.py
"""
import os
import pytest
import tempfile
from pathlib import Path


class TestSQLiteClient:
    """Test suite for SQLiteClient fallback."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def client(self, temp_db):
        """Create SQLite client with temp database."""
        from app.db.sqlite_client import SQLiteClient
        return SQLiteClient(temp_db)

    def test_client_creates_database_file(self, temp_db):
        """Client should create database file if not exists."""
        os.unlink(temp_db)  # Remove file

        from app.db.sqlite_client import SQLiteClient
        SQLiteClient(temp_db)

        assert os.path.exists(temp_db)

    def test_client_initializes_schema(self, client):
        """Client should create required tables on init."""
        # Check tables exist
        result = client.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row["name"] for row in result]

        assert "discovery_jobs" in tables
        assert "brand_dna" in tables
        assert "discovered_profiles" in tables
        assert "profile_scores" in tables
        assert "profile_contacts" in tables

    def test_insert_creates_record(self, client):
        """Insert should create and return record with ID."""
        result = client.insert("discovery_jobs", {
            "user_id": "test-user",
            "status": "pending",
            "reference_profiles": "[]",
            "settings": "{}"
        })

        assert "id" in result
        assert result["status"] == "pending"

    def test_select_returns_records(self, client):
        """Select should return matching records."""
        # Insert test data
        client.insert("discovery_jobs", {
            "user_id": "user-1",
            "status": "pending",
            "reference_profiles": "[]",
            "settings": "{}"
        })
        client.insert("discovery_jobs", {
            "user_id": "user-1",
            "status": "completed",
            "reference_profiles": "[]",
            "settings": "{}"
        })

        result = client.select("discovery_jobs", filters={"user_id": "user-1"})
        assert len(result) == 2

    def test_select_with_limit_and_offset(self, client):
        """Select should respect limit and offset."""
        for _ in range(5):
            client.insert("discovery_jobs", {
                "user_id": "user-1",
                "status": "pending",
                "reference_profiles": "[]",
                "settings": "{}"
            })

        result = client.select("discovery_jobs", limit=2, offset=2)
        assert len(result) == 2

    def test_update_modifies_record(self, client):
        """Update should modify existing record."""
        created = client.insert("discovery_jobs", {
            "user_id": "user-1",
            "status": "pending",
            "reference_profiles": "[]",
            "settings": "{}"
        })

        updated = client.update("discovery_jobs", created["id"], {
            "status": "completed"
        })

        assert updated["status"] == "completed"

    def test_delete_removes_record(self, client):
        """Delete should remove record."""
        created = client.insert("discovery_jobs", {
            "user_id": "user-1",
            "status": "pending",
            "reference_profiles": "[]",
            "settings": "{}"
        })

        result = client.delete("discovery_jobs", created["id"])
        assert result is True

        # Verify deleted
        found = client.select_one("discovery_jobs", created["id"])
        assert found is None

    def test_count_returns_record_count(self, client):
        """Count should return number of matching records."""
        for _ in range(3):
            client.insert("discovery_jobs", {
                "user_id": "user-1",
                "status": "pending",
                "reference_profiles": "[]",
                "settings": "{}"
            })

        count = client.count("discovery_jobs")
        assert count == 3


class TestSQLiteClientInterface:
    """Test that SQLite client matches Supabase client interface."""

    def test_interface_compatibility(self):
        """SQLite client should have same methods as Supabase client."""
        from app.db.sqlite_client import SQLiteClient
        from app.db.supabase_client import SupabaseClient

        sqlite_methods = {m for m in dir(SQLiteClient) if not m.startswith("_")}
        supabase_methods = {m for m in dir(SupabaseClient) if not m.startswith("_")}

        # SQLite should implement core methods
        required_methods = {"insert", "select", "select_one", "update", "delete", "count"}
        assert required_methods.issubset(sqlite_methods)
