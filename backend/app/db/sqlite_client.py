"""
SQLite fallback client for offline development.
Provides same interface as SupabaseClient for seamless switching.
"""
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger

logger = get_logger(__name__)

# SQL schema for creating tables
SCHEMA = """
-- Users table (simplified, auth handled separately)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    user_metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Discovery jobs
CREATE TABLE IF NOT EXISTS discovery_jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    reference_profiles TEXT DEFAULT '[]',
    settings TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Brand DNA extracted from reference profiles
CREATE TABLE IF NOT EXISTS brand_dna (
    id TEXT PRIMARY KEY,
    job_id TEXT UNIQUE NOT NULL,
    hashtags TEXT DEFAULT '[]',
    keywords TEXT DEFAULT '[]',
    competitors TEXT DEFAULT '[]',
    embedding TEXT DEFAULT '[]',
    analysis TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES discovery_jobs(id) ON DELETE CASCADE
);

-- Discovered Instagram profiles
CREATE TABLE IF NOT EXISTS discovered_profiles (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    username TEXT NOT NULL,
    profile_url TEXT,
    display_name TEXT,
    bio TEXT,
    follower_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    profile_pic_url TEXT,
    is_verified INTEGER DEFAULT 0,
    is_business INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new',
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES discovery_jobs(id) ON DELETE CASCADE
);

-- Profile scores from AI scoring
CREATE TABLE IF NOT EXISTS profile_scores (
    id TEXT PRIMARY KEY,
    profile_id TEXT UNIQUE NOT NULL,
    overall_score INTEGER DEFAULT 0,
    category_scores TEXT DEFAULT '{}',
    reasoning TEXT,
    metadata TEXT DEFAULT '{}',
    scored_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES discovered_profiles(id) ON DELETE CASCADE
);

-- Extracted contact information
CREATE TABLE IF NOT EXISTS profile_contacts (
    id TEXT PRIMARY KEY,
    profile_id TEXT UNIQUE NOT NULL,
    email TEXT,
    source TEXT,
    confidence REAL DEFAULT 0.0,
    extracted_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES discovered_profiles(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX IF NOT EXISTS idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX IF NOT EXISTS idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX IF NOT EXISTS idx_profile_scores_overall ON profile_scores(overall_score);
"""


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Convert sqlite3 row to dictionary."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


class SQLiteClient:
    """
    SQLite client with Supabase-compatible interface.

    Provides fallback database functionality for offline development.
    """

    def __init__(self, database_path: str):
        """
        Initialize SQLite client.

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = Path(database_path)

        # Ensure directory exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_schema()

        logger.info("SQLite client initialized", path=str(self.database_path))

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(str(self.database_path))
        conn.row_factory = dict_factory
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        try:
            conn.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()

    def execute(
        self,
        query: str,
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(query, params or ())
            results = cursor.fetchall()
            conn.commit()
            return results
        except sqlite3.Error as e:
            logger.error("SQL execution failed", query=query, error=str(e))
            raise DatabaseError(f"SQL error: {str(e)}", operation="execute")
        finally:
            conn.close()

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a record into a table.

        Args:
            table: Table name
            data: Record data

        Returns:
            Created record with ID
        """
        if table == "discovery_jobs" and "user_id" in data:
            user_id = data["user_id"]
            if not self.select_one("users", user_id):
                self.insert(
                    "users",
                    {"id": user_id, "email": f"{user_id}@local.invalid"}
                )

        if table == "discovered_profiles" and "profile_url" not in data:
            username = data.get("username")
            if username:
                data["profile_url"] = f"https://www.instagram.com/{username}/"

        # Generate UUID if not provided
        if "id" not in data:
            data["id"] = str(uuid.uuid4())

        # Add timestamps only for tables that include these columns
        now = datetime.utcnow().isoformat()
        created_at_tables = {"users", "discovery_jobs", "brand_dna"}
        if "created_at" not in data and table in created_at_tables:
            data["created_at"] = now
        if "updated_at" not in data and table == "discovery_jobs":
            data["updated_at"] = now

        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        values = list(data.values())

        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        conn = self._get_connection()
        try:
            conn.execute(query, tuple(values))
            conn.commit()

            # Return the created record
            created = self.select_one(table, data["id"])
            if not created:
                raise DatabaseError("Insert returned no record", operation="insert")
            return created
        except sqlite3.Error as e:
            logger.error("Insert failed", table=table, error=str(e))
            raise DatabaseError(f"Insert failed: {str(e)}", operation="insert")
        finally:
            conn.close()

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
            columns: Columns to select
            filters: Key-value filters
            order_by: Column to order by (prefix with - for desc)
            limit: Maximum records
            offset: Records to skip

        Returns:
            List of matching records
        """
        query = f"SELECT {columns} FROM {table}"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        if order_by:
            if order_by.startswith("-"):
                query += f" ORDER BY {order_by[1:]} DESC"
            else:
                query += f" ORDER BY {order_by} ASC"

        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        results = self.execute(query, tuple(params))
        return [self._deserialize_record(table, r) for r in results]

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
        results = self.select(table, columns, filters={"id": record_id}, limit=1)
        return results[0] if results else None

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
        """
        # Add updated_at timestamp
        if table == "discovery_jobs":
            data["updated_at"] = datetime.utcnow().isoformat()

        set_clauses = [f"{key} = ?" for key in data.keys()]
        values = list(data.values()) + [record_id]

        query = f"""
            UPDATE {table}
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """

        conn = self._get_connection()
        try:
            cursor = conn.execute(query, tuple(values))
            conn.commit()

            if cursor.rowcount == 0:
                raise DatabaseError(f"Record not found: {record_id}", operation="update")

            updated = self.select_one(table, record_id)
            if not updated:
                raise DatabaseError("Update returned no record", operation="update")
            return updated
        except sqlite3.Error as e:
            logger.error("Update failed", table=table, id=record_id, error=str(e))
            raise DatabaseError(f"Update failed: {str(e)}", operation="update")
        finally:
            conn.close()

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
            True if deleted
        """
        query = f"DELETE FROM {table} WHERE id = ?"

        conn = self._get_connection()
        try:
            cursor = conn.execute(query, (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error("Delete failed", table=table, id=record_id, error=str(e))
            raise DatabaseError(f"Delete failed: {str(e)}", operation="delete")
        finally:
            conn.close()

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
        existing = None
        if on_conflict in data:
            existing = self.select_one(table, data[on_conflict])

        if existing:
            return self.update(table, data[on_conflict], data)
        else:
            return self.insert(table, data)

    def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records in a table.

        Args:
            table: Table name
            filters: Optional filters

        Returns:
            Count of matching records
        """
        query = f"SELECT COUNT(*) as count FROM {table}"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        results = self.execute(query, tuple(params))
        return results[0]["count"] if results else 0

    def _deserialize_record(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if not record:
            return record

        json_fields = {
            "discovery_jobs": {"reference_profiles", "settings"},
            "brand_dna": {"hashtags", "keywords", "competitors", "embedding", "analysis"},
            "profile_scores": {"category_scores", "metadata"},
        }

        fields = json_fields.get(table, set())
        for field in fields:
            if field in record and isinstance(record[field], str):
                try:
                    record[field] = json.loads(record[field])
                except json.JSONDecodeError:
                    pass

        return record


def get_sqlite_client() -> SQLiteClient:
    """
    Get SQLite client instance.

    Returns:
        SQLiteClient instance
    """
    from app.core.config import get_settings
    settings = get_settings()
    return SQLiteClient(settings.sqlite_database_path)
