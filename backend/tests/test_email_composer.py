"""
PartnerScout AI - Email Composer Agent Unit Tests (STORY-3.3.5)

Unit tests for the EmailComposerAgent covering:
- Agent initialization
- compose() method with all tones (professional, friendly, casual)
- Prompt variable building
- LLM output parsing
- Error handling

Test Markers:
- @pytest.mark.unit: Fast unit tests with mocked dependencies
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from app.agents.email_composer import (
    EmailComposerAgent,
    EmailComposerRequest,
    EmailComposerResponse,
    EmailComposerOutput,
    get_email_composer_agent,
)
from app.core.exceptions import AgentError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_profile():
    """Create a sample profile dictionary."""
    return {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "username": "eco_influencer",
        "full_name": "Jane Smith",
        "bio": "Sustainable living advocate | Fashion enthusiast",
        "followers_count": 75000,
        "following_count": 500,
        "posts_count": 850,
        "engagement_rate": 3.5,
        "is_verified": False,
        "is_business_account": True,
        "instagram_url": "https://instagram.com/eco_influencer",
        "external_url": "https://linktr.ee/ecoinfluencer",
    }


@pytest.fixture
def sample_brand_dna():
    """Create sample brand DNA dictionary."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly"],
        "keywords": ["sustainable", "ethical", "eco-friendly"],
        "visual_themes": ["minimalist", "natural"],
        "content_pillars": ["sustainability", "fashion"],
    }


@pytest.fixture
def sample_llm_output():
    """Create sample LLM email output."""
    return {
        "subject": "Partnership Opportunity: Sustainable Fashion x Jane",
        "body": (
            "Hi Jane,\n\n"
            "I've been following your content at @eco_influencer and love "
            "what you're doing! Your focus on sustainable living and fashion "
            "aligns perfectly with our brand values.\n\n"
            "We're a sustainable fashion brand and would love to explore "
            "a collaboration. Would you be interested in a quick chat?\n\n"
            "Best regards,\nThe Team"
        ),
        "metadata": {
            "tone": "friendly",
            "word_count": 75,
            "personalization_elements": ["Referenced username", "Mentioned content"],
        },
    }


# =============================================================================
# Validation Test (from STORY-3.3.5 document)
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_email_composer_compose_returns_subject_and_body(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """
    Validation test from STORY-3.3.5:
    result = await agent.compose(profile, brand_dna, brand_description, "friendly")
    assert "subject" in result
    assert "body" in result
    assert len(result["body"]) > 50
    """
    agent = EmailComposerAgent()

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = sample_llm_output

        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Sustainable fashion brand focused on eco-friendly materials",
            tone="friendly",
        )

        assert "subject" in result
        assert "body" in result
        assert len(result["body"]) > 50
        assert result["subject"] == sample_llm_output["subject"]
        mock_invoke.assert_called_once()


# =============================================================================
# EmailComposerOutput Tests
# =============================================================================

@pytest.mark.unit
class TestEmailComposerOutput:
    """Tests for EmailComposerOutput model."""

    def test_parses_llm_output(self, sample_llm_output):
        """Test parsing LLM output into EmailComposerOutput."""
        output = EmailComposerOutput(**sample_llm_output)

        assert output.subject == sample_llm_output["subject"]
        assert output.body == sample_llm_output["body"]
        assert output.metadata["tone"] == "friendly"
        assert "personalization_elements" in output.metadata

    def test_optional_metadata(self):
        """Test that metadata is optional."""
        output = EmailComposerOutput(
            subject="Test Subject",
            body="Test body content",
        )
        assert output.metadata is None or output.metadata == {}


# =============================================================================
# EmailComposerRequest/Response Tests
# =============================================================================

@pytest.mark.unit
class TestEmailComposerModels:
    """Tests for EmailComposerRequest and EmailComposerResponse."""

    def test_request_with_minimal_data(self, sample_profile):
        """Test EmailComposerRequest with minimal required data."""
        request = EmailComposerRequest(
            profile=sample_profile,
            brand_dna={},
            brand_description="Test brand",
        )
        assert request.tone == "friendly"
        assert request.profile_score is None

    def test_request_with_full_data(
        self, sample_profile, sample_brand_dna
    ):
        """Test EmailComposerRequest with all fields."""
        request = EmailComposerRequest(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Sustainable fashion",
            tone="professional",
            profile_score=85,
        )
        assert request.tone == "professional"
        assert request.profile_score == 85

    def test_response_structure(self, sample_llm_output):
        """Test EmailComposerResponse structure."""
        response = EmailComposerResponse(
            subject=sample_llm_output["subject"],
            body=sample_llm_output["body"],
            metadata=sample_llm_output["metadata"],
        )
        assert response.subject
        assert response.body
        assert "metadata" in EmailComposerResponse.model_fields


