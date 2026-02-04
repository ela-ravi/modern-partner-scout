"""
PartnerScout AI - Email Service

Service layer for email generation and sending.
Implements AI-powered outreach email generation and mock sending functionality.

STORY-2.3.2: Implement Scoring & Email Services
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.config import settings
from app.core.exceptions import BusinessError, NotFoundError, ProfileNotFoundError
from app.models.email import (
    EmailTone,
    GeneratedEmail,
    GenerateEmailRequest,
    SendEmailRequest,
    SendEmailResponse,
)
from app.repositories import (
    ProfileRepository,
    ContactRepository,
    BrandRepository,
    JobRepository,
)


logger = logging.getLogger(__name__)


class EmailService:
    """
    Service class for generating and sending outreach emails.
    
    Implements:
    - AI-powered email generation with multiple tones
    - Personalization based on profile and brand data
    - Mock email sending for development/testing
    """
    
    # Email tone templates
    TONE_STYLES = {
        EmailTone.PROFESSIONAL: {
            "greeting": "Dear",
            "closing": "Best regards",
            "style": "formal and business-oriented",
        },
        EmailTone.FRIENDLY: {
            "greeting": "Hi",
            "closing": "Cheers",
            "style": "warm and approachable",
        },
        EmailTone.CASUAL: {
            "greeting": "Hey",
            "closing": "Talk soon",
            "style": "relaxed and conversational",
        },
    }
    
    def __init__(
        self,
        profile_repo: Optional[ProfileRepository] = None,
        contact_repo: Optional[ContactRepository] = None,
        brand_repo: Optional[BrandRepository] = None,
        job_repo: Optional[JobRepository] = None,
    ):
        """
        Initialize the EmailService.
        
        Args:
            profile_repo: Optional ProfileRepository instance
            contact_repo: Optional ContactRepository instance
            brand_repo: Optional BrandRepository instance
            job_repo: Optional JobRepository instance
        """
        self.profile_repo = profile_repo or ProfileRepository()
        self.contact_repo = contact_repo or ContactRepository()
        self.brand_repo = brand_repo or BrandRepository()
        self.job_repo = job_repo or JobRepository()
        
        # Mock email storage for testing
        self._sent_emails: List[Dict[str, Any]] = []
    
    # =========================================================================
    # Email Generation
    # =========================================================================
    
    def generate_email(
        self,
        profile_id: str,
        job_id: str,
        tone: EmailTone = EmailTone.FRIENDLY,
        include_profile_compliment: bool = True,
        custom_context: Optional[str] = None,
        sender_name: Optional[str] = None,
        sender_company: Optional[str] = None,
        use_ai: bool = True,
    ) -> GeneratedEmail:
        """
        Generate a personalized outreach email for a profile.

        When use_ai=True (default), uses EmailComposerAgent for LLM-based generation.
        Falls back to template-based generation if AI fails or use_ai=False.

        Args:
            profile_id: Target profile UUID
            job_id: Discovery job UUID
            tone: Email tone (professional, friendly, casual)
            include_profile_compliment: Include a compliment about the profile
            custom_context: Additional context to include
            sender_name: Sender's name for signature
            sender_company: Company name for signature
            use_ai: Use AI agent for generation (default True)

        Returns:
            GeneratedEmail with subject and body
            
        Raises:
            ProfileNotFoundError: If profile is not found
            BusinessError: If email generation fails
        """
        # Get profile data
        try:
            profile = self.profile_repo.get_by_id(profile_id)
        except NotFoundError:
            raise ProfileNotFoundError(profile_id)
        
        # Get job data for brand context
        try:
            job = self.job_repo.get_by_id(job_id)
        except NotFoundError:
            raise BusinessError(
                message=f"Job not found: {job_id}",
                details={"job_id": job_id}
            )
        
        # Get brand DNA if available
        brand_dna = None
        try:
            brand_dna = self.brand_repo.get_by_job_id_optional(job_id)
        except Exception:
            pass

        # Try AI generation first if enabled
        if use_ai:
            ai_email = self._try_ai_generation(
                profile=profile,
                job=job,
                brand_dna=brand_dna,
                tone=tone,
                custom_context=custom_context,
                sender_name=sender_name,
                sender_company=sender_company,
            )
            if ai_email:
                return ai_email

        # Fall back to template-based generation
        return self._generate_email_content(
            profile=profile,
            job=job,
            brand_dna=brand_dna,
            tone=tone,
            include_profile_compliment=include_profile_compliment,
            custom_context=custom_context,
            sender_name=sender_name,
            sender_company=sender_company,
        )
    
    def _try_ai_generation(
        self,
        profile: Dict[str, Any],
        job: Dict[str, Any],
        brand_dna: Optional[Dict[str, Any]],
        tone: EmailTone,
        custom_context: Optional[str],
        sender_name: Optional[str],
        sender_company: Optional[str],
    ) -> Optional[GeneratedEmail]:
        """
        Try to generate email using EmailComposerAgent.

        Returns GeneratedEmail if successful, None to fall back to templates.
        """
        try:
            from app.agents.email_composer import EmailComposerAgent

            agent = EmailComposerAgent()
            result = asyncio.run(agent.compose(
                profile=profile,
                brand_dna=brand_dna or {},
                brand_description=job.get("brand_description", "our brand"),
                tone=tone.value,
                profile_score=None,  # Could fetch from profile_scores if needed
            ))

            body = result["body"]

            # Append custom context if provided
            if custom_context:
                body = body.rstrip() + f"\n\n{custom_context}"

            return GeneratedEmail(
                subject=result["subject"],
                body=body,
                html_body=self._text_to_html(body),
                tone=tone,
                profile_id=UUID(profile["id"]),
                job_id=UUID(job["id"]),
                personalization_points=result.get("metadata", {}).get(
                    "personalization_elements", []
                ) or ["AI-generated"],
            )
        except Exception as e:
            logger.warning(f"AI email generation failed, using templates: {e}")
            return None

    def _generate_email_content(
        self,
        profile: Dict[str, Any],
        job: Dict[str, Any],
        brand_dna: Optional[Dict[str, Any]],
        tone: EmailTone,
        include_profile_compliment: bool,
        custom_context: Optional[str],
        sender_name: Optional[str],
        sender_company: Optional[str],
    ) -> GeneratedEmail:
        """
        Generate email content based on profile and brand data.
        
        This is a template-based implementation. In production, this would
        call an LLM for more sophisticated generation.
        
        Args:
            profile: Profile data
            job: Job data
            brand_dna: Optional brand DNA data
            tone: Email tone
            include_profile_compliment: Whether to include compliment
            custom_context: Additional context
            sender_name: Sender name
            sender_company: Company name
            
        Returns:
            GeneratedEmail instance
        """
        tone_style = self.TONE_STYLES[tone]
        
        # Extract profile details
        username = profile.get("username", "there")
        full_name = profile.get("full_name") or username
        first_name = full_name.split()[0] if full_name else username
        followers_count = profile.get("followers_count", 0)
        bio = profile.get("bio", "")
        
        # Extract brand/job details
        brand_description = job.get("brand_description", "our brand")
        
        # Generate personalization points
        personalization_points = []
        
        # Build subject line
        subject = self._generate_subject(
            first_name=first_name,
            brand_description=brand_description,
            tone=tone,
        )
        
        # Build greeting
        greeting = f"{tone_style['greeting']} {first_name},"
        
        # Build opening paragraph
        opening = self._generate_opening(
            tone=tone,
            brand_description=brand_description,
            username=username,
        )
        personalization_points.append(f"Referenced @{username}")
        
        # Build compliment if requested
        compliment = ""
        if include_profile_compliment:
            compliment = self._generate_compliment(
                profile=profile,
                brand_dna=brand_dna,
                tone=tone,
            )
            if compliment:
                personalization_points.append("Included profile-specific compliment")
        
        # Build value proposition
        value_prop = self._generate_value_proposition(
            tone=tone,
            brand_description=brand_description,
            followers_count=followers_count,
        )
        
        # Add custom context if provided
        custom_section = ""
        if custom_context:
            custom_section = f"\n{custom_context}\n"
            personalization_points.append("Included custom context")
        
        # Build call to action
        cta = self._generate_call_to_action(tone=tone)
        
        # Build closing
        closing = self._generate_closing(
            tone=tone,
            sender_name=sender_name,
            sender_company=sender_company,
        )
        
        # Combine all parts
        body_parts = [
            greeting,
            "",
            opening,
        ]
        
        if compliment:
            body_parts.extend(["", compliment])
        
        body_parts.extend([
            "",
            value_prop,
        ])
        
        if custom_section:
            body_parts.append(custom_section)
        
        body_parts.extend([
            "",
            cta,
            "",
            closing,
        ])
        
        body = "\n".join(body_parts)
        
        # Generate HTML version
        html_body = self._text_to_html(body)
        
        return GeneratedEmail(
            subject=subject,
            body=body,
            html_body=html_body,
            tone=tone,
            profile_id=UUID(profile["id"]),
            job_id=UUID(job["id"]),
            personalization_points=personalization_points,
        )
    
    def _generate_subject(
        self,
        first_name: str,
        brand_description: str,
        tone: EmailTone,
    ) -> str:
        """Generate email subject line."""
        # Extract key brand terms
        brand_words = brand_description.split()[:3]
        brand_short = " ".join(brand_words)
        
        if tone == EmailTone.PROFESSIONAL:
            return f"Partnership Opportunity: {brand_short} x {first_name}"
        elif tone == EmailTone.FRIENDLY:
            return f"Hey {first_name}! Let's collaborate?"
        else:  # CASUAL
            return f"Quick collab idea for you, {first_name}"
    
    def _generate_opening(
        self,
        tone: EmailTone,
        brand_description: str,
        username: str,
    ) -> str:
        """Generate opening paragraph."""
        if tone == EmailTone.PROFESSIONAL:
            return (
                f"I hope this email finds you well. I'm reaching out on behalf of "
                f"{brand_description}. We've been following your work at @{username} "
                f"and believe there could be a great opportunity for collaboration."
            )
        elif tone == EmailTone.FRIENDLY:
            return (
                f"I've been following your content at @{username} and love what you're doing! "
                f"I work with {brand_description} and couldn't help but reach out."
            )
        else:  # CASUAL
            return (
                f"Just stumbled across your profile @{username} and had to reach out. "
                f"I'm working with {brand_description} and think you'd be a perfect fit!"
            )
    
    def _generate_compliment(
        self,
        profile: Dict[str, Any],
        brand_dna: Optional[Dict[str, Any]],
        tone: EmailTone,
    ) -> str:
        """Generate a profile-specific compliment."""
        followers_count = profile.get("followers_count", 0)
        bio = profile.get("bio", "")
        engagement_rate = profile.get("engagement_rate")
        
        compliments = []
        
        # Engagement-based compliment
        if engagement_rate and float(engagement_rate) > 3.0:
            compliments.append(
                "Your engagement rate is impressive – it's clear you've built a really connected community."
            )
        
        # Follower-based compliment
        if followers_count > 50000:
            compliments.append(
                "The community you've built is incredible."
            )
        
        # Bio-based compliment
        if bio and len(bio) > 20:
            compliments.append(
                "Your profile really stands out with its unique voice and aesthetic."
            )
        
        if not compliments:
            return ""
        
        # Format based on tone
        compliment = compliments[0]
        
        if tone == EmailTone.PROFESSIONAL:
            return f"We were particularly impressed by your content. {compliment}"
        elif tone == EmailTone.FRIENDLY:
            return f"I have to say, {compliment}"
        else:  # CASUAL
            return f"Honestly, {compliment}"
    
    def _generate_value_proposition(
        self,
        tone: EmailTone,
        brand_description: str,
        followers_count: int,
    ) -> str:
        """Generate value proposition paragraph."""
        if tone == EmailTone.PROFESSIONAL:
            return (
                f"We're looking to partner with content creators who share our values "
                f"and vision. Given your audience and content style, we believe a "
                f"collaboration could be mutually beneficial. We offer competitive "
                f"compensation and creative freedom."
            )
        elif tone == EmailTone.FRIENDLY:
            return (
                f"We're all about finding authentic partnerships, not just one-off posts. "
                f"We'd love to explore what a collaboration could look like – whether "
                f"that's sponsored content, product seeding, or something completely unique!"
            )
        else:  # CASUAL
            return (
                f"No strings attached – just wanted to see if you'd be interested in "
                f"checking out what we're building. If it resonates, maybe we can "
                f"figure something out together?"
            )
    
    def _generate_call_to_action(self, tone: EmailTone) -> str:
        """Generate call to action."""
        if tone == EmailTone.PROFESSIONAL:
            return (
                "Would you be available for a brief call this week to discuss potential "
                "collaboration opportunities? I'd be happy to work around your schedule."
            )
        elif tone == EmailTone.FRIENDLY:
            return (
                "Would love to hop on a quick call or chat to explore this further! "
                "No pressure at all – just let me know if you're interested."
            )
        else:  # CASUAL
            return "Let me know if you want to chat! Would love to hear your thoughts."
    
    def _generate_closing(
        self,
        tone: EmailTone,
        sender_name: Optional[str],
        sender_company: Optional[str],
    ) -> str:
        """Generate email closing."""
        tone_style = self.TONE_STYLES[tone]
        closing = tone_style["closing"]
        
        if sender_name and sender_company:
            return f"{closing},\n{sender_name}\n{sender_company}"
        elif sender_name:
            return f"{closing},\n{sender_name}"
        else:
            return f"{closing},\nThe Team"
    
    def _text_to_html(self, text: str) -> str:
        """Convert plain text to simple HTML."""
        # Escape HTML characters
        html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Convert line breaks to HTML
        html = html.replace("\n\n", "</p><p>")
        html = html.replace("\n", "<br>")
        
        # Wrap in paragraph tags
        html = f"<p>{html}</p>"
        
        # Clean up empty paragraphs
        html = html.replace("<p></p>", "")
        
        return html
    
    # =========================================================================
    # Email Sending (Mock Implementation)
    # =========================================================================
    
    def send_email_mock(
        self,
        profile_id: str,
        job_id: str,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_name: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> SendEmailResponse:
        """
        Mock implementation of email sending.
        
        In development/testing, this simulates sending an email and
        stores it for verification. In production, this would integrate
        with an email service like SendGrid, SES, etc.
        
        Args:
            profile_id: Target profile UUID
            job_id: Discovery job UUID
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            html_body: Optional HTML body
            from_name: Sender name
            from_email: Sender email
            
        Returns:
            SendEmailResponse with status
        """
        # Validate email format
        if not self._is_valid_email(recipient_email):
            return SendEmailResponse(
                success=False,
                profile_id=UUID(profile_id),
                recipient_email=recipient_email,
                error="Invalid email format",
            )
        
        # Generate a mock message ID
        message_id = f"mock_{uuid4().hex[:16]}"
        sent_at = datetime.now(timezone.utc)
        
        # Store the mock sent email
        email_record = {
            "message_id": message_id,
            "profile_id": profile_id,
            "job_id": job_id,
            "recipient_email": recipient_email,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "from_name": from_name or "PartnerScout",
            "from_email": from_email or "noreply@partnerscout.ai",
            "sent_at": sent_at.isoformat(),
            "status": "sent",
        }
        
        self._sent_emails.append(email_record)
        
        logger.info(
            f"[MOCK] Sent email to {recipient_email} for profile {profile_id}"
        )
        
        return SendEmailResponse(
            success=True,
            message_id=message_id,
            profile_id=UUID(profile_id),
            recipient_email=recipient_email,
            sent_at=sent_at,
        )
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    # =========================================================================
    # Email History (Mock)
    # =========================================================================
    
    def get_sent_emails(
        self,
        profile_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get mock sent emails (for testing).
        
        Args:
            profile_id: Optional filter by profile
            job_id: Optional filter by job
            
        Returns:
            List of sent email records
        """
        emails = self._sent_emails
        
        if profile_id:
            emails = [e for e in emails if e["profile_id"] == profile_id]
        
        if job_id:
            emails = [e for e in emails if e["job_id"] == job_id]
        
        return emails
    
    def clear_sent_emails(self) -> None:
        """Clear mock sent emails (for testing)."""
        self._sent_emails = []
    
    # =========================================================================
    # Regeneration
    # =========================================================================
    
    def regenerate_email(
        self,
        profile_id: str,
        job_id: str,
        previous_subject: str,
        feedback: str,
        tone: Optional[EmailTone] = None,
    ) -> GeneratedEmail:
        """
        Regenerate an email with feedback.
        
        This is a simplified implementation. In production, this would
        pass the previous email and feedback to an LLM for improvement.
        
        Args:
            profile_id: Profile UUID
            job_id: Job UUID
            previous_subject: Previous email subject
            feedback: User feedback on what to change
            tone: Optional new tone
            
        Returns:
            Regenerated email
        """
        # For now, just regenerate with a different tone if specified
        return self.generate_email(
            profile_id=profile_id,
            job_id=job_id,
            tone=tone or EmailTone.FRIENDLY,
            include_profile_compliment=True,
            custom_context=f"Note: {feedback}",
        )
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_available_tones(self) -> List[Dict[str, str]]:
        """
        Get list of available email tones.
        
        Returns:
            List of tone options with descriptions
        """
        return [
            {
                "value": EmailTone.PROFESSIONAL.value,
                "label": "Professional",
                "description": "Formal and business-oriented tone",
            },
            {
                "value": EmailTone.FRIENDLY.value,
                "label": "Friendly",
                "description": "Warm and approachable tone",
            },
            {
                "value": EmailTone.CASUAL.value,
                "label": "Casual",
                "description": "Relaxed and conversational tone",
            },
        ]
    
    def estimate_email_effectiveness(
        self,
        profile: Dict[str, Any],
        email: GeneratedEmail,
    ) -> Dict[str, Any]:
        """
        Estimate the potential effectiveness of an email.
        
        This is a simple heuristic-based estimation.
        
        Args:
            profile: Target profile data
            email: Generated email
            
        Returns:
            Effectiveness estimate
        """
        score = 50  # Base score
        factors = []
        
        # Check if email has personalization
        if email.personalization_points:
            score += len(email.personalization_points) * 10
            factors.append("Personalized content")
        
        # Check subject line length
        if 30 <= len(email.subject) <= 60:
            score += 10
            factors.append("Optimal subject length")
        
        # Check if profile has business indicators
        if profile.get("is_business_account"):
            score += 10
            factors.append("Business account - more likely to engage")
        
        # Check email length
        body_words = len(email.body.split())
        if 100 <= body_words <= 200:
            score += 10
            factors.append("Good email length")
        
        # Cap at 100
        score = min(100, score)
        
        return {
            "effectiveness_score": score,
            "factors": factors,
            "recommendation": "Good" if score >= 70 else "Consider improving",
        }


# =============================================================================
# Factory Function
# =============================================================================

def get_email_service() -> EmailService:
    """
    Get an EmailService instance.
    
    This is the recommended way to get an EmailService instance,
    as it can be used as a FastAPI dependency.
    
    Returns:
        EmailService instance
    """
    return EmailService()
