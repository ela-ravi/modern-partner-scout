"""
PartnerScout AI - Brand Analyzer Agent Unit Tests (STORY-3.3.2)

Comprehensive unit tests for the BrandAnalyzerAgent covering:
- Agent initialization
- Profile fetching via Apify
- LLM chain for hashtag/keyword extraction
- Embedding generation
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

from app.agents.brand_analyzer import (
    BrandAnalyzerAgent,
    BrandAnalysisOutput,
    get_brand_analyzer_agent,
)
from app.core.exceptions import AgentError, JobNotFoundError
from app.models.agent import BrandAnalyzerRequest, BrandAnalyzerResponse


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_job_id():
    """Generate a sample job ID."""
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
            "https://instagram.com/patagonia",
        ],
        "follower_range_min": 5000,
        "follower_range_max": 500000,
        "discovery_limit": 50,
        "status": "pending",
    }


@pytest.fixture
def sample_profile_data():
    """Create sample Instagram profile data."""
    return [
        {
            "username": "everlane",
            "fullName": "Everlane",
            "biography": "Radical transparency. #sustainablefashion #ethicalclothing",
            "followersCount": 1500000,
            "followsCount": 200,
            "postsCount": 3500,
            "isBusinessAccount": True,
            "businessEmail": "contact@everlane.com",
            "externalUrl": "https://everlane.com",
            "recentPosts": [
                {
                    "caption": "New arrivals for spring #sustainablefashion #newin",
                    "likesCount": 5000,
                    "commentsCount": 150,
                },
                {
                    "caption": "Our commitment to ethical production #ethicalfashion",
                    "likesCount": 4500,
                    "commentsCount": 120,
                },
            ],
        },
        {
            "username": "reformation",
            "fullName": "Reformation",
            "biography": "Sustainable fashion for all. #sustainablestyle #ecofriendly",
            "followersCount": 2000000,
            "followsCount": 150,
            "postsCount": 4000,
            "isBusinessAccount": True,
            "businessEmail": "hello@reformation.com",
            "externalUrl": "https://reformation.com",
            "recentPosts": [
                {
                    "caption": "Dresses made with recycled materials #slowfashion",
                    "likesCount": 8000,
                    "commentsCount": 200,
                },
            ],
        },
    ]


@pytest.fixture
def sample_analysis_output():
    """Create sample LLM analysis output."""
    return {
        "hashtags": ["#sustainablefashion", "#ecofriendly", "#ethicalfashion", "#slowfashion", "#sustainablestyle"],
        "keywords": ["sustainable", "ethical", "eco-friendly", "fashion", "recycled materials"],
        "visual_themes": ["minimalist", "earth tones", "natural textures"],
        "content_pillars": ["sustainability", "fashion", "lifestyle", "transparency"],
        "target_audience_description": "Environmentally conscious millennials and Gen Z consumers interested in ethical fashion",
        "brand_summary": {
            "voice": "Authentic and transparent",
            "aesthetic": "Clean and minimal",
            "audience": "Eco-conscious consumers",
            "differentiators": ["Radical transparency", "Ethical production"]
        },
        "confidence_score": 85
    }


@pytest.fixture
def sample_embedding():
    """Create a sample embedding vector (1536 dimensions)."""
    return [0.01 * i for i in range(1536)]


@pytest.fixture
def mock_job_repo(sample_job):
    """Create a mock job repository."""
    repo = Mock()
    repo.get_by_id.return_value = sample_job
    return repo


@pytest.fixture
def mock_brand_repo():
    """Create a mock brand repository."""
    repo = Mock()
    repo.get_by_job_id_optional.return_value = None
    repo.create.return_value = {
        "id": str(uuid4()),
        "job_id": str(uuid4()),
        "hashtags": ["#test"],
        "keywords": ["test"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    repo.update_by_job_id.return_value = repo.create.return_value
    return repo


@pytest.fixture
def mock_apify_service(sample_profile_data):
    """Create a mock Apify service."""
    service = Mock()
    service.scrape_profiles = AsyncMock(return_value=sample_profile_data)
    service.extract_username_from_url.side_effect = lambda url: url.split("/")[-1]
    return service


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    service = Mock()
    service.llm = Mock()
    service.model = "gpt-4"
    return service


# =============================================================================
# BrandAnalysisOutput Tests
# =============================================================================

@pytest.mark.unit
class TestBrandAnalysisOutput:
    """Tests for BrandAnalysisOutput model."""
    
    def test_default_values(self):
        """Test default values for BrandAnalysisOutput."""
        output = BrandAnalysisOutput()
        
        assert output.hashtags == []
        assert output.keywords == []
        assert output.visual_themes == []
        assert output.content_pillars == []
        assert output.target_audience_description is None
        assert output.confidence_score == 70
    
    def test_with_values(self, sample_analysis_output):
        """Test BrandAnalysisOutput with custom values."""
        output = BrandAnalysisOutput(**sample_analysis_output)
        
        assert len(output.hashtags) == 5
        assert "#sustainablefashion" in output.hashtags
        assert len(output.keywords) == 5
        assert "sustainable" in output.keywords
        assert output.confidence_score == 85
    
    def test_confidence_score_validation(self):
        """Test confidence score validation (0-100)."""
        # Valid values
        output1 = BrandAnalysisOutput(confidence_score=0)
        assert output1.confidence_score == 0
        
        output2 = BrandAnalysisOutput(confidence_score=100)
        assert output2.confidence_score == 100
        
        # Invalid values should raise
        with pytest.raises(ValueError):
            BrandAnalysisOutput(confidence_score=-1)
        
        with pytest.raises(ValueError):
            BrandAnalysisOutput(confidence_score=101)


# =============================================================================
# BrandAnalyzerAgent Initialization Tests
# =============================================================================

@pytest.mark.unit
class TestBrandAnalyzerAgentInit:
    """Tests for BrandAnalyzerAgent initialization."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.brand_analyzer.get_apify_service')
    def test_agent_initializes_correctly(
        self,
        mock_get_apify,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that agent initializes correctly with default services."""
        mock_get_config.return_value = {
            "name": "Brand Analyzer",
            "enabled": True,
            "prompts": {},
            "output": {"min_hashtags": 5, "min_keywords": 5}
        }
        mock_load_prompts.return_value = {"system": "system", "user": "user"}
        
        agent = BrandAnalyzerAgent()
        
        assert agent.agent_name == "brand_analyzer"
        mock_get_apify.assert_called_once()
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_with_custom_services(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo
    ):
        """Test agent initialization with custom services."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = BrandAnalyzerAgent(
            apify_service=mock_apify_service,
            job_repo=mock_job_repo,
            brand_repo=mock_brand_repo
        )
        
        assert agent._apify_service == mock_apify_service
        assert agent._job_repo == mock_job_repo
        assert agent._brand_repo == mock_brand_repo


