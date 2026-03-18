"""
PartnerScout AI - Base Agent Unit Tests (STORY-3.3.1)

Comprehensive unit tests for the BaseAgent abstract class covering:
- Configuration loading from YAML
- Prompt loading from external files
- Chain building with LangChain
- Abstract method enforcement
- Error handling

Test Markers:
- @pytest.mark.unit: Fast unit tests with mocked dependencies
- @pytest.mark.contract: Tests verifying response format contracts
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.agents.base import (
    AgentConfig,
    AgentMetrics,
    AgentResult,
    BaseAgent,
)
from app.core.exceptions import AgentError


# =============================================================================
# Test Input/Output Models
# =============================================================================

class TestInput(BaseModel):
    """Test input model for agent testing."""
    message: str
    count: int = 1


class TestOutput(BaseModel):
    """Test output model for agent testing."""
    response: str
    processed: bool = False


# =============================================================================
# Concrete Test Agent Implementation
# =============================================================================

class ConcreteTestAgent(BaseAgent[TestInput, TestOutput]):
    """Concrete implementation of BaseAgent for testing."""
    
    agent_name = "brand_analyzer"  # Use existing agent name for config/prompts
    
    async def run(self, input_data: TestInput) -> TestOutput:
        """Test implementation of run method."""
        return TestOutput(
            response=f"Processed: {input_data.message}",
            processed=True
        )


class DisabledTestAgent(BaseAgent[TestInput, TestOutput]):
    """Agent that should be disabled in config."""
    
    agent_name = "test_disabled_agent"
    
    async def run(self, input_data: TestInput) -> TestOutput:
        return TestOutput(response="disabled", processed=False)


# =============================================================================
# AgentConfig Tests
# =============================================================================

@pytest.mark.unit
class TestAgentConfig:
    """Tests for AgentConfig model."""
    
    def test_default_config_values(self):
        """Test that AgentConfig has correct defaults."""
        config = AgentConfig(name="test_agent")
        
        assert config.name == "test_agent"
        assert config.enabled is True
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.max_retries == 3
        assert config.timeout_seconds == 60
        assert config.extra == {}
    
    def test_custom_config_values(self):
        """Test AgentConfig with custom values."""
        config = AgentConfig(
            name="custom_agent",
            description="A custom agent",
            enabled=False,
            model="gpt-4",
            temperature=0.5,
            max_tokens=4096,
            max_retries=5,
            timeout_seconds=120,
            extra={"custom_key": "custom_value"}
        )
        
        assert config.name == "custom_agent"
        assert config.description == "A custom agent"
        assert config.enabled is False
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 4096
        assert config.max_retries == 5
        assert config.timeout_seconds == 120
        assert config.extra["custom_key"] == "custom_value"
    
    def test_temperature_validation(self):
        """Test that temperature must be between 0 and 2."""
        # Valid values
        config1 = AgentConfig(name="test", temperature=0.0)
        assert config1.temperature == 0.0
        
        config2 = AgentConfig(name="test", temperature=2.0)
        assert config2.temperature == 2.0
        
        # Invalid values should raise validation error
        with pytest.raises(ValueError):
            AgentConfig(name="test", temperature=-0.1)
        
        with pytest.raises(ValueError):
            AgentConfig(name="test", temperature=2.1)


# =============================================================================
# AgentMetrics Tests
# =============================================================================

@pytest.mark.unit
class TestAgentMetrics:
    """Tests for AgentMetrics model."""
    
    def test_default_metrics(self):
        """Test that AgentMetrics initializes correctly."""
        metrics = AgentMetrics()
        
        assert metrics.started_at is not None
        assert metrics.completed_at is None
        assert metrics.duration_seconds is None
        assert metrics.prompt_tokens == 0
        assert metrics.completion_tokens == 0
        assert metrics.total_tokens == 0
        assert metrics.retries == 0
        assert metrics.success is False
        assert metrics.error_message is None
    
    def test_metrics_with_values(self):
        """Test AgentMetrics with custom values."""
        now = datetime.now(timezone.utc)
        metrics = AgentMetrics(
            started_at=now,
            completed_at=now,
            duration_seconds=5.5,
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            retries=2,
            success=True,
        )
        
        assert metrics.duration_seconds == 5.5
        assert metrics.total_tokens == 300
        assert metrics.success is True


# =============================================================================
# AgentResult Tests
# =============================================================================

@pytest.mark.unit
class TestAgentResult:
    """Tests for AgentResult model."""
    
    def test_success_result(self):
        """Test successful agent result."""
        result = AgentResult(
            agent_name="test_agent",
            success=True,
            data={"key": "value"},
        )
        
        assert result.agent_name == "test_agent"
        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
    
    def test_error_result(self):
        """Test error agent result."""
        result = AgentResult(
            agent_name="test_agent",
            success=False,
            error="Something went wrong",
        )
        
        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data is None


# =============================================================================
# BaseAgent Initialization Tests
# =============================================================================

@pytest.mark.unit
class TestBaseAgentInitialization:
    """Tests for BaseAgent initialization and configuration loading."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_initializes_with_defaults(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that agent initializes correctly with default configuration."""
        # Setup mocks
        mock_get_config.return_value = {
            "name": "Brand Analyzer",
            "description": "Test description",
            "enabled": True,
            "model": "gpt-4-turbo-preview",
            "temperature": 0.5,
            "max_tokens": 2048,
            "prompts": {
                "system": "brand_analyzer/system.txt",
                "user": "brand_analyzer/user.txt",
            },
        }
        mock_load_prompts.return_value = {
            "system": "You are a brand analyzer.",
            "user": "Analyze this brand: {brand}",
        }
        
        # Create agent
        agent = ConcreteTestAgent()
        
        # Verify configuration was loaded
        assert agent.agent_name == "brand_analyzer"
        assert agent.config.name == "Brand Analyzer"
        assert agent.config.enabled is True
        assert agent.is_enabled is True
        
        # Verify prompts were loaded
        mock_load_prompts.assert_called_once_with("brand_analyzer")
        assert agent.system_prompt == "You are a brand analyzer."
        assert agent.user_prompt == "Analyze this brand: {brand}"
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_with_custom_config(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test agent initialization with custom configuration."""
        mock_load_prompts.return_value = {"system": "Custom system", "user": "Custom user"}
        
        custom_config = AgentConfig(
            name="Custom Agent",
            description="Custom description",
            enabled=True,
            model="gpt-4",
            temperature=0.3,
            max_tokens=4096,
        )
        
        agent = ConcreteTestAgent(config=custom_config)
        
        assert agent.config.name == "Custom Agent"
        assert agent.config.temperature == 0.3
        assert agent.config.max_tokens == 4096
        # get_agent_config should not be called when config is provided
        mock_get_config.assert_not_called()
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_agent_with_custom_llm_service(
        self,
        mock_llm_service_class,
        mock_load_prompts,
        mock_get_config
    ):
        """Test agent initialization with custom LLM service."""
        mock_get_config.return_value = {
            "name": "Test",
            "enabled": True,
            "prompts": {},
        }
        mock_load_prompts.return_value = {"system": "sys", "user": "usr"}
        
        # Create custom LLM service
        custom_llm_service = Mock()
        custom_llm_service.llm = Mock()
        custom_llm_service.model = "custom-model"
        
        agent = ConcreteTestAgent(llm_service=custom_llm_service)
        
        assert agent.llm_service == custom_llm_service
        assert agent.llm == custom_llm_service.llm
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    def test_agent_fallback_on_config_error(
        self,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that agent uses defaults when config loading fails."""
        mock_get_config.side_effect = Exception("Config not found")
        mock_load_prompts.return_value = {"system": "sys", "user": "usr"}
        
        with patch('app.agents.base.LLMService'):
            agent = ConcreteTestAgent()
        
        # Should use default config
        assert agent.config.name == "brand_analyzer"
        assert agent.config.enabled is True


# =============================================================================
# Prompt Loading Tests
# =============================================================================

@pytest.mark.unit
class TestPromptLoading:
    """Tests for prompt loading functionality."""
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_prompts_loaded_on_init(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that prompts are loaded during initialization."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {
            "system": "System prompt content",
            "user": "User prompt content",
        }
        
        agent = ConcreteTestAgent()
        
        mock_load_prompts.assert_called_once()
        assert agent.system_prompt == "System prompt content"
        assert agent.user_prompt == "User prompt content"
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_get_formatted_system_prompt_no_vars(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test getting system prompt without variables."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {
            "system": "You are a helpful assistant.",
            "user": "Help me with {task}",
        }
        
        agent = ConcreteTestAgent()
        
        result = agent.get_formatted_system_prompt()
        assert result == "You are a helpful assistant."
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_get_formatted_user_prompt_with_vars(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test getting user prompt with variable substitution."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {
            "system": "System",
            "user": "Analyze brand: {brand_name} with style: {style}",
        }
        
        agent = ConcreteTestAgent()
        
        result = agent.get_formatted_user_prompt(
            variables={"brand_name": "Nike", "style": "athletic"}
        )
        assert result == "Analyze brand: Nike with style: athletic"
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    def test_get_formatted_prompt_missing_var_returns_original(
        self,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that missing variables don't cause errors."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {
            "system": "System",
            "user": "Analyze {brand} with {missing_var}",
        }
        
        agent = ConcreteTestAgent()
        
        # Should return original string when variable is missing
        result = agent.get_formatted_user_prompt(variables={"brand": "Test"})
        assert result == "Analyze {brand} with {missing_var}"
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    @patch('app.agents.base.LLMService')
    @patch('app.agents.base.clear_prompt_cache')
    def test_reload_prompts(
        self,
        mock_clear_cache,
        mock_llm_service,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that reload_prompts clears cache and reloads."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.return_value = {"system": "Old system", "user": "Old user"}
        
        agent = ConcreteTestAgent()
        
        # Update mock to return new prompts
        mock_load_prompts.return_value = {"system": "New system", "user": "New user"}
        
        # Reload prompts
        agent.reload_prompts()
        
        # Verify cache was cleared and prompts reloaded
        mock_clear_cache.assert_called_once()
        assert agent.system_prompt == "New system"
        assert agent.user_prompt == "New user"
    
    @patch('app.agents.base.get_agent_config')
    @patch('app.agents.base.load_prompts')
    def test_prompt_load_failure_raises_error(
        self,
        mock_load_prompts,
        mock_get_config
    ):
        """Test that prompt loading failure raises AgentError."""
        mock_get_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
        mock_load_prompts.side_effect = Exception("Prompt file not found")
        
        with pytest.raises(AgentError) as exc_info:
            with patch('app.agents.base.LLMService'):
                ConcreteTestAgent()
        
        assert "Failed to load prompts" in str(exc_info.value)
        assert exc_info.value.details.get("agent") == "brand_analyzer"


# =============================================================================
# Chain Building Tests
# =============================================================================

@pytest.mark.unit
class TestChainBuilding:
    """Tests for chain building functionality."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for chain testing."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    mock_config.return_value = {
                        "name": "Test",
                        "enabled": True,
                        "prompts": {},
                    }
                    mock_prompts.return_value = {
                        "system": "You are a test assistant.",
                        "user": "Process this: {input}",
                    }
                    
                    # Mock LLM
                    mock_llm_instance = Mock()
                    mock_llm_instance.llm = Mock()
                    mock_llm.return_value = mock_llm_instance
                    
                    agent = ConcreteTestAgent()
                    yield agent
    
    def test_build_prompt_template(self, mock_agent):
        """Test that prompt template is built correctly."""
        template = mock_agent.build_prompt_template()
        
        assert isinstance(template, ChatPromptTemplate)
        # Should have system and user messages
        assert len(template.messages) == 2
    
    def test_build_chain_returns_runnable(self, mock_agent):
        """Test that build_chain returns a runnable sequence."""
        chain = mock_agent.build_chain()
        
        # Should be a valid chain
        assert chain is not None
        # Chain should have the expected structure
        assert hasattr(chain, 'invoke') or hasattr(chain, 'first')
    
    def test_build_chain_with_custom_parser(self, mock_agent):
        """Test building chain with custom output parser."""
        custom_parser = StrOutputParser()
        chain = mock_agent.build_chain(output_parser=custom_parser)
        
        assert chain is not None
    
    def test_build_json_chain(self, mock_agent):
        """Test building chain with JSON output parser."""
        chain = mock_agent.build_json_chain()
        
        assert chain is not None
    
    def test_build_json_chain_with_schema(self, mock_agent):
        """Test building chain with Pydantic schema."""
        chain = mock_agent.build_json_chain(pydantic_schema=TestOutput)
        
        assert chain is not None


# =============================================================================
# Abstract Method Tests
# =============================================================================

@pytest.mark.unit
class TestAbstractMethods:
    """Tests for abstract method enforcement."""
    
    def test_cannot_instantiate_base_agent_directly(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            BaseAgent()
        
        assert "abstract" in str(exc_info.value).lower() or "instantiate" in str(exc_info.value).lower()
    
    def test_subclass_must_implement_run(self):
        """Test that subclass must implement run method."""
        # Create incomplete subclass
        class IncompleteAgent(BaseAgent):
            agent_name = "incomplete"
            # Missing run() implementation
        
        with pytest.raises(TypeError):
            with patch('app.agents.base.get_agent_config') as mock_config:
                with patch('app.agents.base.load_prompts') as mock_prompts:
                    with patch('app.agents.base.LLMService'):
                        mock_config.return_value = {"name": "Test", "enabled": True, "prompts": {}}
                        mock_prompts.return_value = {"system": "s", "user": "u"}
                        IncompleteAgent()


# =============================================================================
# Run Method Tests
# =============================================================================

@pytest.mark.unit
class TestRunMethod:
    """Tests for the run method execution."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for run tests."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService'):
                    mock_config.return_value = {
                        "name": "Test",
                        "enabled": True,
                        "prompts": {},
                    }
                    mock_prompts.return_value = {"system": "s", "user": "u"}
                    yield ConcreteTestAgent()
    
    @pytest.mark.asyncio
    async def test_run_returns_expected_output(self, mock_agent):
        """Test that run method returns correct output."""
        input_data = TestInput(message="Hello", count=1)
        result = await mock_agent.run(input_data)
        
        assert isinstance(result, TestOutput)
        assert result.response == "Processed: Hello"
        assert result.processed is True
    
    @pytest.mark.asyncio
    async def test_validate_input_default(self, mock_agent):
        """Test default input validation returns True."""
        input_data = TestInput(message="Test", count=5)
        result = await mock_agent.validate_input(input_data)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_preprocess_converts_model_to_dict(self, mock_agent):
        """Test that preprocess converts Pydantic model to dict."""
        input_data = TestInput(message="Test", count=5)
        result = await mock_agent.preprocess(input_data)
        
        assert isinstance(result, dict)
        assert result["message"] == "Test"
        assert result["count"] == 5


# =============================================================================
# Error Handling Tests
# =============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Tests for error handling in BaseAgent."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for error handling tests."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    mock_config.return_value = {
                        "name": "Test",
                        "enabled": True,
                        "prompts": {},
                    }
                    mock_prompts.return_value = {"system": "s", "user": "u"}
                    
                    mock_llm_instance = Mock()
                    mock_llm_instance.llm = Mock()
                    mock_llm.return_value = mock_llm_instance
                    
                    yield ConcreteTestAgent()
    
    @pytest.mark.asyncio
    async def test_invoke_chain_handles_errors(self, mock_agent):
        """Test that invoke_chain wraps errors in AgentError."""
        # Create a chain that fails
        mock_chain = AsyncMock()
        mock_chain.ainvoke.side_effect = Exception("LLM failed")
        
        with pytest.raises(AgentError) as exc_info:
            await mock_agent.invoke_chain(mock_chain, {"input": "test"})
        
        assert "chain invocation failed" in str(exc_info.value)
        assert exc_info.value.details.get("agent") == "brand_analyzer"
    
    def test_invoke_chain_sync_handles_errors(self, mock_agent):
        """Test that invoke_chain_sync wraps errors in AgentError."""
        mock_chain = Mock()
        mock_chain.invoke.side_effect = Exception("Sync LLM failed")
        
        with pytest.raises(AgentError) as exc_info:
            mock_agent.invoke_chain_sync(mock_chain, {"input": "test"})
        
        assert "chain invocation failed" in str(exc_info.value)


# =============================================================================
# Metrics Tests
# =============================================================================

@pytest.mark.unit
class TestMetrics:
    """Tests for metrics collection."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for metrics tests."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService'):
                    mock_config.return_value = {
                        "name": "Test",
                        "enabled": True,
                        "prompts": {},
                    }
                    mock_prompts.return_value = {"system": "s", "user": "u"}
                    yield ConcreteTestAgent()
    
    def test_start_metrics(self, mock_agent):
        """Test that start_metrics initializes metrics."""
        metrics = mock_agent._start_metrics()
        
        assert isinstance(metrics, AgentMetrics)
        assert metrics.started_at is not None
        assert metrics.success is False
    
    def test_complete_metrics_success(self, mock_agent):
        """Test completing metrics for successful run."""
        mock_agent._start_metrics()
        metrics = mock_agent._complete_metrics(success=True)
        
        assert metrics.success is True
        assert metrics.completed_at is not None
        assert metrics.duration_seconds is not None
        assert metrics.duration_seconds >= 0
    
    def test_complete_metrics_error(self, mock_agent):
        """Test completing metrics for failed run."""
        mock_agent._start_metrics()
        metrics = mock_agent._complete_metrics(
            success=False,
            error_message="Something went wrong"
        )
        
        assert metrics.success is False
        assert metrics.error_message == "Something went wrong"


# =============================================================================
# Utility Method Tests
# =============================================================================

@pytest.mark.unit
class TestUtilityMethods:
    """Tests for utility methods."""
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for utility tests."""
        with patch('app.agents.base.get_agent_config') as mock_config:
            with patch('app.agents.base.load_prompts') as mock_prompts:
                with patch('app.agents.base.LLMService') as mock_llm:
                    mock_config.return_value = {
                        "name": "Test Agent",
                        "enabled": True,
                        "prompts": {},
                    }
                    mock_prompts.return_value = {"system": "s", "user": "u"}
                    
                    mock_llm_instance = Mock()
                    mock_llm_instance.model = "gpt-4"
                    mock_llm.return_value = mock_llm_instance
                    
                    yield ConcreteTestAgent()
    
    def test_repr(self, mock_agent):
        """Test __repr__ method."""
        repr_str = repr(mock_agent)
        
        assert "ConcreteTestAgent" in repr_str
        assert "brand_analyzer" in repr_str
        assert "enabled=True" in repr_str
    
    def test_str(self, mock_agent):
        """Test __str__ method."""
        str_val = str(mock_agent)
        
        assert "Agent" in str_val


# =============================================================================
# Contract Tests
# =============================================================================

@pytest.mark.contract
class TestAgentContracts:
    """Contract tests verifying response format contracts."""
    
    def test_agent_config_serializes_to_dict(self):
        """Test that AgentConfig serializes correctly."""
        config = AgentConfig(
            name="test",
            description="Test agent",
            enabled=True,
            temperature=0.5,
        )
        
        config_dict = config.model_dump()
        
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "test"
        assert config_dict["temperature"] == 0.5
    
    def test_agent_metrics_serializes_to_dict(self):
        """Test that AgentMetrics serializes correctly."""
        metrics = AgentMetrics(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            success=True,
        )
        
        metrics_dict = metrics.model_dump()
        
        assert isinstance(metrics_dict, dict)
        assert metrics_dict["total_tokens"] == 300
        assert metrics_dict["success"] is True
    
    def test_agent_result_serializes_to_dict(self):
        """Test that AgentResult serializes correctly."""
        result = AgentResult(
            agent_name="test_agent",
            success=True,
            data={"key": "value"},
        )
        
        result_dict = result.model_dump()
        
        assert isinstance(result_dict, dict)
        assert result_dict["agent_name"] == "test_agent"
        assert result_dict["success"] is True
        assert result_dict["data"] == {"key": "value"}
