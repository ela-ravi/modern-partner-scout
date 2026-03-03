"""
PartnerScout AI - Scorer Agent (STORY-3.3.4)

AI agent that scores discovered Instagram profiles across 6 dimensions to evaluate
partnership potential. Implements fake detection, contact extraction, and weighted
score calculation.

Subtasks completed:
- SUB-3.3.4.1.1: Create app/agents/scorer.py
- SUB-3.3.4.1.2: Implement 6-dimension scoring with LLM
- SUB-3.3.4.1.3: Implement fake profile detection logic
- SUB-3.3.4.1.4: Implement email extraction (bio, business_email, website)
- SUB-3.3.4.1.5: Implement weighted final score calculation
- SUB-3.3.4.1.6: Implement database storage in profile_scores and profile_contacts
"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.agents.base import AgentResult, BaseAgent
from app.core.config import settings
from app.core.constants import ProfileStatus
from app.core.exceptions import AgentError, JobNotFoundError, ProfileNotFoundError
from app.core.settings import get_scoring_weights, get_scoring_thresholds
from app.models.agent import ScoreDimension, ScorerRequest, ScorerResponse
from app.repositories.brand_repo import BrandRepository
from app.repositories.contact_repo import ContactRepository
from app.repositories.job_repo import JobRepository
from app.repositories.profile_repo import ProfileRepository
from app.repositories.score_repo import ScoreRepository
from app.services.llm_service import LLMService
from app.services.scoring_service import ScoringService, get_scoring_service


# =============================================================================
# Logger Configuration
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Output Schema
# =============================================================================

class ScoringAnalysisOutput(BaseModel):
    """Schema for LLM scoring analysis output."""
    
    # 6 Dimension Scores
    visual_aesthetic_match: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Visual aesthetic match score (0-100)"
    )
    content_theme_alignment: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Content theme alignment score (0-100)"
    )
    engagement_rate_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Engagement rate quality score (0-100)"
    )
    follower_quality: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Follower quality score (0-100)"
    )
    business_indicators: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Business readiness score (0-100)"
    )
    activity_recency: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Activity recency score (0-100)"
    )
    
    # Fake Detection
    is_fake: bool = Field(
        default=False,
        description="Whether the profile is suspected to be fake"
    )
    fake_indicators: List[str] = Field(
        default_factory=list,
        description="List of indicators suggesting the profile is fake"
    )
    
    # Contact Information
    contact_email: Optional[str] = Field(
        default=None,
        description="Extracted email address"
    )
    contact_website: Optional[str] = Field(
        default=None,
        description="Extracted website URL"
    )
    email_source: Optional[str] = Field(
        default=None,
        description="Source of the email (bio, business_email, website)"
    )
    
    # Location Detection
    detected_country: Optional[str] = Field(
        default=None,
        description="Detected country/region of the profile based on bio, location, and content clues"
    )

    # Reasoning
    reasoning: Dict[str, str] = Field(
        default_factory=dict,
        description="Reasoning for each dimension score"
    )

    # Recommendation
    recommendation: str = Field(
        default="consider",
        description="Recommendation level: highly_recommended, recommended, consider, not_recommended"
    )


class ExtractedContact(BaseModel):
    """Extracted contact information from profile."""
    
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email_source: Optional[str] = None
    other_contacts: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Scorer Agent
# =============================================================================

class ScorerAgent(BaseAgent[ScorerRequest, ScorerResponse]):
    """
    AI agent for scoring discovered Instagram profiles.
    
    This agent:
    1. Fetches profile data and brand DNA
    2. Analyzes profile across 6 dimensions using LLM
    3. Detects potential fake/bot profiles
    4. Extracts contact information
    5. Calculates weighted final score
    6. Stores scores and contacts in database
    
    Scoring Dimensions (configurable weights):
    - Visual Aesthetic Match (15%): Visual style alignment
    - Content Theme Alignment (20%): Topic relevance
    - Engagement Rate Score (25%): Engagement quality
    - Follower Quality (15%): Follower authenticity
    - Business Indicators (15%): Partnership readiness
    - Activity Recency (10%): Recent activity
    
    Example:
        ```python
        agent = ScorerAgent()
        request = ScorerRequest(
            profile_id=UUID("..."),
            job_id=UUID("...")
        )
        response = await agent.run(request)
        print(f"Final score: {response.final_score}")
        ```
    """
    
    agent_name = "scorer"
    
    # Fake detection thresholds
    MIN_ENGAGEMENT_RATE = 0.5  # 0.5%
    MAX_FOLLOWING_RATIO = 3.0  # Following 3x more than followers
    MIN_POSTS_FOR_HIGH_FOLLOWERS = 10
    HIGH_FOLLOWER_THRESHOLD = 10000
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        job_repo: Optional[JobRepository] = None,
        profile_repo: Optional[ProfileRepository] = None,
        brand_repo: Optional[BrandRepository] = None,
        score_repo: Optional[ScoreRepository] = None,
        contact_repo: Optional[ContactRepository] = None,
        scoring_service: Optional[ScoringService] = None,
        **kwargs
    ):
        """
        Initialize the Scorer Agent.
        
        Args:
            llm_service: LLM service for text generation (optional)
            job_repo: Job repository for accessing job data (optional)
            profile_repo: Profile repository for accessing profiles (optional)
            brand_repo: Brand repository for accessing brand DNA (optional)
            score_repo: Score repository for storing scores (optional)
            contact_repo: Contact repository for storing contacts (optional)
            scoring_service: Scoring service for weight calculation (optional)
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(llm_service=llm_service, **kwargs)
        
        # Initialize repositories
        self._job_repo = job_repo or JobRepository()
        self._profile_repo = profile_repo or ProfileRepository()
        self._brand_repo = brand_repo or BrandRepository()
        self._score_repo = score_repo or ScoreRepository()
        self._contact_repo = contact_repo or ContactRepository()
        
        # Initialize scoring service
        self._scoring_service = scoring_service or get_scoring_service()
        
        # Load scoring weights and thresholds
        self._weights = get_scoring_weights()
        self._thresholds = get_scoring_thresholds()
        
        logger.debug(f"Initialized {self.agent_name} agent with weights: {self._weights}")
    
    # =========================================================================
    # Main Run Method (SUB-3.3.4.1.1)
    # =========================================================================
    
    async def run(self, input_data: ScorerRequest) -> ScorerResponse:
        """
        Execute scoring for a discovered profile.
        
        This method:
        1. Fetches profile data and brand DNA
        2. Analyzes profile with LLM across 6 dimensions
        3. Detects fake profile indicators
        4. Extracts contact information
        5. Calculates weighted final score
        6. Stores results in database
        
        Args:
            input_data: ScorerRequest containing profile_id and job_id
            
        Returns:
            ScorerResponse with scoring results
            
        Raises:
            AgentError: If scoring fails
            ProfileNotFoundError: If profile doesn't exist
            JobNotFoundError: If job doesn't exist
        """
        start_time = time.time()
        metrics = self._start_metrics()
        
        profile_id = str(input_data.profile_id)
        job_id = str(input_data.job_id)
        
        logger.info(f"Starting scoring for profile: {profile_id}, job: {job_id}")
        
        try:
            # Step 1: Fetch profile data
            profile_data = input_data.profile_data or await self._fetch_profile(profile_id)
            
            # Step 2: Fetch brand DNA
            brand_dna = input_data.brand_dna or await self._fetch_brand_dna(job_id)
            
            # Step 3: Fetch job for brand description and target country
            job = await self._fetch_job(job_id)
            brand_description = job.get("brand_description", "")
            target_country = job.get("target_country")

            # Step 4: Detect fake indicators (SUB-3.3.4.1.3)
            fake_indicators = self._detect_fake_indicators(profile_data)
            is_fake_suspected = len(fake_indicators) > 0
            
            # Step 5: Extract contact info (SUB-3.3.4.1.4)
            contact = self._extract_contact_info(profile_data)
            
            # Step 6: Analyze with LLM for 6-dimension scoring (SUB-3.3.4.1.2)
            analysis = await self._analyze_profile(
                profile_data=profile_data,
                brand_dna=brand_dna,
                brand_description=brand_description,
                fake_indicators=fake_indicators,
                contact=contact,
                target_country=target_country,
            )
            
            # Step 7: Calculate weighted final score (SUB-3.3.4.1.5)
            dimensions = {
                "visual_aesthetic_match": analysis.visual_aesthetic_match,
                "content_theme_alignment": analysis.content_theme_alignment,
                "engagement_rate_score": analysis.engagement_rate_score,
                "follower_quality": analysis.follower_quality,
                "business_indicators": analysis.business_indicators,
                "activity_recency": analysis.activity_recency,
            }
            
            final_score = self._scoring_service.calculate_final_score_from_dict(dimensions)

            # Apply country boost/penalty if target country is set
            country_boosted = False
            country_penalized = False
            if target_country and analysis.detected_country:
                if target_country.lower() in analysis.detected_country.lower() or \
                   analysis.detected_country.lower() in target_country.lower():
                    # Strong boost for country match (+15)
                    final_score = min(100, final_score + 15)
                    country_boosted = True
                    logger.info(
                        f"Country boost (+15) applied for {profile_data.get('username')}: "
                        f"target={target_country}, detected={analysis.detected_country}, "
                        f"new_score={final_score}"
                    )
                else:
                    # Penalty for country mismatch (-10)
                    final_score = max(0, final_score - 10)
                    country_penalized = True
                    logger.info(
                        f"Country penalty (-10) applied for {profile_data.get('username')}: "
                        f"target={target_country}, detected={analysis.detected_country}, "
                        f"new_score={final_score}"
                    )

            # Get recommendation from scoring service
            recommendation = self._scoring_service.get_recommendation(
                final_score=final_score,
                dimensions=dimensions,
                is_fake_suspected=is_fake_suspected
            )
            
            # Override with LLM recommendation if it's more conservative
            if analysis.recommendation == "not_recommended" and recommendation != "not_recommended":
                recommendation = analysis.recommendation
            
            # Step 8: Store scores and contacts (SUB-3.3.4.1.6)
            await self._store_results(
                profile_id=profile_id,
                dimensions=dimensions,
                final_score=final_score,
                recommendation=recommendation,
                reasoning=analysis.reasoning,
                is_fake_suspected=is_fake_suspected,
                fake_indicators=fake_indicators,
                contact=contact
            )
            
            # Update profile status
            await self._update_profile_status(profile_id, ProfileStatus.SCORED)
            
            # Calculate duration
            duration = time.time() - start_time
            self._complete_metrics(success=True)
            
            logger.info(
                f"Scoring completed for profile {profile_id}: "
                f"score={final_score}, recommendation={recommendation}, "
                f"is_fake={is_fake_suspected}, duration={duration:.2f}s"
            )
            
            # Build dimension list for response
            dimension_list = self._build_dimension_list(dimensions, analysis.reasoning)
            
            return ScorerResponse(
                profile_id=input_data.profile_id,
                job_id=input_data.job_id,
                visual_aesthetic_match=dimensions["visual_aesthetic_match"],
                content_theme_alignment=dimensions["content_theme_alignment"],
                engagement_rate_score=dimensions["engagement_rate_score"],
                follower_quality=dimensions["follower_quality"],
                business_indicators=dimensions["business_indicators"],
                activity_recency=dimensions["activity_recency"],
                final_score=final_score,
                recommendation=recommendation,
                reasoning=analysis.reasoning,
                dimensions=dimension_list,
                is_fake_suspected=is_fake_suspected,
                fake_indicators=fake_indicators,
                contact={
                    "email": contact.email,
                    "website": contact.website,
                    "source": contact.email_source,
                    "phone": contact.phone,
                } if contact.email or contact.website else None,
                scoring_duration_seconds=duration,
            )
            
        except ProfileNotFoundError:
            raise
        except JobNotFoundError:
            raise
        except AgentError:
            raise
        except Exception as e:
            self._complete_metrics(success=False, error_message=str(e))
            logger.error(f"Scoring failed for profile {profile_id}: {e}")
            raise AgentError(
                message=f"Scoring failed: {str(e)}",
                agent_name=self.agent_name,
                details={"profile_id": profile_id, "job_id": job_id, "error": str(e)}
            )
    
    # =========================================================================
    # Data Fetching
    # =========================================================================
    
    async def _fetch_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Fetch profile data from the database.
        
        Args:
            profile_id: Profile UUID string
            
        Returns:
            Profile data dictionary
            
        Raises:
            ProfileNotFoundError: If profile doesn't exist
        """
        logger.debug(f"Fetching profile: {profile_id}")
        return self._profile_repo.get_by_id(profile_id)
    
    async def _fetch_brand_dna(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch brand DNA for the job.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            Brand DNA dictionary or empty dict if not found
        """
        logger.debug(f"Fetching brand DNA for job: {job_id}")
        brand_dna = self._brand_repo.get_by_job_id_optional(job_id)
        return brand_dna or {}
    
    async def _fetch_job(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch job data from the database.
        
        Args:
            job_id: Job UUID string
            
        Returns:
            Job data dictionary
            
        Raises:
            JobNotFoundError: If job doesn't exist
        """
        logger.debug(f"Fetching job: {job_id}")
        return self._job_repo.get_by_id(job_id)
    
    # =========================================================================
    # Fake Detection (SUB-3.3.4.1.3)
    # =========================================================================
    
    def _detect_fake_indicators(self, profile: Dict[str, Any]) -> List[str]:
        """
        Detect indicators that suggest a profile might be fake.
        
        Uses heuristics to identify:
        - Low engagement rate with high followers
        - Suspicious following/follower ratio
        - High followers with very few posts
        - Other patterns indicating purchased followers/engagement
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            List of fake indicator descriptions
        """
        indicators = []
        
        followers = profile.get("followers_count", 0) or 0
        following = profile.get("following_count", 0) or 0
        posts = profile.get("posts_count", 0) or 0
        engagement_rate = profile.get("engagement_rate")
        
        # Check 1: No followers
        if followers == 0:
            indicators.append("No followers")
            return indicators  # Definitely suspicious
        
        # Check 2: Following/Follower ratio
        if followers > 0 and following > 0:
            ratio = following / followers
            if ratio > self.MAX_FOLLOWING_RATIO:
                indicators.append(
                    f"High following/follower ratio ({ratio:.1f}x) - "
                    f"following {following:,} with only {followers:,} followers"
                )
        
        # Check 3: High followers with few posts
        if followers > self.HIGH_FOLLOWER_THRESHOLD and posts < self.MIN_POSTS_FOR_HIGH_FOLLOWERS:
            indicators.append(
                f"High follower count ({followers:,}) with very few posts ({posts})"
            )
        
        # Check 4: Low engagement rate
        if engagement_rate is not None and engagement_rate < self.MIN_ENGAGEMENT_RATE:
            if followers > 5000:  # Only flag if they have meaningful followers
                indicators.append(
                    f"Very low engagement rate ({engagement_rate:.2f}%) "
                    f"for account with {followers:,} followers"
                )
        
        # Check 5: Suspicious growth patterns (no bio with high followers)
        bio = profile.get("bio", "") or ""
        if followers > 50000 and len(bio.strip()) < 10:
            indicators.append(
                f"High follower account ({followers:,}) with minimal/no bio"
            )
        
        # Check 6: Following more than 7500 (Instagram limit warning)
        if following > 7500:
            indicators.append(
                f"Following {following:,} accounts (near/above Instagram limit)"
            )
        
        return indicators
    
    def _is_likely_fake(self, profile: Dict[str, Any]) -> bool:
        """
        Quick check if a profile is likely fake.
        
        Args:
            profile: Profile data
            
        Returns:
            True if profile appears fake
        """
        indicators = self._detect_fake_indicators(profile)
        return len(indicators) >= 2  # Two or more indicators = likely fake
    
    # =========================================================================
    # Contact Extraction (SUB-3.3.4.1.4)
    # =========================================================================
    
    def _extract_contact_info(self, profile: Dict[str, Any]) -> ExtractedContact:
        """
        Extract contact information from profile data.
        
        Extracts from:
        - Bio text (email addresses)
        - Business email field
        - External URL/website
        - Other contact methods
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            ExtractedContact with extracted information
        """
        contact = ExtractedContact()
        
        # Priority 1: Business email (most reliable)
        business_email = profile.get("business_email")
        if business_email and self._is_valid_email(business_email):
            contact.email = business_email
            contact.email_source = "business_email"
        
        # Priority 2: Extract from bio
        if not contact.email:
            bio = profile.get("bio", "") or ""
            bio_emails = self.EMAIL_PATTERN.findall(bio)
            if bio_emails:
                # Filter out common false positives
                valid_emails = [e for e in bio_emails if self._is_valid_email(e)]
                if valid_emails:
                    contact.email = valid_emails[0]
                    contact.email_source = "bio"
        
        # Extract website
        external_url = profile.get("external_url")
        if external_url:
            contact.website = external_url
            
            # Try to extract email from website if we don't have one
            if not contact.email and "@" in external_url:
                # Sometimes email is in the URL (rare but possible)
                pass
        
        # Extract phone if present
        phone = profile.get("phone") or profile.get("business_phone")
        if phone:
            contact.phone = phone
        
        # Collect other contact methods
        other_contacts = {}
        
        # Check for linktree or similar
        if external_url:
            if "linktr.ee" in external_url or "linktree" in external_url.lower():
                other_contacts["linktree"] = external_url
            elif "bio.link" in external_url:
                other_contacts["bio_link"] = external_url
        
        # Check bio for social handles
        bio = profile.get("bio", "") or ""
        
        # Twitter/X
        twitter_match = re.search(r'(?:twitter|x)\.com/(\w+)', bio, re.IGNORECASE)
        if twitter_match:
            other_contacts["twitter"] = f"@{twitter_match.group(1)}"
        
        # TikTok
        tiktok_match = re.search(r'tiktok\.com/@?(\w+)', bio, re.IGNORECASE)
        if tiktok_match:
            other_contacts["tiktok"] = f"@{tiktok_match.group(1)}"
        
        if other_contacts:
            contact.other_contacts = other_contacts
        
        return contact
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email address format and filter common false positives.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email appears valid
        """
        if not email:
            return False
        
        email = email.strip()
        
        # Basic format check
        if not self.EMAIL_PATTERN.match(email):
            return False
        
        # Filter common false positive domains (only the truly fake ones)
        clearly_fake_domains = [
            "example.com", "test.com", "domain.com",
            "email.com", "yourmail.com", "sentry.io"
        ]
        
        domain = email.split("@")[-1].lower()
        if domain in clearly_fake_domains:
            return False
        
        # Filter placeholder emails with generic local parts AND generic free email domains
        placeholder_local_parts = ["email", "mail", "test", "example", "your", "user"]
        generic_free_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        
        local_part = email.split("@")[0].lower()
        if local_part in placeholder_local_parts and domain in generic_free_domains:
            return False  # Likely a placeholder like "email@gmail.com"
        
        return True
    
    # =========================================================================
    # LLM Analysis (SUB-3.3.4.1.2)
    # =========================================================================
    
    async def _analyze_profile(
        self,
        profile_data: Dict[str, Any],
        brand_dna: Dict[str, Any],
        brand_description: str,
        fake_indicators: List[str],
        contact: ExtractedContact,
        target_country: Optional[str] = None,
    ) -> ScoringAnalysisOutput:
        """
        Analyze profile using LLM to score across 6 dimensions.
        
        Args:
            profile_data: Profile data dictionary
            brand_dna: Brand DNA with hashtags, keywords, etc.
            brand_description: Original brand description
            fake_indicators: Pre-detected fake indicators
            contact: Extracted contact information
            
        Returns:
            ScoringAnalysisOutput with scores and reasoning
        """
        logger.debug(f"Analyzing profile with LLM: {profile_data.get('username')}")
        
        # Format profile data for prompt
        profile_summary = self._format_profile_for_prompt(profile_data)
        
        # Format brand DNA for prompt
        brand_dna_summary = self._format_brand_dna_for_prompt(brand_dna)
        
        # Build the chain with JSON output parser
        chain = self.build_json_chain(pydantic_schema=ScoringAnalysisOutput)
        
        # Prepare input variables
        country_instruction = ""
        if target_country:
            country_instruction = (
                f"\n\n## Country/Region Detection\n"
                f"The brand is targeting partners in: **{target_country}**\n"
                f"Please analyze the profile's bio, location, language, and content clues "
                f"to detect what country/region this profile is likely from. "
                f"Set the 'detected_country' field to your best guess (e.g., 'India', 'USA', 'Germany') "
                f"or null if you cannot determine it."
            )

        input_vars = {
            "brand_description": brand_description + country_instruction,
            "brand_dna": brand_dna_summary,
            "username": profile_data.get("username", "unknown"),
            "profile_url": profile_data.get("instagram_url", ""),
            "profile_data": profile_summary,
        }
        
        try:
            # Invoke the chain
            logger.info(f"Invoking LLM chain for profile: {profile_data.get('username')}")
            result = await self.invoke_chain(chain, input_vars)
            logger.info(f"LLM chain returned result type: {type(result)}")
            
            # Parse result into ScoringAnalysisOutput
            if isinstance(result, dict):
                logger.info(f"LLM raw scores: visual={result.get('visual_aesthetic_match')}, content={result.get('content_theme_alignment')}")
                analysis = ScoringAnalysisOutput(**result)
            else:
                analysis = result
            
            # Merge pre-detected fake indicators
            if fake_indicators:
                analysis.is_fake = True
                existing_indicators = set(analysis.fake_indicators)
                for indicator in fake_indicators:
                    if indicator not in existing_indicators:
                        analysis.fake_indicators.append(indicator)
            
            # Merge contact info if LLM found additional
            if contact.email and not analysis.contact_email:
                analysis.contact_email = contact.email
                analysis.email_source = contact.email_source
            if contact.website and not analysis.contact_website:
                analysis.contact_website = contact.website
            
            logger.debug(
                f"LLM analysis complete for {profile_data.get('username')}: "
                f"scores={analysis.visual_aesthetic_match}, "
                f"{analysis.content_theme_alignment}, "
                f"{analysis.engagement_rate_score}"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(
                f"LLM analysis failed for {profile_data.get('username')}: {type(e).__name__}: {e}",
                exc_info=True  # Include full traceback
            )
            logger.warning(
                f"Falling back to heuristic scoring for {profile_data.get('username')} "
                f"due to LLM error"
            )
            
            # Return fallback scores based on heuristics
            return self._generate_fallback_scores(
                profile_data=profile_data,
                brand_dna=brand_dna,
                fake_indicators=fake_indicators,
                contact=contact
            )
    
    def _format_profile_for_prompt(self, profile: Dict[str, Any]) -> str:
        """
        Format profile data for LLM prompt.
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            Formatted string for prompt
        """
        parts = []
        
        # Basic info
        parts.append(f"Username: @{profile.get('username', 'unknown')}")
        parts.append(f"Full Name: {profile.get('full_name') or 'N/A'}")
        
        # Stats
        followers = profile.get("followers_count", 0)
        following = profile.get("following_count", 0)
        posts = profile.get("posts_count", 0)
        
        parts.append(f"Followers: {followers:,}")
        parts.append(f"Following: {following:,}")
        parts.append(f"Posts: {posts:,}")
        
        # Engagement
        engagement = profile.get("engagement_rate")
        if engagement:
            parts.append(f"Engagement Rate: {engagement:.2f}%")
        
        # Account type
        is_verified = profile.get("is_verified", False)
        is_business = profile.get("is_business_account")
        
        account_type = []
        if is_verified:
            account_type.append("Verified")
        if is_business:
            account_type.append("Business Account")
        if account_type:
            parts.append(f"Account Type: {', '.join(account_type)}")
        
        # Bio
        bio = profile.get("bio", "") or ""
        if bio:
            parts.append(f"Bio: {bio[:500]}")
        
        # External URL
        external_url = profile.get("external_url")
        if external_url:
            parts.append(f"Website: {external_url}")
        
        # Business category
        category = profile.get("business_category")
        if category:
            parts.append(f"Business Category: {category}")
        
        return "\n".join(parts)
    
    def _format_brand_dna_for_prompt(self, brand_dna: Dict[str, Any]) -> str:
        """
        Format brand DNA for LLM prompt.
        
        Args:
            brand_dna: Brand DNA dictionary
            
        Returns:
            Formatted string for prompt
        """
        if not brand_dna:
            return "No brand DNA available."
        
        parts = []
        
        # Hashtags
        hashtags = brand_dna.get("hashtags", [])
        if hashtags:
            parts.append(f"Brand Hashtags: {', '.join(hashtags[:15])}")
        
        # Keywords
        keywords = brand_dna.get("keywords", [])
        if keywords:
            parts.append(f"Brand Keywords: {', '.join(keywords[:15])}")
        
        # Visual themes
        themes = brand_dna.get("visual_themes", [])
        if themes:
            parts.append(f"Visual Themes: {', '.join(themes[:10])}")
        
        # Content pillars
        pillars = brand_dna.get("content_pillars", [])
        if pillars:
            parts.append(f"Content Pillars: {', '.join(pillars[:10])}")
        
        # Target audience
        audience = brand_dna.get("target_audience_description")
        if audience:
            parts.append(f"Target Audience: {audience[:200]}")
        
        return "\n".join(parts) if parts else "No brand DNA available."
    
    def _generate_fallback_scores(
        self,
        profile_data: Dict[str, Any],
        brand_dna: Dict[str, Any],
        fake_indicators: List[str],
        contact: ExtractedContact
    ) -> ScoringAnalysisOutput:
        """
        Generate fallback scores using heuristics when LLM fails.
        
        Args:
            profile_data: Profile data
            brand_dna: Brand DNA
            fake_indicators: Detected fake indicators
            contact: Extracted contact
            
        Returns:
            ScoringAnalysisOutput with heuristic-based scores
        """
        logger.warning("Using fallback heuristic scoring")
        
        # Default middle scores
        scores = {
            "visual_aesthetic_match": 50,
            "content_theme_alignment": 50,
            "engagement_rate_score": 50,
            "follower_quality": 50,
            "business_indicators": 50,
            "activity_recency": 50,
        }
        
        reasoning = {}
        
        # Engagement rate scoring
        engagement = profile_data.get("engagement_rate", 0) or 0
        if engagement >= 6:
            scores["engagement_rate_score"] = 95
            reasoning["engagement_rate_score"] = "Excellent engagement rate"
        elif engagement >= 3:
            scores["engagement_rate_score"] = 80
            reasoning["engagement_rate_score"] = "Good engagement rate"
        elif engagement >= 1.5:
            scores["engagement_rate_score"] = 65
            reasoning["engagement_rate_score"] = "Average engagement rate"
        elif engagement >= 0.5:
            scores["engagement_rate_score"] = 40
            reasoning["engagement_rate_score"] = "Below average engagement rate"
        else:
            scores["engagement_rate_score"] = 20
            reasoning["engagement_rate_score"] = "Low engagement rate"
        
        # Follower quality based on ratio
        followers = profile_data.get("followers_count", 0) or 0
        following = profile_data.get("following_count", 0) or 0
        
        if followers > 0 and following > 0:
            ratio = following / followers
            if ratio < 0.5:
                scores["follower_quality"] = 80
                reasoning["follower_quality"] = "Good follower/following ratio"
            elif ratio < 1.0:
                scores["follower_quality"] = 65
                reasoning["follower_quality"] = "Acceptable follower/following ratio"
            elif ratio < 2.0:
                scores["follower_quality"] = 45
                reasoning["follower_quality"] = "Moderate follower/following ratio"
            else:
                scores["follower_quality"] = 25
                reasoning["follower_quality"] = "Poor follower/following ratio"
        
        # Business indicators
        is_business = profile_data.get("is_business_account", False)
        has_email = bool(contact.email)
        has_website = bool(contact.website)
        is_verified = profile_data.get("is_verified", False)
        
        business_score = 40  # Base
        if is_business:
            business_score += 20
        if has_email:
            business_score += 15
        if has_website:
            business_score += 15
        if is_verified:
            business_score += 10
        
        scores["business_indicators"] = min(100, business_score)
        reasoning["business_indicators"] = "Based on business account features"
        
        # Activity recency (default to moderate if no data)
        scores["activity_recency"] = 60
        reasoning["activity_recency"] = "Activity data not available for detailed analysis"
        
        # Visual and content alignment (default without LLM)
        scores["visual_aesthetic_match"] = 50
        scores["content_theme_alignment"] = 50
        reasoning["visual_aesthetic_match"] = "Unable to analyze visual content without LLM"
        reasoning["content_theme_alignment"] = "Unable to analyze content themes without LLM"
        
        # Reduce scores if fake indicators present
        is_fake = len(fake_indicators) >= 2
        if is_fake:
            for key in scores:
                scores[key] = max(10, scores[key] - 20)
        
        return ScoringAnalysisOutput(
            visual_aesthetic_match=scores["visual_aesthetic_match"],
            content_theme_alignment=scores["content_theme_alignment"],
            engagement_rate_score=scores["engagement_rate_score"],
            follower_quality=scores["follower_quality"],
            business_indicators=scores["business_indicators"],
            activity_recency=scores["activity_recency"],
            is_fake=is_fake,
            fake_indicators=fake_indicators,
            contact_email=contact.email,
            contact_website=contact.website,
            email_source=contact.email_source,
            reasoning=reasoning,
            recommendation="not_recommended" if is_fake else "consider"
        )
    
    # =========================================================================
    # Score Calculation (SUB-3.3.4.1.5)
    # =========================================================================
    
    def _build_dimension_list(
        self,
        dimensions: Dict[str, int],
        reasoning: Dict[str, str]
    ) -> List[ScoreDimension]:
        """
        Build list of ScoreDimension objects for response.
        
        Args:
            dimensions: Dict of dimension scores
            reasoning: Dict of dimension reasoning
            
        Returns:
            List of ScoreDimension objects
        """
        dimension_list = []
        
        for dim_name, score in dimensions.items():
            weight = self._weights.get(dim_name, 0)
            reason = reasoning.get(dim_name, "")
            
            dimension_list.append(ScoreDimension(
                name=dim_name,
                score=score,
                weight=weight,
                reasoning=reason
            ))
        
        return dimension_list
    
    # =========================================================================
    # Database Storage (SUB-3.3.4.1.6)
    # =========================================================================
    
    async def _store_results(
        self,
        profile_id: str,
        dimensions: Dict[str, int],
        final_score: int,
        recommendation: str,
        reasoning: Dict[str, str],
        is_fake_suspected: bool,
        fake_indicators: List[str],
        contact: ExtractedContact
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Store scoring results in the database.
        
        Args:
            profile_id: Profile UUID
            dimensions: Dimension scores
            final_score: Calculated final score
            recommendation: Recommendation level
            reasoning: Reasoning for each dimension
            is_fake_suspected: Whether fake is suspected
            fake_indicators: List of fake indicators
            contact: Extracted contact info
            
        Returns:
            Tuple of (score_record, contact_record)
        """
        logger.debug(f"Storing results for profile: {profile_id}")
        
        # Store reasoning with fake indicators
        full_reasoning = {
            **reasoning,
            "fake_indicators": fake_indicators if fake_indicators else [],
            "recommendation_reason": f"Final score: {final_score}, "
                                     f"Fake suspected: {is_fake_suspected}"
        }
        
        # Check if score already exists
        existing_score = self._score_repo.get_by_profile_id_optional(profile_id)

        score_update_data = {
            "visual_aesthetic_match": dimensions["visual_aesthetic_match"],
            "content_theme_alignment": dimensions["content_theme_alignment"],
            "engagement_rate_score": dimensions["engagement_rate_score"],
            "follower_quality": dimensions["follower_quality"],
            "business_indicators": dimensions["business_indicators"],
            "activity_recency": dimensions["activity_recency"],
            "final_score": final_score,
            "recommendation": recommendation,
            "reasoning": full_reasoning,
            "is_fake_suspected": is_fake_suspected,
        }

        if existing_score:
            # Update existing score
            score_record = self._score_repo.update_by_profile_id(
                profile_id=profile_id,
                data=score_update_data,
            )
            logger.debug(f"Updated existing score for profile: {profile_id}")
        else:
            try:
                # Create new score
                score_record = self._score_repo.create_full_score(
                    profile_id=profile_id,
                    dimensions=dimensions,
                    final_score=final_score,
                    recommendation=recommendation,
                    reasoning=full_reasoning,
                    is_fake_suspected=is_fake_suspected
                )
                logger.debug(f"Created new score for profile: {profile_id}")
            except Exception as e:
                # Handle race condition: score inserted between SELECT and INSERT
                if "duplicate" in str(e).lower() or "23505" in str(e):
                    logger.debug(f"Score race condition for profile {profile_id}, falling back to update")
                    score_record = self._score_repo.update_by_profile_id(
                        profile_id=profile_id,
                        data=score_update_data,
                    )
                else:
                    raise
        
        # Store contact information if available
        contact_record = None
        if contact.email or contact.website or contact.phone:
            contact_record = self._contact_repo.upsert(
                profile_id=profile_id,
                email=contact.email,
                email_source=contact.email_source,
                phone=contact.phone,
                website=contact.website,
                other_contacts=contact.other_contacts if contact.other_contacts else None
            )
            logger.debug(f"Stored contact info for profile: {profile_id}")
        
        return score_record, contact_record
    
    async def _update_profile_status(
        self,
        profile_id: str,
        status: ProfileStatus
    ) -> None:
        """
        Update the profile status.

        Args:
            profile_id: Profile UUID
            status: New status
        """
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self._profile_repo.update_status(profile_id, status)
                logger.info(f"Updated profile {profile_id} status to {status.value}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Failed to update profile {profile_id} status (attempt {attempt + 1}), retrying: {e}"
                    )
                else:
                    logger.error(
                        f"Failed to update profile {profile_id} status after {max_retries} attempts: {e}"
                    )
    
    # =========================================================================
    # Validation
    # =========================================================================
    
    async def validate_input(self, input_data: ScorerRequest) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input request data
            
        Returns:
            True if valid
            
        Raises:
            AgentError: If validation fails
        """
        if not input_data.profile_id:
            raise AgentError(
                message="profile_id is required",
                agent_name=self.agent_name,
                details={"field": "profile_id"}
            )
        
        if not input_data.job_id:
            raise AgentError(
                message="job_id is required",
                agent_name=self.agent_name,
                details={"field": "job_id"}
            )
        
        return True


# =============================================================================
# Factory Function
# =============================================================================

def get_scorer_agent(
    llm_service: Optional[LLMService] = None,
    scoring_service: Optional[ScoringService] = None,
) -> ScorerAgent:
    """
    Factory function to create a Scorer Agent.
    
    Args:
        llm_service: Optional custom LLM service
        scoring_service: Optional custom scoring service
        
    Returns:
        ScorerAgent instance
    """
    return ScorerAgent(
        llm_service=llm_service,
        scoring_service=scoring_service,
    )
