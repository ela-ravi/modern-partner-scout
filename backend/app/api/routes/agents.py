"""
PartnerScout AI - Agent API Routes (STORY-3.3.6)

API routes for AI agent operations including brand analysis, discovery, and scoring.
These endpoints are called by the internal orchestration pipeline.

Subtasks completed:
- SUB-3.3.6.1.1: Create app/api/routes/agents.py
- SUB-3.3.6.1.2: Implement POST /api/agent/analyze-brand
- SUB-3.3.6.1.3: Implement POST /api/agent/discover (STORY-3.3.3)
- SUB-3.3.6.1.4: Implement POST /api/agent/score (STORY-3.3.4)
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.agents.brand_analyzer import BrandAnalyzerAgent, get_brand_analyzer_agent
from app.agents.discovery import DiscoveryAgent, get_discovery_agent
from app.agents.scorer import ScorerAgent, get_scorer_agent
from app.core.constants import HttpStatus
from app.core.exceptions import AgentError, JobNotFoundError, ProfileNotFoundError
from app.guards.auth import get_service_context, ServiceContext
from app.models.agent import (
    BrandAnalyzerRequest,
    BrandAnalyzerResponse,
    DiscoveryRequest,
    DiscoveryResponse,
    ScorerRequest,
    ScorerResponse,
)


# =============================================================================
# Router Configuration
# =============================================================================

router = APIRouter(prefix="/agent", tags=["Agents"])

logger = logging.getLogger(__name__)


# =============================================================================
# Brand Analyzer Endpoint (SUB-3.3.6.1.2)
# =============================================================================

@router.post(
    "/analyze-brand",
    response_model=BrandAnalyzerResponse,
    status_code=HttpStatus.OK,
    summary="Analyze brand identity",
    description="""
    Analyze brand identity from job's brand description and reference profiles.
    
    This endpoint:
    1. Fetches reference Instagram profiles via Apify
    2. Analyzes brand with LLM to extract hashtags, keywords, themes
    3. Generates embedding vector for semantic similarity
    4. Stores brand DNA in the database
    
    **Authentication:** Requires X-Service-Key header.
    
    **Returns:** Brand DNA with hashtags, keywords, themes, and embedding vector.
    """,
    responses={
        200: {
            "description": "Brand analysis completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "11111111-1111-1111-1111-111111111111",
                        "hashtags": ["#sustainablefashion", "#ecofriendly", "#slowfashion"],
                        "keywords": ["sustainable", "ethical", "eco-friendly"],
                        "visual_themes": ["minimalist", "earth tones", "natural textures"],
                        "content_pillars": ["sustainability", "fashion", "lifestyle"],
                        "target_audience_description": "Environmentally conscious millennials...",
                        "embedding_vector": [0.01, 0.02, 0.03],
                        "profiles_analyzed": 3,
                        "posts_analyzed": 45,
                        "analysis_duration_seconds": 12.5
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing service key"},
        404: {"description": "Job not found"},
        500: {"description": "Agent processing error"}
    }
)
async def analyze_brand(
    request: BrandAnalyzerRequest,
    _: ServiceContext = Depends(get_service_context),
) -> BrandAnalyzerResponse:
    """
    Analyze brand identity for a discovery job.
    
    Args:
        request: BrandAnalyzerRequest containing job_id
        _: Service key validation (via dependency)
        
    Returns:
        BrandAnalyzerResponse with extracted brand DNA
        
    Raises:
        HTTPException: On error
    """
    logger.info(f"Brand analysis requested for job: {request.job_id}")
    
    try:
        # Get the agent
        agent = get_brand_analyzer_agent()
        
        # Run brand analysis
        response = await agent.run(request)
        
        logger.info(
            f"Brand analysis completed for job {request.job_id}: "
            f"{len(response.hashtags)} hashtags, {len(response.keywords)} keywords"
        )
        
        return response
        
    except JobNotFoundError as e:
        logger.warning(f"Job not found: {request.job_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job with ID {request.job_id} not found",
                }
            }
        )
    except AgentError as e:
        logger.error(f"Agent error during brand analysis: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_ERROR",
                    "message": str(e),
                    "details": e.details if hasattr(e, 'details') else {}
                }
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error during brand analysis: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during brand analysis",
                }
            }
        )


# =============================================================================
# Discovery Agent Endpoint (STORY-3.3.3)
# =============================================================================

@router.post(
    "/discover",
    response_model=DiscoveryResponse,
    status_code=HttpStatus.OK,
    summary="Discover similar profiles",
    description="""
    Discover similar Instagram profiles using hashtags and keywords.
    
    This endpoint:
    1. Searches Instagram hashtags via Apify
    2. Extracts unique profile usernames from posts
    3. Fetches detailed profile data
    4. Filters by follower range and quality indicators
    5. Deduplicates profiles by username
    6. Stores discovered profiles in the database
    
    **Authentication:** Requires X-Service-Key header.
    
    **Returns:** List of discovered profiles with metadata.
    """,
    responses={
        200: {
            "description": "Discovery completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "job_id": "11111111-1111-1111-1111-111111111111",
                        "profiles": [
                            {
                                "id": "22222222-2222-2222-2222-222222222222",
                                "username": "eco_influencer",
                                "followers_count": 75000,
                                "status": "new"
                            }
                        ],
                        "total_discovered": 10,
                        "deduplicated": 5,
                        "filtered_out": 15,
                        "discovery_duration_seconds": 45.2
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing service key"},
        404: {"description": "Job not found"},
        500: {"description": "Agent processing error"}
    }
)
async def discover_profiles(
    request: DiscoveryRequest,
    _: ServiceContext = Depends(get_service_context),
) -> DiscoveryResponse:
    """
    Discover similar Instagram profiles for a discovery job.
    
    Args:
        request: DiscoveryRequest containing job_id and search criteria
        
    Returns:
        DiscoveryResponse with discovered profiles
        
    Raises:
        HTTPException: On error
    """
    logger.info(
        f"Discovery requested for job: {request.job_id}, "
        f"hashtags: {request.hashtags}, limit: {request.limit}"
    )
    
    try:
        # Get the agent
        agent = get_discovery_agent()
        
        # Run discovery
        response = await agent.run(request)
        
        logger.info(
            f"Discovery completed for job {request.job_id}: "
            f"{response.total_discovered} profiles discovered, "
            f"{response.deduplicated} deduplicated"
        )
        
        return response
        
    except JobNotFoundError as e:
        logger.warning(f"Job not found: {request.job_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job with ID {request.job_id} not found",
                }
            }
        )
    except AgentError as e:
        logger.error(f"Agent error during discovery: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_ERROR",
                    "message": str(e),
                    "details": e.details if hasattr(e, 'details') else {}
                }
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error during discovery: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during profile discovery",
                }
            }
        )


# =============================================================================
# Scorer Agent Endpoint (STORY-3.3.4)
# =============================================================================

@router.post(
    "/score",
    response_model=ScorerResponse,
    status_code=HttpStatus.OK,
    summary="Score a discovered profile",
    description="""
    Score a discovered profile across 6 dimensions and extract contact info.
    
    This endpoint:
    1. Fetches profile data and brand DNA
    2. Analyzes profile with LLM across 6 dimensions
    3. Detects potential fake/bot profiles
    4. Extracts contact information (email, website)
    5. Calculates weighted final score
    6. Stores scores and contacts in database
    
    **Scoring Dimensions:**
    - Visual Aesthetic Match (15%): Visual style alignment
    - Content Theme Alignment (20%): Topic relevance
    - Engagement Rate Score (25%): Engagement quality
    - Follower Quality (15%): Follower authenticity
    - Business Indicators (15%): Partnership readiness
    - Activity Recency (10%): Recent activity
    
    **Authentication:** Requires X-Service-Key header.
    
    **Returns:** Complete scoring results with dimension breakdown and recommendation.
    """,
    responses={
        200: {
            "description": "Scoring completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "profile_id": "22222222-2222-2222-2222-222222222222",
                        "job_id": "11111111-1111-1111-1111-111111111111",
                        "visual_aesthetic_match": 75,
                        "content_theme_alignment": 82,
                        "engagement_rate_score": 88,
                        "follower_quality": 70,
                        "business_indicators": 85,
                        "activity_recency": 90,
                        "final_score": 82,
                        "recommendation": "highly_recommended",
                        "is_fake_suspected": False,
                        "contact": {
                            "email": "contact@example.com",
                            "source": "business_email"
                        },
                        "scoring_duration_seconds": 3.5
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing service key"},
        404: {"description": "Profile or job not found"},
        500: {"description": "Agent processing error"}
    }
)
async def score_profile(
    request: ScorerRequest,
    _: ServiceContext = Depends(get_service_context),
) -> ScorerResponse:
    """
    Score a discovered profile across 6 dimensions.
    
    Args:
        request: ScorerRequest containing profile_id and job_id
        _: Service key validation (via dependency)
        
    Returns:
        ScorerResponse with complete scoring results
        
    Raises:
        HTTPException: On error
    """
    logger.info(
        f"Scoring requested for profile: {request.profile_id}, "
        f"job: {request.job_id}"
    )
    
    try:
        # Get the agent
        agent = get_scorer_agent()
        
        # Run scoring
        response = await agent.run(request)
        
        logger.info(
            f"Scoring completed for profile {request.profile_id}: "
            f"score={response.final_score}, "
            f"recommendation={response.recommendation}"
        )
        
        return response
        
    except ProfileNotFoundError as e:
        logger.warning(f"Profile not found: {request.profile_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={
                "error": {
                    "code": "PROFILE_NOT_FOUND",
                    "message": f"Profile with ID {request.profile_id} not found",
                }
            }
        )
    except JobNotFoundError as e:
        logger.warning(f"Job not found: {request.job_id}")
        raise HTTPException(
            status_code=HttpStatus.NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": f"Job with ID {request.job_id} not found",
                }
            }
        )
    except AgentError as e:
        logger.error(f"Agent error during scoring: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_ERROR",
                    "message": str(e),
                    "details": e.details if hasattr(e, 'details') else {}
                }
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error during scoring: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred during profile scoring",
                }
            }
        )


# =============================================================================
# Agent Health/Status Endpoint
# =============================================================================

@router.get(
    "/status",
    status_code=HttpStatus.OK,
    summary="Get agent status",
    description="Check the status and availability of AI agents.",
)
async def get_agent_status() -> Dict[str, Any]:
    """
    Get status of all AI agents.
    
    Returns:
        Dictionary with agent availability status
    """
    return {
        "agents": {
            "brand_analyzer": {
                "status": "available",
                "description": "Analyzes brand identity from description and reference profiles"
            },
            "discovery": {
                "status": "available",
                "description": "Discovers similar Instagram profiles via hashtag search"
            },
            "scorer": {
                "status": "available",
                "description": "Scores discovered profiles across 6 dimensions with fake detection and contact extraction"
            },
            "email_composer": {
                "status": "not_implemented",
                "description": "Generates outreach emails"
            }
        }
    }
