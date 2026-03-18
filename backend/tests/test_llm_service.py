"""
PartnerScout AI - LLM Service Unit Tests (STORY-3.1.1)

Comprehensive tests for the LLM Provider Abstraction layer including:
- Provider enum validation
- Configuration model validation
- Factory functions for each provider
- LLMService class functionality
- Provider selection via environment variable
- Utility functions
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Any

from pydantic import ValidationError

from app.services.llm_service import (
    # Enums
    LLMProvider,
    LLMModel,
    # Config
    LLMConfig,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    # Factory Functions
    create_openai_llm,
    create_gemini_llm,
    create_ollama_llm,
    get_llm,
    get_openai_llm,
    get_gemini_llm,
    get_ollama_llm,
    get_llm_service,
    get_default_llm_service,
    # Service Class
    LLMService,
    # Utility Functions
    get_available_providers,
    get_provider_info,
    is_provider_configured,
    get_current_provider,
)
from app.core.exceptions import AgentError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_openai_settings():
    """Mock OpenAI settings with valid API key."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.openai.api_key = "test-openai-key-12345"
        mock_settings.openai.model = "gpt-4-turbo-preview"
        mock_settings.gemini.api_key = "test-gemini-key-12345"
        mock_settings.gemini.model = "gemini-pro"
        mock_settings.ollama.base_url = "http://localhost:11434"
        mock_settings.ollama.model = "llama2"
        mock_settings.llm_provider = "openai"
        yield mock_settings


@pytest.fixture
def mock_gemini_settings():
    """Mock Gemini settings with valid API key."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.openai.api_key = "test-openai-key-12345"
        mock_settings.openai.model = "gpt-4-turbo-preview"
        mock_settings.gemini.api_key = "test-gemini-key-12345"
        mock_settings.gemini.model = "gemini-pro"
        mock_settings.ollama.base_url = "http://localhost:11434"
        mock_settings.ollama.model = "llama2"
        mock_settings.llm_provider = "gemini"
        yield mock_settings


@pytest.fixture
def mock_ollama_settings():
    """Mock Ollama settings."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.openai.api_key = "test-openai-key-12345"
        mock_settings.openai.model = "gpt-4-turbo-preview"
        mock_settings.gemini.api_key = "test-gemini-key-12345"
        mock_settings.gemini.model = "gemini-pro"
        mock_settings.ollama.base_url = "http://localhost:11434"
        mock_settings.ollama.model = "llama2"
        mock_settings.llm_provider = "ollama"
        yield mock_settings


@pytest.fixture
def mock_unconfigured_openai():
    """Mock unconfigured OpenAI settings."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.openai.api_key = "your-openai-api-key"  # Placeholder
        mock_settings.openai.model = "gpt-4-turbo-preview"
        mock_settings.llm_provider = "openai"
        yield mock_settings


@pytest.fixture
def mock_unconfigured_gemini():
    """Mock unconfigured Gemini settings."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.gemini.api_key = ""  # Empty
        mock_settings.gemini.model = "gemini-pro"
        mock_settings.llm_provider = "gemini"
        yield mock_settings


@pytest.fixture
def default_llm_config():
    """Create default LLM configuration."""
    return LLMConfig()


@pytest.fixture
def openai_llm_config():
    """Create OpenAI LLM configuration."""
    return LLMConfig(
        provider=LLMProvider.OPENAI,
        model="gpt-4",
        temperature=0.5,
        max_tokens=2048,
    )


@pytest.fixture
def gemini_llm_config():
    """Create Gemini LLM configuration."""
    return LLMConfig(
        provider=LLMProvider.GEMINI,
        model="gemini-pro",
        temperature=0.8,
    )


@pytest.fixture
def ollama_llm_config():
    """Create Ollama LLM configuration."""
    return LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="llama2",
        temperature=0.7,
    )


# =============================================================================
# Test LLMProvider Enum
# =============================================================================

