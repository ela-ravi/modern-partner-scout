"""
PartnerScout AI - Scorer Agent Unit Tests (STORY-3.3.4)

Comprehensive unit tests for the ScorerAgent covering:
- Agent initialization
- Fake profile detection
- Contact extraction
- LLM scoring analysis
- Weighted score calculation
- Database storage
- Error handling

Test Markers:
- @pytest.mark.unit: Fast unit tests with mocked dependencies
- @pytest.mark.asyncio: Async test functions
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from app.agents.scorer import (
    ScorerAgent,
    ScoringAnalysisOutput,
    ExtractedContact,
    get_scorer_agent,
)
from app.core.exceptions import AgentError, JobNotFoundError, ProfileNotFoundError
from app.models.agent import ScorerRequest, ScorerResponse, ScoreDimension


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
def sample_job(sample_job_id):
    """Create a sample job dictionary."""
    return {
        "id": sample_job_id,
        "user_id": str(uuid4()),
        "brand_description": "A sustainable fashion brand focused on eco-friendly materials and ethical production",
        "reference_profiles": [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": "scoring",
    }


@pytest.fixture
def sample_profile(sample_profile_id, sample_job_id):
    """Create a sample profile dictionary."""
    return {
        "id": sample_profile_id,
        "job_id": sample_job_id,
        "username": "eco_influencer",
        "full_name": "Eco Influencer",
        "bio": "Sustainable living advocate 🌱 | contact@ecoinfluencer.com | linktr.ee/ecoinfluencer",
        "followers_count": 75000,
        "following_count": 500,
        "posts_count": 850,
        "engagement_rate": 3.5,
        "is_verified": False,
        "is_business_account": True,
        "external_url": "https://linktr.ee/ecoinfluencer",
        "business_email": "business@ecoinfluencer.com",
        "business_category": "Fashion",
        "instagram_url": "https://instagram.com/eco_influencer",
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_fake_profile(sample_profile_id, sample_job_id):
    """Create a sample fake profile dictionary."""
    return {
        "id": sample_profile_id,
        "job_id": sample_job_id,
        "username": "fake_influencer",
        "full_name": "Fake Account",
        "bio": "",
        "followers_count": 100000,
        "following_count": 8000,  # High following ratio
        "posts_count": 5,  # Very few posts
        "engagement_rate": 0.1,  # Very low engagement
        "is_verified": False,
        "is_business_account": False,
        "instagram_url": "https://instagram.com/fake_influencer",
        "status": "new",
    }


@pytest.fixture
def sample_brand_dna():
    """Create sample brand DNA dictionary."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly", "#ethicalfashion", "#slowfashion"],
        "keywords": ["sustainable", "ethical", "eco-friendly", "fashion"],
        "visual_themes": ["minimalist", "earth tones", "natural textures"],
        "content_pillars": ["sustainability", "fashion", "lifestyle"],
        "target_audience_description": "Environmentally conscious millennials",
    }


@pytest.fixture
def sample_analysis_output():
    """Create sample LLM analysis output."""
    return {
        "visual_aesthetic_match": 75,
        "content_theme_alignment": 82,
        "engagement_rate_score": 88,
        "follower_quality": 70,
        "business_indicators": 85,
        "activity_recency": 90,
        "is_fake": False,
        "fake_indicators": [],
        "contact_email": "business@ecoinfluencer.com",
        "contact_website": "https://linktr.ee/ecoinfluencer",
        "email_source": "business_email",
        "reasoning": {
            "visual_aesthetic_match": "Clean, natural aesthetic aligns with brand",
            "content_theme_alignment": "Strong focus on sustainability topics",
            "engagement_rate_score": "3.5% engagement rate is above average",
            "follower_quality": "Good follower/following ratio",
            "business_indicators": "Business account with contact info",
            "activity_recency": "Recent and consistent posting",
        },
        "recommendation": "highly_recommended"
    }


@pytest.fixture
def mock_job_repo(sample_job):
    """Create a mock job repository."""
    repo = Mock()
    repo.get_by_id.return_value = sample_job
    return repo


@pytest.fixture
def mock_profile_repo(sample_profile):
    """Create a mock profile repository."""
    repo = Mock()
    repo.get_by_id.return_value = sample_profile
    repo.update_status.return_value = sample_profile
    return repo


