"""
PartnerScout AI - Demo Service

Service for creating demo jobs with pre-seeded data.
Supports the "Watch Demo" feature in the empty dashboard.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from app.core.constants import JobStatus, ProfileStatus
from app.repositories import JobRepository, ProfileRepository
from app.repositories.brand_repo import BrandRepository
from app.repositories.score_repo import ScoreRepository
from app.repositories.contact_repo import ContactRepository


logger = logging.getLogger(__name__)


class DemoService:
    """Service for creating demo jobs with seeded data."""
    
    def __init__(
        self,
        job_repo: Optional[JobRepository] = None,
        profile_repo: Optional[ProfileRepository] = None,
        brand_dna_repo: Optional[BrandRepository] = None,
        score_repo: Optional[ScoreRepository] = None,
        contact_repo: Optional[ContactRepository] = None,
    ):
        """Initialize demo service with repositories."""
        self.job_repo = job_repo or JobRepository()
        self.profile_repo = profile_repo or ProfileRepository()
        self.brand_dna_repo = brand_dna_repo or BrandRepository()
        self.score_repo = score_repo or ScoreRepository()
        self.contact_repo = contact_repo or ContactRepository()
    
    def create_demo_job(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a demo job with pre-seeded profiles.
        
        Args:
            user_id: Optional user ID (uses generated demo user if not provided)
            
        Returns:
            Demo job details with redirect URL
        """
        from app.data.demo_seed import (
            DEMO_BRAND_DESCRIPTION, 
            DEMO_BRAND_DNA, 
            DEMO_PROFILES
        )
        
        # Use provided user_id or None for anonymous demo
        # Note: user_id=None is allowed to avoid FK constraint with auth.users
        effective_user_id = user_id
        
        logger.info(f"Creating demo job for user {effective_user_id}")
        
        # Create job
        job = self.job_repo.create(
            user_id=effective_user_id,
            brand_description=DEMO_BRAND_DESCRIPTION.strip(),
            reference_profiles=[
                "https://instagram.com/ecolife_brand",
                "https://instagram.com/sustainable_co"
            ],
            name="[DEMO] Sustainable Lifestyle Partners",
            follower_range_min=5000,
            follower_range_max=500000,
            discovery_limit=10,
            keywords=DEMO_BRAND_DNA["keywords"],
            hashtags=DEMO_BRAND_DNA["hashtags"],
            min_score_threshold=50,
        )
        
        job_id = job["id"]
        
        # Mark job as completed immediately (skip pending state validation)
        self.job_repo.update_status(
            id=job_id,
            status=JobStatus.COMPLETED,
        )
        
        # Insert brand DNA
        try:
            self.brand_dna_repo.create(
                job_id=job_id,
                hashtags=DEMO_BRAND_DNA["hashtags"],
                keywords=DEMO_BRAND_DNA["keywords"],
                visual_themes=DEMO_BRAND_DNA.get("visual_themes", []),
                content_pillars=DEMO_BRAND_DNA.get("content_pillars", []),
                target_audience_description=DEMO_BRAND_DNA.get("target_audience_description", ""),
            )
        except Exception as e:
            logger.warning(f"Failed to create brand DNA for demo job: {e}")
        
        # Insert demo profiles with scores and contacts
        profiles_created = 0
        for profile_data in DEMO_PROFILES:
            try:
                profile = self.profile_repo.create(
                    job_id=job_id,
                    instagram_url=f"https://instagram.com/{profile_data['username']}",
                    username=profile_data["username"],
                    full_name=profile_data.get("full_name"),
                    bio=profile_data.get("bio"),
                    followers_count=profile_data["followers_count"],
                    following_count=profile_data.get("following_count"),
                    posts_count=profile_data.get("posts_count"),
                    engagement_rate=profile_data.get("engagement_rate"),
                    is_verified=profile_data.get("is_verified", False),
                    is_business_account=profile_data.get("is_business_account", False),
                    external_url=profile_data.get("external_url"),
                )
                
                # Update profile status to done (DB enum uses 'done' for scored)
                try:
                    self.profile_repo.update_status(profile["id"], ProfileStatus.SCORED)
                except Exception:
                    # Fallback: DB enum might use 'done' instead of 'scored'
                    self.profile_repo.update_status(profile["id"], "done")
                
                profile_id = profile["id"]
                profiles_created += 1
                
                # Insert score
                dims = profile_data.get("dimension_scores", {})
                try:
                    self.score_repo.create(
                        profile_id=profile_id,
                        final_score=profile_data["score"],
                        recommendation=profile_data["recommendation"],
                        visual_aesthetic_match=dims.get("visual_aesthetic_match", 75),
                        content_theme_alignment=dims.get("content_theme_alignment", 75),
                        engagement_rate_score=dims.get("engagement_rate_score", 75),
                        follower_quality=dims.get("follower_quality", 75),
                        business_indicators=dims.get("business_indicators", 75),
                        activity_recency=dims.get("activity_recency", 75),
                        reasoning={"demo": True, "note": "Pre-seeded demo data"},
                    )
                except Exception as e:
                    logger.warning(f"Failed to create score for demo profile {profile_data['username']}: {e}")
                
                # Insert contact if email available
                if profile_data.get("contact_email"):
                    try:
                        self.contact_repo.create(
                            profile_id=profile_id,
                            email=profile_data["contact_email"],
                            email_source="bio",
                            website=profile_data.get("external_url"),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create contact for demo profile {profile_data['username']}: {e}")
                        
            except Exception as e:
                logger.warning(f"Failed to create demo profile {profile_data['username']}: {e}")
        
        logger.info(f"Created demo job {job_id} with {profiles_created} profiles")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "message": f"Demo job created with {profiles_created} sample profiles",
            "profiles_count": profiles_created,
            "redirect_url": f"/jobs/{job_id}",
            "is_demo": True,
        }


def get_demo_service() -> DemoService:
    """
    Get a DemoService instance.
    
    This is the recommended way to get a DemoService instance,
    as it can be used as a FastAPI dependency.
    
    Returns:
        DemoService instance
    """
    return DemoService()
