"""
PartnerScout AI - Base Repository

Provides a generic base class for all repositories with common
CRUD operations and query utilities.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from app.db import get_admin_db, SupabaseClient
from app.core.constants import Tables
from app.core.exceptions import NotFoundError, SupabaseError


# Type variable for the entity type
T = TypeVar("T", bound=Dict[str, Any])


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common database operations.
    
    All repositories should inherit from this class and specify
    their table name and entity type.
    """
    
    def __init__(self, db: Optional[SupabaseClient] = None):
        """
        Initialize the repository.
        
        Args:
            db: Optional database client. If not provided, uses admin client.
        """
        self._db = db or get_admin_db()
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the name of the database table."""
        pass
    
    @property
    def db(self) -> SupabaseClient:
        """Get the database client."""
        return self._db
    
    def _table(self):
        """Get a query builder for this repository's table."""
        return self._db.table(self.table_name)
    
    def _handle_response(self, response) -> List[Dict[str, Any]]:
        """
        Handle Supabase response and extract data.
        
        Args:
            response: Supabase API response
            
        Returns:
            List of data dictionaries
            
        Raises:
            SupabaseError: If the response contains an error
        """
        if hasattr(response, 'data'):
            return response.data
        return []
    
    def _handle_single_response(
        self, 
        response, 
        raise_if_empty: bool = True,
        entity_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Handle Supabase response expecting a single result.
        
        Args:
            response: Supabase API response
            raise_if_empty: Whether to raise NotFoundError if no results
            entity_id: Optional ID for error message
            
        Returns:
            Single data dictionary or None
            
        Raises:
            NotFoundError: If no results and raise_if_empty is True
        """
        data = self._handle_response(response)
        if data:
            return data[0]
        if raise_if_empty:
            raise NotFoundError(
                f"{self.table_name} not found",
                resource_type=self.table_name,
                resource_id=entity_id
            )
        return None
    
    # =========================================================================
    # Generic CRUD Operations
    # =========================================================================
    
    def get_by_id(self, id: str | UUID, select: str = "*") -> Optional[Dict[str, Any]]:
        """
        Get a single entity by its ID.
        
        Args:
            id: The UUID of the entity
            select: Columns to select (default "*")
            
        Returns:
            Entity data dictionary or None if not found
            
        Raises:
            NotFoundError: If entity is not found
        """
        response = (
            self._table()
            .select(select)
            .eq("id", str(id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(id))
    
    def get_by_id_optional(self, id: str | UUID, select: str = "*") -> Optional[Dict[str, Any]]:
        """
        Get a single entity by its ID, returning None if not found.
        
        Args:
            id: The UUID of the entity
            select: Columns to select (default "*")
            
        Returns:
            Entity data dictionary or None
        """
        response = (
            self._table()
            .select(select)
            .eq("id", str(id))
            .execute()
        )
        return self._handle_single_response(response, raise_if_empty=False)
    
    def list_all(
        self,
        select: str = "*",
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all entities with pagination.
        
        Args:
            select: Columns to select (default "*")
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Column to order by
            ascending: Sort ascending if True, descending if False
            
        Returns:
            List of entity dictionaries
        """
        response = (
            self._table()
            .select(select)
            .order(order_by, desc=not ascending)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return self._handle_response(response)
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching optional filters.
        
        Args:
            filters: Dictionary of column=value filters
            
        Returns:
            Count of matching entities
        """
        query = self._table().select("id", count="exact")
        
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        response = query.execute()
        return response.count if hasattr(response, 'count') else len(response.data)
    
    def exists(self, id: str | UUID) -> bool:
        """
        Check if an entity exists by ID.
        
        Args:
            id: The UUID to check
            
        Returns:
            True if entity exists, False otherwise
        """
        response = (
            self._table()
            .select("id")
            .eq("id", str(id))
            .execute()
        )
        data = self._handle_response(response)
        return len(data) > 0
    
    def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a new entity.
        
        Args:
            data: Entity data to insert
            
        Returns:
            Inserted entity with generated fields (id, created_at, etc.)
        """
        response = (
            self._table()
            .insert(data)
            .execute()
        )
        return self._handle_single_response(response, raise_if_empty=False) or data
    
    def insert_many(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Insert multiple entities.
        
        Args:
            data: List of entity data to insert
            
        Returns:
            List of inserted entities
        """
        if not data:
            return []
        
        response = (
            self._table()
            .insert(data)
            .execute()
        )
        return self._handle_response(response)
    
    def update(self, id: str | UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an entity by ID.
        
        Args:
            id: The UUID of the entity to update
            data: Fields to update
            
        Returns:
            Updated entity data
            
        Raises:
            NotFoundError: If entity is not found
        """
        response = (
            self._table()
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(id))
    
    def update_where(
        self, 
        filters: Dict[str, Any], 
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Update entities matching filters.
        
        Args:
            filters: Dictionary of column=value filters
            data: Fields to update
            
        Returns:
            List of updated entities
        """
        query = self._table().update(data)
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        return self._handle_response(response)
    
    def delete(self, id: str | UUID) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            id: The UUID of the entity to delete
            
        Returns:
            True if entity was deleted
        """
        response = (
            self._table()
            .delete()
            .eq("id", str(id))
            .execute()
        )
        data = self._handle_response(response)
        return len(data) > 0
    
    def delete_where(self, filters: Dict[str, Any]) -> int:
        """
        Delete entities matching filters.
        
        Args:
            filters: Dictionary of column=value filters
            
        Returns:
            Number of deleted entities
        """
        query = self._table().delete()
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        return len(self._handle_response(response))
    
    # =========================================================================
    # Query Builder Helpers
    # =========================================================================
    
    def find_by(
        self,
        filters: Dict[str, Any],
        select: str = "*",
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find entities matching filters.
        
        Args:
            filters: Dictionary of column=value filters
            select: Columns to select
            limit: Maximum number of results
            order_by: Column to order by
            ascending: Sort ascending if True
            
        Returns:
            List of matching entities
        """
        query = self._table().select(select)
        
        for column, value in filters.items():
            if value is None:
                query = query.is_(column, "null")
            elif isinstance(value, list):
                query = query.in_(column, value)
            else:
                query = query.eq(column, value)
        
        if order_by:
            query = query.order(order_by, desc=not ascending)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return self._handle_response(response)
    
    def find_one_by(
        self,
        filters: Dict[str, Any],
        select: str = "*"
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single entity matching filters.
        
        Args:
            filters: Dictionary of column=value filters
            select: Columns to select
            
        Returns:
            Entity data or None
        """
        results = self.find_by(filters, select=select, limit=1)
        return results[0] if results else None
