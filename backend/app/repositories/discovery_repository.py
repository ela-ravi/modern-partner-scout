"""
Repository for DiscoveryJob entities.
"""
from typing import List, Optional

from app.core.constants import DiscoveryStatus
from app.models.discovery import DiscoveryJob, BrandDNA
from app.repositories.base import BaseRepository


class DiscoveryJobRepository(BaseRepository[DiscoveryJob]):
    """
    Repository for DiscoveryJob CRUD operations.
    """

    table_name = "discovery_jobs"
    model_class = DiscoveryJob

    def get_by_user(
        self,
        user_id: str,
        status: Optional[DiscoveryStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[DiscoveryJob]:
        """
        Get discovery jobs for a user.

        Args:
            user_id: User UUID
            status: Optional status filter
            limit: Maximum records
            offset: Records to skip

        Returns:
            List of discovery jobs
        """
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status.value

        return self.get_all(
            filters=filters,
            order_by="-created_at",
            limit=limit,
            offset=offset
        )

    def get_pending(self) -> List[DiscoveryJob]:
        """
        Get all pending discovery jobs.

        Returns:
            List of pending jobs
        """
        return self.get_all(
            filters={"status": DiscoveryStatus.PENDING.value},
            order_by="created_at"
        )

    def update_status(
        self,
        job_id: str,
        status: DiscoveryStatus | str
    ) -> DiscoveryJob:
        """
        Update job status.

        Args:
            job_id: Job UUID
            status: New status

        Returns:
            Updated job
        """
        if isinstance(status, str):
            status = DiscoveryStatus(status)
        return self.update(job_id, {"status": status.value})

    def count_by_user(self, user_id: str) -> int:
        """
        Count jobs for a user.

        Args:
            user_id: User UUID

        Returns:
            Count
        """
        return self.count(filters={"user_id": user_id})


class BrandDNARepository(BaseRepository[BrandDNA]):
    """
    Repository for BrandDNA CRUD operations.
    """

    table_name = "brand_dna"
    model_class = BrandDNA

    def get_by_job(self, job_id: str) -> Optional[BrandDNA]:
        """
        Get Brand DNA for a discovery job.

        Args:
            job_id: Job UUID

        Returns:
            BrandDNA if exists
        """
        results = self.get_all(filters={"job_id": job_id}, limit=1)
        return results[0] if results else None

    def upsert_for_job(
        self,
        job_id: str,
        data: dict
    ) -> BrandDNA:
        """
        Create or update Brand DNA for a job.

        Args:
            job_id: Job UUID
            data: Brand DNA data

        Returns:
            BrandDNA entity
        """
        existing = self.get_by_job(job_id)
        if existing:
            return self.update(str(existing.id), data)
        else:
            data["job_id"] = job_id
            return self.create(data)
