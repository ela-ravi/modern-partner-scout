"""
Compatibility wrapper for SQLite client.
"""
from app.db.sqlite_client import SQLiteClient, get_sqlite_client

__all__ = ["SQLiteClient", "get_sqlite_client"]
