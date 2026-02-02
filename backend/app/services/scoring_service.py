"""
PartnerScout AI - Scoring Service

Service layer for calculating profile scores and recommendations.
Implements weighted score calculation and recommendation logic based on thresholds.

STORY-2.3.2: Implement Scoring & Email Services
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.core.settings import (
    get_scoring_config,
    get_scoring_weights,
    get_scoring_thresholds,
)
from app.core.exceptions import BusinessError
from app.repositories import ScoreRepository


logger = logging.getLogger(__name__)


class ScoringService:
    """
    Service class for calculating and managing profile scores.
    
    Implements:
    - Weighted score calculation across 6 dimensions
    - Recommendation logic based on configurable thresholds
    - Score categorization (excellent, good, moderate, low)
    """
    
    # Scoring dimension names
    DIMENSIONS = [
        "visual_aesthetic_match",
        "content_theme_alignment",
        "engagement_rate_score",
        "follower_quality",
        "business_indicators",
        "activity_recency",
    ]
    
    # Recommendation levels
    HIGHLY_RECOMMENDED = "highly_recommended"
    RECOMMENDED = "recommended"
    CONSIDER = "consider"
    NOT_RECOMMENDED = "not_recommended"
    
    def __init__(
        self,
        score_repo: Optional[ScoreRepository] = None,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the ScoringService.
        
        Args:
            score_repo: Optional ScoreRepository instance
            weights: Optional custom weights (for testing)
            thresholds: Optional custom thresholds (for testing)
        """
        self.score_repo = score_repo or ScoreRepository()
        
        # Load from YAML config or use provided values
        self._weights = weights or get_scoring_weights()
        self._thresholds = thresholds or get_scoring_thresholds()
        
        # Validate weights sum to 1.0
        self._validate_weights()
    
    # =========================================================================
    # Weight and Threshold Properties
    # =========================================================================
    
    @property
    def weights(self) -> Dict[str, float]:
        """Get the scoring dimension weights."""
        return self._weights.copy()
    
    @property
    def thresholds(self) -> Dict[str, Any]:
        """Get the scoring thresholds."""
        return self._thresholds.copy()
    
    @property
    def min_recommendation_score(self) -> int:
        """Get the minimum score for recommendation."""
        return self._thresholds.get("min_recommendation_score", 50)
    
    @property
    def high_score_threshold(self) -> int:
        """Get the high score threshold."""
        return self._thresholds.get("high_score", 80)
    
    def _validate_weights(self) -> None:
        """
        Validate that weights sum to approximately 1.0.
        
        Raises:
            BusinessError: If weights don't sum to 1.0
        """
        total = sum(self._weights.values())
        if not (0.99 <= total <= 1.01):
            logger.warning(f"Scoring weights sum to {total}, expected 1.0")
            raise BusinessError(
                message=f"Scoring weights must sum to 1.0, but got {total}",
                details={"weights": self._weights, "total": total}
            )
    
    # =========================================================================
    # Score Calculation
    # =========================================================================
    
    def calculate_final_score(
        self,
        visual_aesthetic_match: int = 0,
        content_theme_alignment: int = 0,
        engagement_rate_score: int = 0,
        follower_quality: int = 0,
        business_indicators: int = 0,
        activity_recency: int = 0,
    ) -> int:
        """
        Calculate the weighted final score from dimension scores.
        
        Each dimension should be scored 0-100. The final score is computed
        as a weighted average using the configured weights.
        
        Args:
            visual_aesthetic_match: Visual aesthetic match score (0-100)
            content_theme_alignment: Content theme alignment score (0-100)
            engagement_rate_score: Engagement rate score (0-100)
            follower_quality: Follower quality score (0-100)
            business_indicators: Business indicators score (0-100)
            activity_recency: Activity recency score (0-100)
            
        Returns:
            Weighted final score (0-100)
        """
        dimensions = {
            "visual_aesthetic_match": visual_aesthetic_match,
            "content_theme_alignment": content_theme_alignment,
            "engagement_rate_score": engagement_rate_score,
            "follower_quality": follower_quality,
            "business_indicators": business_indicators,
            "activity_recency": activity_recency,
        }
        
        return self.calculate_final_score_from_dict(dimensions)
    
    def calculate_final_score_from_dict(
        self,
        dimensions: Dict[str, int],
    ) -> int:
        """
        Calculate the weighted final score from a dictionary of dimension scores.
        
        Args:
            dimensions: Dict mapping dimension names to scores (0-100)
            
        Returns:
            Weighted final score (0-100)
        """
        weighted_sum = 0.0
        
        for dimension, weight in self._weights.items():
            score = dimensions.get(dimension, 0)
            # Clamp score to 0-100
            score = max(0, min(100, score))
            weighted_sum += score * weight
        
        # Round to nearest integer
        final_score = round(weighted_sum)
        return max(0, min(100, final_score))
    
    # =========================================================================
    # Recommendation Logic
    # =========================================================================
    
    def get_recommendation(
        self,
        final_score: int,
        dimensions: Optional[Dict[str, int]] = None,
        is_fake_suspected: bool = False,
    ) -> str:
        """
        Determine the recommendation level based on score and dimensions.
        
        Recommendation levels:
        - highly_recommended: Score >= high threshold, key dimensions strong
        - recommended: Score >= min threshold, meets minimum requirements
        - consider: Score below threshold but has some potential
        - not_recommended: Score too low or fake suspected
        
        Args:
            final_score: The calculated final score
            dimensions: Optional dict of dimension scores for advanced logic
            is_fake_suspected: Whether the profile is suspected to be fake
            
        Returns:
            Recommendation level string
        """
        # Fake profiles are never recommended
        if is_fake_suspected:
            return self.NOT_RECOMMENDED
        
        # Check high score threshold
        high_threshold = self._thresholds.get("high_score", 80)
        min_threshold = self._thresholds.get("min_recommendation_score", 50)
        
        # Get minimum requirements from config
        min_requirements = self._thresholds.get("minimum_requirements", {})
        required_above_40 = min_requirements.get("required_dimensions_above_40", [])
        
        # Check if dimensions meet minimum requirements
        dimensions_meet_requirements = True
        if dimensions and required_above_40:
            for dim in required_above_40:
                if dimensions.get(dim, 0) < 40:
                    dimensions_meet_requirements = False
                    break
        
        # Determine recommendation
        if final_score >= 90 and dimensions_meet_requirements:
            return self.HIGHLY_RECOMMENDED
        elif final_score >= high_threshold and dimensions_meet_requirements:
            return self.HIGHLY_RECOMMENDED
        elif final_score >= min_threshold and dimensions_meet_requirements:
            return self.RECOMMENDED
        elif final_score >= 35:
            return self.CONSIDER
        else:
            return self.NOT_RECOMMENDED
    
    def get_score_category(self, final_score: int) -> Dict[str, Any]:
        """
        Get the category for a given score.
        
        Categories from scoring.yaml:
        - excellent (90-100): "Excellent Match"
        - good (75-89): "Good Match"
        - moderate (50-74): "Moderate Match"
        - low (0-49): "Low Match"
        
        Args:
            final_score: The score to categorize
            
        Returns:
            Dict with category info (label, color, name)
        """
        if final_score >= 90:
            return {
                "name": "excellent",
                "label": "Excellent Match",
                "color": "#22c55e",
                "min": 90,
                "max": 100,
            }
        elif final_score >= 75:
            return {
                "name": "good",
                "label": "Good Match",
                "color": "#3b82f6",
                "min": 75,
                "max": 89,
            }
        elif final_score >= 50:
            return {
                "name": "moderate",
                "label": "Moderate Match",
                "color": "#f59e0b",
                "min": 50,
                "max": 74,
            }
        else:
            return {
                "name": "low",
                "label": "Low Match",
                "color": "#ef4444",
                "min": 0,
                "max": 49,
            }
    
    # =========================================================================
    # Full Score Processing
    # =========================================================================
    
    def process_score(
        self,
        dimensions: Dict[str, int],
        is_fake_suspected: bool = False,
    ) -> Dict[str, Any]:
        """
        Process dimension scores into a complete scoring result.
        
        This combines:
        - Final score calculation
        - Recommendation determination
        - Category assignment
        
        Args:
            dimensions: Dict mapping dimension names to scores
            is_fake_suspected: Whether the profile is suspected fake
            
        Returns:
            Complete scoring result dict
        """
        # Calculate final score
        final_score = self.calculate_final_score_from_dict(dimensions)
        
        # Get recommendation
        recommendation = self.get_recommendation(
            final_score=final_score,
            dimensions=dimensions,
            is_fake_suspected=is_fake_suspected,
        )
        
        # Get category
        category = self.get_score_category(final_score)
        
        return {
            "final_score": final_score,
            "recommendation": recommendation,
            "category": category,
            "is_fake_suspected": is_fake_suspected,
            "dimensions": dimensions,
        }
    
    def score_profile(
        self,
        profile_id: str,
        dimensions: Dict[str, int],
        reasoning: Optional[Dict[str, Any]] = None,
        is_fake_suspected: bool = False,
    ) -> Dict[str, Any]:
        """
        Score a profile and save to database.
        
        Args:
            profile_id: Profile UUID
            dimensions: Dict of dimension scores
            reasoning: AI reasoning for each dimension
            is_fake_suspected: Whether profile is suspected fake
            
        Returns:
            Created score record
        """
        # Process the score
        result = self.process_score(
            dimensions=dimensions,
            is_fake_suspected=is_fake_suspected,
        )
        
        # Save to database
        score_record = self.score_repo.create_full_score(
            profile_id=profile_id,
            dimensions=dimensions,
            final_score=result["final_score"],
            recommendation=result["recommendation"],
            reasoning=reasoning or {},
            is_fake_suspected=is_fake_suspected,
        )
        
        logger.info(
            f"Scored profile {profile_id}: {result['final_score']} "
            f"({result['recommendation']})"
        )
        
        return {
            **score_record,
            "category": result["category"],
        }
    
    # =========================================================================
    # Scoring Analytics
    # =========================================================================
    
    def get_dimension_weights_display(self) -> List[Dict[str, Any]]:
        """
        Get weights formatted for display.
        
        Returns:
            List of dimension weight info for UI display
        """
        config = get_scoring_config()
        dimensions_config = config.get("dimensions", {})
        
        result = []
        for dim_name, weight in self._weights.items():
            dim_info = dimensions_config.get(dim_name, {})
            result.append({
                "dimension": dim_name,
                "name": dim_info.get("name", dim_name.replace("_", " ").title()),
                "description": dim_info.get("description", ""),
                "weight": weight,
                "weight_percent": round(weight * 100),
            })
        
        # Sort by weight descending
        result.sort(key=lambda x: x["weight"], reverse=True)
        return result
    
    def calculate_dimension_contribution(
        self,
        dimensions: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """
        Calculate how much each dimension contributes to the final score.
        
        Args:
            dimensions: Dict of dimension scores
            
        Returns:
            List of dimension contribution breakdowns
        """
        final_score = self.calculate_final_score_from_dict(dimensions)
        
        result = []
        for dim_name, weight in self._weights.items():
            score = dimensions.get(dim_name, 0)
            contribution = round(score * weight, 1)
            result.append({
                "dimension": dim_name,
                "score": score,
                "weight": weight,
                "contribution": contribution,
                "contribution_percent": round((contribution / final_score * 100) if final_score > 0 else 0, 1),
            })
        
        # Sort by contribution descending
        result.sort(key=lambda x: x["contribution"], reverse=True)
        return result
    
    # =========================================================================
    # Score Statistics
    # =========================================================================
    
    def get_score_statistics(
        self,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        Get scoring statistics for a job.
        
        Args:
            job_id: Job UUID
            
        Returns:
            Statistics including counts by recommendation level
        """
        stats = self.score_repo.get_score_stats_for_job(job_id)
        recommendation_counts = self.score_repo.count_by_recommendation(job_id)
        
        return {
            **stats,
            "recommendation_counts": recommendation_counts,
        }
    
    def is_high_quality_match(self, final_score: int) -> bool:
        """
        Check if a score qualifies as high quality.
        
        Args:
            final_score: The score to check
            
        Returns:
            True if score >= high threshold
        """
        return final_score >= self.high_score_threshold
    
    def is_recommendable(
        self,
        final_score: int,
        is_fake_suspected: bool = False,
    ) -> bool:
        """
        Check if a profile is recommendable based on score.
        
        Args:
            final_score: The score to check
            is_fake_suspected: Whether profile is suspected fake
            
        Returns:
            True if profile meets recommendation requirements
        """
        if is_fake_suspected:
            return False
        return final_score >= self.min_recommendation_score


# =============================================================================
# Factory Function
# =============================================================================

def get_scoring_service() -> ScoringService:
    """
    Get a ScoringService instance.
    
    This is the recommended way to get a ScoringService instance,
    as it can be used as a FastAPI dependency.
    
    Returns:
        ScoringService instance
    """
    return ScoringService()
