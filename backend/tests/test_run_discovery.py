"""
Tests for STORY-4.2.1: Implement Python Fallback Script

Unit and integration tests for the Python fallback orchestrator script.
Tests verify that the script correctly calls API endpoints and handles errors.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

import httpx

# Import the script functions
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.run_discovery import (
    update_job_status,
    update_profile_status,
    call_brand_analyzer,
    call_discovery_agent,
    call_scorer_agent,
    run_discovery,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def sample_profile_id():
    """Generate a sample profile ID."""
    return str(uuid4())


@pytest.fixture
def mock_brand_response():
    """Mock brand analyzer response."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly", "#slowfashion"],
        "keywords": ["sustainable", "ethical", "eco-friendly"],
        "visual_themes": ["minimalist", "earth tones"],
        "content_pillars": ["sustainability", "fashion"],
        "target_audience_description": "Environmentally conscious millennials",
        "embedding_vector": [0.01] * 1536,
        "profiles_analyzed": 3,
        "posts_analyzed": 45,
        "analysis_duration_seconds": 12.5
    }


@pytest.fixture
def mock_brand_response_nested():
    """Mock brand analyzer response with nested brand_dna."""
    return {
        "brand_dna": {
            "hashtags": ["#sustainablefashion", "#ecofriendly"],
            "keywords": ["sustainable", "ethical"],
            "embedding_vector": [0.01] * 1536
        }
    }


@pytest.fixture
def mock_discovery_response(sample_job_id):
    """Mock discovery agent response."""
    return {
        "profiles": [
            {
                "id": str(uuid4()),
                "username": "test_profile_1",
                "full_name": "Test Profile 1",
                "followers_count": 50000,
                "status": "new"
            },
            {
                "id": str(uuid4()),
                "username": "test_profile_2",
                "full_name": "Test Profile 2",
                "followers_count": 75000,
                "status": "new"
            }
        ],
        "total_discovered": 2,
        "deduplicated": 0,
        "filtered_out": 5,
        "discovery_duration_seconds": 45.2
    }


@pytest.fixture
def mock_scorer_response():
    """Mock scorer agent response."""
    return {
        "profile_id": str(uuid4()),
        "job_id": str(uuid4()),
        "visual_aesthetic_match": 75,
        "content_theme_alignment": 82,
        "engagement_rate_score": 88,
        "follower_quality": 70,
        "business_indicators": 85,
        "activity_recency": 90,
        "final_score": 82,
        "score": 82,  # Some responses use "score" instead of "final_score"
        "recommendation": "highly_recommended",
        "is_fake_suspected": False,
        "contact": {
            "email": "contact@example.com",
            "source": "business_email"
        },
        "scoring_duration_seconds": 3.5
    }


# =============================================================================
# Unit Tests: Status Update Functions
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_job_status_success(sample_job_id):
    """Test successful job status update."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": sample_job_id,
        "status": "analyzing",
        "updated_at": "2024-01-15T10:00:00Z"
    }
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(
            return_value=mock_response
        )
        
        result = await update_job_status(sample_job_id, "analyzing")
        
        assert result["id"] == sample_job_id
        assert result["status"] == "analyzing"
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_job_status_with_error_message(sample_job_id):
    """Test job status update with error message."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": sample_job_id,
        "status": "failed",
        "error_message": "Test error",
        "updated_at": "2024-01-15T10:00:00Z"
    }
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(
            return_value=mock_response
        )
        
        result = await update_job_status(
            sample_job_id,
            "failed",
            error_message="Test error"
        )
        
        assert result["status"] == "failed"
        assert result["error_message"] == "Test error"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_job_status_http_error(sample_job_id):
    """Test job status update with HTTP error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Job not found"
    
    error = httpx.HTTPStatusError(
        "Not Found",
        request=Mock(),
        response=mock_response
    )
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(
            side_effect=error
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await update_job_status(sample_job_id, "analyzing")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_profile_status_success(sample_profile_id):
    """Test successful profile status update."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "id": sample_profile_id,
        "status": "processing",
        "updated_at": "2024-01-15T10:00:00Z"
    }
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(
            return_value=mock_response
        )
        
        result = await update_profile_status(sample_profile_id, "processing")
        
        assert result["id"] == sample_profile_id
        assert result["status"] == "processing"


# =============================================================================
# Unit Tests: Agent Call Functions
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_brand_analyzer_success(sample_job_id, mock_brand_response):
    """Test successful brand analyzer call."""
    mock_response = Mock()
    mock_response.json.return_value = mock_brand_response
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await call_brand_analyzer(sample_job_id)
        
        assert "hashtags" in result
        assert len(result["hashtags"]) == 3


