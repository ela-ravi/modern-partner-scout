"""
PartnerScout AI - Score Repository

Repository for managing profile scores in the database.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.repositories.base_repo import BaseRepository
from app.core.constants import Tables, ScoringDimensions
from app.core.exceptions import NotFoundError
from app.db import SupabaseClient


class ScoreRepository(BaseRepository[Dict[str, Any]]):
    """
    Repository for profile_scores table operations.
    
    Handles CRUD operations for AI-generated profile scores.
    """
    
    @property
    def table_name(self) -> str:
        return Tables.PROFILE_SCORES
    
    # =========================================================================
    # Create Operations
    # =========================================================================
    
    def create(
        self,
        profile_id: str,
        final_score: int,
        visual_aesthetic_match: Optional[int] = None,
        content_theme_alignment: Optional[int] = None,
        engagement_rate_score: Optional[int] = None,
        follower_quality: Optional[int] = None,
        business_indicators: Optional[int] = None,
        activity_recency: Optional[int] = None,
        recommendation: Optional[str] = None,
        reasoning: Optional[Dict[str, Any]] = None,
        is_fake_suspected: bool = False
    ) -> Dict[str, Any]:
        """
        Create a score for a profile.
        
        Args:
            profile_id: ID of the profile
            final_score: Weighted final score (0-100)
            visual_aesthetic_match: Score for visual aesthetic (0-100)
            content_theme_alignment: Score for content alignment (0-100)
            engagement_rate_score: Score for engagement rate (0-100)
            follower_quality: Score for follower quality (0-100)
            business_indicators: Score for business readiness (0-100)
            activity_recency: Score for recent activity (0-100)
            recommendation: Recommendation level
            reasoning: JSON reasoning data
            is_fake_suspected: Whether fake account is suspected
            
        Returns:
            Created score data
        """
        score_data = {
            "profile_id": profile_id,
            "final_score": final_score,
            "is_fake_suspected": is_fake_suspected,
        }
        
        # Add dimension scores
        if visual_aesthetic_match is not None:
            score_data["visual_aesthetic_match"] = visual_aesthetic_match
        if content_theme_alignment is not None:
            score_data["content_theme_alignment"] = content_theme_alignment
        if engagement_rate_score is not None:
            score_data["engagement_rate_score"] = engagement_rate_score
        if follower_quality is not None:
            score_data["follower_quality"] = follower_quality
        if business_indicators is not None:
            score_data["business_indicators"] = business_indicators
        if activity_recency is not None:
            score_data["activity_recency"] = activity_recency
        
        # Add recommendation and reasoning
        if recommendation:
            score_data["recommendation"] = recommendation
        if reasoning:
            score_data["reasoning"] = reasoning
        
        return self.insert(score_data)
    
    def create_full_score(
        self,
        profile_id: str,
        dimensions: Dict[str, int],
        final_score: int,
        recommendation: str,
        reasoning: Dict[str, Any],
        is_fake_suspected: bool = False
    ) -> Dict[str, Any]:
        """
        Create a complete score with all dimensions.
        
        Args:
            profile_id: Profile UUID
            dimensions: Dict with all 6 dimension scores
            final_score: Weighted final score
            recommendation: Recommendation level
            reasoning: Reasoning data
            is_fake_suspected: Fake account flag
            
        Returns:
            Created score data
        """
        return self.create(
            profile_id=profile_id,
            final_score=final_score,
            visual_aesthetic_match=dimensions.get("visual_aesthetic_match"),
            content_theme_alignment=dimensions.get("content_theme_alignment"),
            engagement_rate_score=dimensions.get("engagement_rate_score"),
            follower_quality=dimensions.get("follower_quality"),
            business_indicators=dimensions.get("business_indicators"),
            activity_recency=dimensions.get("activity_recency"),
            recommendation=recommendation,
            reasoning=reasoning,
            is_fake_suspected=is_fake_suspected
        )
    
    # =========================================================================
    # Read Operations
    # =========================================================================
    
    def get_by_profile_id(self, profile_id: str | UUID) -> Dict[str, Any]:
        """
        Get score for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Score data
            
        Raises:
            NotFoundError: If score not found
        """
        score = self.get_by_profile_id_optional(profile_id)
        if not score:
            raise NotFoundError(
                f"Score not found for profile: {profile_id}",
                resource_type="profile_score",
                resource_id=str(profile_id)
            )
        return score
    
    def get_by_profile_id_optional(self, profile_id: str | UUID) -> Optional[Dict[str, Any]]:
        """
        Get score for a profile, returning None if not found.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Score data or None
        """
        response = (
            self._table()
            .select("*")
            .eq("profile_id", str(profile_id))
            .execute()
        )
        data = self._handle_response(response)
        return data[0] if data else None
    
    def exists_for_profile(self, profile_id: str | UUID) -> bool:
        """
        Check if a score exists for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if score exists
        """
        response = (
            self._table()
            .select("id")
            .eq("profile_id", str(profile_id))
            .execute()
        )
        return len(self._handle_response(response)) > 0
    
    def list_by_job(
        self,
        job_id: str,
        min_score: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List scores for profiles in a job.
        
        Note: This joins with discovered_profiles to filter by job.
        
        Args:
            job_id: Job UUID
            min_score: Optional minimum score filter
            limit: Maximum results
            
        Returns:
            List of scores with profile IDs
        """
        # Join scores with profiles to filter by job
        query = (
            self._table()
            .select("*, discovered_profiles!inner(job_id, username)")
            .eq("discovered_profiles.job_id", job_id)
            .order("final_score", desc=True)
            .limit(limit)
        )
        
        if min_score is not None:
            query = query.gte("final_score", min_score)
        
        response = query.execute()
        return self._handle_response(response)
    
    def get_dimension_breakdown(self, profile_id: str | UUID) -> Dict[str, int]:
        """
        Get all dimension scores for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Dictionary of dimension name to score
        """
        score = self.get_by_profile_id(profile_id)
        
        return {
            dim: score.get(dim, 0)
            for dim in ScoringDimensions.all_dimensions()
        }
    
    # =========================================================================
    # Update Operations
    # =========================================================================
    
    def update_by_profile_id(
        self,
        profile_id: str | UUID,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update score by profile ID.
        
        Args:
            profile_id: Profile UUID
            data: Fields to update
            
        Returns:
            Updated score data
        """
        response = (
            self._table()
            .update(data)
            .eq("profile_id", str(profile_id))
            .execute()
        )
        return self._handle_single_response(response, entity_id=str(profile_id))
    
    def update_score(
        self,
        profile_id: str | UUID,
        final_score: int,
        recommendation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the final score and recommendation.
        
        Args:
            profile_id: Profile UUID
            final_score: New final score
            recommendation: New recommendation
            
        Returns:
            Updated score data
        """
        update_data = {"final_score": final_score}
        if recommendation:
            update_data["recommendation"] = recommendation
        return self.update_by_profile_id(profile_id, update_data)
    
    def mark_as_fake(self, profile_id: str | UUID) -> Dict[str, Any]:
        """
        Mark a profile's score as suspected fake.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Updated score data
        """
        return self.update_by_profile_id(profile_id, {"is_fake_suspected": True})
    
    # =========================================================================
    # Delete Operations
    # =========================================================================
    
    def delete_by_profile_id(self, profile_id: str | UUID) -> bool:
        """
        Delete score for a profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if deleted
        """
        response = (
            self._table()
            .delete()
            .eq("profile_id", str(profile_id))
            .execute()
        )
        return len(self._handle_response(response)) > 0
    
    # =========================================================================
    # Aggregation Queries
    # =========================================================================
    
    def get_score_stats_for_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get score statistics for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Dict with avg, min, max, count
        """
        scores = self.list_by_job(job_id, limit=1000)
        
        if not scores:
            return {
                "count": 0,
                "avg_score": None,
                "min_score": None,
                "max_score": None,
            }
        
        final_scores = [s["final_score"] for s in scores]
        
        return {
            "count": len(final_scores),
            "avg_score": round(sum(final_scores) / len(final_scores), 1),
            "min_score": min(final_scores),
            "max_score": max(final_scores),
        }
    
    def count_by_recommendation(self, job_id: str) -> Dict[str, int]:
        """
        Count scores by recommendation level for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Dict mapping recommendation to count
        """
        scores = self.list_by_job(job_id, limit=1000)
        
        counts = {
            "highly_recommended": 0,
            "recommended": 0,
            "consider": 0,
            "not_recommended": 0,
        }
        
        for score in scores:
            rec = score.get("recommendation")
            if rec and rec in counts:
                counts[rec] += 1
        
        return counts
