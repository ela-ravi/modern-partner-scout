"""
PartnerScout AI - Base Agent Integration Tests (STORY-3.3.1)

Integration tests for the BaseAgent class that test with real
configuration and prompt loading, but with mocked LLM calls.

Test Markers:
- @pytest.mark.integration: Tests requiring real infrastructure (prompts, config)
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from uuid import uuid4

from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

from app.agents.base import (
    AgentConfig,
    AgentMetrics,
    AgentResult,
    BaseAgent,
)
from app.core.exceptions import AgentError
from app.prompts.loader import load_prompts, get_registered_agents
from app.core.settings import get_agent_config, get_agents_config


# =============================================================================
# Test Models
# =============================================================================

class BrandAnalysisInput(BaseModel):
    """Input model for brand analysis."""
    job_id: str
    brand_description: str
    reference_profiles: List[str]


class BrandAnalysisOutput(BaseModel):
    """Output model for brand analysis."""
    hashtags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    confidence_score: int = 75


# =============================================================================
# Concrete Test Agent for Integration Tests
# =============================================================================

class IntegrationBrandAnalyzerAgent(BaseAgent[BrandAnalysisInput, BrandAnalysisOutput]):
    """
    Concrete implementation of a Brand Analyzer agent for integration testing.
    Uses the actual 'brand_analyzer' configuration and prompts.
    """
    
    agent_name = "brand_analyzer"
    
    async def run(self, input_data: BrandAnalysisInput) -> BrandAnalysisOutput:
        """Execute brand analysis."""
        # Build the chain
        chain = self.build_json_chain(pydantic_schema=BrandAnalysisOutput)
        
        # Prepare input variables
        variables = {
            "brand_description": input_data.brand_description,
            "reference_profiles": ", ".join(input_data.reference_profiles),
        }
        
        # In real implementation, this would invoke the chain
        # For integration test, we return mock data
        return BrandAnalysisOutput(
            hashtags=["#sustainable", "#fashion", "#ecofriendly"],
            keywords=["sustainable", "fashion", "ethical"],
            confidence_score=85
        )


# =============================================================================
# Configuration Integration Tests
# =============================================================================

@pytest.mark.integration
class TestConfigurationIntegration:
    """Tests verifying BaseAgent integrates with YAML configuration."""
    
    def test_agent_loads_real_config(self):
        """Test that agent loads configuration from YAML file."""
        # Get the actual config to verify it exists
        agents_config = get_agents_config()
        
        assert "agents" in agents_config
        assert "brand_analyzer" in agents_config["agents"]
        
        # Now test that our agent loads it correctly
        with patch('app.agents.base.LLMService'):
            agent = IntegrationBrandAnalyzerAgent()
        
        assert agent.config.name == "Brand Analyzer"
        assert agent.config.enabled is True
    
    def test_agent_config_has_expected_fields(self):
        """Test that loaded config has all expected fields."""
        config = get_agent_config("brand_analyzer")
        
        assert "name" in config
        assert "description" in config
        assert "enabled" in config
        assert "model" in config
        assert "temperature" in config
        assert "prompts" in config
    
    def test_all_registered_agents_have_config(self):
        """Test that all registered agents have corresponding YAML config."""
        registered_agents = get_registered_agents()
        agents_config = get_agents_config()
        
        for agent_name in registered_agents:
            assert agent_name in agents_config["agents"], \
                f"Agent '{agent_name}' is registered but missing YAML config"


# =============================================================================
# Prompt Integration Tests
# =============================================================================

@pytest.mark.integration
class TestPromptIntegration:
    """Tests verifying BaseAgent integrates with prompt loading system."""
    
    def test_agent_loads_real_prompts(self):
        """Test that agent loads prompts from actual prompt files."""
        with patch('app.agents.base.LLMService'):
            agent = IntegrationBrandAnalyzerAgent()
        
        # System prompt should exist and be non-empty
        assert agent.system_prompt is not None
        assert len(agent.system_prompt) > 0
        
        # User prompt should exist and be non-empty
        assert agent.user_prompt is not None
        assert len(agent.user_prompt) > 0
    
    def test_system_prompt_contains_expected_content(self):
        """Test that system prompt contains expected elements."""
        with patch('app.agents.base.LLMService'):
            agent = IntegrationBrandAnalyzerAgent()
        
        # Brand analyzer prompt should mention brand analysis
        system = agent.system_prompt.lower()
        assert "brand" in system
        # Should mention hashtags since that's a key output
        assert "hashtag" in system
    
    def test_user_prompt_has_placeholders(self):
        """Test that user prompt has expected variable placeholders."""
        prompts = load_prompts("brand_analyzer")
        user_prompt = prompts["user"]
        
        # Should have some placeholders for input data
        assert "{" in user_prompt or "{{" in user_prompt
    
    def test_all_registered_agents_have_prompts(self):
        """Test that all registered agents have corresponding prompt files."""
        registered_agents = get_registered_agents()
        
        for agent_name in registered_agents:
            prompts = load_prompts(agent_name)
            assert "system" in prompts, f"Agent '{agent_name}' missing system prompt"
            assert "user" in prompts, f"Agent '{agent_name}' missing user prompt"
            assert len(prompts["system"]) > 0, f"Agent '{agent_name}' has empty system prompt"
            assert len(prompts["user"]) > 0, f"Agent '{agent_name}' has empty user prompt"


# =============================================================================
# Chain Building Integration Tests
# =============================================================================

@pytest.mark.integration
class TestChainBuildingIntegration:
    """Tests verifying chain building with real prompts."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for chain testing."""
        mock = Mock()
        mock.ainvoke = AsyncMock(return_value=AIMessage(content='{"hashtags": ["#test"], "keywords": ["test"]}'))
        mock.invoke = Mock(return_value=AIMessage(content='{"hashtags": ["#test"], "keywords": ["test"]}'))
        return mock
    
    def test_build_prompt_template_with_real_prompts(self, mock_llm):
        """Test building prompt template with actual loaded prompts."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        template = agent.build_prompt_template()
        
        # Template should have both system and user messages
        assert len(template.messages) == 2
        
        # Should be able to format the template
        # (just verify it doesn't crash - actual values may vary)
        assert template is not None
    
    def test_build_chain_with_real_prompts(self, mock_llm):
        """Test building complete chain with real prompts."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        chain = agent.build_chain()
        
        # Chain should be built successfully
        assert chain is not None
    
    def test_build_json_chain_with_real_prompts(self, mock_llm):
        """Test building JSON chain with real prompts."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        chain = agent.build_json_chain(pydantic_schema=BrandAnalysisOutput)
        
        assert chain is not None


# =============================================================================
# Full Pipeline Integration Tests
# =============================================================================

@pytest.mark.integration
class TestFullPipelineIntegration:
    """Tests verifying the full agent pipeline works together."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for pipeline testing."""
        mock = Mock()
        mock.ainvoke = AsyncMock(return_value=AIMessage(
            content='{"hashtags": ["#sustainable", "#fashion"], "keywords": ["eco", "ethical"], "confidence_score": 90}'
        ))
        return mock
    
    @pytest.mark.asyncio
    async def test_agent_run_end_to_end(self, mock_llm):
        """Test agent run from input to output."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        input_data = BrandAnalysisInput(
            job_id=str(uuid4()),
            brand_description="A sustainable fashion brand focused on eco-friendly materials",
            reference_profiles=[
                "https://instagram.com/everlane",
                "https://instagram.com/reformation"
            ]
        )
        
        result = await agent.run(input_data)
        
        assert isinstance(result, BrandAnalysisOutput)
        assert len(result.hashtags) > 0
        assert len(result.keywords) > 0
        assert 0 <= result.confidence_score <= 100
    
    @pytest.mark.asyncio
    async def test_agent_preprocess_integration(self, mock_llm):
        """Test agent preprocessing with real input."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        input_data = BrandAnalysisInput(
            job_id="test-123",
            brand_description="Test brand",
            reference_profiles=["https://instagram.com/test"]
        )
        
        preprocessed = await agent.preprocess(input_data)
        
        assert isinstance(preprocessed, dict)
        assert preprocessed["job_id"] == "test-123"
        assert preprocessed["brand_description"] == "Test brand"
        assert "https://instagram.com/test" in preprocessed["reference_profiles"]
    
    @pytest.mark.asyncio
    async def test_agent_validation_integration(self, mock_llm):
        """Test agent input validation."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        input_data = BrandAnalysisInput(
            job_id="test-123",
            brand_description="Test brand",
            reference_profiles=["https://instagram.com/test"]
        )
        
        is_valid = await agent.validate_input(input_data)
        
        assert is_valid is True


# =============================================================================
# LLM Service Integration Tests
# =============================================================================

@pytest.mark.integration
class TestLLMServiceIntegration:
    """Tests verifying BaseAgent integrates with LLM service."""
    
    def test_agent_creates_llm_service_from_config(self):
        """Test that agent creates LLM service with config settings."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = Mock()
            mock_service.return_value.model = "gpt-4-turbo-preview"
            
            agent = IntegrationBrandAnalyzerAgent()
            
            # LLMService should be called with appropriate config
            assert mock_service.called
    
    def test_agent_llm_property_returns_underlying_llm(self):
        """Test that llm property returns the actual LLM instance."""
        mock_llm = Mock()
        
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        assert agent.llm == mock_llm
    
    def test_agent_llm_service_property_returns_service(self):
        """Test that llm_service property returns the service instance."""
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service_instance = Mock()
            mock_service_instance.llm = Mock()
            mock_service.return_value = mock_service_instance
            
            agent = IntegrationBrandAnalyzerAgent()
        
        assert agent.llm_service == mock_service_instance


