"""
PartnerScout AI - Email Composer Agent Integration Tests (STORY-3.3.5)

Integration tests for the EmailComposerAgent that test:
- Agent through email generation API
- EmailService integration with agent
- Full compose flow with mocked LLM
- Prompt loading and variable substitution

Test Markers:
- @pytest.mark.integration: Integration tests
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.agents.email_composer import (
    EmailComposerAgent,
    EmailComposerRequest,
    get_email_composer_agent,
)
from app.core.config import settings
from app.models.email import EmailTone, GeneratedEmail


# =============================================================================
# Pytest Markers
# =============================================================================

pytestmark = pytest.mark.integration


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create test client for the full application."""
    return TestClient(app)


@pytest.fixture
def valid_user_id():
    """Generate a valid user ID."""
    return str(uuid4())


@pytest.fixture
def valid_token(valid_user_id):
    """Create a valid JWT token."""
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    payload = {
        "sub": valid_user_id,
        "email": "test@example.com",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "aud": "authenticated",
    }
    return jwt.encode(
        payload, settings.supabase.jwt_secret, algorithm="HS256"
    )


@pytest.fixture
def sample_profile_id():
    """Generate a sample profile ID."""
    return str(uuid4())


@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
    return str(uuid4())


@pytest.fixture
def mock_profile(sample_profile_id, sample_job_id):
    """Create a mock profile dictionary."""
    return {
        "id": sample_profile_id,
        "job_id": sample_job_id,
        "username": "fashion_influencer",
        "full_name": "Jane Smith",
        "bio": "Fashion enthusiast | Sustainable living advocate",
        "followers_count": 75000,
        "following_count": 500,
        "posts_count": 450,
        "engagement_rate": 3.5,
        "is_verified": False,
        "is_business_account": True,
        "instagram_url": "https://instagram.com/fashion_influencer",
        "external_url": "https://janesmith.com",
        "status": "scored",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_job(sample_job_id, valid_user_id):
    """Create a mock job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": valid_user_id,
        "brand_description": "Sustainable fashion brand focused on eco-friendly materials",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def mock_brand_dna():
    """Create mock brand DNA."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly"],
        "keywords": ["sustainable", "ethical"],
        "visual_themes": ["minimalist"],
    }


@pytest.fixture
def sample_llm_email_output():
    """Sample output from LLM for email composition."""
    return {
        "subject": "Partnership Opportunity: Sustainable Fashion x Jane",
        "body": (
            "Hi Jane,\n\nI've been following your content at @fashion_influencer "
            "and love what you're doing! Your focus on sustainable fashion aligns "
            "perfectly with our brand.\n\nWe'd love to explore a collaboration. "
            "Would you be interested in a quick chat?\n\nCheers,\nThe Team"
        ),
        "metadata": {"tone": "friendly", "personalization_elements": ["Referenced content"]},
    }


# =============================================================================
# Integration: Email API with Agent
# =============================================================================

class TestEmailAPIWithAgent:
    """Integration tests for email generation API with EmailComposerAgent."""

    def test_generate_email_endpoint_with_mocked_service(
        self,
        client,
        valid_token,
        sample_profile_id,
        sample_job_id,
        mock_profile,
        mock_job,
        sample_llm_email_output,
    ):
        """Test POST /api/email/generate returns valid email structure."""
        from app.api.routes.email import (
            get_profile_repository,
            get_job_repository,
            get_email_service,
        )

        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile

        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job

        # Mock email service to return pre-built email (simulating agent output)
        mock_email_service = Mock()
        mock_email_service.generate_email.return_value = GeneratedEmail(
            subject=sample_llm_email_output["subject"],
            body=sample_llm_email_output["body"],
            tone=EmailTone.FRIENDLY,
            profile_id=uuid4(),
            job_id=uuid4(),
        )

        app.dependency_overrides[get_profile_repository] = lambda: mock_profile_repo
        app.dependency_overrides[get_job_repository] = lambda: mock_job_repo
        app.dependency_overrides[get_email_service] = lambda: mock_email_service

        try:
            response = client.post(
                "/api/email/generate",
                json={
                    "profile_id": sample_profile_id,
                    "job_id": sample_job_id,
                    "tone": "friendly",
                },
                headers={"Authorization": f"Bearer {valid_token}"},
            )

            assert response.status_code == 200
            data = response.json()
            assert "email" in data
            assert "subject" in data["email"]
            assert "body" in data["email"]
            assert len(data["email"]["body"]) > 50
        finally:
            app.dependency_overrides.clear()


# =============================================================================
# Integration: Agent Through Service
# =============================================================================

