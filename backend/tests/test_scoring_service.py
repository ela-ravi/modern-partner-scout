"""
Tests for STORY-2.3.2: Implement Scoring Service

These tests validate that the ScoringService implements all required
scoring logic correctly, including weighted score calculation,
recommendation determination, and category assignment.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from app.services.scoring_service import ScoringService, get_scoring_service
from app.core.exceptions import BusinessError


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_score_repo():
    """Create a mock ScoreRepository."""
    return Mock()


@pytest.fixture
def default_weights():
    """Default scoring weights that sum to 1.0."""
    return {
        "visual_aesthetic_match": 0.15,
        "content_theme_alignment": 0.20,
        "engagement_rate_score": 0.25,
        "follower_quality": 0.15,
        "business_indicators": 0.15,
        "activity_recency": 0.10,
    }


@pytest.fixture
def default_thresholds():
    """Default scoring thresholds."""
    return {
        "min_recommendation_score": 50,
        "high_score": 80,
        "minimum_requirements": {
            "required_dimensions_above_40": [
                "engagement_rate_score",
                "content_theme_alignment",
            ]
        }
    }


@pytest.fixture
def scoring_service(mock_score_repo, default_weights, default_thresholds):
    """Create a ScoringService with mocked repository."""
    return ScoringService(
        score_repo=mock_score_repo,
        weights=default_weights,
        thresholds=default_thresholds,
    )


@pytest.fixture
def perfect_scores():
    """All dimension scores at 100."""
    return {
        "visual_aesthetic_match": 100,
        "content_theme_alignment": 100,
        "engagement_rate_score": 100,
        "follower_quality": 100,
        "business_indicators": 100,
        "activity_recency": 100,
    }


@pytest.fixture
def zero_scores():
    """All dimension scores at 0."""
    return {
        "visual_aesthetic_match": 0,
        "content_theme_alignment": 0,
        "engagement_rate_score": 0,
        "follower_quality": 0,
        "business_indicators": 0,
        "activity_recency": 0,
    }


@pytest.fixture
def mixed_scores():
    """Mixed dimension scores."""
    return {
        "visual_aesthetic_match": 80,
        "content_theme_alignment": 75,
        "engagement_rate_score": 90,
        "follower_quality": 70,
        "business_indicators": 65,
        "activity_recency": 85,
    }


# =============================================================================
# Test: Weight Validation
# =============================================================================

class TestWeightValidation:
    """Tests for weight validation."""
    
    def test_valid_weights_accepted(self, mock_score_repo, default_weights, default_thresholds):
        """Test that valid weights are accepted."""
        service = ScoringService(
            score_repo=mock_score_repo,
            weights=default_weights,
            thresholds=default_thresholds,
        )
        assert service is not None
        assert sum(service.weights.values()) == pytest.approx(1.0, abs=0.01)
    
    def test_weights_not_summing_to_one_raises_error(self, mock_score_repo, default_thresholds):
        """Test that weights not summing to 1.0 raise an error."""
        invalid_weights = {
            "visual_aesthetic_match": 0.30,
            "content_theme_alignment": 0.30,
            "engagement_rate_score": 0.30,
            "follower_quality": 0.30,
            "business_indicators": 0.30,
            "activity_recency": 0.30,
        }
        
        with pytest.raises(BusinessError) as exc_info:
            ScoringService(
                score_repo=mock_score_repo,
                weights=invalid_weights,
                thresholds=default_thresholds,
            )
        
        assert "must sum to 1.0" in str(exc_info.value.message)
    
    def test_weights_property_returns_copy(self, scoring_service):
        """Test that weights property returns a copy, not the original."""
        weights1 = scoring_service.weights
        weights2 = scoring_service.weights
        
        # Modifying one shouldn't affect the other
        weights1["visual_aesthetic_match"] = 999
        assert weights2["visual_aesthetic_match"] != 999


# =============================================================================
# Test: calculate_final_score()
# =============================================================================

class TestCalculateFinalScore:
    """Tests for the calculate_final_score method."""
    
    def test_perfect_scores_return_100(self, scoring_service):
        """Test that all 100s returns 100."""
        score = scoring_service.calculate_final_score(
            visual_aesthetic_match=100,
            content_theme_alignment=100,
            engagement_rate_score=100,
            follower_quality=100,
            business_indicators=100,
            activity_recency=100,
        )
        assert score == 100
    
    def test_zero_scores_return_0(self, scoring_service):
        """Test that all 0s returns 0."""
        score = scoring_service.calculate_final_score(
            visual_aesthetic_match=0,
            content_theme_alignment=0,
            engagement_rate_score=0,
            follower_quality=0,
            business_indicators=0,
            activity_recency=0,
        )
        assert score == 0
    
    def test_weighted_calculation_is_correct(self, scoring_service):
        """Test that weighted calculation is mathematically correct."""
        # Given these weights from default_weights:
        # visual: 0.15, content: 0.20, engagement: 0.25
        # follower: 0.15, business: 0.15, activity: 0.10
        
        # Calculate expected: 80*0.15 + 60*0.20 + 100*0.25 + 50*0.15 + 40*0.15 + 70*0.10
        # = 12 + 12 + 25 + 7.5 + 6 + 7 = 69.5 -> 70 (rounded)
        
        score = scoring_service.calculate_final_score(
            visual_aesthetic_match=80,
            content_theme_alignment=60,
            engagement_rate_score=100,
            follower_quality=50,
            business_indicators=40,
            activity_recency=70,
        )
        
        expected = round(80*0.15 + 60*0.20 + 100*0.25 + 50*0.15 + 40*0.15 + 70*0.10)
        assert score == expected
    
    def test_score_clamped_to_0_100(self, scoring_service):
        """Test that scores outside 0-100 are clamped."""
        # Using very high and negative values (though they shouldn't occur)
        score = scoring_service.calculate_final_score(
            visual_aesthetic_match=150,  # Over 100
            content_theme_alignment=100,
            engagement_rate_score=100,
            follower_quality=100,
            business_indicators=100,
            activity_recency=100,
        )
        assert 0 <= score <= 100
    
    def test_calculate_final_score_from_dict(self, scoring_service, mixed_scores):
        """Test calculation from dictionary."""
        score = scoring_service.calculate_final_score_from_dict(mixed_scores)
        
        # Verify manually
        expected = round(
            80*0.15 +   # visual
            75*0.20 +   # content
            90*0.25 +   # engagement
            70*0.15 +   # follower
            65*0.15 +   # business
            85*0.10     # activity
        )
        assert score == expected
    
    def test_missing_dimensions_default_to_zero(self, scoring_service):
        """Test that missing dimensions default to 0."""
        score = scoring_service.calculate_final_score_from_dict({
            "visual_aesthetic_match": 100,
            # Missing all other dimensions
        })
        
        # Only visual contributes: 100 * 0.15 = 15
        assert score == 15


# =============================================================================
# Test: get_recommendation()
# =============================================================================

class TestGetRecommendation:
    """Tests for the get_recommendation method."""
    
    def test_fake_profile_not_recommended(self, scoring_service):
        """Test that fake suspected profiles are not recommended."""
        recommendation = scoring_service.get_recommendation(
            final_score=95,
            is_fake_suspected=True,
        )
        assert recommendation == "not_recommended"
    
    def test_excellent_score_highly_recommended(self, scoring_service, perfect_scores):
        """Test that scores >= 90 with good dimensions are highly recommended."""
        recommendation = scoring_service.get_recommendation(
            final_score=92,
            dimensions=perfect_scores,
        )
        assert recommendation == "highly_recommended"
    
    def test_high_score_highly_recommended(self, scoring_service, mixed_scores):
        """Test that scores >= high threshold are highly recommended."""
        recommendation = scoring_service.get_recommendation(
            final_score=85,
            dimensions=mixed_scores,
        )
        assert recommendation == "highly_recommended"
    
    def test_moderate_score_recommended(self, scoring_service, mixed_scores):
        """Test that scores >= min threshold are recommended."""
        # Modify dimensions to meet requirements but lower final score
        dimensions = mixed_scores.copy()
        dimensions["engagement_rate_score"] = 45  # Above 40
        dimensions["content_theme_alignment"] = 45  # Above 40
        
        recommendation = scoring_service.get_recommendation(
            final_score=60,
            dimensions=dimensions,
        )
        assert recommendation == "recommended"
    
    def test_low_score_with_potential_consider(self, scoring_service):
        """Test that borderline scores get 'consider'."""
        recommendation = scoring_service.get_recommendation(
            final_score=40,
            dimensions=None,
        )
        assert recommendation == "consider"
    
    def test_very_low_score_not_recommended(self, scoring_service):
        """Test that very low scores are not recommended."""
        recommendation = scoring_service.get_recommendation(
            final_score=20,
            dimensions=None,
        )
        assert recommendation == "not_recommended"
    
    def test_dimensions_below_40_affect_recommendation(self, scoring_service):
        """Test that key dimensions below 40 can affect recommendation."""
        dimensions = {
            "visual_aesthetic_match": 80,
            "content_theme_alignment": 30,  # Below 40 - required dimension
            "engagement_rate_score": 30,    # Below 40 - required dimension
            "follower_quality": 80,
            "business_indicators": 80,
            "activity_recency": 80,
        }
        
        recommendation = scoring_service.get_recommendation(
            final_score=65,
            dimensions=dimensions,
        )
        # Should be downgraded because required dimensions are below 40
        assert recommendation == "consider"
    
    @pytest.mark.parametrize("score,expected", [
        (95, "highly_recommended"),
        (85, "highly_recommended"),
        (70, "recommended"),
        (55, "recommended"),
        (40, "consider"),
        (30, "not_recommended"),
        (10, "not_recommended"),
    ])
    def test_recommendation_thresholds(self, scoring_service, mixed_scores, score, expected):
        """Test various score thresholds produce correct recommendations."""
        # Use mixed_scores which meet dimension requirements
        recommendation = scoring_service.get_recommendation(
            final_score=score,
            dimensions=mixed_scores if score >= 50 else None,
        )
        assert recommendation == expected


# =============================================================================
# Test: get_score_category()
# =============================================================================

class TestGetScoreCategory:
    """Tests for the get_score_category method."""
    
    @pytest.mark.parametrize("score,expected_name", [
        (100, "excellent"),
        (95, "excellent"),
        (90, "excellent"),
        (89, "good"),
        (80, "good"),
        (75, "good"),
        (74, "moderate"),
        (60, "moderate"),
        (50, "moderate"),
        (49, "low"),
        (25, "low"),
        (0, "low"),
    ])
    def test_category_assignment(self, scoring_service, score, expected_name):
        """Test correct category assignment for various scores."""
        category = scoring_service.get_score_category(score)
        assert category["name"] == expected_name
    
    def test_category_includes_all_fields(self, scoring_service):
        """Test that category includes all required fields."""
        category = scoring_service.get_score_category(85)
        
        assert "name" in category
        assert "label" in category
        assert "color" in category
        assert "min" in category
        assert "max" in category
    
    def test_excellent_category_properties(self, scoring_service):
        """Test excellent category has correct properties."""
        category = scoring_service.get_score_category(95)
        
        assert category["name"] == "excellent"
        assert category["label"] == "Excellent Match"
        assert category["color"] == "#22c55e"  # Green
        assert category["min"] == 90
        assert category["max"] == 100


# =============================================================================
# Test: process_score()
# =============================================================================

class TestProcessScore:
    """Tests for the process_score method."""
    
    def test_process_score_returns_complete_result(self, scoring_service, mixed_scores):
        """Test that process_score returns all expected fields."""
        result = scoring_service.process_score(
            dimensions=mixed_scores,
            is_fake_suspected=False,
        )
        
        assert "final_score" in result
        assert "recommendation" in result
        assert "category" in result
        assert "is_fake_suspected" in result
        assert "dimensions" in result
    
    def test_process_score_calculates_correctly(self, scoring_service, mixed_scores):
        """Test that process_score calculates all values correctly."""
        result = scoring_service.process_score(
            dimensions=mixed_scores,
            is_fake_suspected=False,
        )
        
        # Verify final score calculation
        expected_score = scoring_service.calculate_final_score_from_dict(mixed_scores)
        assert result["final_score"] == expected_score
        
        # Verify recommendation
        expected_recommendation = scoring_service.get_recommendation(
            expected_score,
            mixed_scores,
            False,
        )
        assert result["recommendation"] == expected_recommendation
    
    def test_process_score_with_fake_suspected(self, scoring_service, perfect_scores):
        """Test process_score with fake suspected flag."""
        result = scoring_service.process_score(
            dimensions=perfect_scores,
            is_fake_suspected=True,
        )
        
        assert result["is_fake_suspected"] is True
        assert result["recommendation"] == "not_recommended"


# =============================================================================
# Test: score_profile()
# =============================================================================

class TestScoreProfile:
    """Tests for the score_profile method."""
    
    def test_score_profile_creates_record(self, scoring_service, mock_score_repo, mixed_scores):
        """Test that score_profile creates a database record."""
        profile_id = str(uuid4())
        
        mock_score_repo.create_full_score.return_value = {
            "id": str(uuid4()),
            "profile_id": profile_id,
            "final_score": 78,
            "recommendation": "recommended",
        }
        
        result = scoring_service.score_profile(
            profile_id=profile_id,
            dimensions=mixed_scores,
            reasoning={"test": "reasoning"},
        )
        
        mock_score_repo.create_full_score.assert_called_once()
        assert "category" in result
    
    def test_score_profile_passes_correct_arguments(self, scoring_service, mock_score_repo, mixed_scores):
        """Test that score_profile passes correct arguments to repository."""
        profile_id = str(uuid4())
        reasoning = {"visual": "looks good"}
        
        mock_score_repo.create_full_score.return_value = {"id": str(uuid4())}
        
        scoring_service.score_profile(
            profile_id=profile_id,
            dimensions=mixed_scores,
            reasoning=reasoning,
            is_fake_suspected=True,
        )
        
        call_args = mock_score_repo.create_full_score.call_args
        assert call_args.kwargs["profile_id"] == profile_id
        assert call_args.kwargs["dimensions"] == mixed_scores
        assert call_args.kwargs["reasoning"] == reasoning
        assert call_args.kwargs["is_fake_suspected"] is True


# =============================================================================
# Test: Utility Methods
# =============================================================================

class TestUtilityMethods:
    """Tests for utility methods."""
    
    def test_is_high_quality_match(self, scoring_service):
        """Test is_high_quality_match method."""
        assert scoring_service.is_high_quality_match(85) is True
        assert scoring_service.is_high_quality_match(80) is True
        assert scoring_service.is_high_quality_match(79) is False
        assert scoring_service.is_high_quality_match(50) is False
    
    def test_is_recommendable(self, scoring_service):
        """Test is_recommendable method."""
        assert scoring_service.is_recommendable(75) is True
        assert scoring_service.is_recommendable(50) is True
        assert scoring_service.is_recommendable(49) is False
        assert scoring_service.is_recommendable(95, is_fake_suspected=True) is False
    
    def test_min_recommendation_score_property(self, scoring_service):
        """Test min_recommendation_score property."""
        assert scoring_service.min_recommendation_score == 50
    
    def test_high_score_threshold_property(self, scoring_service):
        """Test high_score_threshold property."""
        assert scoring_service.high_score_threshold == 80


# =============================================================================
# Test: Dimension Analytics
# =============================================================================

class TestDimensionAnalytics:
    """Tests for dimension analytics methods."""
    
    def test_get_dimension_weights_display(self, scoring_service):
        """Test get_dimension_weights_display method."""
        with patch("app.services.scoring_service.get_scoring_config") as mock_config:
            mock_config.return_value = {
                "dimensions": {
                    "visual_aesthetic_match": {
                        "name": "Visual Aesthetic Match",
                        "description": "Test description",
                    }
                }
            }
            
            display = scoring_service.get_dimension_weights_display()
            
            assert len(display) == 6  # All dimensions
            assert all("dimension" in d for d in display)
            assert all("weight" in d for d in display)
            assert all("weight_percent" in d for d in display)
    
    def test_calculate_dimension_contribution(self, scoring_service, mixed_scores):
        """Test calculate_dimension_contribution method."""
        contributions = scoring_service.calculate_dimension_contribution(mixed_scores)
        
        assert len(contributions) == 6
        assert all("dimension" in c for c in contributions)
        assert all("score" in c for c in contributions)
        assert all("weight" in c for c in contributions)
        assert all("contribution" in c for c in contributions)
        
        # Verify sorted by contribution descending
        for i in range(len(contributions) - 1):
            assert contributions[i]["contribution"] >= contributions[i+1]["contribution"]


# =============================================================================
# Test: get_scoring_service Factory
# =============================================================================

class TestGetScoringServiceFactory:
    """Tests for the get_scoring_service factory function."""
    
    def test_get_scoring_service_returns_instance(self):
        """Test factory returns ScoringService instance."""
        service = get_scoring_service()
        
        assert isinstance(service, ScoringService)
        assert service.score_repo is not None


# =============================================================================
# Test: Module Exports
# =============================================================================

class TestModuleExports:
    """Test module exports correctly."""
    
    def test_import_from_services(self):
        """Test importing ScoringService from services module."""
        from app.services import ScoringService, get_scoring_service
        
        assert ScoringService is not None
        assert get_scoring_service is not None


# =============================================================================
# Test: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_boundary_scores(self, scoring_service):
        """Test boundary score values."""
        # Test at exact boundaries
        assert scoring_service.get_score_category(90)["name"] == "excellent"
        assert scoring_service.get_score_category(89)["name"] == "good"
        assert scoring_service.get_score_category(75)["name"] == "good"
        assert scoring_service.get_score_category(74)["name"] == "moderate"
        assert scoring_service.get_score_category(50)["name"] == "moderate"
        assert scoring_service.get_score_category(49)["name"] == "low"
    
    def test_empty_dimensions_dict(self, scoring_service):
        """Test calculation with empty dimensions dict."""
        score = scoring_service.calculate_final_score_from_dict({})
        assert score == 0
    
    def test_extra_dimensions_ignored(self, scoring_service):
        """Test that extra dimension keys are ignored."""
        dimensions = {
            "visual_aesthetic_match": 100,
            "content_theme_alignment": 100,
            "engagement_rate_score": 100,
            "follower_quality": 100,
            "business_indicators": 100,
            "activity_recency": 100,
            "unknown_dimension": 100,  # Should be ignored
        }
        score = scoring_service.calculate_final_score_from_dict(dimensions)
        assert score == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