@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_brand_analyzer_nested_response(
    sample_job_id,
    mock_brand_response_nested
):
    """Test brand analyzer call with nested brand_dna response."""
    mock_response = Mock()
    mock_response.json.return_value = mock_brand_response_nested
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await call_brand_analyzer(sample_job_id)
        
        assert "brand_dna" in result
        assert "hashtags" in result["brand_dna"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_discovery_agent_success(
    sample_job_id,
    mock_discovery_response
):
    """Test successful discovery agent call."""
    mock_response = Mock()
    mock_response.json.return_value = mock_discovery_response
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await call_discovery_agent(
            job_id=sample_job_id,
            hashtags=["#test"],
            keywords=["test"],
            limit=50
        )
        
        assert "profiles" in result
        assert len(result["profiles"]) == 2
        assert result["total_discovered"] == 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_scorer_agent_success(
    sample_profile_id,
    sample_job_id,
    mock_scorer_response
):
    """Test successful scorer agent call."""
    mock_response = Mock()
    mock_response.json.return_value = mock_scorer_response
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await call_scorer_agent(sample_profile_id, sample_job_id)
        
        assert "score" in result or "final_score" in result
        assert result.get("score") == 82 or result.get("final_score") == 82


# =============================================================================
# Integration Tests: Full Workflow
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_success(
    sample_job_id,
    mock_brand_response,
    mock_discovery_response,
    mock_scorer_response
):
    """Test successful full discovery workflow."""
    # Setup mocks
    mock_job_status_responses = [
        Mock(json=Mock(return_value={"id": sample_job_id, "status": "analyzing"})),
        Mock(json=Mock(return_value={"id": sample_job_id, "status": "discovering"})),
        Mock(json=Mock(return_value={"id": sample_job_id, "status": "scoring"})),
        Mock(json=Mock(return_value={"id": sample_job_id, "status": "completed"})),
    ]
    for resp in mock_job_status_responses:
        resp.raise_for_status = Mock()
    
    # Flatten profile responses
    profile_responses = []
    for profile in mock_discovery_response["profiles"]:
        profile_responses.append(
            Mock(json=Mock(return_value={"id": profile["id"], "status": "processing"}))
        )
        profile_responses.append(
            Mock(json=Mock(return_value={"id": profile["id"], "status": "done"}))
        )
    for resp in profile_responses:
        resp.raise_for_status = Mock()
    
    mock_brand_response_obj = Mock(json=Mock(return_value=mock_brand_response))
    mock_brand_response_obj.raise_for_status = Mock()
    
    mock_discovery_response_obj = Mock(json=Mock(return_value=mock_discovery_response))
    mock_discovery_response_obj.raise_for_status = Mock()
    
    mock_scorer_response_objs = [
        Mock(json=Mock(return_value={**mock_scorer_response, "profile_id": p["id"]}))
        for p in mock_discovery_response["profiles"]
    ]
    for resp in mock_scorer_response_objs:
        resp.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.update_profile_status") as mock_update_profile, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand, \
         patch("scripts.run_discovery.call_discovery_agent") as mock_discover, \
         patch("scripts.run_discovery.call_scorer_agent") as mock_scorer:
        
        # Configure mocks
        mock_update_job.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_brand.return_value = mock_brand_response
        mock_discover.return_value = mock_discovery_response
        mock_scorer.return_value = mock_scorer_response
        
        # Run discovery
        await run_discovery(sample_job_id)
        
        # Verify calls
        assert mock_update_job.call_count == 4  # analyzing, discovering, scoring, completed
        assert mock_brand.call_count == 1
        assert mock_discover.call_count == 1
        assert mock_scorer.call_count == len(mock_discovery_response["profiles"])
        assert mock_update_profile.call_count == len(mock_discovery_response["profiles"]) * 2  # processing + done
        
        # Verify status transitions
        status_calls = [call[0][1] for call in mock_update_job.call_args_list]
        assert "analyzing" in status_calls
        assert "discovering" in status_calls
        assert "scoring" in status_calls
        assert "completed" in status_calls


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_no_profiles(
    sample_job_id,
    mock_brand_response
):
    """Test discovery workflow when no profiles are discovered."""
    mock_discovery_response_empty = {
        "profiles": [],
        "total_discovered": 0,
        "deduplicated": 0
    }
    
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand, \
         patch("scripts.run_discovery.call_discovery_agent") as mock_discover:
        
        mock_update_job.return_value = AsyncMock()
        mock_brand.return_value = mock_brand_response
        mock_discover.return_value = mock_discovery_response_empty
        
        await run_discovery(sample_job_id)
        
        # Should complete without scoring phase
        assert mock_update_job.call_count == 3  # analyzing, discovering, completed
        status_calls = [call[0][1] for call in mock_update_job.call_args_list]
        assert "completed" in status_calls
        assert "scoring" not in status_calls


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_brand_analyzer_error(sample_job_id):
    """Test discovery workflow when brand analyzer fails."""
    error = httpx.HTTPStatusError(
        "Internal Server Error",
        request=Mock(),
        response=Mock(status_code=500, text="Brand analysis failed")
    )
    
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand:
        
        mock_update_job.return_value = AsyncMock()
        mock_brand.side_effect = error
        
        with pytest.raises(httpx.HTTPStatusError):
            await run_discovery(sample_job_id)
        
        # Should update status to failed
        status_calls = [call[0][1] for call in mock_update_job.call_args_list]
        assert "failed" in status_calls


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_scorer_error(
    sample_job_id,
    mock_brand_response,
    mock_discovery_response
):
    """Test discovery workflow when scorer fails for a profile."""
    profile_id = mock_discovery_response["profiles"][0]["id"]
    scorer_error = httpx.HTTPStatusError(
        "Internal Server Error",
        request=Mock(),
        response=Mock(status_code=500, text="Scoring failed")
    )
    
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.update_profile_status") as mock_update_profile, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand, \
         patch("scripts.run_discovery.call_discovery_agent") as mock_discover, \
         patch("scripts.run_discovery.call_scorer_agent") as mock_scorer:
        
        mock_update_job.return_value = AsyncMock()
        mock_update_profile.return_value = AsyncMock()
        mock_brand.return_value = mock_brand_response
        mock_discover.return_value = mock_discovery_response
        mock_scorer.side_effect = scorer_error
        
        await run_discovery(sample_job_id)
        
        # Should mark profile as skipped and continue
        profile_status_calls = [call[0][1] for call in mock_update_profile.call_args_list]
        assert "skipped" in profile_status_calls
        
        # Should still complete the job
        job_status_calls = [call[0][1] for call in mock_update_job.call_args_list]
        assert "completed" in job_status_calls


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_profile_missing_id(
    sample_job_id,
    mock_brand_response
):
    """Test discovery workflow when profile is missing ID."""
    mock_discovery_response_invalid = {
        "profiles": [
            {
                "username": "test_profile",
                "full_name": "Test Profile",
                # Missing "id" field
            }
        ],
        "total_discovered": 1
    }
    
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand, \
         patch("scripts.run_discovery.call_discovery_agent") as mock_discover:
        
        mock_update_job.return_value = AsyncMock()
        mock_brand.return_value = mock_brand_response
        mock_discover.return_value = mock_discovery_response_invalid
        
        await run_discovery(sample_job_id)
        
        # Should complete without errors (skips invalid profile)
        job_status_calls = [call[0][1] for call in mock_update_job.call_args_list]
        assert "completed" in job_status_calls


@pytest.mark.asyncio
@pytest.mark.integration
async def test_run_discovery_nested_brand_dna(
    sample_job_id,
    mock_brand_response_nested,
    mock_discovery_response
):
    """Test discovery workflow with nested brand_dna response."""
    with patch("scripts.run_discovery.update_job_status") as mock_update_job, \
         patch("scripts.run_discovery.call_brand_analyzer") as mock_brand, \
         patch("scripts.run_discovery.call_discovery_agent") as mock_discover:
        
        mock_update_job.return_value = AsyncMock()
        mock_brand.return_value = mock_brand_response_nested
        mock_discover.return_value = mock_discovery_response
        
        await run_discovery(sample_job_id)
        
        # Should extract hashtags from nested brand_dna
        assert mock_discover.called
        call_args = mock_discover.call_args
        assert "hashtags" in call_args.kwargs
        assert len(call_args.kwargs["hashtags"]) == 2


# =============================================================================
# Edge Case Tests
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_call_scorer_agent_final_score_field(
    sample_profile_id,
    sample_job_id
):
    """Test scorer agent response with final_score field instead of score."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "final_score": 85,
        "recommendation": "highly_recommended"
    }
    mock_response.raise_for_status = Mock()
    
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )
        
        result = await call_scorer_agent(sample_profile_id, sample_job_id)
        
        assert result.get("final_score") == 85


@pytest.mark.asyncio
@pytest.mark.unit
async def test_update_job_status_timeout(sample_job_id):
    """Test job status update with timeout."""
    with patch("scripts.run_discovery.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.patch = AsyncMock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        with pytest.raises(httpx.TimeoutException):
            await update_job_status(sample_job_id, "analyzing")