class TestLLMProviderEnum:
    """Tests for LLMProvider enum."""
    
    def test_openai_value(self):
        """Test OpenAI provider value."""
        assert LLMProvider.OPENAI.value == "openai"
    
    def test_gemini_value(self):
        """Test Gemini provider value."""
        assert LLMProvider.GEMINI.value == "gemini"
    
    def test_ollama_value(self):
        """Test Ollama provider value."""
        assert LLMProvider.OLLAMA.value == "ollama"
    
    def test_provider_from_string(self):
        """Test creating provider from string."""
        assert LLMProvider("openai") == LLMProvider.OPENAI
        assert LLMProvider("gemini") == LLMProvider.GEMINI
        assert LLMProvider("ollama") == LLMProvider.OLLAMA
    
    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(ValueError):
            LLMProvider("invalid_provider")
    
    def test_all_providers_exist(self):
        """Test all expected providers exist."""
        providers = list(LLMProvider)
        assert len(providers) == 5
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.GEMINI in providers
        assert LLMProvider.OLLAMA in providers
        assert LLMProvider.OPENROUTER in providers
        assert LLMProvider.HUGGINGFACE in providers


# =============================================================================
# Test LLMModel Enum
# =============================================================================

class TestLLMModelEnum:
    """Tests for LLMModel enum."""
    
    def test_openai_models_exist(self):
        """Test OpenAI model values."""
        assert LLMModel.GPT_4_TURBO.value == "gpt-4-turbo-preview"
        assert LLMModel.GPT_4.value == "gpt-4"
        assert LLMModel.GPT_35_TURBO.value == "gpt-3.5-turbo"
        assert LLMModel.GPT_4O.value == "gpt-4o"
        assert LLMModel.GPT_4O_MINI.value == "gpt-4o-mini"
    
    def test_gemini_models_exist(self):
        """Test Gemini model values."""
        assert LLMModel.GEMINI_PRO.value == "gemini-pro"
        assert LLMModel.GEMINI_PRO_VISION.value == "gemini-pro-vision"
        assert LLMModel.GEMINI_15_PRO.value == "gemini-1.5-pro"
        assert LLMModel.GEMINI_15_FLASH.value == "gemini-1.5-flash"
    
    def test_ollama_models_exist(self):
        """Test Ollama model values."""
        assert LLMModel.LLAMA2.value == "llama2"
        assert LLMModel.LLAMA3.value == "llama3"
        assert LLMModel.MISTRAL.value == "mistral"
        assert LLMModel.MIXTRAL.value == "mixtral"
        assert LLMModel.CODELLAMA.value == "codellama"


# =============================================================================
# Test LLMConfig Model
# =============================================================================

class TestLLMConfig:
    """Tests for LLMConfig Pydantic model."""
    
    def test_default_values(self, default_llm_config):
        """Test default configuration values."""
        assert default_llm_config.provider == LLMProvider.OPENAI
        assert default_llm_config.model is None
        assert default_llm_config.temperature == DEFAULT_TEMPERATURE
        assert default_llm_config.max_tokens == DEFAULT_MAX_TOKENS
        assert default_llm_config.timeout == DEFAULT_TIMEOUT
        assert default_llm_config.extra_kwargs == {}
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider=LLMProvider.GEMINI,
            model="gemini-1.5-pro",
            temperature=0.3,
            max_tokens=8192,
            timeout=120,
            extra_kwargs={"top_p": 0.9}
        )
        
        assert config.provider == LLMProvider.GEMINI
        assert config.model == "gemini-1.5-pro"
        assert config.temperature == 0.3
        assert config.max_tokens == 8192
        assert config.timeout == 120
        assert config.extra_kwargs == {"top_p": 0.9}
    
    def test_temperature_validation_min(self):
        """Test temperature minimum validation."""
        with pytest.raises(ValidationError):
            LLMConfig(temperature=-0.1)
    
    def test_temperature_validation_max(self):
        """Test temperature maximum validation."""
        with pytest.raises(ValidationError):
            LLMConfig(temperature=2.5)
    
    def test_temperature_boundary_values(self):
        """Test temperature boundary values are accepted."""
        config_min = LLMConfig(temperature=0.0)
        config_max = LLMConfig(temperature=2.0)
        
        assert config_min.temperature == 0.0
        assert config_max.temperature == 2.0
    
    def test_max_tokens_validation(self):
        """Test max_tokens minimum validation."""
        with pytest.raises(ValidationError):
            LLMConfig(max_tokens=0)
    
    def test_timeout_validation(self):
        """Test timeout minimum validation."""
        with pytest.raises(ValidationError):
            LLMConfig(timeout=0)
    
    def test_provider_from_string(self):
        """Test provider can be set from string."""
        config = LLMConfig(provider="gemini")  # type: ignore
        assert config.provider == LLMProvider.GEMINI