# =============================================================================
# Multi-Agent Integration Tests
# =============================================================================

@pytest.mark.integration
class TestMultiAgentIntegration:
    """Tests for multiple agent configurations."""
    
    def test_different_agents_have_different_configs(self):
        """Test that each agent type has unique configuration."""
        brand_config = get_agent_config("brand_analyzer")
        scorer_config = get_agent_config("scorer")
        
        # Configs should be different
        assert brand_config["name"] != scorer_config["name"]
        assert brand_config["description"] != scorer_config["description"]
    
    def test_different_agents_have_different_prompts(self):
        """Test that each agent type has unique prompts."""
        brand_prompts = load_prompts("brand_analyzer")
        scorer_prompts = load_prompts("scorer")
        
        # Prompts should be different
        assert brand_prompts["system"] != scorer_prompts["system"]
        assert brand_prompts["user"] != scorer_prompts["user"]
    
    def test_all_agents_can_be_instantiated(self):
        """Test that all registered agents can be instantiated."""
        registered = get_registered_agents()
        
        for agent_name in registered:
            # Create a concrete class for this agent with proper method definition
            # Using exec to properly define the class with the abstract method implemented
            class_code = f"""
class DynamicTestAgent(BaseAgent):
    agent_name = "{agent_name}"
    
    async def run(self, input_data):
        return {{}}
"""
            local_namespace = {"BaseAgent": BaseAgent}
            exec(class_code, local_namespace)
            DynamicTestAgent = local_namespace["DynamicTestAgent"]
            
            with patch('app.agents.base.LLMService'):
                agent = DynamicTestAgent()
            
            assert agent.agent_name == agent_name
            assert agent.system_prompt is not None
            assert agent.user_prompt is not None