# =============================================================================
# Profile Fetching Tests (SUB-3.3.2.1.2)
# =============================================================================

@pytest.mark.unit
class TestProfileFetching:
    """Tests for profile fetching via Apify."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
    
    @pytest.mark.asyncio
    async def test_fetch_profiles_extracts_usernames(self, agent, mock_apify_service):
        """Test that usernames are correctly extracted from URLs."""
        profile_urls = [
            "https://instagram.com/everlane",
            "https://instagram.com/reformation",
        ]
        
        await agent._fetch_profiles(profile_urls)
        
        # Verify usernames were extracted and passed to Apify
        mock_apify_service.scrape_profiles.assert_called_once()
        call_args = mock_apify_service.scrape_profiles.call_args
        usernames = call_args.kwargs.get("usernames", call_args.args[0] if call_args.args else [])
        assert "everlane" in usernames
        assert "reformation" in usernames
    
    @pytest.mark.asyncio
    async def test_fetch_profiles_counts_posts(self, agent, sample_profile_data):
        """Test that posts are counted correctly."""
        profiles, profiles_count, posts_count = await agent._fetch_profiles(
            ["https://instagram.com/everlane"]
        )
        
        assert profiles_count == 2  # From mock data
        assert posts_count == 3  # 2 posts from everlane + 1 from reformation
    
    @pytest.mark.asyncio
    async def test_fetch_profiles_handles_apify_error(self, agent, mock_apify_service):
        """Test graceful handling of Apify errors."""
        from app.core.exceptions import ApifyError
        
        mock_apify_service.scrape_profiles = AsyncMock(
            side_effect=ApifyError(message="API error", actor_id="test")
        )
        
        profiles, profiles_count, posts_count = await agent._fetch_profiles(
            ["https://instagram.com/test"]
        )
        
        # Should return empty results on error
        assert profiles == []
        assert profiles_count == 0
        assert posts_count == 0


# =============================================================================
# LLM Analysis Tests (SUB-3.3.2.1.3)
# =============================================================================

@pytest.mark.unit
class TestLLMAnalysis:
    """Tests for LLM brand analysis."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {
                    "name": "Test",
                    "enabled": True,
                    "prompts": {},
                    "output": {"min_hashtags": 5, "min_keywords": 5}
                }
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
    
    def test_format_profiles_for_prompt(self, agent, sample_profile_data):
        """Test profile formatting for LLM prompt."""
        formatted = agent._format_profiles_for_prompt(sample_profile_data)
        
        assert "@everlane" in formatted
        assert "@reformation" in formatted
        assert "1,500,000" in formatted  # Followers formatted
    
    def test_format_profiles_empty(self, agent):
        """Test formatting empty profile list."""
        formatted = agent._format_profiles_for_prompt([])
        
        assert "No reference profiles available" in formatted
    
    def test_extract_hashtags_from_profile(self, agent, sample_profile_data):
        """Test hashtag extraction from profile."""
        hashtags = agent._extract_hashtags_from_profile(sample_profile_data[0])
        
        assert "#sustainablefashion" in hashtags
        assert "#ethicalclothing" in hashtags
    
    def test_normalize_hashtags(self, agent):
        """Test hashtag normalization."""
        raw_hashtags = ["sustainablefashion", "#EcoFriendly", "  #test  ", ""]
        normalized = agent._normalize_hashtags(raw_hashtags)
        
        assert "#sustainablefashion" in normalized
        assert "#ecofriendly" in normalized
        assert "#test" in normalized
        assert "" not in normalized


