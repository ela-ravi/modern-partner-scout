"""
PartnerScout AI - Job Repository

Repository for managing discovery jobs in the database.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.core.constants import Tables, JobStatus
from app.core.exceptions import JobNotFoundError, InvalidStatusTransitionError
from app.db import SupabaseClient


class JobRepository(BaseRepository[Dict[str, Any]]):
    """
    Repository for discovery_jobs table operations.
    
    Handles CRUD operations and specialized queries for discovery jobs.
    """
    
    @property
    def table_name(self) -> str:
        return Tables.DISCOVERY_JOBS
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create(
        self,
        user_id: str,
        brand_description: str,
        reference_profiles: List[str],
        name: Optional[str] = None,
        follower_range_min: int = 10000,
        follower_range_max: int = 500000,
        discovery_limit: int = 50
    ) -> Dict[str, Any]:
        """
        Create a new discovery job.
        
        Args:
            user_id: ID of the user creating the job
            brand_description: Description of the brand
            reference_profiles: List of Instagram profile URLs
            name: Optional job name
            follower_range_min: Minimum followers for discovery
            follower_range_max: Maximum followers for discovery
            discovery_limit: Maximum profiles to discover
            
        Returns:
            Created job data with generated ID
        """
        job_data = {
            "user_id": user_id,
            "brand_description": brand_description,
            "reference_profiles": reference_profiles,
            "follower_range_min": follower_range_min,
            "follower_range_max": follower_range_max,
            "discovery_limit": discovery_limit,
            "status": JobStatus.PENDING.value,
        }
        
        if name:
            job_data["name"] = name
        
        return self.insert(job_data)
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_id(self, id: str | UUID, select: str = "*") -> Dict[str, Any]:
        """
        Get a job by ID.
        
        Args:
            id: Job UUID
            select: Columns to select
            
        Returns:
            Job data
            
        Raises:
            JobNotFoundError: If job is not found
        """
        job = self.get_by_id_optional(id, select)
        if not job:
            raise JobNotFoundError(str(id))
        return job
    
    def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List jobs for a specific user.
        
        Args:
            user_id: User ID to filter by
            status: Optional status filter
            limit: Maximum results
            offset: Results to skip
            
        Returns:
            List of jobs for the user
        """
        query = (
            self._table()
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        return self._handle_response(response)
    
    def list_by_status(
        self,
        status: str | JobStatus,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List jobs by status.
        
        Args:
            status: Status to filter by
            limit: Maximum results
            
        Returns:
            List of jobs with the given status
        """
        status_value = status.value if isinstance(status, JobStatus) else status
        
        response = (
            self._table()
            .select("*")
            .eq("status", status_value)
            .order("created_at", desc=False)  # Oldest first for processing
            .limit(limit)
            .execute()
        )
        return self._handle_response(response)
    
    def count_user_jobs_today(self, user_id: str) -> int:
        """
        Count jobs created by user in the last 24 hours.
        
        Args:
            user_id: User ID to count jobs for
            
        Returns:
            Number of jobs created today
        """
        # Calculate 24 hours ago
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        yesterday_iso = yesterday.isoformat()
        
        response = (
            self._table()
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", yesterday_iso)
            .execute()
        )
        
        return response.count if hasattr(response, 'count') and response.count else len(response.data)
    
    def get_with_brand_dna(self, id: str | UUID) -> Dict[str, Any]:
        """
        Get a job with its brand DNA.
        
        Args:
            id: Job UUID
            
        Returns:
            Job data with brand_dna relation
        """
        response = (
            self._table()
            .select("*, brand_dna(*)")
            .eq("id", str(id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(id))
    
    def get_job_summary(self, id: str | UUID) -> Optional[Dict[str, Any]]:
        """
        Get job summary from the v_job_summary view.
        
        Args:
            id: Job UUID
            
        Returns:
            Job summary with statistics
        """
        response = (
            self.db.table(Tables.V_JOB_SUMMARY)
            .select("*")
            .eq("job_id", str(id))
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_status(
        self,
        id: str | UUID,
        status: str | JobStatus,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update job status.
        
        Args:
            id: Job UUID
            status: New status
            error_message: Optional error message (for failed status)
            
        Returns:
            Updated job data
        """
        status_value = status.value if isinstance(status, JobStatus) else status
        
        update_data = {"status": status_value}
        
        if error_message:
            update_data["error_message"] = error_message
        elif status_value == JobStatus.PENDING.value:
            # Clear error message when retrying
            update_data["error_message"] = None
        
        return self.update(str(id), update_data)
    
    def update_name(self, id: str | UUID, name: str) -> Dict[str, Any]:
        """
        Update job name.
        
        Args:
            id: Job UUID
            name: New name
            
        Returns:
            Updated job data
        """
        return self.update(str(id), {"name": name})
    
    def increment_profiles_discovered(self, id: str | UUID, count: int = 1) -> Dict[str, Any]:
        """
        Manually increment the profiles_discovered counter.
        
        Note: This is typically handled by database triggers, but
        provided for manual adjustments if needed.
        
        Args:
            id: Job UUID
            count: Amount to increment by
            
        Returns:
            Updated job data
        """
        job = self.get_by_id(id)
        new_count = job.get("profiles_discovered", 0) + count
        return self.update(str(id), {"profiles_discovered": new_count})
    
    def increment_profiles_scored(self, id: str | UUID, count: int = 1) -> Dict[str, Any]:
        """
        Manually increment the profiles_scored counter.
        
        Note: This is typically handled by database triggers, but
        provided for manual adjustments if needed.
        
        Args:
            id: Job UUID
            count: Amount to increment by
            
        Returns:
            Updated job data
        """
        job = self.get_by_id(id)
        new_count = job.get("profiles_scored", 0) + count
        return self.update(str(id), {"profiles_scored": new_count})
    
    # =========================================================================
    # Delete Operations
    # =========================================================================
    
    def delete_job(self, id: str | UUID) -> bool:
        """
        Delete a job and all related data (cascades via foreign keys).
        
        Args:
            id: Job UUID
            
        Returns:
            True if job was deleted
        """
        return self.delete(id)
    
    # =========================================================================
    # Specialized Queries
    # =========================================================================
    
    def get_active_jobs_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active (in-progress) jobs for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active jobs
        """
        active_statuses = [s.value for s in JobStatus.active_statuses()]
        
        response = (
            self._table()
            .select("*")
            .eq("user_id", user_id)
            .in_("status", active_statuses)
            .execute()
        )
        return self._handle_response(response)
    
    def get_retryable_jobs(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get failed jobs that can be retried.
        
        Args:
            user_id: User ID
            
        Returns:
            List of retryable jobs
        """
        retryable_statuses = [s.value for s in JobStatus.retryable_statuses()]
        
        response = (
            self._table()
            .select("*")
            .eq("user_id", user_id)
            .in_("status", retryable_statuses)
            .execute()
        )
        return self._handle_response(response)
    
    def get_pending_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get pending jobs ready to be processed.
        
        Args:
            limit: Maximum jobs to return
            
        Returns:
            List of pending jobs, oldest first
        """
        return self.list_by_status(JobStatus.PENDING, limit=limit)