class TestAgentThroughService:
    """Test EmailComposerAgent integration with EmailService."""

    def test_email_service_falls_back_when_agent_fails(
        self, mock_profile, mock_job, mock_brand_dna
    ):
        """Test EmailService falls back to templates when agent fails."""
        from app.services.email_service import EmailService
        from unittest.mock import Mock

        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile

        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job

        mock_brand_repo = Mock()
        mock_brand_repo.get_by_job_id_optional.return_value = mock_brand_dna

        service = EmailService(
            profile_repo=mock_profile_repo,
            job_repo=mock_job_repo,
            brand_repo=mock_brand_repo,
        )

        # Patch _try_ai_generation to return None (simulating failure)
        with patch.object(service, "_try_ai_generation", return_value=None):
            result = service.generate_email(
                profile_id=mock_profile["id"],
                job_id=mock_job["id"],
                use_ai=True,
            )

        # Should get template-based result
        assert isinstance(result, GeneratedEmail)
        assert result.subject
        assert result.body
        assert "Jane" in result.body or "fashion_influencer" in result.body

    def test_email_service_with_use_ai_false(
        self, mock_profile, mock_job, mock_brand_dna
    ):
        """Test EmailService uses templates when use_ai=False."""
        from app.services.email_service import EmailService
        from unittest.mock import Mock

        mock_profile_repo = Mock()
        mock_profile_repo.get_by_id.return_value = mock_profile

        mock_job_repo = Mock()
        mock_job_repo.get_by_id.return_value = mock_job

        mock_brand_repo = Mock()
        mock_brand_repo.get_by_job_id_optional.return_value = mock_brand_dna

        service = EmailService(
            profile_repo=mock_profile_repo,
            job_repo=mock_job_repo,
            brand_repo=mock_brand_repo,
        )

        result = service.generate_email(
            profile_id=mock_profile["id"],
            job_id=mock_job["id"],
            use_ai=False,
        )

        assert isinstance(result, GeneratedEmail)
        assert result.subject
        assert result.body


# =============================================================================
# Integration: Agent Prompts
# =============================================================================

class TestAgentPromptsIntegration:
    """Test agent prompt loading and variable substitution."""

    def test_email_composer_prompts_loaded(self):
        """Test that email composer prompts are loaded correctly."""
        from app.prompts.loader import load_prompts

        prompts = load_prompts("email_composer")
        assert "system" in prompts
        assert "user" in prompts
        assert len(prompts["system"]) > 50
        assert len(prompts["user"]) > 50

    def test_user_prompt_has_required_variables(self):
        """Test user prompt contains required variable placeholders."""
        from app.prompts.loader import load_prompt

        user_prompt = load_prompt("email_composer", "user")
        required_vars = [
            "brand_name", "brand_description", "username",
            "profile_url", "follower_count", "bio",
            "profile_summary", "score", "tone"
        ]
        for var in required_vars:
            assert "{" + var + "}" in user_prompt, f"Missing variable: {var}"

    def test_agent_loads_prompts_on_init(self):
        """Test agent loads prompts during initialization."""
        agent = EmailComposerAgent()
        assert agent.system_prompt is not None
        assert agent.user_prompt is not None


# =============================================================================
# Integration: Full Agent Flow
# =============================================================================

@pytest.mark.asyncio
class TestFullAgentFlow:
    """Test full agent flow with mocked LLM."""

    async def test_agent_compose_end_to_end(
        self, mock_profile, mock_job, mock_brand_dna, sample_llm_email_output
    ):
        """Test complete compose flow with mocked chain."""
        agent = EmailComposerAgent()

        with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = sample_llm_email_output

            result = await agent.compose(
                profile=mock_profile,
                brand_dna=mock_brand_dna,
                brand_description=mock_job["brand_description"],
                tone="friendly",
            )

            assert "subject" in result
            assert "body" in result
            assert len(result["body"]) > 50
            assert "metadata" in result

            # Verify invoke was called with correct variables
            call_args = mock_invoke.call_args[0][1]
            assert call_args["username"] == "fashion_influencer"
            assert call_args["tone"] == "friendly"

    async def test_agent_all_tones(
        self, mock_profile, mock_brand_dna
    ):
        """Test agent works with all supported tones."""
        agent = EmailComposerAgent()

        for tone in ["professional", "friendly", "casual"]:
            with patch.object(agent, "invoke_chain", new_callable=AsyncMock) as mock_invoke:
                mock_invoke.return_value = {
                    "subject": f"Test subject for {tone}",
                    "body": f"Test body for {tone} tone. " * 20,
                    "metadata": {"tone": tone},
                }

                result = await agent.compose(
                    profile=mock_profile,
                    brand_dna=mock_brand_dna,
                    brand_description="Test brand",
                    tone=tone,
                )

                assert result["subject"]
                assert len(result["body"]) > 50


# =============================================================================
# Integration: Module Exports
# =============================================================================

class TestModuleExports:
    """Test that EmailComposerAgent is properly exported."""

    def test_agents_module_exports_email_composer(self):
        """Test app.agents exports EmailComposerAgent."""
        from app.agents import EmailComposerAgent, get_email_composer_agent

        assert EmailComposerAgent is not None
        assert get_email_composer_agent is not None

    def test_agent_can_be_instantiated(self):
        """Test EmailComposerAgent can be instantiated."""
        from app.agents import EmailComposerAgent

        agent = EmailComposerAgent()
        assert agent is not None
        assert agent.agent_name == "email_composer"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
