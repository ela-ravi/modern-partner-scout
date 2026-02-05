"""
Database client factory for Supabase or SQLite fallback.
"""
from typing import Union

from app.core.config import get_settings
from app.db.sqlite_client import SQLiteClient, get_sqlite_client
from app.db.supabase_client import SupabaseClient, get_supabase_client, get_admin_client

DatabaseClient = Union[SupabaseClient, SQLiteClient]


def get_db_client() -> DatabaseClient:
    """
    Return the active database client based on settings.

    Uses SQLite when fallback is enabled or Supabase is unavailable.
    """
    settings = get_settings()
    if settings.use_sqlite_fallback:
        return get_sqlite_client()

    supabase = get_supabase_client()
    if supabase is None:
        return get_sqlite_client()

    return supabase


def get_admin_db_client() -> DatabaseClient:
    """
    Return admin-capable client for privileged operations.

    Falls back to SQLite when configured.
    """
    settings = get_settings()
    if settings.use_sqlite_fallback:
        return get_sqlite_client()

    return get_admin_client()
