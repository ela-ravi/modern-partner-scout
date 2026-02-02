"""
PartnerScout AI - LLM Provider Abstraction Service (STORY-3.1.1)

Provides a unified interface for interacting with multiple LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini (Gemini Pro)
- Ollama (Local models like Llama2)

The service uses LangChain for consistent interface across providers
and allows switching providers via environment variable.
"""

from abc import ABC, abstractmethod
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Type, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import AgentError


# =============================================================================
# Enums and Constants
# =============================================================================

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class LLMModel(str, Enum):
    """Common model identifiers."""
    # OpenAI Models
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    
    # Gemini Models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"
    
    # Ollama Models (local)
    LLAMA2 = "llama2"
    LLAMA3 = "llama3"
    MISTRAL = "mistral"
    MIXTRAL = "mixtral"
    CODELLAMA = "codellama"


# Default configuration values
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT = 60


# =============================================================================
# LLM Configuration Model
# =============================================================================

class LLMConfig(BaseModel):
    """Configuration for LLM instances."""
    
    provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="The LLM provider to use"
    )
    model: Optional[str] = Field(
        default=None,
        description="Model name/identifier (defaults to provider's configured model)"
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="Temperature for response randomness"
    )
    max_tokens: Optional[int] = Field(
        default=DEFAULT_MAX_TOKENS,
        ge=1,
        description="Maximum tokens in response"
    )
    timeout: int = Field(
        default=DEFAULT_TIMEOUT,
        ge=1,
        description="Request timeout in seconds"
    )
    
    # Additional provider-specific settings
    extra_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional kwargs passed to the provider"
    )


# =============================================================================
# Provider Factory Functions
# =============================================================================

def create_openai_llm(config: LLMConfig) -> BaseChatModel:
    """
    Create an OpenAI Chat LLM instance.
    
    Args:
        config: LLM configuration
        
    Returns:
        ChatOpenAI instance
        
    Raises:
        AgentError: If OpenAI API key is not configured
    """
    from langchain_openai import ChatOpenAI
    
    api_key = settings.openai.api_key
    if not api_key or api_key == "your-openai-api-key":
        raise AgentError(
            message="OpenAI API key is not configured",
            agent_name="llm_service",
            details={"provider": "openai"}
        )
    
    model = config.model or settings.openai.model
    
    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout=config.timeout,
        **config.extra_kwargs
    )


