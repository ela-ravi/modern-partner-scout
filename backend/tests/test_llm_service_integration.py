"""
PartnerScout AI - LLM Service Integration Tests (STORY-3.1.1)

Integration tests for the LLM Provider Abstraction layer that verify:
- End-to-end workflows with mocked LLM responses
- Configuration loading from environment
- Service instantiation via FastAPI dependency injection
- Chain building and execution
- Provider switching at runtime

These tests use mocked LLM backends but test the full integration flow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import List

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel

from app.services.llm_service import (
    LLMService,
    LLMProvider,
    LLMConfig,
    get_llm,
    get_llm_service,
    get_default_llm_service,
    get_available_providers,
    is_provider_configured,
)
from app.core.exceptions import AgentError


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def full_mock_settings():
    """Full mock settings for integration tests."""
    with patch("app.services.llm_service.settings") as mock_settings:
        # OpenAI
        mock_settings.openai.api_key = "sk-test-openai-key"
        mock_settings.openai.model = "gpt-4-turbo-preview"
        # Gemini
        mock_settings.gemini.api_key = "test-gemini-key"
        mock_settings.gemini.model = "gemini-pro"
        # Ollama
        mock_settings.ollama.base_url = "http://localhost:11434"
        mock_settings.ollama.model = "llama2"
        # Default provider
        mock_settings.llm_provider = "openai"
        yield mock_settings


@pytest.fixture
def mock_openai_response():
    """Mock response from OpenAI."""
    response = Mock()
    response.content = "This is a test response from OpenAI."
    return response


@pytest.fixture
def mock_gemini_response():
    """Mock response from Gemini."""
    response = Mock()
    response.content = "This is a test response from Gemini."
    return response


@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama."""
    response = Mock()
    response.content = "This is a test response from Ollama."
    return response


# =============================================================================
# End-to-End Service Workflow Tests
# =============================================================================

class TestServiceWorkflow:
    """End-to-end workflow tests for LLMService."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_openai_workflow(self, mock_chat_openai, full_mock_settings, mock_openai_response):
        """Test complete OpenAI workflow: init -> configure -> generate."""
        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_openai_response
        mock_chat_openai.return_value = mock_instance
        
        # Initialize service
        service = LLMService(provider=LLMProvider.OPENAI)
        
        # Verify provider
        assert service.provider == LLMProvider.OPENAI
        
        # Configure with lower temperature
        service = service.with_temperature(0.3)
        assert service.config.temperature == 0.3
        
        # Generate response
        result = service.generate_sync("Test prompt")
        
        assert result == "This is a test response from OpenAI."
        mock_instance.invoke.assert_called_once()
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_gemini_workflow(self, mock_chat_gemini, full_mock_settings, mock_gemini_response):
        """Test complete Gemini workflow."""
        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_gemini_response
        mock_chat_gemini.return_value = mock_instance
        
        # Initialize service
        service = LLMService(provider=LLMProvider.GEMINI)
        
        # Verify provider
        assert service.provider == LLMProvider.GEMINI
        
        # Generate response
        result = service.generate_sync("Test prompt")
        
        assert result == "This is a test response from Gemini."
    
    @patch("langchain_community.chat_models.ChatOllama")
    def test_ollama_workflow(self, mock_chat_ollama, full_mock_settings, mock_ollama_response):
        """Test complete Ollama workflow."""
        mock_instance = Mock()
        mock_instance.invoke.return_value = mock_ollama_response
        mock_chat_ollama.return_value = mock_instance
        
        # Initialize service
        service = LLMService(provider=LLMProvider.OLLAMA)
        
        # Verify provider
        assert service.provider == LLMProvider.OLLAMA
        
        # Generate response
        result = service.generate_sync("Test prompt")
        
        assert result == "This is a test response from Ollama."


class TestAsyncWorkflows:
    """Async workflow tests."""
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_async_generate_workflow(self, mock_chat_openai, full_mock_settings):
        """Test async generate workflow."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "Async response"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        result = await service.generate("Async test prompt")
        
        assert result == "Async response"
        mock_instance.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_async_chat_workflow(self, mock_chat_openai, full_mock_settings):
        """Test async chat workflow with conversation history."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "I remember you're interested in AI."
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "I'm interested in AI."},
            {"role": "assistant", "content": "Great! AI is a fascinating field."},
            {"role": "user", "content": "What do you remember about me?"},
        ]
        
        result = await service.chat(messages)
        
        assert result == "I remember you're interested in AI."
        
        # Verify message count
        call_args = mock_instance.ainvoke.call_args
        passed_messages = call_args[0][0]
        assert len(passed_messages) == 4


# =============================================================================
# Chain Building Integration Tests
# =============================================================================

class TestChainIntegration:
    """Tests for LangChain chain building and execution."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_simple_chain_execution(self, mock_chat_openai, full_mock_settings):
        """Test building and executing a simple chain."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Python is a programming language."
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        # Create a simple prompt template
        template = ChatPromptTemplate.from_template(
            "Explain {topic} in one sentence."
        )
        
        # Build chain
        chain = service.create_chain(template)
        
        # Chain should be a Runnable
        assert hasattr(chain, 'invoke')
    
    @patch("langchain_openai.ChatOpenAI")
    def test_chain_with_custom_parser(self, mock_chat_openai, full_mock_settings):
        """Test chain with custom output parser."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Parsed output"
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        template = ChatPromptTemplate.from_template("Tell me about {topic}")
        custom_parser = StrOutputParser()
        
        chain = service.create_chain(template, output_parser=custom_parser)
        
        # Chain should include the custom parser
        assert chain is not None


