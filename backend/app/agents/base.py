"""
PartnerScout AI - Base Agent Class (STORY-3.3.1)

Abstract base class for all AI agents providing common functionality:
- Prompt loading from external files
- LLM chain building with LangChain
- Structured output parsing
- Error handling and logging
- Configuration management

All agents (BrandAnalyzer, Discovery, Scorer, EmailComposer) should inherit
from this base class to ensure consistent behavior and interface.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableSequence
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import AgentError
from app.core.settings import get_agent_config, get_agents_config
from app.prompts.loader import clear_prompt_cache, load_prompt, load_prompts
from app.services.llm_service import LLMConfig, LLMProvider, LLMService, get_llm_service


# Type variables for generic typing
InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


# =============================================================================
# Agent Configuration Model
# =============================================================================

class AgentConfig(BaseModel):
    """Configuration model for an agent instance."""
    
    name: str = Field(..., description="Agent name identifier")
    description: Optional[str] = Field(None, description="Agent description")
    enabled: bool = Field(default=True, description="Whether agent is enabled")
    
    # LLM Settings
    model: Optional[str] = Field(None, description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=2048, ge=1, description="Maximum tokens for response")
    
    # Prompt paths
    system_prompt_path: Optional[str] = Field(None, description="Path to system prompt")
    user_prompt_path: Optional[str] = Field(None, description="Path to user prompt")
    
    # Additional settings
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=60, ge=1, description="Operation timeout")
    
    # Extra configuration (agent-specific)
    extra: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific config")


class AgentMetrics(BaseModel):
    """Metrics collected during agent execution."""
    
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # LLM metrics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Execution metrics
    retries: int = 0
    success: bool = False
    error_message: Optional[str] = None


class AgentResult(BaseModel, Generic[OutputT]):
    """Standard result wrapper for agent outputs."""
    
    agent_name: str
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    metrics: Optional[AgentMetrics] = None
    
    class Config:
        arbitrary_types_allowed = True


# =============================================================================
# Base Agent Abstract Class
# =============================================================================

class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all PartnerScout AI agents.
    
    Provides common functionality for:
    - Loading prompts from external files
    - Building LangChain chains for LLM interaction
    - Structured output parsing
    - Metrics collection and logging
    - Error handling
    
    Subclasses must implement:
    - agent_name (class attribute): Unique identifier for the agent
    - run(input_data): Main execution method
    
    Example:
        ```python
        class BrandAnalyzerAgent(BaseAgent[BrandAnalyzerRequest, BrandAnalyzerResponse]):
            agent_name = "brand_analyzer"
            
            async def run(self, input_data: BrandAnalyzerRequest) -> BrandAnalyzerResponse:
                # Agent implementation
                pass
        ```
    """
    
    # Class attributes to be overridden by subclasses
    agent_name: str = "base_agent"
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm_service: Optional[LLMService] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the base agent.
        
        Args:
            config: Agent configuration (loads from YAML if not provided)
            llm_service: LLM service instance (creates new if not provided)
            logger: Logger instance (creates new if not provided)
        """
        # Setup logger
        self._logger = logger or logging.getLogger(f"agent.{self.agent_name}")
        
        # Load configuration
        self._config = config or self._load_config()
        
        # Validate agent is enabled
        if not self._config.enabled:
            self._logger.warning(f"Agent '{self.agent_name}' is disabled in configuration")
        
        # Initialize LLM service
        self._llm_service = llm_service or self._create_llm_service()
        
        # Load prompts
        self._system_prompt: Optional[str] = None
        self._user_prompt: Optional[str] = None
        self._load_prompts()
        
        # Initialize metrics
        self._current_metrics: Optional[AgentMetrics] = None
        
        self._logger.debug(f"Initialized {self.agent_name} agent")
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def config(self) -> AgentConfig:
        """Get agent configuration."""
        return self._config
    
    @property
    def llm(self) -> BaseChatModel:
        """Get the underlying LLM instance."""
        return self._llm_service.llm
    
    @property
    def llm_service(self) -> LLMService:
        """Get the LLM service instance."""
        return self._llm_service
    
    @property
    def system_prompt(self) -> Optional[str]:
        """Get the system prompt."""
        return self._system_prompt
    
    @property
    def user_prompt(self) -> Optional[str]:
        """Get the user prompt template."""
        return self._user_prompt
    
    @property
    def is_enabled(self) -> bool:
        """Check if agent is enabled."""
        return self._config.enabled
    
    # =========================================================================
    # Configuration Loading (SUB-3.3.1.1.3)
    # =========================================================================
    
    def _load_config(self) -> AgentConfig:
        """
        Load agent configuration from YAML file.
        
        Returns:
            AgentConfig instance with loaded settings
            
        Raises:
            AgentError: If configuration cannot be loaded
        """
        try:
            # Try to load from YAML config
            yaml_config = get_agent_config(self.agent_name)
            
            # Extract prompt paths
            prompts_config = yaml_config.get("prompts", {})
            
            return AgentConfig(
                name=yaml_config.get("name", self.agent_name),
                description=yaml_config.get("description"),
                enabled=yaml_config.get("enabled", True),
                model=yaml_config.get("model"),
                temperature=yaml_config.get("temperature", 0.7),
                max_tokens=yaml_config.get("max_tokens", 2048),
                system_prompt_path=prompts_config.get("system"),
                user_prompt_path=prompts_config.get("user"),
                max_retries=yaml_config.get("max_retries", 3),
                timeout_seconds=yaml_config.get("timeout_seconds", 60),
                extra=yaml_config,
            )
        except Exception as e:
            self._logger.warning(
                f"Could not load config for '{self.agent_name}', using defaults: {e}"
            )
            # Return default configuration
            return AgentConfig(
                name=self.agent_name,
                description=f"Default configuration for {self.agent_name}",
            )
    
    def _create_llm_service(self) -> LLMService:
        """
        Create an LLM service instance based on configuration.
        
        Returns:
            LLMService instance configured for this agent
        """
        llm_config = LLMConfig(
            provider=LLMProvider(settings.llm_provider.lower()),
            model=self._config.model,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
            timeout=self._config.timeout_seconds,
        )
        return LLMService(config=llm_config)
    
    # =========================================================================
    # Prompt Loading (SUB-3.3.1.1.3)
    # =========================================================================
    
    def _load_prompts(self) -> None:
        """
        Load system and user prompts from external files.
        
        Prompts are loaded using the prompt loader module and cached
        for subsequent use.
        
        Raises:
            AgentError: If prompts cannot be loaded
        """
        try:
            prompts = load_prompts(self.agent_name)
            self._system_prompt = prompts.get("system")
            self._user_prompt = prompts.get("user")
            
            self._logger.debug(
                f"Loaded prompts for {self.agent_name}: "
                f"system={len(self._system_prompt or '')} chars, "
                f"user={len(self._user_prompt or '')} chars"
            )
        except Exception as e:
            self._logger.error(f"Failed to load prompts for {self.agent_name}: {e}")
            raise AgentError(
                message=f"Failed to load prompts for agent '{self.agent_name}'",
                agent_name=self.agent_name,
                details={"error": str(e)},
            )
    
    def reload_prompts(self) -> None:
        """
        Reload prompts from files (useful for hot-reloading during development).
        
        Clears the prompt cache and reloads from disk.
        """
        clear_prompt_cache()
        self._load_prompts()
        self._logger.info(f"Reloaded prompts for {self.agent_name}")
    
    def get_formatted_system_prompt(
        self,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get the system prompt with optional variable substitution.
        
        Args:
            variables: Dictionary of variables to substitute in the prompt
            
        Returns:
            Formatted system prompt string
        """
        if not self._system_prompt:
            return ""
        
        if variables:
            try:
                return self._system_prompt.format(**variables)
            except KeyError:
                return self._system_prompt
        
        return self._system_prompt
    
    def get_formatted_user_prompt(
        self,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get the user prompt with optional variable substitution.
        
        Args:
            variables: Dictionary of variables to substitute in the prompt
            
        Returns:
            Formatted user prompt string
        """
        if not self._user_prompt:
            return ""
        
        if variables:
            try:
                return self._user_prompt.format(**variables)
            except KeyError:
                return self._user_prompt
        
        return self._user_prompt
    
    # =========================================================================
    # Chain Building Methods (SUB-3.3.1.1.4)
    # =========================================================================
    
    def build_prompt_template(
        self,
        input_variables: Optional[List[str]] = None,
    ) -> ChatPromptTemplate:
        """
        Build a ChatPromptTemplate from loaded prompts.
        
        Args:
            input_variables: List of variable names expected in the user prompt
            
        Returns:
            ChatPromptTemplate ready for chain composition
        """
        messages = []
        
        # Add system message if available
        if self._system_prompt:
            messages.append(SystemMessagePromptTemplate.from_template(
                self._system_prompt,
                template_format="f-string"
            ))
        
        # Add user message template
        if self._user_prompt:
            messages.append(HumanMessagePromptTemplate.from_template(
                self._user_prompt,
                template_format="f-string"
            ))
        
        return ChatPromptTemplate.from_messages(messages)
    
    def build_chain(
        self,
        output_parser: Optional[BaseOutputParser] = None,
        prompt_template: Optional[ChatPromptTemplate] = None,
    ) -> RunnableSequence:
        """
        Build a complete LangChain chain for this agent.
        
        Creates a chain: prompt_template | llm | output_parser
        
        Args:
            output_parser: Output parser to use (defaults to StrOutputParser)
            prompt_template: Custom prompt template (uses loaded prompts if not provided)
            
        Returns:
            RunnableSequence that can be invoked with input variables
        """
        # Use provided or default prompt template
        template = prompt_template or self.build_prompt_template()
        
        # Use provided or default output parser
        parser = output_parser or StrOutputParser()
        
        # Build the chain: prompt | llm | parser
        chain = template | self.llm | parser
        
        self._logger.debug(f"Built chain for {self.agent_name}")
        return chain
    
    def build_json_chain(
        self,
        pydantic_schema: Optional[Type[BaseModel]] = None,
        prompt_template: Optional[ChatPromptTemplate] = None,
    ) -> RunnableSequence:
        """
        Build a chain that outputs parsed JSON.
        
        Args:
            pydantic_schema: Optional Pydantic model for structured output
            prompt_template: Custom prompt template
            
        Returns:
            RunnableSequence that outputs parsed JSON/dict
        """
        # Use JSON output parser, optionally with Pydantic schema
        if pydantic_schema:
            parser = JsonOutputParser(pydantic_object=pydantic_schema)
        else:
            parser = JsonOutputParser()
        
        return self.build_chain(output_parser=parser, prompt_template=prompt_template)
    
    # =========================================================================
    # Execution Helpers
    # =========================================================================
    
    async def invoke_chain(
        self,
        chain: RunnableSequence,
        input_data: Dict[str, Any],
    ) -> Any:
        """
        Invoke a chain with error handling and metrics collection.
        
        Args:
            chain: The chain to invoke
            input_data: Input variables for the chain
            
        Returns:
            Chain output
            
        Raises:
            AgentError: If chain invocation fails
        """
        start_time = time.time()
        
        try:
            result = await chain.ainvoke(input_data)
            
            self._logger.debug(
                f"Chain invocation completed in {time.time() - start_time:.2f}s"
            )
            return result
            
        except Exception as e:
            self._logger.error(f"Chain invocation failed: {e}")
            raise AgentError(
                message=f"Agent '{self.agent_name}' chain invocation failed",
                agent_name=self.agent_name,
                details={"error": str(e), "input_keys": list(input_data.keys())},
            )
    
    def invoke_chain_sync(
        self,
        chain: RunnableSequence,
        input_data: Dict[str, Any],
    ) -> Any:
        """
        Synchronously invoke a chain with error handling.
        
        Args:
            chain: The chain to invoke
            input_data: Input variables for the chain
            
        Returns:
            Chain output
            
        Raises:
            AgentError: If chain invocation fails
        """
        start_time = time.time()
        
        try:
            result = chain.invoke(input_data)
            
            self._logger.debug(
                f"Sync chain invocation completed in {time.time() - start_time:.2f}s"
            )
            return result
            
        except Exception as e:
            self._logger.error(f"Sync chain invocation failed: {e}")
            raise AgentError(
                message=f"Agent '{self.agent_name}' chain invocation failed",
                agent_name=self.agent_name,
                details={"error": str(e), "input_keys": list(input_data.keys())},
            )
    
    async def generate_response(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a simple text response from the LLM.
        
        Args:
            user_prompt: The user's prompt/question
            system_prompt: Optional system prompt (uses loaded prompt if not provided)
            **kwargs: Additional arguments passed to LLM
            
        Returns:
            Generated text response
        """
        system = system_prompt or self._system_prompt
        return await self._llm_service.generate(
            prompt=user_prompt,
            system_prompt=system,
            **kwargs
        )
    
    # =========================================================================
    # Metrics and Logging
    # =========================================================================
    
    def _start_metrics(self) -> AgentMetrics:
        """Start collecting metrics for a run."""
        self._current_metrics = AgentMetrics()
        return self._current_metrics
    
    def _complete_metrics(
        self,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AgentMetrics:
        """Complete metrics collection."""
        if self._current_metrics:
            self._current_metrics.completed_at = datetime.now(timezone.utc)
            self._current_metrics.duration_seconds = (
                self._current_metrics.completed_at - self._current_metrics.started_at
            ).total_seconds()
            self._current_metrics.success = success
            self._current_metrics.error_message = error_message
        
        return self._current_metrics or AgentMetrics(success=success)
    
    # =========================================================================
    # Abstract Methods (SUB-3.3.1.1.5)
    # =========================================================================
    
    @abstractmethod
    async def run(self, input_data: InputT) -> OutputT:
        """
        Execute the agent's main task.
        
        This method must be implemented by all subclasses. It receives
        typed input data and returns typed output data.
        
        Args:
            input_data: Agent-specific input data model
            
        Returns:
            Agent-specific output data model
            
        Raises:
            AgentError: If execution fails
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    # =========================================================================
    # Optional Override Methods
    # =========================================================================
    
    async def validate_input(self, input_data: InputT) -> bool:
        """
        Validate input data before processing.
        
        Override this method to add custom validation logic.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, raises exception if invalid
        """
        return True
    
    async def preprocess(self, input_data: InputT) -> Dict[str, Any]:
        """
        Preprocess input data before running the agent.
        
        Override this method to add custom preprocessing logic.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Preprocessed data dictionary for chain input
        """
        if isinstance(input_data, BaseModel):
            return input_data.model_dump()
        return dict(input_data) if input_data else {}
    
    async def postprocess(self, raw_output: Any) -> OutputT:
        """
        Postprocess the raw output from the LLM.
        
        Override this method to add custom postprocessing logic.
        
        Args:
            raw_output: Raw output from LLM chain
            
        Returns:
            Processed output data
        """
        return raw_output
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.agent_name}, "
            f"enabled={self.is_enabled}, "
            f"model={self._llm_service.model})"
        )
    
    def __str__(self) -> str:
        return f"{self._config.name or self.agent_name} Agent"