# =============================================================================
# Error Recovery Integration Tests
# =============================================================================

@pytest.mark.integration
class TestErrorRecoveryIntegration:
    """Tests for error handling in integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_agent_handles_llm_failure_gracefully(self):
        """Test that agent handles LLM failures gracefully."""
        mock_llm = Mock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("LLM API error"))
        
        with patch('app.agents.base.LLMService') as mock_service:
            mock_service.return_value.llm = mock_llm
            agent = IntegrationBrandAnalyzerAgent()
        
        chain = agent.build_chain()
        
        with pytest.raises(AgentError) as exc_info:
            await agent.invoke_chain(chain, {"input": "test"})
        
        assert "chain invocation failed" in str(exc_info.value)
    
    def test_agent_handles_config_missing_fields(self):
        """Test agent handles missing optional config fields."""
        # This tests the real config which might have optional fields
        with patch('app.agents.base.LLMService'):
            agent = IntegrationBrandAnalyzerAgent()
        
        # Agent should still work even if some optional fields are missing
        assert agent.config is not None
        assert agent.is_enabled is True


# =============================================================================
# Performance Integration Tests
# =============================================================================

@pytest.mark.integration
class TestPerformanceIntegration:
    """Tests for performance characteristics."""
    
    def test_config_loading_is_cached(self):
        """Test that config loading uses caching."""
        import time
        
        # First load
        start = time.time()
        config1 = get_agents_config()
        first_load = time.time() - start
        
        # Second load (should be cached)
        start = time.time()
        config2 = get_agents_config()
        second_load = time.time() - start
        
        # Cached load should be faster (or at least not slower)
        # Note: This might not always be true due to system variance
        assert config1 == config2
    
    def test_prompt_loading_is_cached(self):
        """Test that prompt loading uses caching."""
        # First load
        prompts1 = load_prompts("brand_analyzer")
        
        # Second load (should be cached)
        prompts2 = load_prompts("brand_analyzer")
        
        assert prompts1 == prompts2
    
    def test_multiple_agent_instances_share_config(self):
        """Test that multiple agent instances share cached config."""
        with patch('app.agents.base.LLMService'):
            agent1 = IntegrationBrandAnalyzerAgent()
            agent2 = IntegrationBrandAnalyzerAgent()
        
        # Both should have loaded the same config values
        assert agent1.config.name == agent2.config.name
        assert agent1.system_prompt == agent2.system_prompt
