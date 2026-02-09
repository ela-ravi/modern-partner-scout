"""
PartnerScout AI - Profile Repository

Repository for managing discovered profiles in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.core.constants import Tables, ProfileStatus
from app.core.exceptions import ProfileNotFoundError
from app.db import SupabaseClient


class ProfileRepository(BaseRepository[Dict[str, Any]]):
    """
    Repository for discovered_profiles table operations.
    
    Handles CRUD operations and specialized queries for discovered profiles.
    """
    
    @property
    def table_name(self) -> str:
        return Tables.DISCOVERED_PROFILES
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create(
        self,
        job_id: str,
        instagram_url: str,
        username: str,
        full_name: Optional[str] = None,
        profile_picture_url: Optional[str] = None,
        bio: Optional[str] = None,
        followers_count: int = 0,
        following_count: Optional[int] = None,
        posts_count: Optional[int] = None,
        engagement_rate: Optional[float] = None,
        is_verified: bool = False,
        is_business_account: Optional[bool] = None,
        external_url: Optional[str] = None,
        business_email: Optional[str] = None,
        business_category: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        recent_posts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new discovered profile.
        
        Args:
            job_id: ID of the parent discovery job
            instagram_url: Profile URL
            username: Instagram username
            full_name: Full name from profile
            profile_picture_url: Profile picture URL
            bio: Profile bio text
            followers_count: Number of followers
            following_count: Number of accounts followed
            posts_count: Number of posts
            engagement_rate: Calculated engagement rate
            is_verified: Whether account is verified
            is_business_account: Whether it's a business account
            external_url: External website link
            business_email: Business email if available
            business_category: Business category
            cover_image_url: Profile header image
            recent_posts: List of recent post data
            
        Returns:
            Created profile data
        """
        # Calculate following ratio if we have both counts
        following_ratio = None
        if following_count and followers_count > 0:
            following_ratio = round(following_count / followers_count, 2)
        
        profile_data = {
            "job_id": job_id,
            "instagram_url": instagram_url,
            "username": username,
            "followers_count": followers_count,
            "status": ProfileStatus.NEW.value,
        }
        
        # Add optional fields
        optional_fields = {
            "full_name": full_name,
            "profile_picture_url": profile_picture_url,
            "bio": bio,
            "following_count": following_count,
            "posts_count": posts_count,
            "engagement_rate": engagement_rate,
            "following_ratio": following_ratio,
            "is_verified": is_verified,
            "is_business_account": is_business_account,
            "external_url": external_url,
            "business_email": business_email,
            "business_category": business_category,
            "cover_image_url": cover_image_url,
            "recent_posts": recent_posts
        }
        
        for key, value in optional_fields.items():
            if value is not None:
                profile_data[key] = value
        
        return self.insert(profile_data)
    
    def create_many(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple profiles at once.
        
        Args:
            profiles: List of profile data dictionaries
            
        Returns:
            List of created profiles
        """
        # Ensure all profiles have status set
        for profile in profiles:
            if "status" not in profile:
                profile["status"] = ProfileStatus.NEW.value
        
        return self.insert_many(profiles)
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_id(self, id: str | UUID, select: str = "*") -> Dict[str, Any]:
        """
        Get a profile by ID.
        
        Args:
            id: Profile UUID
            select: Columns to select
            
        Returns:
            Profile data
            
        Raises:
            ProfileNotFoundError: If profile is not found
        """
        profile = self.get_by_id_optional(id, select)
        if not profile:
            raise ProfileNotFoundError(str(id))
        return profile
    
    def list_by_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List profiles for a specific job.
        
        Args:
            job_id: Job ID to filter by
            status: Optional status filter
            limit: Maximum results
            offset: Results to skip
            order_by: Column to order by
            ascending: Sort direction
            
        Returns:
            List of profiles for the job
        """
        query = (
            self._table()
            .select("*")
            .eq("job_id", job_id)
            .order(order_by, desc=not ascending)
            .range(offset, offset + limit - 1)
        )
        
        if status:
            query = query.eq("status", status)
        
        response = query.execute()
        return self._handle_response(response)
    
    def list_by_job_with_scores(
        self,
        job_id: str,
        min_score: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List profiles for a job with their scores joined.
        
        Args:
            job_id: Job ID to filter by
            min_score: Optional minimum final score filter
            status: Optional status filter
            limit: Maximum results
            offset: Results to skip
            
        Returns:
            List of profiles with scores
        """
        # Use the complete profiles view for joined data
        query = (
            self.db.table(Tables.V_COMPLETE_PROFILES)
            .select("*")
            .eq("job_id", job_id)
            .order("final_score", desc=True, nullsfirst=False)
            .range(offset, offset + limit - 1)
        )
        
        if status:
            query = query.eq("status", status)
        
        if min_score is not None:
            query = query.gte("final_score", min_score)
        
        response = query.execute()
        return self._handle_response(response)
    
    def list_by_status(
        self,
        job_id: str,
        status: str | ProfileStatus
    ) -> List[Dict[str, Any]]:
        """
        List profiles by status within a job.
        
        Args:
            job_id: Job ID
            status: Status to filter by
            
        Returns:
            List of profiles with the given status
        """
        status_value = status.value if isinstance(status, ProfileStatus) else status
        
        response = (
            self._table()
            .select("*")
            .eq("job_id", job_id)
            .eq("status", status_value)
            .execute()
        )
        return self._handle_response(response)
    
    def get_profile_with_score(self, id: str | UUID) -> Optional[Dict[str, Any]]:
        """
        Get a profile with its score.
        
        Args:
            id: Profile UUID
            
        Returns:
            Profile data with score
        """
        response = (
            self.db.table(Tables.V_COMPLETE_PROFILES)
            .select("*")
            .eq("id", str(id))
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    def get_by_username(self, job_id: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a profile by username within a job.
        
        Args:
            job_id: Job ID
            username: Instagram username
            
        Returns:
            Profile data or None
        """
        response = (
            self._table()
            .select("*")
            .eq("job_id", job_id)
            .eq("username", username)
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    def count_by_job(self, job_id: str, status: Optional[str] = None) -> int:
        """
        Count profiles for a job.
        
        Args:
            job_id: Job ID
            status: Optional status filter
            
        Returns:
            Profile count
        """
        filters = {"job_id": job_id}
        if status:
            filters["status"] = status
        return self.count(filters)
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_status(
        self,
        id: str | UUID,
        status: str | ProfileStatus
    ) -> Dict[str, Any]:
        """
        Update profile status.
        
        Args:
            id: Profile UUID
            status: New status
            
        Returns:
            Updated profile data
        """
        status_value = status.value if isinstance(status, ProfileStatus) else status
        return self.update(str(id), {"status": status_value})
    
    def update_status_batch(
        self,
        job_id: str,
        from_status: str | ProfileStatus,
        to_status: str | ProfileStatus
    ) -> List[Dict[str, Any]]:
        """
        Update status for all profiles matching a criteria.
        
        Args:
            job_id: Job ID
            from_status: Current status to match
            to_status: New status to set
            
        Returns:
            List of updated profiles
        """
        from_value = from_status.value if isinstance(from_status, ProfileStatus) else from_status
        to_value = to_status.value if isinstance(to_status, ProfileStatus) else to_status
        
        return self.update_where(
            {"job_id": job_id, "status": from_value},
            {"status": to_value}
        )
    
    # =========================================================================
    # Specialized Queries
    # =========================================================================
    
    def get_unprocessed_profiles(
        self,
        job_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get profiles that haven't been scored yet.
        
        Args:
            job_id: Job ID
            limit: Maximum profiles to return
            
        Returns:
            List of unprocessed profiles
        """
        processable_statuses = [s.value for s in ProfileStatus.processable_statuses()]
        
        response = (
            self._table()
            .select("*")
            .eq("job_id", job_id)
            .in_("status", processable_statuses)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return self._handle_response(response)
    
    def get_high_score_profiles(
        self,
        job_id: str,
        min_score: int = 80,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get high-scoring profiles for a job.
        
        Args:
            job_id: Job ID
            min_score: Minimum score threshold
            limit: Maximum results
            
        Returns:
            List of high-scoring profiles with scores
        """
        response = (
            self.db.table(Tables.V_COMPLETE_PROFILES)
            .select("*")
            .eq("job_id", job_id)
            .gte("final_score", min_score)
            .order("final_score", desc=True)
            .limit(limit)
            .execute()
        )
        return self._handle_response(response)
    
    def get_profiles_with_email(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Get profiles that have contact email available.
        
        Args:
            job_id: Job ID
            
        Returns:
            List of profiles with emails
        """
        response = (
            self.db.table(Tables.V_COMPLETE_PROFILES)
            .select("*")
            .eq("job_id", job_id)
            .not_.is_("contact_email", "null")
            .order("final_score", desc=True)
            .execute()
        )
        return self._handle_response(response)
    
    def check_duplicate(self, job_id: str, username: str) -> bool:
        """
        Check if a username already exists for this job.
        
        Args:
            job_id: Job ID
            username: Username to check
            
        Returns:
            True if duplicate exists
        """
        return self.get_by_username(job_id, username) is not None
