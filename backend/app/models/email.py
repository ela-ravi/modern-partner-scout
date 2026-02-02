"""
PartnerScout AI - Email Models

Pydantic models for email generation and sending.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import Defaults


# =============================================================================
# Email Tone Enum
# =============================================================================

class EmailTone(str, Enum):
    """Available email tones for outreach."""
    
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"


# =============================================================================
# Email Generation Models
# =============================================================================

class GenerateEmailRequest(BaseModel):
    """Request model for generating an outreach email."""
    
    profile_id: UUID = Field(..., description="ID of the target profile")
    job_id: UUID = Field(..., description="ID of the discovery job")
    tone: EmailTone = Field(
        default=EmailTone.FRIENDLY,
        description="Tone of the email"
    )
    include_profile_compliment: bool = Field(
        default=True,
        description="Include a specific compliment about the profile"
    )
    custom_context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional context to include in the email"
    )
    sender_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name of the sender for signature"
    )
    sender_company: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Company name for signature"
    )


class GeneratedEmail(BaseModel):
    """Generated email content."""
    
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    html_body: Optional[str] = Field(
        default=None,
        description="HTML formatted email body"
    )
    
    # Metadata
    tone: EmailTone
    profile_id: UUID
    job_id: UUID
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Personalization details
    personalization_points: List[str] = Field(
        default_factory=list,
        description="List of personalization elements used"
    )


class GenerateEmailResponse(BaseModel):
    """Response model for email generation."""
    
    email: GeneratedEmail
    profile_name: Optional[str] = None
    profile_username: str
    generation_duration_seconds: Optional[float] = None
    tokens_used: Optional[int] = None


class RegenerateEmailRequest(BaseModel):
    """Request model for regenerating an email with adjustments."""
    
    profile_id: UUID
    job_id: UUID
    previous_email: GeneratedEmail
    feedback: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Feedback on what to change"
    )
    tone: Optional[EmailTone] = None


# =============================================================================
# Email Sending Models
# =============================================================================

class SendEmailRequest(BaseModel):
    """Request model for sending an email."""
    
    profile_id: UUID = Field(..., description="ID of the target profile")
    job_id: UUID = Field(..., description="ID of the discovery job")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=10)
    html_body: Optional[str] = None
    
    # Sender information
    from_name: Optional[str] = Field(default=None, max_length=100)
    from_email: Optional[EmailStr] = None
    reply_to: Optional[EmailStr] = None
    
    # Email options
    track_opens: bool = True
    track_clicks: bool = True
    schedule_for: Optional[datetime] = None


class SendEmailResponse(BaseModel):
    """Response model for sending an email."""
    
    success: bool
    message_id: Optional[str] = None
    profile_id: UUID
    recipient_email: str
    sent_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    error: Optional[str] = None


class BatchSendEmailRequest(BaseModel):
    """Request model for sending emails to multiple profiles."""
    
    job_id: UUID
    emails: List[SendEmailRequest] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of emails to send (max 50)"
    )
    delay_between_ms: int = Field(
        default=1000,
        ge=0,
        le=60000,
        description="Delay between sends in milliseconds"
    )


class BatchSendEmailResponse(BaseModel):
    """Response model for batch email sending."""
    
    total_requested: int = 0
    total_sent: int = 0
    total_failed: int = 0
    results: List[SendEmailResponse] = Field(default_factory=list)


# =============================================================================
# Email Template Models
# =============================================================================

class EmailTemplate(BaseModel):
    """Email template model."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    subject_template: str
    body_template: str
    tone: EmailTone = EmailTone.FRIENDLY
    variables: List[str] = Field(
        default_factory=list,
        description="Template variables (e.g., {{profile_name}})"
    )
    created_at: datetime
    updated_at: datetime


class CreateEmailTemplateRequest(BaseModel):
    """Request model for creating an email template."""
    
    name: str = Field(..., min_length=1, max_length=100)
    subject_template: str = Field(..., min_length=1, max_length=200)
    body_template: str = Field(..., min_length=10)
    tone: EmailTone = EmailTone.FRIENDLY


class EmailHistory(BaseModel):
    """Email history record."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    profile_id: UUID
    job_id: UUID
    subject: str
    body: str
    recipient_email: str
    status: str = Field(
        ...,
        description="sent, delivered, opened, clicked, bounced, failed"
    )
    sent_at: datetime
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