@pytest.fixture
def mock_brand_repo(sample_brand_dna):
    """Create a mock brand repository."""
    repo = Mock()
    repo.get_by_job_id_optional.return_value = sample_brand_dna
    return repo


@pytest.fixture
def mock_score_repo():
    """Create a mock score repository."""
    repo = Mock()
    repo.get_by_profile_id_optional.return_value = None
    repo.create_full_score.return_value = {
        "id": str(uuid4()),
        "profile_id": str(uuid4()),
        "final_score": 82,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    repo.update_by_profile_id.return_value = repo.create_full_score.return_value
    return repo


@pytest.fixture
def mock_contact_repo():
    """Create a mock contact repository."""
    repo = Mock()
    repo.upsert.return_value = {
        "id": str(uuid4()),
        "profile_id": str(uuid4()),
        "email": "test@example.com",
        "email_source": "business_email",
    }
    return repo


@pytest.fixture
def mock_scoring_service():
    """Create a mock scoring service."""
    service = Mock()
    service.calculate_final_score_from_dict.return_value = 82
    service.get_recommendation.return_value = "highly_recommended"
    return service


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.llm = Mock()
    service.model = "gpt-4"
    return service


# =============================================================================
# ScoringAnalysisOutput Tests
# =============================================================================

@pytest.mark.unit
class TestScoringAnalysisOutput:
    """Tests for ScoringAnalysisOutput model."""
    
    def test_default_values(self):
        """Test default values for ScoringAnalysisOutput."""
        output = ScoringAnalysisOutput()
        
        assert output.visual_aesthetic_match == 50
        assert output.content_theme_alignment == 50
        assert output.engagement_rate_score == 50
        assert output.follower_quality == 50
        assert output.business_indicators == 50
        assert output.activity_recency == 50
        assert output.is_fake is False
        assert output.fake_indicators == []
        assert output.recommendation == "consider"
    
    def test_with_values(self, sample_analysis_output):
        """Test ScoringAnalysisOutput with custom values."""
        output = ScoringAnalysisOutput(**sample_analysis_output)
        
        assert output.visual_aesthetic_match == 75
        assert output.content_theme_alignment == 82
        assert output.engagement_rate_score == 88
        assert output.is_fake is False
        assert output.contact_email == "business@ecoinfluencer.com"
        assert output.recommendation == "highly_recommended"
    
    def test_score_validation(self):
        """Test score validation (0-100)."""
        # Valid boundary values
        output1 = ScoringAnalysisOutput(visual_aesthetic_match=0)
        assert output1.visual_aesthetic_match == 0
        
        output2 = ScoringAnalysisOutput(visual_aesthetic_match=100)
        assert output2.visual_aesthetic_match == 100
        
        # Invalid values should raise
        with pytest.raises(ValueError):
            ScoringAnalysisOutput(visual_aesthetic_match=-1)
        
        with pytest.raises(ValueError):
            ScoringAnalysisOutput(visual_aesthetic_match=101)


@pytest.mark.unit
class TestExtractedContact:
    """Tests for ExtractedContact model."""
    
    def test_default_values(self):
        """Test default values for ExtractedContact."""
        contact = ExtractedContact()
        
        assert contact.email is None
        assert contact.phone is None
        assert contact.website is None
        assert contact.email_source is None
        assert contact.other_contacts == {}
    
    def test_with_values(self):
        """Test ExtractedContact with custom values."""
        contact = ExtractedContact(
            email="test@example.com",
            email_source="bio",
            website="https://example.com",
            other_contacts={"linktree": "https://linktr.ee/test"}
        )
        
        assert contact.email == "test@example.com"
        assert contact.email_source == "bio"
        assert contact.website == "https://example.com"
        assert "linktree" in contact.other_contacts


# =============================================================================
# ScorerAgent Initialization Tests
# =============================================================================

@pytest.mark.unit
class TestScorerAgentInit:
    """Tests for ScorerAgent initialization."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.scorer.get_scoring_service')
    def test_agent_initializes_correctly(
        self,
        mock_get_scoring,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that agent initializes correctly with default services."""
        mock_get_config.return_value = {
            "name": "Scorer",
            "enabled": True,
            "prompts": {},
        }
        mock_load_prompts.return_value = {"system": "system", "user": "user"}
        
        agent = ScorerAgent()
        
        assert agent.agent_name == "scorer"
        mock_get_scoring.assert_called_once()
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_with_custom_services(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_job_repo,
        mock_profile_repo,
        mock_brand_repo,
        mock_score_repo,
        mock_contact_repo,
        mock_scoring_service
    ):
        """Test agent initialization with custom services."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = ScorerAgent(
            job_repo=mock_job_repo,
            profile_repo=mock_profile_repo,
            brand_repo=mock_brand_repo,
            score_repo=mock_score_repo,
            contact_repo=mock_contact_repo,
            scoring_service=mock_scoring_service
        )
        
        assert agent._job_repo == mock_job_repo
        assert agent._profile_repo == mock_profile_repo
        assert agent._brand_repo == mock_brand_repo
        assert agent._score_repo == mock_score_repo
        assert agent._contact_repo == mock_contact_repo
        assert agent._scoring_service == mock_scoring_service


# =============================================================================
# Fake Detection Tests (SUB-3.3.4.1.3)
# =============================================================================

@pytest.mark.unit
class TestFakeDetection:
    """Tests for fake profile detection."""
    
    @pytest.fixture
    def agent(
        self,
        mock_llm_service,
        mock_job_repo,
        mock_profile_repo,
        mock_brand_repo,
        mock_score_repo,
        mock_contact_repo,
        mock_scoring_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(
                    llm_service=mock_llm_service,
                    job_repo=mock_job_repo,
                    profile_repo=mock_profile_repo,
                    brand_repo=mock_brand_repo,
                    score_repo=mock_score_repo,
                    contact_repo=mock_contact_repo,
                    scoring_service=mock_scoring_service
                )
    
    def test_detect_fake_high_following_ratio(self, agent):
        """Test fake detection for high following/follower ratio."""
        profile = {
            "followers_count": 10000,
            "following_count": 50000,  # 5x ratio
            "posts_count": 100,
        }
        
        indicators = agent._detect_fake_indicators(profile)
        
        assert len(indicators) > 0
        assert any("following/follower ratio" in i.lower() for i in indicators)
    
    def test_detect_fake_high_followers_few_posts(self, agent):
        """Test fake detection for high followers with few posts."""
        profile = {
            "followers_count": 50000,
            "following_count": 500,
            "posts_count": 5,  # Very few posts
        }
        
        indicators = agent._detect_fake_indicators(profile)
        
        assert len(indicators) > 0
        assert any("few posts" in i.lower() for i in indicators)
    
    def test_detect_fake_low_engagement(self, agent):
        """Test fake detection for low engagement rate."""
        profile = {
            "followers_count": 100000,
            "following_count": 500,
            "posts_count": 200,
            "engagement_rate": 0.1,  # Very low
        }
        
        indicators = agent._detect_fake_indicators(profile)
        
        assert len(indicators) > 0
        assert any("engagement rate" in i.lower() for i in indicators)
    
    def test_detect_fake_no_bio_high_followers(self, agent):
        """Test fake detection for no bio with high followers."""
        profile = {
            "followers_count": 100000,
            "following_count": 500,
            "posts_count": 200,
            "bio": "",  # No bio
        }
        
        indicators = agent._detect_fake_indicators(profile)
        
        assert len(indicators) > 0
        assert any("bio" in i.lower() for i in indicators)
    
    def test_detect_fake_no_indicators_for_legit_profile(self, agent, sample_profile):
        """Test no fake indicators for legitimate profile."""
        indicators = agent._detect_fake_indicators(sample_profile)
        
        # Should have no or minimal indicators
        assert len(indicators) <= 1
    
    def test_detect_fake_no_followers(self, agent):
        """Test fake detection for profile with no followers."""
        profile = {
            "followers_count": 0,
            "following_count": 100,
            "posts_count": 10,
        }
        
        indicators = agent._detect_fake_indicators(profile)
        
        assert len(indicators) > 0
        assert any("no followers" in i.lower() for i in indicators)
    
    def test_is_likely_fake_multiple_indicators(self, agent, sample_fake_profile):
        """Test is_likely_fake returns True for multiple indicators."""
        is_fake = agent._is_likely_fake(sample_fake_profile)
        
        assert is_fake is True
    
    def test_is_likely_fake_returns_false_for_legit(self, agent, sample_profile):
        """Test is_likely_fake returns False for legitimate profile."""
        is_fake = agent._is_likely_fake(sample_profile)
        
        assert is_fake is False


# =============================================================================
# Contact Extraction Tests (SUB-3.3.4.1.4)
# =============================================================================

@pytest.mark.unit
class TestContactExtraction:
    """Tests for contact information extraction."""
    
    @pytest.fixture
    def agent(self, mock_llm_service):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(llm_service=mock_llm_service)
    
    def test_extract_business_email(self, agent):
        """Test extracting business email (highest priority)."""
        profile = {
            "business_email": "business@brandname.com",
            "bio": "Contact: bio@othersite.com",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert contact.email == "business@brandname.com"
        assert contact.email_source == "business_email"
    
    def test_extract_bio_email(self, agent):
        """Test extracting email from bio."""
        profile = {
            "bio": "Contact me at hello@mybrand.com for collabs!",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert contact.email == "hello@mybrand.com"
        assert contact.email_source == "bio"
    
    def test_extract_website(self, agent):
        """Test extracting website URL."""
        profile = {
            "external_url": "https://example.com",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert contact.website == "https://example.com"
    
    def test_extract_linktree(self, agent):
        """Test extracting linktree."""
        profile = {
            "external_url": "https://linktr.ee/testuser",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert contact.website == "https://linktr.ee/testuser"
        assert "linktree" in contact.other_contacts
    
    def test_extract_multiple_contacts(self, agent):
        """Test extracting multiple contact methods."""
        profile = {
            "business_email": "business@mybrand.com",
            "external_url": "https://linktr.ee/user",
            "phone": "+1234567890",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert contact.email == "business@mybrand.com"
        assert contact.website == "https://linktr.ee/user"
        assert contact.phone == "+1234567890"
    
    def test_is_valid_email_filters_false_positives(self, agent):
        """Test email validation filters common false positives."""
        assert agent._is_valid_email("realuser@gmail.com") is True
        assert agent._is_valid_email("example@example.com") is False  # Fake domain
        assert agent._is_valid_email("test@test.com") is False  # Fake domain
        assert agent._is_valid_email("info@sentry.io") is False  # Filtered domain
        assert agent._is_valid_email("email@gmail.com") is False  # Placeholder + generic
    
    def test_is_valid_email_format(self, agent):
        """Test email format validation."""
        assert agent._is_valid_email("valid@realdomain.com") is True
        assert agent._is_valid_email("contact@company.co") is True
        assert agent._is_valid_email("hello@brand.org") is True
        assert agent._is_valid_email("not-an-email") is False
        assert agent._is_valid_email("") is False
        assert agent._is_valid_email(None) is False
    
    def test_extract_twitter_from_bio(self, agent):
        """Test extracting Twitter handle from bio."""
        profile = {
            "bio": "Check my twitter.com/myhandle for updates",
        }
        
        contact = agent._extract_contact_info(profile)
        
        assert "twitter" in contact.other_contacts
        assert "@myhandle" in contact.other_contacts["twitter"]


# =============================================================================
# Score Calculation Tests (SUB-3.3.4.1.5)
# =============================================================================

@pytest.mark.unit
class TestScoreCalculation:
    """Tests for score calculation."""
    
    @pytest.fixture
    def agent(self, mock_llm_service, mock_scoring_service):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(
                    llm_service=mock_llm_service,
                    scoring_service=mock_scoring_service
                )
    
    def test_build_dimension_list(self, agent):
        """Test building dimension list for response."""
        dimensions = {
            "visual_aesthetic_match": 75,
            "content_theme_alignment": 82,
            "engagement_rate_score": 88,
            "follower_quality": 70,
            "business_indicators": 85,
            "activity_recency": 90,
        }
        reasoning = {
            "visual_aesthetic_match": "Good visual style",
            "content_theme_alignment": "Strong topic alignment",
        }
        
        dimension_list = agent._build_dimension_list(dimensions, reasoning)
        
        assert len(dimension_list) == 6
        assert all(isinstance(d, ScoreDimension) for d in dimension_list)
        
        # Find visual aesthetic dimension
        visual_dim = next(d for d in dimension_list if d.name == "visual_aesthetic_match")
        assert visual_dim.score == 75
        assert visual_dim.reasoning == "Good visual style"


# =============================================================================
# Fallback Scoring Tests
# =============================================================================

@pytest.mark.unit
class TestFallbackScoring:
    """Tests for fallback heuristic scoring when LLM fails."""
    
    @pytest.fixture
    def agent(self, mock_llm_service, mock_scoring_service):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(
                    llm_service=mock_llm_service,
                    scoring_service=mock_scoring_service
                )
    
    def test_fallback_scores_high_engagement(self, agent, sample_profile):
        """Test fallback scoring gives high score for high engagement."""
        sample_profile["engagement_rate"] = 8.0  # Excellent engagement
        
        contact = ExtractedContact(email="test@test.com", email_source="bio")
        
        result = agent._generate_fallback_scores(
            profile_data=sample_profile,
            brand_dna={},
            fake_indicators=[],
            contact=contact
        )
        
        assert result.engagement_rate_score >= 90
    
    def test_fallback_scores_low_engagement(self, agent, sample_profile):
        """Test fallback scoring gives low score for low engagement."""
        sample_profile["engagement_rate"] = 0.2  # Very low
        
        contact = ExtractedContact()
        
        result = agent._generate_fallback_scores(
            profile_data=sample_profile,
            brand_dna={},
            fake_indicators=[],
            contact=contact
        )
        
        assert result.engagement_rate_score <= 30
    
    def test_fallback_scores_business_indicators(self, agent, sample_profile):
        """Test fallback scoring for business indicators."""
        sample_profile["is_business_account"] = True
        sample_profile["is_verified"] = True
        
        contact = ExtractedContact(
            email="test@test.com",
            email_source="business_email",
            website="https://example.com"
        )
        
        result = agent._generate_fallback_scores(
            profile_data=sample_profile,
            brand_dna={},
            fake_indicators=[],
            contact=contact
        )
        
        # Business account + email + website + verified = high score
        assert result.business_indicators >= 80
    
    def test_fallback_scores_reduced_for_fake(self, agent, sample_fake_profile):
        """Test fallback scoring reduces scores for suspected fake."""
        fake_indicators = ["High following ratio", "Low engagement"]
        
        contact = ExtractedContact()
        
        result = agent._generate_fallback_scores(
            profile_data=sample_fake_profile,
            brand_dna={},
            fake_indicators=fake_indicators,
            contact=contact
        )
        
        assert result.is_fake is True
        # All scores should be reduced
        assert result.engagement_rate_score <= 50
        assert result.recommendation == "not_recommended"


# =============================================================================
# LLM Analysis Tests (SUB-3.3.4.1.2)
# =============================================================================

@pytest.mark.unit
class TestLLMAnalysis:
    """Tests for LLM profile analysis."""
    
    @pytest.fixture
    def agent(
        self,
        mock_llm_service,
        mock_job_repo,
        mock_profile_repo,
        mock_brand_repo,
        mock_score_repo,
        mock_contact_repo,
        mock_scoring_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(
                    llm_service=mock_llm_service,
                    job_repo=mock_job_repo,
                    profile_repo=mock_profile_repo,
                    brand_repo=mock_brand_repo,
                    score_repo=mock_score_repo,
                    contact_repo=mock_contact_repo,
                    scoring_service=mock_scoring_service
                )
    
    def test_format_profile_for_prompt(self, agent, sample_profile):
        """Test profile formatting for LLM prompt."""
        formatted = agent._format_profile_for_prompt(sample_profile)
        
        assert "@eco_influencer" in formatted
        assert "75,000" in formatted  # Followers formatted
        assert "Eco Influencer" in formatted
        assert "Business Account" in formatted
    
    def test_format_brand_dna_for_prompt(self, agent, sample_brand_dna):
        """Test brand DNA formatting for LLM prompt."""
        formatted = agent._format_brand_dna_for_prompt(sample_brand_dna)
        
        assert "#sustainablefashion" in formatted
        assert "sustainable" in formatted
        assert "minimalist" in formatted
    
    def test_format_brand_dna_empty(self, agent):
        """Test formatting empty brand DNA."""
        formatted = agent._format_brand_dna_for_prompt({})
        
        assert "No brand DNA available" in formatted


# =============================================================================
# Database Storage Tests (SUB-3.3.4.1.6)
# =============================================================================

@pytest.mark.unit
class TestDatabaseStorage:
    """Tests for database storage."""
    
    @pytest.fixture
    def agent(
        self,
        mock_llm_service,
        mock_job_repo,
        mock_profile_repo,
        mock_brand_repo,
        mock_score_repo,
        mock_contact_repo,
        mock_scoring_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(
                    llm_service=mock_llm_service,
                    job_repo=mock_job_repo,
                    profile_repo=mock_profile_repo,
                    brand_repo=mock_brand_repo,
                    score_repo=mock_score_repo,
                    contact_repo=mock_contact_repo,
                    scoring_service=mock_scoring_service
                )
    
    @pytest.mark.asyncio
    async def test_store_results_creates_new_score(
        self,
        agent,
        mock_score_repo,
        mock_contact_repo,
        sample_profile_id
    ):
        """Test creating new score record."""
        mock_score_repo.get_by_profile_id_optional.return_value = None
        
        dimensions = {
            "visual_aesthetic_match": 75,
            "content_theme_alignment": 82,
            "engagement_rate_score": 88,
            "follower_quality": 70,
            "business_indicators": 85,
            "activity_recency": 90,
        }
        contact = ExtractedContact(email="test@test.com", email_source="bio")
        
        await agent._store_results(
            profile_id=sample_profile_id,
            dimensions=dimensions,
            final_score=82,
            recommendation="highly_recommended",
            reasoning={"test": "reason"},
            is_fake_suspected=False,
            fake_indicators=[],
            contact=contact
        )
        
        mock_score_repo.create_full_score.assert_called_once()
        mock_contact_repo.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_results_updates_existing_score(
        self,
        agent,
        mock_score_repo,
        sample_profile_id
    ):
        """Test updating existing score record."""
        mock_score_repo.get_by_profile_id_optional.return_value = {"id": "existing"}
        
        dimensions = {
            "visual_aesthetic_match": 75,
            "content_theme_alignment": 82,
            "engagement_rate_score": 88,
            "follower_quality": 70,
            "business_indicators": 85,
            "activity_recency": 90,
        }
        contact = ExtractedContact()
        
        await agent._store_results(
            profile_id=sample_profile_id,
            dimensions=dimensions,
            final_score=82,
            recommendation="highly_recommended",
            reasoning={},
            is_fake_suspected=False,
            fake_indicators=[],
            contact=contact
        )
        
        mock_score_repo.update_by_profile_id.assert_called_once()
        mock_score_repo.create_full_score.assert_not_called()


# =============================================================================
# Run Method Tests
# =============================================================================

@pytest.mark.unit
class TestRunMethod:
    """Tests for the main run method."""
    
    @pytest.fixture
    def agent(
        self,
        mock_llm_service,
        mock_job_repo,
        mock_profile_repo,
        mock_brand_repo,
        mock_score_repo,
        mock_contact_repo,
        mock_scoring_service,
        sample_analysis_output
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                agent = ScorerAgent(
                    llm_service=mock_llm_service,
                    job_repo=mock_job_repo,
                    profile_repo=mock_profile_repo,
                    brand_repo=mock_brand_repo,
                    score_repo=mock_score_repo,
                    contact_repo=mock_contact_repo,
                    scoring_service=mock_scoring_service
                )
                
                # Mock the LLM analysis
                agent._analyze_profile = AsyncMock(
                    return_value=ScoringAnalysisOutput(**sample_analysis_output)
                )
                
                return agent
    
    @pytest.mark.asyncio
    async def test_run_success(self, agent, sample_profile_id, sample_job_id):
        """Test successful run method execution."""
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=sample_job_id
        )
        
        response = await agent.run(request)
        
        assert isinstance(response, ScorerResponse)
        assert str(response.profile_id) == sample_profile_id
        assert response.final_score == 82
        assert response.recommendation == "highly_recommended"
    
    @pytest.mark.asyncio
    async def test_run_profile_not_found(self, agent, mock_profile_repo, sample_job_id):
        """Test run method with non-existent profile."""
        mock_profile_repo.get_by_id.side_effect = ProfileNotFoundError("test-id")
        
        request = ScorerRequest(
            profile_id=uuid4(),
            job_id=sample_job_id
        )
        
        with pytest.raises(ProfileNotFoundError):
            await agent.run(request)
    
    @pytest.mark.asyncio
    async def test_run_job_not_found(self, agent, mock_job_repo, sample_profile_id):
        """Test run method with non-existent job."""
        mock_job_repo.get_by_id.side_effect = JobNotFoundError("test-id")
        
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=uuid4()
        )
        
        with pytest.raises(JobNotFoundError):
            await agent.run(request)
    
    @pytest.mark.asyncio
    async def test_run_with_fake_profile(
        self,
        agent,
        mock_profile_repo,
        sample_fake_profile,
        sample_profile_id,
        sample_job_id,
        mock_scoring_service
    ):
        """Test run method with suspected fake profile."""
        mock_profile_repo.get_by_id.return_value = sample_fake_profile
        mock_scoring_service.get_recommendation.return_value = "not_recommended"
        
        # Update analysis to reflect fake detection
        agent._analyze_profile = AsyncMock(
            return_value=ScoringAnalysisOutput(
                is_fake=True,
                fake_indicators=["High following ratio", "Low engagement"],
                recommendation="not_recommended"
            )
        )
        
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=sample_job_id
        )
        
        response = await agent.run(request)
        
        assert response.is_fake_suspected is True
        assert len(response.fake_indicators) > 0


# =============================================================================
# Input Validation Tests
# =============================================================================

@pytest.mark.unit
class TestInputValidation:
    """Tests for input validation."""
    
    @pytest.fixture
    def agent(self, mock_llm_service):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return ScorerAgent(llm_service=mock_llm_service)
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self, agent, sample_profile_id, sample_job_id):
        """Test validation of valid input."""
        request = ScorerRequest(
            profile_id=sample_profile_id,
            job_id=sample_job_id
        )
        
        result = await agent.validate_input(request)
        
        assert result is True


# =============================================================================
# Factory Function Tests
# =============================================================================

@pytest.mark.unit
class TestFactoryFunction:
    """Tests for the factory function."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.scorer.get_scoring_service')
    def test_get_scorer_agent(
        self,
        mock_get_scoring,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test factory function creates agent correctly."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = get_scorer_agent()
        
        assert isinstance(agent, ScorerAgent)
        assert agent.agent_name == "scorer"


# =============================================================================
# Contract Tests
# =============================================================================

@pytest.mark.contract
class TestScorerContracts:
    """Contract tests verifying response format contracts."""
    
    def test_scorer_request_validates(self):
        """Test that ScorerRequest validates correctly."""
        profile_id = uuid4()
        job_id = uuid4()
        
        request = ScorerRequest(profile_id=profile_id, job_id=job_id)
        
        assert request.profile_id == profile_id
        assert request.job_id == job_id
    
    def test_scorer_response_serializes(self):
        """Test that ScorerResponse serializes correctly."""
        profile_id = uuid4()
        job_id = uuid4()
        
        response = ScorerResponse(
            profile_id=profile_id,
            job_id=job_id,
            visual_aesthetic_match=75,
            content_theme_alignment=82,
            engagement_rate_score=88,
            follower_quality=70,
            business_indicators=85,
            activity_recency=90,
            final_score=82,
            recommendation="highly_recommended",
            scoring_duration_seconds=3.5,
        )
        
        response_dict = response.model_dump()
        
        assert isinstance(response_dict, dict)
        assert response_dict["final_score"] == 82
        assert response_dict["recommendation"] == "highly_recommended"
    
    def test_score_dimension_validates(self):
        """Test that ScoreDimension validates correctly."""
        dimension = ScoreDimension(
            name="visual_aesthetic_match",
            score=75,
            weight=0.15,
            reasoning="Good visual alignment"
        )
        
        assert dimension.name == "visual_aesthetic_match"
        assert dimension.score == 75
        assert 0 <= dimension.weight <= 1
