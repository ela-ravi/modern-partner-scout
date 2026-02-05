"""
Compatibility wrapper for Supabase client.
"""
from app.db.supabase_client import SupabaseClient, get_admin_client, get_supabase_client

__all__ = ["SupabaseClient", "get_admin_client", "get_supabase_client"]