# =============================================================================
# Provider Switching Integration Tests
# =============================================================================

class TestProviderSwitching:
    """Tests for runtime provider switching."""
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    @patch("langchain_openai.ChatOpenAI")
    def test_switch_from_openai_to_gemini(
        self, 
        mock_openai, 
        mock_gemini, 
        full_mock_settings
    ):
        """Test switching from OpenAI to Gemini at runtime."""
        openai_response = Mock()
        openai_response.content = "OpenAI response"
        gemini_response = Mock()
        gemini_response.content = "Gemini response"
        
        mock_openai_instance = Mock()
        mock_openai_instance.invoke.return_value = openai_response
        mock_openai.return_value = mock_openai_instance
        
        mock_gemini_instance = Mock()
        mock_gemini_instance.invoke.return_value = gemini_response
        mock_gemini.return_value = mock_gemini_instance
        
        # Start with OpenAI
        openai_service = LLMService(provider=LLMProvider.OPENAI)
        assert openai_service.provider == LLMProvider.OPENAI
        
        result1 = openai_service.generate_sync("Test")
        assert result1 == "OpenAI response"
        
        # Switch to Gemini
        gemini_service = LLMService(provider=LLMProvider.GEMINI)
        assert gemini_service.provider == LLMProvider.GEMINI
        
        result2 = gemini_service.generate_sync("Test")
        assert result2 == "Gemini response"
    
    @patch("langchain_community.chat_models.ChatOllama")
    @patch("langchain_openai.ChatOpenAI")
    def test_switch_with_different_configs(
        self, 
        mock_openai, 
        mock_ollama, 
        full_mock_settings
    ):
        """Test switching providers with different configurations."""
        openai_response = Mock()
        openai_response.content = "High temp response"
        ollama_response = Mock()
        ollama_response.content = "Low temp response"
        
        mock_openai_instance = Mock()
        mock_openai_instance.invoke.return_value = openai_response
        mock_openai.return_value = mock_openai_instance
        
        mock_ollama_instance = Mock()
        mock_ollama_instance.invoke.return_value = ollama_response
        mock_ollama.return_value = mock_ollama_instance
        
        # OpenAI with high temperature
        openai_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            temperature=0.9,
            max_tokens=2048
        )
        openai_service = LLMService(config=openai_config)
        
        # Ollama with low temperature
        ollama_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            temperature=0.1,
            max_tokens=512
        )
        ollama_service = LLMService(config=ollama_config)
        
        # Verify different configs
        assert openai_service.config.temperature == 0.9
        assert ollama_service.config.temperature == 0.1


# =============================================================================
# FastAPI Dependency Injection Integration Tests
# =============================================================================

