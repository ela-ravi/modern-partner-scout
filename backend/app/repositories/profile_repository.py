"""
Repository for Profile-related entities.
"""
from typing import List, Optional

from app.core.constants import ProfileStatus
from app.models.profile import DiscoveredProfile, ProfileScore, ProfileContact
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[DiscoveredProfile]):
    """
    Repository for DiscoveredProfile CRUD operations.
    """

    table_name = "discovered_profiles"
    model_class = DiscoveredProfile

    def get_by_job(
        self,
        job_id: str,
        status: Optional[ProfileStatus] = None,
        min_score: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[DiscoveredProfile]:
        """
        Get profiles for a discovery job.

        Args:
            job_id: Job UUID
            status: Optional status filter
            min_score: Minimum score filter (requires join)
            limit: Maximum records
            offset: Records to skip

        Returns:
            List of profiles
        """
        filters = {"job_id": job_id}
        if status:
            filters["status"] = status.value

        return self.get_all(
            filters=filters,
            order_by="-discovered_at",
            limit=limit,
            offset=offset
        )

    def get_by_username(
        self,
        job_id: str,
        username: str
    ) -> Optional[DiscoveredProfile]:
        """
        Get profile by username within a job.

        Args:
            job_id: Job UUID
            username: Instagram username

        Returns:
            Profile if found
        """
        results = self.get_all(
            filters={"job_id": job_id, "username": username},
            limit=1
        )
        return results[0] if results else None

    def update_status(
        self,
        profile_id: str,
        status: ProfileStatus
    ) -> DiscoveredProfile:
        """
        Update profile status.

        Args:
            profile_id: Profile UUID
            status: New status

        Returns:
            Updated profile
        """
        return self.update(profile_id, {"status": status.value})

    def count_by_job(
        self,
        job_id: str,
        status: Optional[ProfileStatus] = None
    ) -> int:
        """
        Count profiles for a job.

        Args:
            job_id: Job UUID
            status: Optional status filter

        Returns:
            Count
        """
        filters = {"job_id": job_id}
        if status:
            filters["status"] = status.value
        return self.count(filters)

    def bulk_create(
        self,
        profiles: List[dict]
    ) -> List[DiscoveredProfile]:
        """
        Create multiple profiles.

        Args:
            profiles: List of profile data

        Returns:
            List of created profiles
        """
        return [self.create(p) for p in profiles]


class ProfileScoreRepository(BaseRepository[ProfileScore]):
    """
    Repository for ProfileScore CRUD operations.
    """

    table_name = "profile_scores"
    model_class = ProfileScore

    def get_by_profile(self, profile_id: str) -> Optional[ProfileScore]:
        """
        Get score for a profile.

        Args:
            profile_id: Profile UUID

        Returns:
            Score if exists
        """
        results = self.get_all(filters={"profile_id": profile_id}, limit=1)
        return results[0] if results else None

    def get_top_scores(
        self,
        job_id: str,
        limit: int = 10
    ) -> List[ProfileScore]:
        """
        Get top scoring profiles for a job.

        Note: Requires join with profiles table for job_id filter.
        This is a simplified version.

        Args:
            job_id: Job UUID
            limit: Maximum records

        Returns:
            List of top scores
        """
        # This would need a custom query for proper implementation
        return self.get_all(order_by="-overall_score", limit=limit)

    def upsert_for_profile(
        self,
        profile_id: str,
        score_data: dict
    ) -> ProfileScore:
        """
        Create or update score for a profile.

        Args:
            profile_id: Profile UUID
            score_data: Score data

        Returns:
            ProfileScore entity
        """
        existing = self.get_by_profile(profile_id)
        if existing:
            return self.update(str(existing.id), score_data)
        else:
            score_data["profile_id"] = profile_id
            return self.create(score_data)


class ProfileContactRepository(BaseRepository[ProfileContact]):
    """
    Repository for ProfileContact CRUD operations.
    """

    table_name = "profile_contacts"
    model_class = ProfileContact

    def get_by_profile(self, profile_id: str) -> Optional[ProfileContact]:
        """
        Get contact for a profile.

        Args:
            profile_id: Profile UUID

        Returns:
            Contact if exists
        """
        results = self.get_all(filters={"profile_id": profile_id}, limit=1)
        return results[0] if results else None

    def get_with_email(
        self,
        job_id: str,
        min_confidence: float = 0.5
    ) -> List[ProfileContact]:
        """
        Get contacts with emails for a job.

        Note: Requires join for job_id filter.

        Args:
            job_id: Job UUID
            min_confidence: Minimum confidence threshold

        Returns:
            List of contacts with emails
        """
        # Simplified - would need custom query
        results = self.get_all()
        return [c for c in results if c.email and c.confidence >= min_confidence]