def create_gemini_llm(config: LLMConfig) -> BaseChatModel:
    """
    Create a Google Gemini Chat LLM instance.
    
    Args:
        config: LLM configuration
        
    Returns:
        ChatGoogleGenerativeAI instance
        
    Raises:
        AgentError: If Gemini API key is not configured
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    api_key = settings.gemini.api_key
    if not api_key or api_key == "your-gemini-api-key":
        raise AgentError(
            message="Gemini API key is not configured",
            agent_name="llm_service",
            details={"provider": "gemini"}
        )
    
    model = config.model or settings.gemini.model
    
    return ChatGoogleGenerativeAI(
        google_api_key=api_key,
        model=model,
        temperature=config.temperature,
        max_output_tokens=config.max_tokens,
        timeout=config.timeout,
        **config.extra_kwargs
    )


def create_ollama_llm(config: LLMConfig) -> BaseChatModel:
    """
    Create an Ollama (local) Chat LLM instance.
    
    Args:
        config: LLM configuration
        
    Returns:
        ChatOllama instance
    """
    from langchain_community.chat_models import ChatOllama
    
    base_url = settings.ollama.base_url
    model = config.model or settings.ollama.model
    
    return ChatOllama(
        base_url=base_url,
        model=model,
        temperature=config.temperature,
        num_predict=config.max_tokens,
        **config.extra_kwargs
    )


# Provider factory registry
_PROVIDER_FACTORIES = {
    LLMProvider.OPENAI: create_openai_llm,
    LLMProvider.GEMINI: create_gemini_llm,
    LLMProvider.OLLAMA: create_ollama_llm,
}


# =============================================================================
# Main LLM Service Class
# =============================================================================

class LLMService:
    """
    LLM Service providing a unified interface for multiple LLM providers.
    
    This service abstracts the complexity of different LLM providers
    and provides a consistent API for:
    - Text generation
    - Chat completion
    - Structured output parsing
    - Chain building
    
    Example:
        ```python
        # Using default provider from environment
        llm_service = LLMService()
        response = await llm_service.generate("Tell me a joke")
        
        # Using specific provider
        llm_service = LLMService(provider=LLMProvider.GEMINI)
        
        # Using custom configuration
        config = LLMConfig(provider=LLMProvider.OPENAI, temperature=0.5)
        llm_service = LLMService(config=config)
        ```
    """
    
    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        provider: Optional[Union[LLMProvider, str]] = None,
    ):
        """
        Initialize the LLM service.
        
        Args:
            config: Full LLM configuration (takes precedence)
            provider: Provider to use (if config not provided)
        """
        if config:
            self._config = config
        else:
            # Determine provider from argument or environment
            if provider:
                provider_enum = (
                    provider if isinstance(provider, LLMProvider)
                    else LLMProvider(provider.lower())
                )
            else:
                provider_enum = LLMProvider(settings.llm_provider.lower())
            
            self._config = LLMConfig(provider=provider_enum)
        
        self._llm: Optional[BaseChatModel] = None
    
    @property
    def config(self) -> LLMConfig:
        """Get current configuration."""
        return self._config
    
    @property
    def provider(self) -> LLMProvider:
        """Get current provider."""
        return self._config.provider
    
    @property
    def model(self) -> str:
        """Get current model name."""
        if self._config.model:
            return self._config.model
        
        # Return default model based on provider
        if self._config.provider == LLMProvider.OPENAI:
            return settings.openai.model
        elif self._config.provider == LLMProvider.GEMINI:
            return settings.gemini.model
        else:
            return settings.ollama.model
    
    @property
    def llm(self) -> BaseChatModel:
        """
        Get or create the LLM instance (lazy initialization).
        
        Returns:
            BaseChatModel instance for the configured provider
        """
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm
    
    def _create_llm(self) -> BaseChatModel:
        """
        Create LLM instance using the appropriate factory.
        
        Returns:
            BaseChatModel instance
            
        Raises:
            AgentError: If provider is not supported
        """
        factory = _PROVIDER_FACTORIES.get(self._config.provider)
        if not factory:
            raise AgentError(
                message=f"Unsupported LLM provider: {self._config.provider}",
                agent_name="llm_service",
                details={"provider": self._config.provider.value}
            )
        return factory(self._config)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            **kwargs: Additional arguments passed to the LLM
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = await self.llm.ainvoke(messages, **kwargs)
        return response.content
    
    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text synchronously.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            **kwargs: Additional arguments passed to the LLM
            
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(messages, **kwargs)
        return response.content
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Have a chat conversation with the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Roles can be: 'system', 'user', 'assistant'
            **kwargs: Additional arguments passed to the LLM
            
        Returns:
            Assistant's response
        """
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user").lower()
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                from langchain_core.messages import AIMessage
                langchain_messages.append(AIMessage(content=content))
            else:  # user or default
                langchain_messages.append(HumanMessage(content=content))
        
        response = await self.llm.ainvoke(langchain_messages, **kwargs)
        return response.content
    
    def create_chain(
        self,
        prompt_template: ChatPromptTemplate,
        output_parser: Optional[Any] = None
    ) -> Any:
        """
        Create a LangChain chain with the LLM.
        
        Args:
            prompt_template: The prompt template to use
            output_parser: Optional output parser (defaults to StrOutputParser)
            
        Returns:
            LangChain chain (Runnable)
        """
        if output_parser is None:
            output_parser = StrOutputParser()
        
        return prompt_template | self.llm | output_parser
    
    def with_temperature(self, temperature: float) -> "LLMService":
        """
        Create a new service instance with different temperature.
        
        Args:
            temperature: New temperature value (0.0 to 2.0)
            
        Returns:
            New LLMService instance with updated temperature
        """
        new_config = self._config.model_copy(update={"temperature": temperature})
        return LLMService(config=new_config)
    
    def with_model(self, model: str) -> "LLMService":
        """
        Create a new service instance with different model.
        
        Args:
            model: New model name
            
        Returns:
            New LLMService instance with updated model
        """
        new_config = self._config.model_copy(update={"model": model})
        return LLMService(config=new_config)
    
    def __repr__(self) -> str:
        return f"LLMService(provider={self.provider.value}, model={self.model})"


# =============================================================================
# Factory Functions (Convenience)
# =============================================================================

def get_llm(
    provider: Optional[Union[LLMProvider, str]] = None,
    **kwargs
) -> BaseChatModel:
    """
    Get an LLM instance for the specified provider.
    
    This is a convenience function that returns just the LangChain
    LLM instance without the service wrapper.
    
    Args:
        provider: Provider to use (defaults to LLM_PROVIDER env var)
        **kwargs: Additional configuration passed to LLMConfig
        
    Returns:
        BaseChatModel instance
        
    Example:
        ```python
        # Using default provider
        llm = get_llm()
        
        # Using specific provider
        llm = get_llm("gemini")
        
        # With custom temperature
        llm = get_llm(temperature=0.5)
        ```
    """
    if provider:
        provider_enum = (
            provider if isinstance(provider, LLMProvider)
            else LLMProvider(provider.lower())
        )
    else:
        provider_enum = LLMProvider(settings.llm_provider.lower())
    
    config = LLMConfig(provider=provider_enum, **kwargs)
    factory = _PROVIDER_FACTORIES.get(provider_enum)
    
    if not factory:
        raise AgentError(
            message=f"Unsupported LLM provider: {provider_enum}",
            agent_name="llm_service",
            details={"provider": provider_enum.value}
        )
    
    return factory(config)