class TestFastAPIDependencyInjection:
    """Tests for FastAPI dependency injection integration."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_dependency_injection_in_route(self, mock_chat_openai, full_mock_settings):
        """Test LLM service injection in FastAPI route."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "DI response"
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        # Create test app
        app = FastAPI()
        
        @app.get("/test")
        def test_route(llm_service: LLMService = Depends(get_llm_service)):
            result = llm_service.generate_sync("Test")
            return {"response": result, "provider": llm_service.provider.value}
        
        # Clear cache to ensure fresh instance
        get_default_llm_service.cache_clear()
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "DI response"
        assert data["provider"] == "openai"
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_dependency_with_custom_provider(self, mock_chat_gemini, full_mock_settings):
        """Test DI with custom provider."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Custom provider response"
        mock_instance.invoke.return_value = mock_response
        mock_chat_gemini.return_value = mock_instance
        
        app = FastAPI()
        
        def get_gemini_service():
            return get_llm_service(provider=LLMProvider.GEMINI)
        
        @app.get("/gemini")
        def gemini_route(llm_service: LLMService = Depends(get_gemini_service)):
            result = llm_service.generate_sync("Test")
            return {"response": result, "provider": llm_service.provider.value}
        
        client = TestClient(app)
        response = client.get("/gemini")
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "gemini"


# =============================================================================
# Configuration Integration Tests
# =============================================================================

class TestConfigurationIntegration:
    """Tests for configuration loading and application."""
    
    def test_all_providers_available(self, full_mock_settings):
        """Test that all providers are available."""
        providers = get_available_providers()
        
        assert len(providers) == 5
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.GEMINI in providers
        assert LLMProvider.OLLAMA in providers
        assert LLMProvider.OPENROUTER in providers
        assert LLMProvider.HUGGINGFACE in providers
    
    def test_configured_providers(self, full_mock_settings):
        """Test provider configuration status."""
        assert is_provider_configured(LLMProvider.OPENAI) == True
        assert is_provider_configured(LLMProvider.GEMINI) == True
        assert is_provider_configured(LLMProvider.OLLAMA) == True
    
    def test_unconfigured_provider(self):
        """Test unconfigured provider detection."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai.api_key = ""
            mock_settings.openai.model = "gpt-4"
            
            assert is_provider_configured(LLMProvider.OPENAI) == False


# =============================================================================
# Multi-Model Workflow Tests
# =============================================================================

