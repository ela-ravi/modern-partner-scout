"""
Base repository pattern implementation.
Provides common CRUD operations for all entities.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Type variable for entity models
T = TypeVar("T", bound=BaseModel)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository with common CRUD operations.

    Subclasses must define:
    - table_name: Database table name
    - model_class: Pydantic model class for the entity
    """

    table_name: str
    model_class: Type[T]

    def __init__(self, db_client: Any) -> None:
        """
        Initialize repository with database client.

        Args:
            db_client: Database client (Supabase or SQLite)
        """
        self._db = db_client

    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.

        Args:
            data: Entity data

        Returns:
            Created entity
        """
        result = self._db.insert(self.table_name, data)
        logger.debug(f"Created {self.table_name} record", id=result.get("id"))
        return self._to_model(result)

    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity UUID

        Returns:
            Entity if found, None otherwise
        """
        result = self._db.select_one(self.table_name, entity_id, "*")
        if result:
            return self._to_model(result)
        return None

    def get_by_id_or_raise(self, entity_id: str) -> T:
        """
        Get entity by ID or raise NotFoundError.

        Args:
            entity_id: Entity UUID

        Returns:
            Entity

        Raises:
            NotFoundError: If entity not found
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            raise NotFoundError(
                f"{self.table_name} not found: {entity_id}",
                resource_type=self.table_name
            )
        return entity

    def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Get all entities matching filters.

        Args:
            filters: Key-value filters
            order_by: Column to order by
            limit: Maximum records
            offset: Records to skip

        Returns:
            List of entities
        """
        results = self._db.select(
            self.table_name,
            "*",
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset
        )
        return [self._to_model(r) for r in results]

    def update(self, entity_id: str, data: Dict[str, Any]) -> T:
        """
        Update an entity.

        Args:
            entity_id: Entity UUID
            data: Fields to update

        Returns:
            Updated entity
        """
        result = self._db.update(self.table_name, entity_id, data)
        logger.debug(f"Updated {self.table_name} record", id=entity_id)
        return self._to_model(result)

    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity UUID

        Returns:
            True if deleted
        """
        result = self._db.delete(self.table_name, entity_id)
        logger.debug(f"Deleted {self.table_name} record", id=entity_id)
        return bool(result)

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities matching filters.

        Args:
            filters: Optional filters

        Returns:
            Count
        """
        return int(self._db.count(self.table_name, filters))

    def exists(self, entity_id: str) -> bool:
        """
        Check if entity exists.

        Args:
            entity_id: Entity UUID

        Returns:
            True if exists
        """
        result = self._db.select_one(self.table_name, entity_id, "id")
        return result is not None

    def _to_model(self, data: Dict[str, Any]) -> T:
        """
        Convert database record to Pydantic model.

        Args:
            data: Database record

        Returns:
            Pydantic model instance
        """
        return cast(T, self.model_class.model_validate(data))

    def _serialize(self, model: T) -> Dict[str, Any]:
        """
        Serialize Pydantic model to database format.

        Args:
            model: Pydantic model

        Returns:
            Dict for database
        """
        return cast(Dict[str, Any], model.model_dump(mode="json"))