# =============================================================================
# Compose Method Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_friendly_tone(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """Test compose with friendly tone."""
    agent = EmailComposerAgent()

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = sample_llm_output

        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Eco fashion brand",
            tone="friendly",
        )

        assert result["subject"]
        assert result["body"]
        assert len(result["body"]) > 50
        call_args = mock_invoke.call_args[0][1]
        assert call_args["tone"] == "friendly"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_professional_tone(
    sample_profile, sample_brand_dna
):
    """Test compose with professional tone."""
    agent = EmailComposerAgent()
    llm_output = {
        "subject": "Partnership Inquiry: Sustainable Fashion Collaboration",
        "body": "Dear Jane,\n\nWe are reaching out regarding a potential partnership opportunity...",
        "metadata": {"tone": "professional"},
    }

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = llm_output

        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Sustainable fashion",
            tone="professional",
        )

        assert "subject" in result
        assert "body" in result
        call_args = mock_invoke.call_args[0][1]
        assert call_args["tone"] == "professional"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_casual_tone(sample_profile, sample_brand_dna):
    """Test compose with casual tone."""
    agent = EmailComposerAgent()
    llm_output = {
        "subject": "Hey Jane! Quick collab idea",
        "body": "Hey Jane!\n\nStumbled across your profile and had to reach out...",
        "metadata": {"tone": "casual"},
    }

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = llm_output

        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Cool fashion brand",
            tone="casual",
        )

        assert "subject" in result
        assert "body" in result
        call_args = mock_invoke.call_args[0][1]
        assert call_args["tone"] == "casual"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_invalid_tone_defaults_to_friendly(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """Test that invalid tone defaults to friendly."""
    agent = EmailComposerAgent()

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = sample_llm_output

        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Test brand",
            tone="invalid_tone",
        )

        call_args = mock_invoke.call_args[0][1]
        assert call_args["tone"] == "friendly"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_with_profile_score(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """Test compose with profile score."""
    agent = EmailComposerAgent()

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = sample_llm_output

        await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Test brand",
            tone="friendly",
            profile_score=85,
        )

        call_args = mock_invoke.call_args[0][1]
        assert call_args["score"] == 85


@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_handles_agent_error(
    sample_profile, sample_brand_dna
):
    """Test compose raises AgentError on failure."""
    agent = EmailComposerAgent()

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.side_effect = AgentError(
            message="LLM failed",
            agent_name="email_composer",
        )

        with pytest.raises(AgentError) as exc_info:
            await agent.compose(
                profile=sample_profile,
                brand_dna=sample_brand_dna,
                brand_description="Test brand",
                tone="friendly",
            )

        assert exc_info.value.details.get("agent") == "email_composer"


# =============================================================================
# Prompt Building Tests
# =============================================================================

@pytest.mark.unit
class TestPromptBuilding:
    """Tests for _build_prompt_variables and _format_profile_summary."""

    def test_build_prompt_variables_includes_all_required(
        self, sample_profile, sample_brand_dna
    ):
        """Test that prompt variables include all required keys."""
        agent = EmailComposerAgent()
        request = EmailComposerRequest(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Sustainable fashion brand",
            tone="friendly",
        )

        # Access the protected method for testing
        vars = agent._build_prompt_variables(
            profile=request.profile,
            brand_dna=request.brand_dna,
            brand_description=request.brand_description,
            tone=request.tone,
            profile_score=85,
        )

        required_keys = [
            "brand_name", "brand_description", "username", "profile_url",
            "follower_count", "bio", "profile_summary", "score", "tone"
        ]
        for key in required_keys:
            assert key in vars, f"Missing required key: {key}"

        assert vars["username"] == "eco_influencer"
        assert vars["score"] == 85
        assert vars["tone"] == "friendly"

    def test_format_profile_summary_includes_key_data(
        self, sample_profile, sample_brand_dna
    ):
        """Test profile summary includes key profile data."""
        agent = EmailComposerAgent()
        summary = agent._format_profile_summary(
            sample_profile, sample_brand_dna
        )

        assert "Jane Smith" in summary
        assert "75,000" in summary or "75000" in summary
        assert "Sustainable" in summary or "Fashion" in summary


# =============================================================================
# Run Method Tests
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_run_returns_response(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """Test run() returns EmailComposerResponse."""
    agent = EmailComposerAgent()
    request = EmailComposerRequest(
        profile=sample_profile,
        brand_dna=sample_brand_dna,
        brand_description="Test brand",
        tone="friendly",
    )

    with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = sample_llm_output

        response = await agent.run(request)

        assert isinstance(response, EmailComposerResponse)
        assert response.subject == sample_llm_output["subject"]
        assert response.body == sample_llm_output["body"]


# =============================================================================
# Factory and Initialization Tests
# =============================================================================

@pytest.mark.unit
class TestEmailComposerAgentInit:
    """Tests for agent initialization."""

    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = EmailComposerAgent()
        assert agent.agent_name == "email_composer"
        assert agent.is_enabled

    def test_get_email_composer_agent_factory(self):
        """Test factory function returns agent instance."""
        agent = get_email_composer_agent()
        assert isinstance(agent, EmailComposerAgent)


# =============================================================================
# Integration with Minimal Mock (Chain Level)
# =============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_compose_full_flow_with_mocked_chain(
    sample_profile, sample_brand_dna, sample_llm_output
):
    """
    Test full compose flow with mocked chain.
    Patches build_json_chain to return a mock that returns sample output.
    """
    import json

    agent = EmailComposerAgent()

    async def mock_ainvoke(input_data):
        return sample_llm_output

    mock_chain = AsyncMock()
    mock_chain.ainvoke = mock_ainvoke

    with patch.object(agent, "build_json_chain", return_value=mock_chain):
        result = await agent.compose(
            profile=sample_profile,
            brand_dna=sample_brand_dna,
            brand_description="Sustainable fashion brand",
            tone="friendly",
        )

    assert "subject" in result
    assert "body" in result
    assert len(result["body"]) > 50
    assert result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