# =============================================================================
# Embedding Generation Tests (SUB-3.3.2.1.4)
# =============================================================================

@pytest.mark.unit
class TestEmbeddingGeneration:
    """Tests for embedding generation."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
    
    def test_create_embedding_text(self, agent, sample_analysis_output):
        """Test embedding text creation."""
        analysis = BrandAnalysisOutput(**sample_analysis_output)
        
        embedding_text = agent._create_embedding_text(
            "A sustainable fashion brand",
            analysis
        )
        
        assert "sustainable fashion brand" in embedding_text
        assert "Hashtags:" in embedding_text
        assert "Keywords:" in embedding_text
    
    @pytest.mark.asyncio
    @patch('langchain_openai.OpenAIEmbeddings')
    async def test_generate_embedding_success(
        self,
        mock_embeddings_class,
        agent,
        sample_embedding,
        sample_analysis_output
    ):
        """Test successful embedding generation."""
        mock_embeddings = Mock()
        mock_embeddings.aembed_query = AsyncMock(return_value=sample_embedding)
        mock_embeddings_class.return_value = mock_embeddings
        
        analysis = BrandAnalysisOutput(**sample_analysis_output)
        
        result = await agent._generate_embedding("Test brand", analysis)
        
        assert result is not None
        assert len(result) == 1536
    
    @pytest.mark.asyncio
    @patch('langchain_openai.OpenAIEmbeddings')
    async def test_generate_embedding_handles_error(
        self,
        mock_embeddings_class,
        agent,
        sample_analysis_output
    ):
        """Test graceful handling of embedding generation errors."""
        mock_embeddings = Mock()
        mock_embeddings.aembed_query = AsyncMock(side_effect=Exception("API error"))
        mock_embeddings_class.return_value = mock_embeddings
        
        analysis = BrandAnalysisOutput(**sample_analysis_output)
        
        result = await agent._generate_embedding("Test brand", analysis)
        
        # Should return None on error
        assert result is None


# =============================================================================
# Database Storage Tests (SUB-3.3.2.1.5)
# =============================================================================

@pytest.mark.unit
class TestDatabaseStorage:
    """Tests for brand DNA storage."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
    
    @pytest.mark.asyncio
    async def test_store_brand_dna_creates_new(
        self,
        agent,
        mock_brand_repo,
        sample_job_id,
        sample_analysis_output,
        sample_embedding
    ):
        """Test creating new brand DNA record."""
        mock_brand_repo.get_by_job_id_optional.return_value = None
        
        analysis = BrandAnalysisOutput(**sample_analysis_output)
        
        await agent._store_brand_dna(sample_job_id, analysis, sample_embedding)
        
        mock_brand_repo.create.assert_called_once()
        call_kwargs = mock_brand_repo.create.call_args.kwargs
        assert call_kwargs["job_id"] == sample_job_id
        assert call_kwargs["hashtags"] == analysis.hashtags
    
    @pytest.mark.asyncio
    async def test_store_brand_dna_updates_existing(
        self,
        agent,
        mock_brand_repo,
        sample_job_id,
        sample_analysis_output,
        sample_embedding
    ):
        """Test updating existing brand DNA record."""
        mock_brand_repo.get_by_job_id_optional.return_value = {"id": "existing"}
        
        analysis = BrandAnalysisOutput(**sample_analysis_output)
        
        await agent._store_brand_dna(sample_job_id, analysis, sample_embedding)
        
        mock_brand_repo.update_by_job_id.assert_called_once()
        mock_brand_repo.create.assert_not_called()