# =============================================================================
# Test Factory Functions
# =============================================================================

class TestOpenAIFactory:
    """Tests for OpenAI factory function."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_create_openai_llm_success(self, mock_chat_openai, mock_openai_settings, openai_llm_config):
        """Test successful OpenAI LLM creation."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        result = create_openai_llm(openai_llm_config)
        
        mock_chat_openai.assert_called_once_with(
            api_key="test-openai-key-12345",
            model="gpt-4",
            temperature=0.5,
            max_tokens=2048,
            timeout=DEFAULT_TIMEOUT,
        )
        assert result == mock_instance
    
    def test_create_openai_llm_unconfigured(self, mock_unconfigured_openai, default_llm_config):
        """Test OpenAI creation fails when not configured."""
        with pytest.raises(AgentError) as exc_info:
            create_openai_llm(default_llm_config)
        
        assert "OpenAI API key is not configured" in str(exc_info.value.message)
        # agent_name is stored in details["agent"]
        assert exc_info.value.details.get("agent") == "llm_service"


class TestGeminiFactory:
    """Tests for Gemini factory function."""
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_create_gemini_llm_success(self, mock_chat_gemini, mock_gemini_settings, gemini_llm_config):
        """Test successful Gemini LLM creation."""
        mock_instance = Mock()
        mock_chat_gemini.return_value = mock_instance
        
        result = create_gemini_llm(gemini_llm_config)
        
        mock_chat_gemini.assert_called_once_with(
            google_api_key="test-gemini-key-12345",
            model="gemini-pro",
            temperature=0.8,
            max_output_tokens=DEFAULT_MAX_TOKENS,
            timeout=DEFAULT_TIMEOUT,
            convert_system_message_to_human=True,
        )
        assert result == mock_instance
    
    def test_create_gemini_llm_unconfigured(self, mock_unconfigured_gemini, gemini_llm_config):
        """Test Gemini creation fails when not configured."""
        with pytest.raises(AgentError) as exc_info:
            create_gemini_llm(gemini_llm_config)
        
        assert "Gemini API key is not configured" in str(exc_info.value.message)


class TestOllamaFactory:
    """Tests for Ollama factory function."""
    
    @patch("langchain_community.chat_models.ChatOllama")
    def test_create_ollama_llm_success(self, mock_chat_ollama, mock_ollama_settings, ollama_llm_config):
        """Test successful Ollama LLM creation."""
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance
        
        result = create_ollama_llm(ollama_llm_config)
        
        mock_chat_ollama.assert_called_once_with(
            base_url="http://localhost:11434",
            model="llama2",
            temperature=0.7,
            num_predict=DEFAULT_MAX_TOKENS,
        )
        assert result == mock_instance


# =============================================================================
# Test LLMService Class
# =============================================================================

