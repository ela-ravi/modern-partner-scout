"""
PartnerScout AI - Supabase Database Client

Provides database client factory functions and FastAPI dependencies
for interacting with Supabase (PostgreSQL backend).
"""

from functools import lru_cache
from typing import Optional, Generator
from contextlib import contextmanager

from supabase import create_client, Client

from app.core.config import settings
from app.core.exceptions import SupabaseError


class SupabaseClient:
    """
    Wrapper around the Supabase client that provides
    additional functionality and error handling.
    """
    
    def __init__(self, client: Client, is_service_role: bool = False):
        """
        Initialize the Supabase client wrapper.
        
        Args:
            client: The underlying Supabase client
            is_service_role: Whether this client uses service role credentials
        """
        self._client = client
        self._is_service_role = is_service_role
    
    @property
    def client(self) -> Client:
        """Get the underlying Supabase client."""
        return self._client
    
    @property
    def is_service_role(self) -> bool:
        """Check if this client has service role privileges."""
        return self._is_service_role
    
    def table(self, table_name: str):
        """
        Get a table reference for querying.
        
        Args:
            table_name: Name of the table to query
            
        Returns:
            Supabase table query builder
        """
        return self._client.table(table_name)
    
    def rpc(self, function_name: str, params: Optional[dict] = None):
        """
        Call a Supabase RPC function.
        
        Args:
            function_name: Name of the PostgreSQL function
            params: Optional parameters to pass to the function
            
        Returns:
            RPC response
        """
        return self._client.rpc(function_name, params or {})
    
    def auth(self):
        """Get the Supabase auth client."""
        return self._client.auth
    
    def storage(self):
        """Get the Supabase storage client."""
        return self._client.storage
    
    def realtime(self):
        """Get the Supabase realtime client."""
        return self._client.realtime


def _create_supabase_client(use_service_role: bool = False) -> SupabaseClient:
    """
    Create a new Supabase client instance.
    
    Args:
        use_service_role: If True, use service role key (bypasses RLS).
                         If False, use anon key (respects RLS).
    
    Returns:
        SupabaseClient wrapper instance
        
    Raises:
        SupabaseError: If client creation fails
    """
    try:
        url = settings.supabase.url
        key = (
            settings.supabase.service_role_key 
            if use_service_role 
            else settings.supabase.anon_key
        )
        
        if not url or not key:
            raise SupabaseError(
                "Supabase URL or key not configured",
                details={"url_set": bool(url), "key_set": bool(key)}
            )
        
        # Create client with default options
        # The supabase-py library handles configuration internally
        client = create_client(url, key)
        
        return SupabaseClient(client, is_service_role=use_service_role)
        
    except Exception as e:
        if isinstance(e, SupabaseError):
            raise
        raise SupabaseError(
            f"Failed to create Supabase client: {str(e)}",
            details={"error_type": type(e).__name__}
        )


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """
    Get a cached Supabase client using the anon key.
    
    This client respects Row Level Security (RLS) policies.
    Use this for user-authenticated requests.
    
    Returns:
        SupabaseClient: Client with anon key
    """
    return _create_supabase_client(use_service_role=False)


@lru_cache()
def get_supabase_admin_client() -> SupabaseClient:
    """
    Get a cached Supabase client using the service role key.
    
    This client bypasses Row Level Security (RLS) policies.
    Use this for admin operations, background jobs, and service-to-service calls.
    
    ⚠️ WARNING: This client has full database access. Use with caution.
    
    Returns:
        SupabaseClient: Client with service role key
    """
    return _create_supabase_client(use_service_role=True)


def get_db() -> SupabaseClient:
    """
    FastAPI dependency for getting a database client.
    
    This is the primary dependency to use in route handlers.
    Returns the anon client by default (respects RLS).
    
    Usage:
        @app.get("/items")
        async def get_items(db: SupabaseClient = Depends(get_db)):
            result = db.table("items").select("*").execute()
            return result.data
    
    Returns:
        SupabaseClient: Database client for use in request handlers
    """
    return get_supabase_client()


def get_admin_db() -> SupabaseClient:
    """
    FastAPI dependency for getting an admin database client.
    
    This client bypasses RLS and should only be used for:
    - Background jobs and cron tasks
    - Service-to-service communication (N8N webhooks)
    - Admin operations
    
    Usage:
        @app.post("/internal/update-status")
        async def update_status(db: SupabaseClient = Depends(get_admin_db)):
            # Can modify any record regardless of RLS
            result = db.table("jobs").update({"status": "done"}).execute()
            return result.data
    
    Returns:
        SupabaseClient: Admin database client
    """
    return get_supabase_admin_client()


def create_authenticated_client(access_token: str) -> SupabaseClient:
    """
    Create a Supabase client authenticated with a user's JWT token.
    
    This allows making requests on behalf of a specific user,
    with RLS policies applied based on their user ID.
    
    Args:
        access_token: JWT access token from Supabase Auth
        
    Returns:
        SupabaseClient: Client authenticated as the user
        
    Raises:
        SupabaseError: If client creation or authentication fails
    """
    try:
        url = settings.supabase.url
        key = settings.supabase.anon_key
        
        if not url or not key:
            raise SupabaseError("Supabase URL or key not configured")
        
        # Create client with default options
        client = create_client(url, key)
        
        # Set the user's session
        client.auth.set_session(access_token, "")
        
        return SupabaseClient(client, is_service_role=False)
        
    except Exception as e:
        if isinstance(e, SupabaseError):
            raise
        raise SupabaseError(
            f"Failed to create authenticated client: {str(e)}",
            details={"error_type": type(e).__name__}
        )


@contextmanager
def get_transaction_client() -> Generator[SupabaseClient, None, None]:
    """
    Context manager for transaction-like operations.
    
    Note: Supabase doesn't support true transactions via the REST API.
    This provides a pattern for operations that should be grouped logically.
    For true transactions, use database functions (RPC).
    
    Usage:
        with get_transaction_client() as db:
            db.table("jobs").insert(job_data).execute()
            db.table("profiles").insert(profiles_data).execute()
    
    Yields:
        SupabaseClient: Admin client for the transaction scope
    """
    client = get_supabase_admin_client()
    try:
        yield client
    except Exception as e:
        # Log the error but re-raise
        # In a true transaction, we would rollback here
        raise SupabaseError(
            f"Transaction failed: {str(e)}",
            details={"error_type": type(e).__name__}
        )


def clear_client_cache() -> None:
    """
    Clear the cached Supabase clients.
    
    Useful for testing or when credentials have changed.
    """
    get_supabase_client.cache_clear()
    get_supabase_admin_client.cache_clear()


def check_connection() -> bool:
    """
    Check if the Supabase connection is working.
    
    Performs a simple query to verify connectivity.
    
    Returns:
        bool: True if connection is successful
        
    Raises:
        SupabaseError: If connection check fails
    """
    try:
        client = get_supabase_admin_client()
        # Try to query the discovery_jobs table (should exist)
        # Using a simple select with limit 0 just to check connectivity
        result = client.table("discovery_jobs").select("id").limit(1).execute()
        return True
    except Exception as e:
        raise SupabaseError(
            f"Database connection check failed: {str(e)}",
            details={"error_type": type(e).__name__}
        )
