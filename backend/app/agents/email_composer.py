"""
PartnerScout AI - Email Composer Agent (STORY-3.3.5)

AI agent that generates personalized outreach emails for partnership proposals.
Uses LLM to compose compelling, personalized emails tailored to each influencer
with support for multiple tones (professional, friendly, casual).

Subtasks completed:
- SUB-3.3.5.1.1: Create app/agents/email_composer.py
- SUB-3.3.5.1.2: Implement email generation with LLM
- SUB-3.3.5.1.3: Support multiple tones (professional, friendly, casual)
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.core.exceptions import AgentError
from app.services.llm_service import LLMService


# =============================================================================
# Logger Configuration
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Output Schema
# =============================================================================

class EmailComposerOutput(BaseModel):
    """Schema for LLM email composer output."""

    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata with tone, word_count, personalization_elements"
    )


# =============================================================================
# Request/Response Models
# =============================================================================

class EmailComposerRequest(BaseModel):
    """Request model for Email Composer Agent."""

    profile: Dict[str, Any] = Field(..., description="Profile data dictionary")
    brand_dna: Dict[str, Any] = Field(
        default_factory=dict,
        description="Brand DNA with hashtags, keywords, etc."
    )
    brand_description: str = Field(..., description="Brand description")
    tone: str = Field(
        default="friendly",
        description="Email tone: professional, friendly, or casual"
    )
    profile_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Partnership score (0-100) if available"
    )


class EmailComposerResponse(BaseModel):
    """Response model from Email Composer Agent."""

    subject: str = Field(..., description="Generated email subject")
    body: str = Field(..., description="Generated email body")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generation metadata"
    )


# =============================================================================
# Email Composer Agent
# =============================================================================

class EmailComposerAgent(BaseAgent[EmailComposerRequest, EmailComposerResponse]):
    """
    AI agent for composing personalized outreach emails.

    This agent:
    1. Takes profile data, brand DNA, and brand description
    2. Uses LLM with specialized prompts to generate personalized emails
    3. Supports professional, friendly, and casual tones
    4. Returns subject and body in structured format

    Example:
        ```python
        agent = EmailComposerAgent()
        result = await agent.compose(
            profile={"username": "jane", "bio": "...", ...},
            brand_dna={"hashtags": [...], "keywords": [...]},
            brand_description="Sustainable fashion brand",
            tone="friendly"
        )
        print(result["subject"], result["body"])
        ```
    """

    agent_name = "email_composer"

    # Valid tones
    VALID_TONES = {"professional", "friendly", "casual"}

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        **kwargs
    ):
        """
        Initialize the Email Composer Agent.

        Args:
            llm_service: LLM service for text generation (optional)
            **kwargs: Additional arguments passed to BaseAgent
        """
        super().__init__(llm_service=llm_service, **kwargs)
        logger.debug(f"Initialized {self.agent_name} agent")

    # =========================================================================
    # Main Compose Method (Primary API - SUB-3.3.5.1.2)
    # =========================================================================

    async def compose(
        self,
        profile: Dict[str, Any],
        brand_dna: Dict[str, Any],
        brand_description: str,
        tone: str = "friendly",
        profile_score: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Compose a personalized outreach email for an influencer.

        This is the primary interface matching the validation test signature.

        Args:
            profile: Profile data dictionary (username, bio, followers_count, etc.)
            brand_dna: Brand DNA with hashtags, keywords, themes
            brand_description: Description of the brand
            tone: Email tone - professional, friendly, or casual
            profile_score: Optional partnership score (0-100)

        Returns:
            Dict with keys: subject, body, metadata

        Raises:
            AgentError: If composition fails
        """
        request = EmailComposerRequest(
            profile=profile,
            brand_dna=brand_dna or {},
            brand_description=brand_description,
            tone=tone.lower(),
            profile_score=profile_score,
        )
        response = await self.run(request)
        return {
            "subject": response.subject,
            "body": response.body,
            "metadata": response.metadata,
        }

    # =========================================================================
    # BaseAgent run() Implementation
    # =========================================================================

    async def run(self, input_data: EmailComposerRequest) -> EmailComposerResponse:
        """
        Execute email composition.

        Args:
            input_data: EmailComposerRequest with profile, brand data, tone

        Returns:
            EmailComposerResponse with subject, body, metadata

        Raises:
            AgentError: If composition fails
        """
        start_time = time.time()
        self._start_metrics()

        profile = input_data.profile
        brand_dna = input_data.brand_dna
        brand_description = input_data.brand_description
        tone = input_data.tone.lower()
        profile_score = input_data.profile_score

        logger.info(
            f"Composing email for @{profile.get('username', 'unknown')} "
            f"(tone: {tone})"
        )

        try:
            # Validate tone
            if tone not in self.VALID_TONES:
                tone = "friendly"
                logger.warning(f"Invalid tone, defaulting to friendly")

            # Format inputs for prompt
            prompt_vars = self._build_prompt_variables(
                profile=profile,
                brand_dna=brand_dna,
                brand_description=brand_description,
                tone=tone,
                profile_score=profile_score,
            )

            # Build and invoke chain
            chain = self.build_json_chain(pydantic_schema=EmailComposerOutput)
            result = await self.invoke_chain(chain, prompt_vars)

            # Parse result
            if isinstance(result, dict):
                output = EmailComposerOutput(**result)
            else:
                output = result

            duration = time.time() - start_time
            self._complete_metrics(success=True)

            logger.info(
                f"Email composed for @{profile.get('username')} "
                f"in {duration:.2f}s (subject length: {len(output.subject)})"
            )

            return EmailComposerResponse(
                subject=output.subject,
                body=output.body,
                metadata=output.metadata or {},
            )

        except AgentError:
            raise
        except Exception as e:
            self._complete_metrics(success=False, error_message=str(e))
            logger.error(f"Email composition failed: {e}")
            raise AgentError(
                message=f"Email composition failed: {str(e)}",
                agent_name=self.agent_name,
                details={"error": str(e)},
            )

    # =========================================================================
    # Prompt Building (SUB-3.3.5.1.3)
    # =========================================================================

    def _build_prompt_variables(
        self,
        profile: Dict[str, Any],
        brand_dna: Dict[str, Any],
        brand_description: str,
        tone: str,
        profile_score: Optional[int],
    ) -> Dict[str, Any]:
        """
        Build variables for the user prompt template.

        The user prompt expects: brand_name, brand_description, username,
        profile_url, follower_count, bio, profile_summary, score, tone.
        """
        # Extract brand name (first few words of description or placeholder)
        brand_words = brand_description.split()[:3]
        brand_name = " ".join(brand_words) if brand_words else "Our Brand"

        # Profile details
        username = profile.get("username", "influencer")
        profile_url = profile.get("instagram_url") or profile.get("profile_url") or ""
        if not profile_url and username:
            profile_url = f"https://instagram.com/{username}"

        follower_count = profile.get("followers_count", 0) or 0
        bio = profile.get("bio", "") or ""

        # Build profile summary
        profile_summary = self._format_profile_summary(profile, brand_dna)

        # Score
        score = profile_score if profile_score is not None else 75

        return {
            "brand_name": brand_name,
            "brand_description": brand_description,
            "username": username,
            "profile_url": profile_url,
            "follower_count": f"{follower_count:,}",
            "bio": bio,
            "profile_summary": profile_summary,
            "score": score,
            "tone": tone,
        }

    def _format_profile_summary(
        self,
        profile: Dict[str, Any],
        brand_dna: Dict[str, Any],
    ) -> str:
        """Format profile data into a summary for the prompt."""
        parts = []

        # Basic info
        full_name = profile.get("full_name") or profile.get("username", "Influencer")
        parts.append(f"Full Name: {full_name}")

        # Stats
        followers = profile.get("followers_count", 0) or 0
        following = profile.get("following_count", 0) or 0
        posts = profile.get("posts_count", 0) or 0
        parts.append(f"Followers: {followers:,} | Following: {following:,} | Posts: {posts:,}")

        # Engagement
        engagement = profile.get("engagement_rate")
        if engagement:
            parts.append(f"Engagement Rate: {engagement:.2f}%")

        # Account type
        if profile.get("is_verified"):
            parts.append("Verified Account")
        if profile.get("is_business_account"):
            parts.append("Business Account")

        # Bio
        bio = profile.get("bio", "") or ""
        if bio:
            parts.append(f"Bio: {bio[:300]}")

        # External URL
        url = profile.get("external_url")
        if url:
            parts.append(f"Website: {url}")

        # Business category
        category = profile.get("business_category")
        if category:
            parts.append(f"Category: {category}")

        return "\n".join(parts)


# =============================================================================
# Factory Function
# =============================================================================

def get_email_composer_agent(
    llm_service: Optional[LLMService] = None,
) -> EmailComposerAgent:
    """
    Factory function to create an Email Composer Agent.

    Args:
        llm_service: Optional custom LLM service

    Returns:
        EmailComposerAgent instance
    """
    return EmailComposerAgent(llm_service=llm_service)