class TestLLMService:
    """Tests for LLMService class."""
    
    def test_init_with_default_provider(self, mock_openai_settings):
        """Test initialization with default provider."""
        service = LLMService()
        
        assert service.provider == LLMProvider.OPENAI
        assert service.config.provider == LLMProvider.OPENAI
    
    def test_init_with_specific_provider(self, mock_gemini_settings):
        """Test initialization with specific provider."""
        service = LLMService(provider=LLMProvider.GEMINI)
        
        assert service.provider == LLMProvider.GEMINI
    
    def test_init_with_provider_string(self, mock_ollama_settings):
        """Test initialization with provider as string."""
        service = LLMService(provider="ollama")
        
        assert service.provider == LLMProvider.OLLAMA
    
    def test_init_with_config(self, mock_openai_settings):
        """Test initialization with full config."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            temperature=0.3,
            max_tokens=1000,
        )
        service = LLMService(config=config)
        
        assert service.config.temperature == 0.3
        assert service.config.max_tokens == 1000
    
    def test_config_takes_precedence(self, mock_openai_settings):
        """Test that config takes precedence over provider argument."""
        config = LLMConfig(provider=LLMProvider.GEMINI)
        service = LLMService(config=config, provider=LLMProvider.OPENAI)
        
        assert service.provider == LLMProvider.GEMINI
    
    def test_model_property_with_config_model(self, mock_openai_settings):
        """Test model property when model is set in config."""
        config = LLMConfig(provider=LLMProvider.OPENAI, model="gpt-4")
        service = LLMService(config=config)
        
        assert service.model == "gpt-4"
    
    def test_model_property_uses_default(self, mock_openai_settings):
        """Test model property uses provider default when not set."""
        service = LLMService(provider=LLMProvider.OPENAI)
        
        assert service.model == "gpt-4-turbo-preview"
    
    @patch("langchain_openai.ChatOpenAI")
    def test_llm_lazy_initialization(self, mock_chat_openai, mock_openai_settings):
        """Test LLM is lazily initialized."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        # LLM should not be created yet
        mock_chat_openai.assert_not_called()
        
        # Access llm property triggers creation
        _ = service.llm
        mock_chat_openai.assert_called_once()
    
    @patch("langchain_openai.ChatOpenAI")
    def test_llm_cached(self, mock_chat_openai, mock_openai_settings):
        """Test LLM instance is cached after first access."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        # Access multiple times
        llm1 = service.llm
        llm2 = service.llm
        
        # Should only create once
        mock_chat_openai.assert_called_once()
        assert llm1 is llm2
    
    def test_with_temperature(self, mock_openai_settings):
        """Test with_temperature creates new instance."""
        service = LLMService(provider=LLMProvider.OPENAI)
        new_service = service.with_temperature(0.3)
        
        assert new_service is not service
        assert new_service.config.temperature == 0.3
        assert service.config.temperature == DEFAULT_TEMPERATURE
    
    def test_with_model(self, mock_openai_settings):
        """Test with_model creates new instance."""
        service = LLMService(provider=LLMProvider.OPENAI)
        new_service = service.with_model("gpt-4")
        
        assert new_service is not service
        assert new_service.config.model == "gpt-4"
        assert service.config.model is None
    
    def test_repr(self, mock_openai_settings):
        """Test string representation."""
        service = LLMService(provider=LLMProvider.OPENAI)
        
        repr_str = repr(service)
        
        assert "LLMService" in repr_str
        assert "openai" in repr_str
        assert "gpt-4-turbo-preview" in repr_str


class TestLLMServiceGenerate:
    """Tests for LLMService generate methods."""
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_generate_with_prompt(self, mock_chat_openai, mock_openai_settings):
        """Test async generate with simple prompt."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        result = await service.generate("Test prompt")
        
        assert result == "Generated response"
        mock_instance.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_generate_with_system_prompt(self, mock_chat_openai, mock_openai_settings):
        """Test async generate with system prompt."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "System-informed response"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        result = await service.generate("User prompt", system_prompt="System prompt")
        
        assert result == "System-informed response"
        
        # Verify messages contain both system and user
        call_args = mock_instance.ainvoke.call_args
        messages = call_args[0][0]
        assert len(messages) == 2
    
    @patch("langchain_openai.ChatOpenAI")
    def test_generate_sync(self, mock_chat_openai, mock_openai_settings):
        """Test sync generate."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Sync response"
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        result = service.generate_sync("Test prompt")
        
        assert result == "Sync response"
        mock_instance.invoke.assert_called_once()


