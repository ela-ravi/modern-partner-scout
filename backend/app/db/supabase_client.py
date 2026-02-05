"""
Supabase client wrapper with typed operations and error handling.
"""
from functools import lru_cache
from typing import Any, Dict, List, Optional, TypeVar, cast

from supabase import create_client, Client

from app.core.config import Settings, get_settings
from app.core.exceptions import DatabaseError
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=Dict[str, Any])


class SupabaseClient:
    """
    Wrapper around Supabase client with typed operations.

    Provides a simplified interface for common database operations
    with proper error handling and logging.
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        use_service_role: bool = False
    ):
        """
        Initialize Supabase client.

        Args:
            settings: Application settings (uses get_settings() if not provided)
            use_service_role: Use service role key for admin operations
        """
        self._settings = settings or get_settings()

        key = (
            self._settings.supabase_service_role_key
            if use_service_role
            else self._settings.supabase_key
        )

        if not self._settings.supabase_url or not key:
            raise DatabaseError("Supabase credentials are not configured", operation="init")

        self._client: Client = create_client(
            cast(str, self._settings.supabase_url),
            cast(str, key)
        )

        logger.debug(
            "Supabase client initialized",
            url=self._settings.supabase_url,
            service_role=use_service_role
        )

    def table(self, name: str) -> Any:
        """
        Get a table reference for chained operations.

        Args:
            name: Table name

        Returns:
            Supabase table reference
        """
        return self._client.table(name)

    def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = "*"
    ) -> Dict[str, Any]:
        """
        Insert a record into a table.

        Args:
            table: Table name
            data: Record data to insert
            returning: Columns to return (default: all)

        Returns:
            Created record

        Raises:
            DatabaseError: If insert fails
        """
        try:
            response = (
                self._client
                .table(table)
                .insert(data)
                .execute()
            )

            if response.data:
                logger.debug(f"Inserted record into {table}", id=response.data[0].get("id"))
                return cast(Dict[str, Any], response.data[0])

            raise DatabaseError(f"Insert into {table} returned no data", operation="insert")

        except Exception as e:
            logger.error("Insert failed", table=table, error=str(e))
            raise DatabaseError(f"Failed to insert into {table}: {str(e)}", operation="insert")

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Select records from a table.

        Args:
            table: Table name
            columns: Columns to select (default: all)
            filters: Key-value filters to apply
            order_by: Column to order by (prefix with - for desc)
            limit: Maximum records to return
            offset: Records to skip

        Returns:
            List of matching records

        Raises:
            DatabaseError: If select fails
        """
        try:
            query = self._client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            if order_by:
                if order_by.startswith("-"):
                    query = query.order(order_by[1:], desc=True)
                else:
                    query = query.order(order_by)

            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            response = query.execute()
            return cast(List[Dict[str, Any]], response.data or [])

        except Exception as e:
            logger.error("Select failed", table=table, error=str(e))
            raise DatabaseError(f"Failed to select from {table}: {str(e)}", operation="select")

    def select_one(
        self,
        table: str,
        record_id: str,
        columns: str = "*"
    ) -> Optional[Dict[str, Any]]:
        """
        Select a single record by ID.

        Args:
            table: Table name
            record_id: Record UUID
            columns: Columns to select

        Returns:
            Record if found, None otherwise
        """
        try:
            response = (
                self._client
                .table(table)
                .select(columns)
                .eq("id", record_id)
                .maybe_single()
                .execute()
            )
            return cast(Optional[Dict[str, Any]], response.data)

        except Exception as e:
            logger.error("Select one failed", table=table, id=record_id, error=str(e))
            raise DatabaseError(f"Failed to select from {table}: {str(e)}", operation="select_one")

    def update(
        self,
        table: str,
        record_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a record by ID.

        Args:
            table: Table name
            record_id: Record UUID
            data: Fields to update

        Returns:
            Updated record

        Raises:
            DatabaseError: If update fails
        """
        try:
            response = (
                self._client
                .table(table)
                .update(data)
                .eq("id", record_id)
                .execute()
            )

            if response.data:
                logger.debug(f"Updated record in {table}", id=record_id)
                return cast(Dict[str, Any], response.data[0])

            raise DatabaseError(f"Update in {table} returned no data", operation="update")

        except Exception as e:
            logger.error("Update failed", table=table, id=record_id, error=str(e))
            raise DatabaseError(f"Failed to update {table}: {str(e)}", operation="update")

    def delete(
        self,
        table: str,
        record_id: str
    ) -> bool:
        """
        Delete a record by ID.

        Args:
            table: Table name
            record_id: Record UUID

        Returns:
            True if deleted successfully

        Raises:
            DatabaseError: If delete fails
        """
        try:
            (
                self._client
                .table(table)
                .delete()
                .eq("id", record_id)
                .execute()
            )

            logger.debug(f"Deleted record from {table}", id=record_id)
            return True

        except Exception as e:
            logger.error("Delete failed", table=table, id=record_id, error=str(e))
            raise DatabaseError(f"Failed to delete from {table}: {str(e)}", operation="delete")

    def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: str = "id"
    ) -> Dict[str, Any]:
        """
        Insert or update a record.

        Args:
            table: Table name
            data: Record data
            on_conflict: Column to check for conflicts

        Returns:
            Upserted record
        """
        try:
            response = (
                self._client
                .table(table)
                .upsert(data, on_conflict=on_conflict)
                .execute()
            )

            if response.data:
                return cast(Dict[str, Any], response.data[0])

            raise DatabaseError(f"Upsert into {table} returned no data", operation="upsert")

        except Exception as e:
            logger.error("Upsert failed", table=table, error=str(e))
            raise DatabaseError(f"Failed to upsert into {table}: {str(e)}", operation="upsert")

    def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records in a table.

        Args:
            table: Table name
            filters: Optional filters to apply

        Returns:
            Count of matching records
        """
        try:
            query = self._client.table(table).select("*", count="exact")

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return response.count or 0

        except Exception as e:
            logger.error("Count failed", table=table, error=str(e))
            raise DatabaseError(f"Failed to count {table}: {str(e)}", operation="count")

    @property
    def auth(self) -> Any:
        """Access Supabase auth client."""
        return self._client.auth


@lru_cache()
def get_supabase_client() -> Optional[SupabaseClient]:
    """
    Get cached Supabase client instance.

    Returns:
        SupabaseClient instance, or None if using SQLite fallback
    """
    settings = get_settings()

    if settings.use_sqlite_fallback:
        logger.info("SQLite fallback enabled, Supabase client not created")
        return None

    return SupabaseClient(settings)


def get_admin_client() -> SupabaseClient:
    """
    Get Supabase client with service role (admin) privileges.

    Use for operations that bypass RLS policies.

    Returns:
        SupabaseClient with service role key
    """
    return SupabaseClient(use_service_role=True)