class TestMultiModelWorkflows:
    """Tests for workflows using multiple models."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_model_switching_same_provider(self, mock_chat_openai, full_mock_settings):
        """Test switching models within same provider."""
        gpt4_response = Mock()
        gpt4_response.content = "GPT-4 response"
        gpt35_response = Mock()
        gpt35_response.content = "GPT-3.5 response"
        
        call_count = 0
        def mock_init(**kwargs):
            nonlocal call_count
            mock_instance = Mock()
            if kwargs.get('model') == 'gpt-4':
                mock_instance.invoke.return_value = gpt4_response
            else:
                mock_instance.invoke.return_value = gpt35_response
            call_count += 1
            return mock_instance
        
        mock_chat_openai.side_effect = mock_init
        
        # Use GPT-4
        gpt4_service = LLMService(provider=LLMProvider.OPENAI)
        gpt4_service = gpt4_service.with_model("gpt-4")
        
        # Use GPT-3.5
        gpt35_service = gpt4_service.with_model("gpt-3.5-turbo")
        
        # Verify different models
        assert gpt4_service.config.model == "gpt-4"
        assert gpt35_service.config.model == "gpt-3.5-turbo"
        
        # Verify they're different instances
        assert gpt4_service is not gpt35_service


# =============================================================================
# Error Recovery Integration Tests
# =============================================================================

class TestErrorRecovery:
    """Tests for error handling and recovery."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_graceful_error_on_api_failure(self, mock_chat_openai, full_mock_settings):
        """Test graceful error handling on API failure."""
        mock_instance = Mock()
        mock_instance.invoke.side_effect = Exception("API Error")
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        with pytest.raises(Exception) as exc_info:
            service.generate_sync("Test")
        
        assert "API Error" in str(exc_info.value)
    
    def test_unconfigured_provider_error(self):
        """Test error when provider is not configured."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai.api_key = "your-openai-api-key"
            mock_settings.openai.model = "gpt-4"
            mock_settings.llm_provider = "openai"
            
            service = LLMService(provider=LLMProvider.OPENAI)
            
            with pytest.raises(AgentError) as exc_info:
                _ = service.llm
            
            assert "OpenAI API key is not configured" in str(exc_info.value.message)


# =============================================================================
# System Prompt Integration Tests
# =============================================================================

class TestSystemPromptIntegration:
    """Tests for system prompt handling."""
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_system_prompt_included(self, mock_chat_openai, full_mock_settings):
        """Test that system prompt is properly included in messages."""
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "Response with system context"
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        result = await service.generate(
            "What's your purpose?",
            system_prompt="You are a helpful coding assistant."
        )
        
        # Verify system message was included
        call_args = mock_instance.ainvoke.call_args
        messages = call_args[0][0]
        
        # First message should be system
        from langchain_core.messages import SystemMessage
        assert isinstance(messages[0], SystemMessage)
        assert "coding assistant" in messages[0].content
    
    @patch("langchain_openai.ChatOpenAI")
    def test_no_system_prompt(self, mock_chat_openai, full_mock_settings):
        """Test generation without system prompt."""
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.content = "Response without system context"
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        service = LLMService(provider=LLMProvider.OPENAI)
        
        result = service.generate_sync("Hello")
        
        # Verify only user message was included
        call_args = mock_instance.invoke.call_args
        messages = call_args[0][0]
        
        # Should only have one message (user)
        assert len(messages) == 1
        from langchain_core.messages import HumanMessage
        assert isinstance(messages[0], HumanMessage)


# =============================================================================
# Service Caching Tests
# =============================================================================

class TestServiceCaching:
    """Tests for service instance caching."""
    
    def test_default_service_cached(self, full_mock_settings):
        """Test that default service is cached."""
        # Clear cache first
        get_default_llm_service.cache_clear()
        
        service1 = get_default_llm_service()
        service2 = get_default_llm_service()
        
        assert service1 is service2
    
    def test_custom_config_not_cached(self, full_mock_settings):
        """Test that custom config creates new instance."""
        config1 = LLMConfig(provider=LLMProvider.OPENAI, temperature=0.5)
        config2 = LLMConfig(provider=LLMProvider.OPENAI, temperature=0.5)
        
        service1 = get_llm_service(config=config1)
        service2 = get_llm_service(config=config2)
        
        # Different configs create different instances
        assert service1 is not service2
    
    def test_cache_clear(self, full_mock_settings):
        """Test cache clearing."""
        # Get cached instance
        service1 = get_default_llm_service()
        
        # Clear cache
        get_default_llm_service.cache_clear()
        
        # Get new instance
        service2 = get_default_llm_service()
        
        # Should be different instances
        assert service1 is not service2


# =============================================================================
# Validation Test (as specified in STORY-3.1.1)
# =============================================================================

class TestStoryValidation:
    """
    Validation tests as specified in STORY-3.1.1.
    
    These tests directly implement the validation requirements from the story.
    """
    
    @patch("langchain_openai.ChatOpenAI")
    def test_llm_provider_openai(self, mock_chat_openai, full_mock_settings):
        """
        Test LLM provider selection for OpenAI.
        
        This is the exact validation test from STORY-3.1.1:
        ```python
        def test_llm_provider_openai():
            os.environ["LLM_PROVIDER"] = "openai"
            llm = get_llm()
            assert isinstance(llm, ChatOpenAI)
        ```
        """
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        # Set provider via mock (simulating env var)
        full_mock_settings.llm_provider = "openai"
        
        # Get LLM
        llm = get_llm()
        
        # Verify OpenAI was instantiated
        mock_chat_openai.assert_called_once()
        assert llm == mock_instance
    
    @patch("langchain_google_genai.ChatGoogleGenerativeAI")
    def test_llm_provider_gemini(self, mock_chat_gemini, full_mock_settings):
        """Test LLM provider selection for Gemini."""
        mock_instance = Mock()
        mock_chat_gemini.return_value = mock_instance
        
        llm = get_llm(provider="gemini")
        
        mock_chat_gemini.assert_called_once()
        assert llm == mock_instance
    
    @patch("langchain_community.chat_models.ChatOllama")
    def test_llm_provider_ollama(self, mock_chat_ollama, full_mock_settings):
        """Test LLM provider selection for Ollama."""
        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance
        
        llm = get_llm(provider="ollama")
        
        mock_chat_ollama.assert_called_once()
        assert llm == mock_instance