def get_openai_llm(**kwargs) -> BaseChatModel:
    """
    Get an OpenAI LLM instance.
    
    Args:
        **kwargs: Configuration options passed to LLMConfig
        
    Returns:
        ChatOpenAI instance
    """
    return get_llm(LLMProvider.OPENAI, **kwargs)


def get_gemini_llm(**kwargs) -> BaseChatModel:
    """
    Get a Gemini LLM instance.
    
    Args:
        **kwargs: Configuration options passed to LLMConfig
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return get_llm(LLMProvider.GEMINI, **kwargs)


def get_ollama_llm(**kwargs) -> BaseChatModel:
    """
    Get an Ollama LLM instance.
    
    Args:
        **kwargs: Configuration options passed to LLMConfig
        
    Returns:
        ChatOllama instance
    """
    return get_llm(LLMProvider.OLLAMA, **kwargs)


@lru_cache()
def get_default_llm_service() -> LLMService:
    """
    Get a cached default LLM service instance.
    
    Uses LRU cache to ensure only one instance is created
    for the default configuration.
    
    Returns:
        LLMService instance with default configuration
    """
    return LLMService()


def get_llm_service(
    provider: Optional[Union[LLMProvider, str]] = None,
    config: Optional[LLMConfig] = None,
) -> LLMService:
    """
    Get an LLM service instance.
    
    Dependency injection factory for FastAPI.
    
    Args:
        provider: Optional provider override
        config: Optional full configuration override
        
    Returns:
        LLMService instance
    """
    if config:
        return LLMService(config=config)
    elif provider:
        return LLMService(provider=provider)
    else:
        return get_default_llm_service()


# =============================================================================
# Utility Functions
# =============================================================================

def get_available_providers() -> List[LLMProvider]:
    """
    Get list of available LLM providers.
    
    Returns:
        List of LLMProvider enum values
    """
    return list(LLMProvider)


def get_provider_info(provider: Union[LLMProvider, str]) -> Dict[str, Any]:
    """
    Get information about a specific provider.
    
    Args:
        provider: Provider to get info for
        
    Returns:
        Dictionary with provider information
    """
    if isinstance(provider, str):
        provider = LLMProvider(provider.lower())
    
    info = {
        "provider": provider.value,
        "configured": False,
        "default_model": None,
    }
    
    if provider == LLMProvider.OPENAI:
        info["configured"] = bool(
            settings.openai.api_key and 
            settings.openai.api_key != "your-openai-api-key"
        )
        info["default_model"] = settings.openai.model
        info["models"] = [
            LLMModel.GPT_4_TURBO.value,
            LLMModel.GPT_4.value,
            LLMModel.GPT_35_TURBO.value,
            LLMModel.GPT_4O.value,
            LLMModel.GPT_4O_MINI.value,
        ]
    elif provider == LLMProvider.GEMINI:
        info["configured"] = bool(
            settings.gemini.api_key and 
            settings.gemini.api_key != "your-gemini-api-key"
        )
        info["default_model"] = settings.gemini.model
        info["models"] = [
            LLMModel.GEMINI_PRO.value,
            LLMModel.GEMINI_PRO_VISION.value,
            LLMModel.GEMINI_15_PRO.value,
            LLMModel.GEMINI_15_FLASH.value,
        ]
    elif provider == LLMProvider.OLLAMA:
        info["configured"] = True  # Ollama doesn't require API key
        info["default_model"] = settings.ollama.model
        info["base_url"] = settings.ollama.base_url
        info["models"] = [
            LLMModel.LLAMA2.value,
            LLMModel.LLAMA3.value,
            LLMModel.MISTRAL.value,
            LLMModel.MIXTRAL.value,
            LLMModel.CODELLAMA.value,
        ]
    
    return info


def is_provider_configured(provider: Union[LLMProvider, str]) -> bool:
    """
    Check if a provider is properly configured.
    
    Args:
        provider: Provider to check
        
    Returns:
        True if provider is configured, False otherwise
    """
    info = get_provider_info(provider)
    return info["configured"]


def get_current_provider() -> LLMProvider:
    """
    Get the currently configured default provider.
    
    Returns:
        LLMProvider enum value
    """
    return LLMProvider(settings.llm_provider.lower())