# =============================================================================
# Run Method Tests
# =============================================================================

@pytest.mark.unit
class TestRunMethod:
    """Tests for the main run method."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service,
        sample_analysis_output
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                agent = BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
                
                # Mock LLM analysis
                agent._analyze_brand = AsyncMock(
                    return_value=BrandAnalysisOutput(**sample_analysis_output)
                )
                agent._generate_embedding = AsyncMock(return_value=[0.0] * 1536)
                
                return agent
    
    @pytest.mark.asyncio
    async def test_run_success(self, agent, sample_job_id):
        """Test successful run method execution."""
        request = BrandAnalyzerRequest(job_id=sample_job_id)
        
        response = await agent.run(request)
        
        assert isinstance(response, BrandAnalyzerResponse)
        assert response.job_id == request.job_id
        assert len(response.hashtags) >= 5
        assert len(response.keywords) >= 5
    
    @pytest.mark.asyncio
    async def test_run_job_not_found(self, agent, mock_job_repo):
        """Test run method with non-existent job."""
        mock_job_repo.get_by_id.side_effect = JobNotFoundError("test-id")
        
        request = BrandAnalyzerRequest(job_id=uuid4())
        
        with pytest.raises(JobNotFoundError):
            await agent.run(request)
    
    @pytest.mark.asyncio
    async def test_run_no_reference_profiles(self, agent, mock_job_repo, sample_job_id):
        """Test run method with no reference profiles."""
        mock_job_repo.get_by_id.return_value = {
            "id": sample_job_id,
            "brand_description": "Test brand",
            "reference_profiles": [],
        }
        
        request = BrandAnalyzerRequest(job_id=sample_job_id)
        
        with pytest.raises(AgentError) as exc_info:
            await agent.run(request)
        
        assert "No reference profiles" in str(exc_info.value)


# =============================================================================
# Input Validation Tests
# =============================================================================

@pytest.mark.unit
class TestInputValidation:
    """Tests for input validation."""
    
    @pytest.fixture
    def agent(
        self,
        mock_apify_service,
        mock_job_repo,
        mock_brand_repo,
        mock_llm_service
    ):
        """Create an agent with mocked dependencies."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                mock_prompts.return_value = {"system": "s", "user": "u"}
                
                return BrandAnalyzerAgent(
                    llm_service=mock_llm_service,
                    apify_service=mock_apify_service,
                    job_repo=mock_job_repo,
                    brand_repo=mock_brand_repo
                )
    
    @pytest.mark.asyncio
    async def test_validate_input_valid(self, agent, sample_job_id):
        """Test validation of valid input."""
        request = BrandAnalyzerRequest(job_id=sample_job_id)
        
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
    @patch('app.agents.brand_analyzer.get_apify_service')
    def test_get_brand_analyzer_agent(
        self,
        mock_get_apify,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test factory function creates agent correctly."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "s", "user": "u"}
        
        agent = get_brand_analyzer_agent()
        
        assert isinstance(agent, BrandAnalyzerAgent)
        assert agent.agent_name == "brand_analyzer"


# =============================================================================
# Contract Tests
# =============================================================================

@pytest.mark.contract
class TestBrandAnalyzerContracts:
    """Contract tests verifying response format contracts."""
    
    def test_brand_analyzer_request_validates(self):
        """Test that BrandAnalyzerRequest validates correctly."""
        job_id = uuid4()
        request = BrandAnalyzerRequest(job_id=job_id)
        
        assert request.job_id == job_id
        assert request.max_posts_per_profile == 20  # Default
    
    def test_brand_analyzer_response_serializes(self):
        """Test that BrandAnalyzerResponse serializes correctly."""
        job_id = uuid4()
        response = BrandAnalyzerResponse(
            job_id=job_id,
            hashtags=["#test1", "#test2"],
            keywords=["keyword1", "keyword2"],
            profiles_analyzed=3,
            posts_analyzed=45,
            analysis_duration_seconds=12.5,
        )
        
        response_dict = response.model_dump()
        
        assert isinstance(response_dict, dict)
        assert response_dict["hashtags"] == ["#test1", "#test2"]
        assert response_dict["profiles_analyzed"] == 3
    
    def test_brand_analysis_output_required_fields(self):
        """Test that BrandAnalysisOutput has expected fields."""
        output = BrandAnalysisOutput(
            hashtags=["#test"],
            keywords=["test"],
            confidence_score=80
        )
        
        assert hasattr(output, "hashtags")
        assert hasattr(output, "keywords")
        assert hasattr(output, "visual_themes")
        assert hasattr(output, "content_pillars")
        assert hasattr(output, "target_audience_description")
        assert hasattr(output, "confidence_score")