class TestLLMServiceChat:
    """Tests for LLMService chat method."""
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_chat_with_messages(self, mock_chat_openai, mock_openai_settings):
        """Test chat with message history."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "Chat response"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"},
        ]
        result = await service.chat(messages)
        
        assert result == "Chat response"
        
        # Verify all messages were converted
        call_args = mock_instance.ainvoke.call_args
        converted_messages = call_args[0][0]
        assert len(converted_messages) == 4


class TestLLMServiceChain:
    """Tests for LLMService chain creation."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_create_chain(self, mock_chat_openai, mock_openai_settings):
        """Test chain creation."""
        from langchain_core.prompts import ChatPromptTemplate
        
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        template = ChatPromptTemplate.from_template("Tell me about {topic}")
        
        chain = service.create_chain(template)
        
        # Chain should be created (RunnableSequence)
        assert chain is not None


# =============================================================================
# Test Convenience Factory Functions
# =============================================================================

class TestGetLLMFunction:
    """Tests for get_llm convenience function."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm_default_provider(self, mock_chat_openai, mock_openai_settings):
        """Test get_llm uses default provider."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        result = get_llm()
        
        mock_chat_openai.assert_called_once()
        assert result == mock_instance
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_get_llm_with_provider_string(self, mock_chat_gemini, mock_gemini_settings):
        """Test get_llm with provider as string."""
        mock_instance = Mock()
        mock_chat_gemini.return_value = mock_instance
        
        result = get_llm("gemini")
        
        mock_chat_gemini.assert_called_once()
        assert result == mock_instance
    
    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm_with_provider_enum(self, mock_chat_openai, mock_openai_settings):
        """Test get_llm with provider as enum."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        result = get_llm(LLMProvider.OPENAI)
        
        mock_chat_openai.assert_called_once()
        assert result == mock_instance
    
    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm_with_kwargs(self, mock_chat_openai, mock_openai_settings):
        """Test get_llm passes kwargs to config."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        get_llm(temperature=0.3, max_tokens=1000)
        
        call_args = mock_chat_openai.call_args
        assert call_args.kwargs["temperature"] == 0.3
        assert call_args.kwargs["max_tokens"] == 1000


class TestProviderSpecificFunctions:
    """Tests for provider-specific factory functions."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_get_openai_llm(self, mock_chat_openai, mock_openai_settings):
        """Test get_openai_llm function."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        result = get_openai_llm(temperature=0.5)
        
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        assert call_args.kwargs["temperature"] == 0.5
        assert result == mock_instance
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_get_gemini_llm(self, mock_chat_gemini, mock_gemini_settings):
        """Test get_gemini_llm function."""
        mock_instance = Mock()
        mock_chat_gemini.return_value = mock_instance
        
        result = get_gemini_llm()
        
        mock_chat_gemini.assert_called_once()
    
    @patch("langchain_community.chat_models.ChatOllama")
    def test_get_ollama_llm(self, mock_chat_ollama, mock_ollama_settings):
        """Test get_ollama_llm function."""
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance
        
        result = get_ollama_llm(model="mistral")
        
        mock_chat_ollama.assert_called_once()
        call_args = mock_chat_ollama.call_args
        assert call_args.kwargs["model"] == "mistral"


class TestGetLLMServiceFunction:
    """Tests for get_llm_service dependency factory."""
    
    def test_get_llm_service_with_config(self, mock_openai_settings):
        """Test get_llm_service with config."""
        config = LLMConfig(provider=LLMProvider.OPENAI, temperature=0.3)
        
        service = get_llm_service(config=config)
        
        assert isinstance(service, LLMService)
        assert service.config.temperature == 0.3
    
    def test_get_llm_service_with_provider(self, mock_gemini_settings):
        """Test get_llm_service with provider."""
        service = get_llm_service(provider=LLMProvider.GEMINI)
        
        assert isinstance(service, LLMService)
        assert service.provider == LLMProvider.GEMINI
    
    def test_get_llm_service_default(self, mock_openai_settings):
        """Test get_llm_service returns default cached service."""
        # Clear the cache first
        get_default_llm_service.cache_clear()
        
        service1 = get_llm_service()
        service2 = get_llm_service()
        
        # Should return the same cached instance
        assert service1 is service2


