"""
PartnerScout AI - Database Module

Provides Supabase client factories and FastAPI dependencies
for database operations.

Usage:
    from app.db import get_db, get_admin_db, SupabaseClient
    
    # In FastAPI routes
    @app.get("/items")
    async def get_items(db: SupabaseClient = Depends(get_db)):
        result = db.table("items").select("*").execute()
        return result.data
"""

from app.db.supabase import (
    SupabaseClient,
    get_db,
    get_admin_db,
    get_supabase_client,
    get_supabase_admin_client,
    create_authenticated_client,
    get_transaction_client,
    clear_client_cache,
    check_connection,
)

__all__ = [
    "SupabaseClient",
    "get_db",
    "get_admin_db",
    "get_supabase_client",
    "get_supabase_admin_client",
    "create_authenticated_client",
    "get_transaction_client",
    "clear_client_cache",
    "check_connection",
]