# =============================================================================
# Test Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_get_available_providers(self):
        """Test get_available_providers returns all providers."""
        providers = get_available_providers()

        assert len(providers) == 5
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.GEMINI in providers
        assert LLMProvider.OLLAMA in providers
        assert LLMProvider.OPENROUTER in providers
        assert LLMProvider.HUGGINGFACE in providers
    
    def test_get_provider_info_openai_configured(self, mock_openai_settings):
        """Test get_provider_info for configured OpenAI."""
        info = get_provider_info(LLMProvider.OPENAI)
        
        assert info["provider"] == "openai"
        assert info["configured"] == True
        assert info["default_model"] == "gpt-4-turbo-preview"
        assert "models" in info
        assert "gpt-4-turbo-preview" in info["models"]
    
    def test_get_provider_info_openai_unconfigured(self, mock_unconfigured_openai):
        """Test get_provider_info for unconfigured OpenAI."""
        info = get_provider_info("openai")
        
        assert info["configured"] == False
    
    def test_get_provider_info_gemini(self, mock_gemini_settings):
        """Test get_provider_info for Gemini."""
        info = get_provider_info(LLMProvider.GEMINI)
        
        assert info["provider"] == "gemini"
        assert "gemini-pro" in info["models"]
    
    def test_get_provider_info_ollama(self, mock_ollama_settings):
        """Test get_provider_info for Ollama."""
        info = get_provider_info(LLMProvider.OLLAMA)
        
        assert info["provider"] == "ollama"
        assert info["configured"] == True  # Ollama doesn't need API key
        assert "base_url" in info
        assert "llama2" in info["models"]
    
    def test_is_provider_configured_true(self, mock_openai_settings):
        """Test is_provider_configured returns True."""
        assert is_provider_configured(LLMProvider.OPENAI) == True
    
    def test_is_provider_configured_false(self, mock_unconfigured_openai):
        """Test is_provider_configured returns False."""
        assert is_provider_configured("openai") == False
    
    def test_get_current_provider(self, mock_openai_settings):
        """Test get_current_provider returns configured provider."""
        provider = get_current_provider()
        
        assert provider == LLMProvider.OPENAI


# =============================================================================
# Test Environment Variable Provider Selection
# =============================================================================

class TestEnvironmentVariableSelection:
    """Tests for provider selection via environment variable."""
    
    def test_openai_from_env(self, mock_openai_settings):
        """Test OpenAI provider selected from env."""
        service = LLMService()
        assert service.provider == LLMProvider.OPENAI
    
    def test_gemini_from_env(self):
        """Test Gemini provider selected from env."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.llm_provider = "gemini"
            mock_settings.gemini.api_key = "test-key"
            mock_settings.gemini.model = "gemini-pro"
            
            service = LLMService()
            assert service.provider == LLMProvider.GEMINI
    
    def test_ollama_from_env(self):
        """Test Ollama provider selected from env."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.llm_provider = "ollama"
            mock_settings.ollama.base_url = "http://localhost:11434"
            mock_settings.ollama.model = "llama2"
            
            service = LLMService()
            assert service.provider == LLMProvider.OLLAMA


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_unsupported_provider_in_get_llm(self, mock_openai_settings):
        """Test error for unsupported provider."""
        with pytest.raises(ValueError):
            get_llm("unsupported_provider")
    
    def test_agent_error_properties(self, mock_unconfigured_openai, default_llm_config):
        """Test AgentError has correct properties."""
        with pytest.raises(AgentError) as exc_info:
            create_openai_llm(default_llm_config)
        
        error = exc_info.value
        # agent_name is stored in details["agent"]
        assert error.details.get("agent") == "llm_service"
        assert error.details.get("provider") == "openai"


# =============================================================================
# Test Constants
# =============================================================================

class TestConstants:
    """Tests for module constants."""
    
    def test_default_temperature(self):
        """Test default temperature value."""
        assert DEFAULT_TEMPERATURE == 0.7
    
    def test_default_max_tokens(self):
        """Test default max tokens value."""
        assert DEFAULT_MAX_TOKENS == 4096
    
    def test_default_timeout(self):
        """Test default timeout value."""
        assert DEFAULT_TIMEOUT == 60
