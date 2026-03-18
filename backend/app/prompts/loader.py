"""
PartnerScout AI - Prompt Management System (STORY-3.1.2)

Provides functionality to load and manage LLM prompts from external files.
This allows prompts to be modified without code changes, enabling:
- Easy iteration on prompt engineering
- A/B testing of different prompts
- Version control of prompts separate from code
- Dynamic prompt loading based on agent configuration

Usage:
    from app.prompts.loader import load_prompt, load_prompts
    
    # Load a single prompt
    system_prompt = load_prompt("brand_analyzer", "system")
    
    # Load both system and user prompts
    prompts = load_prompts("brand_analyzer")
    # Returns: {"system": "...", "user": "..."}
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.core.exceptions import AgentError


# =============================================================================
# Constants
# =============================================================================

# Base directory for prompt files
PROMPTS_DIR = Path(__file__).parent

# Default prompt file names
DEFAULT_SYSTEM_PROMPT_FILE = "system.txt"
DEFAULT_USER_PROMPT_FILE = "user.txt"

# Valid prompt types
VALID_PROMPT_TYPES = {"system", "user"}

# Registered agents with their prompt configurations
REGISTERED_AGENTS = {
    "brand_analyzer": {
        "system": "brand_analyzer/system.txt",
        "user": "brand_analyzer/user.txt",
    },
    "discovery": {
        "system": "discovery/system.txt",
        "user": "discovery/user.txt",
    },
    "scorer": {
        "system": "scorer/system.txt",
        "user": "scorer/user.txt",
    },
    "email_composer": {
        "system": "email_composer/system.txt",
        "user": "email_composer/user.txt",
    },
    "contact_enricher": {
        "system": "contact_enricher/system.txt",
        "user": "contact_enricher/user.txt",
    },
}


# =============================================================================
# Exceptions
# =============================================================================

class PromptLoadError(AgentError):
    """Exception raised when a prompt file cannot be loaded."""
    
    def __init__(
        self,
        message: str,
        agent_name: str,
        prompt_type: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        details = {}
        if prompt_type:
            details["prompt_type"] = prompt_type
        if file_path:
            details["file_path"] = file_path
        
        super().__init__(
            message=message,
            agent_name=agent_name,
            details=details if details else None
        )


class PromptNotFoundError(PromptLoadError):
    """Exception raised when a prompt file does not exist."""
    pass


class InvalidPromptTypeError(PromptLoadError):
    """Exception raised when an invalid prompt type is specified."""
    pass


class InvalidAgentError(PromptLoadError):
    """Exception raised when an invalid agent name is specified."""
    pass


# =============================================================================
# Core Functions
# =============================================================================

def load_prompt(
    agent_name: str,
    prompt_type: str,
    variables: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> str:
    """
    Load a prompt file for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., "brand_analyzer", "scorer")
        prompt_type: Type of prompt - either "system" or "user"
        variables: Optional dictionary of variables to substitute in the prompt
        use_cache: Whether to use cached prompts (default: True)
        
    Returns:
        The prompt content as a string, with optional variable substitution
        
    Raises:
        InvalidAgentError: If agent_name is not registered
        InvalidPromptTypeError: If prompt_type is not valid
        PromptNotFoundError: If the prompt file doesn't exist
        PromptLoadError: If the file cannot be read
        
    Example:
        >>> system = load_prompt("brand_analyzer", "system")
        >>> user = load_prompt("brand_analyzer", "user", variables={"brand": "Nike"})
    """
    # Validate agent name
    if agent_name not in REGISTERED_AGENTS:
        raise InvalidAgentError(
            message=f"Unknown agent: '{agent_name}'. Valid agents: {list(REGISTERED_AGENTS.keys())}",
            agent_name=agent_name,
        )
    
    # Validate prompt type
    prompt_type_lower = prompt_type.lower()
    if prompt_type_lower not in VALID_PROMPT_TYPES:
        raise InvalidPromptTypeError(
            message=f"Invalid prompt type: '{prompt_type}'. Valid types: {list(VALID_PROMPT_TYPES)}",
            agent_name=agent_name,
            prompt_type=prompt_type,
        )
    
    # Get the prompt file path
    relative_path = REGISTERED_AGENTS[agent_name][prompt_type_lower]
    file_path = PROMPTS_DIR / relative_path
    
    # Load the prompt (with or without cache)
    if use_cache:
        content = _load_prompt_cached(str(file_path), agent_name, prompt_type_lower)
    else:
        content = _load_prompt_from_file(file_path, agent_name, prompt_type_lower)
    
    # Apply variable substitution if provided
    if variables:
        content = _substitute_variables(content, variables)
    
    return content


def load_prompts(
    agent_name: str,
    variables: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
) -> Dict[str, str]:
    """
    Load both system and user prompts for an agent.
    
    Args:
        agent_name: Name of the agent (e.g., "brand_analyzer", "scorer")
        variables: Optional dictionary of variables to substitute in both prompts
        use_cache: Whether to use cached prompts (default: True)
        
    Returns:
        Dictionary with "system" and "user" keys containing the prompts
        
    Raises:
        InvalidAgentError: If agent_name is not registered
        PromptNotFoundError: If any prompt file doesn't exist
        PromptLoadError: If any file cannot be read
        
    Example:
        >>> prompts = load_prompts("brand_analyzer")
        >>> print(prompts["system"])
        >>> print(prompts["user"])
    """
    return {
        "system": load_prompt(agent_name, "system", variables, use_cache),
        "user": load_prompt(agent_name, "user", variables, use_cache),
    }


def load_prompt_from_path(
    file_path: Union[str, Path],
    variables: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Load a prompt from an arbitrary file path.
    
    This function allows loading prompts from any location,
    useful for custom or experimental prompts.
    
    Args:
        file_path: Path to the prompt file
        variables: Optional dictionary of variables to substitute
        
    Returns:
        The prompt content as a string
        
    Raises:
        PromptNotFoundError: If the file doesn't exist
        PromptLoadError: If the file cannot be read or is empty
    """
    path = Path(file_path)
    
    if not path.exists():
        raise PromptNotFoundError(
            message=f"Prompt file not found: {file_path}",
            agent_name="custom",
            file_path=str(file_path),
        )
    
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise PromptLoadError(
            message=f"Failed to read prompt file: {e}",
            agent_name="custom",
            file_path=str(file_path),
        )
    
    # Validate that the prompt is not empty
    content = content.strip()
    if not content:
        raise PromptLoadError(
            message=f"Prompt file is empty: {file_path}",
            agent_name="custom",
            file_path=str(file_path),
        )
    
    if variables:
        content = _substitute_variables(content, variables)
    
    return content


# =============================================================================
# Cache Management
# =============================================================================

@lru_cache(maxsize=32)
def _load_prompt_cached(
    file_path: str,
    agent_name: str,
    prompt_type: str,
) -> str:
    """
    Load a prompt file with caching.
    
    Uses LRU cache to avoid repeated file system access.
    Cache key is the file path string.
    """
    return _load_prompt_from_file(Path(file_path), agent_name, prompt_type)


def clear_prompt_cache() -> None:
    """
    Clear the prompt cache.
    
    Call this when prompts have been modified and need to be reloaded.
    """
    _load_prompt_cached.cache_clear()


def get_cache_info() -> Dict[str, Any]:
    """
    Get information about the prompt cache.
    
    Returns:
        Dictionary with cache statistics
    """
    info = _load_prompt_cached.cache_info()
    return {
        "hits": info.hits,
        "misses": info.misses,
        "maxsize": info.maxsize,
        "currsize": info.currsize,
    }


# =============================================================================
# Internal Helper Functions
# =============================================================================

def _load_prompt_from_file(
    file_path: Path,
    agent_name: str,
    prompt_type: str,
) -> str:
    """
    Load prompt content from a file.
    
    Args:
        file_path: Path to the prompt file
        agent_name: Name of the agent (for error messages)
        prompt_type: Type of prompt (for error messages)
        
    Returns:
        The prompt content as a string
        
    Raises:
        PromptNotFoundError: If the file doesn't exist
        PromptLoadError: If the file cannot be read
    """
    if not file_path.exists():
        raise PromptNotFoundError(
            message=f"Prompt file not found for agent '{agent_name}'",
            agent_name=agent_name,
            prompt_type=prompt_type,
            file_path=str(file_path),
        )
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except PermissionError:
        raise PromptLoadError(
            message=f"Permission denied reading prompt file for agent '{agent_name}'",
            agent_name=agent_name,
            prompt_type=prompt_type,
            file_path=str(file_path),
        )
    except UnicodeDecodeError:
        raise PromptLoadError(
            message=f"Invalid encoding in prompt file for agent '{agent_name}' (expected UTF-8)",
            agent_name=agent_name,
            prompt_type=prompt_type,
            file_path=str(file_path),
        )
    except Exception as e:
        raise PromptLoadError(
            message=f"Failed to read prompt file: {e}",
            agent_name=agent_name,
            prompt_type=prompt_type,
            file_path=str(file_path),
        )
    
    # Validate that the prompt is not empty
    content = content.strip()
    if not content:
        raise PromptLoadError(
            message=f"Prompt file is empty for agent '{agent_name}'",
            agent_name=agent_name,
            prompt_type=prompt_type,
            file_path=str(file_path),
        )
    
    return content


def _substitute_variables(
    content: str,
    variables: Dict[str, Any],
) -> str:
    """
    Substitute variables in a prompt template.
    
    Uses Python's str.format() for substitution.
    Variables in the prompt should be wrapped in curly braces: {variable_name}
    
    Args:
        content: The prompt content with variable placeholders
        variables: Dictionary of variable names and values
        
    Returns:
        The prompt with variables substituted
    """
    try:
        return content.format(**variables)
    except KeyError as e:
        # Return original content if variable is missing
        # This allows for optional variables
        return content
    except Exception:
        # Return original content on any formatting error
        return content


# =============================================================================
# Utility Functions
# =============================================================================

def get_registered_agents() -> list:
    """
    Get list of all registered agent names.
    
    Returns:
        List of agent names that have registered prompts
    """
    return list(REGISTERED_AGENTS.keys())


def get_agent_prompt_paths(agent_name: str) -> Dict[str, Path]:
    """
    Get the file paths for an agent's prompts.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Dictionary with "system" and "user" keys containing Path objects
        
    Raises:
        InvalidAgentError: If agent_name is not registered
    """
    if agent_name not in REGISTERED_AGENTS:
        raise InvalidAgentError(
            message=f"Unknown agent: '{agent_name}'",
            agent_name=agent_name,
        )
    
    return {
        "system": PROMPTS_DIR / REGISTERED_AGENTS[agent_name]["system"],
        "user": PROMPTS_DIR / REGISTERED_AGENTS[agent_name]["user"],
    }


def prompt_exists(agent_name: str, prompt_type: str) -> bool:
    """
    Check if a prompt file exists.
    
    Args:
        agent_name: Name of the agent
        prompt_type: Type of prompt ("system" or "user")
        
    Returns:
        True if the prompt file exists, False otherwise
    """
    try:
        paths = get_agent_prompt_paths(agent_name)
        return paths[prompt_type.lower()].exists()
    except (InvalidAgentError, KeyError):
        return False


def validate_all_prompts() -> Dict[str, Dict[str, bool]]:
    """
    Validate that all registered prompt files exist.
    
    Returns:
        Dictionary mapping agent names to their prompt validation status
        
    Example:
        >>> status = validate_all_prompts()
        >>> print(status)
        {
            "brand_analyzer": {"system": True, "user": True},
            "scorer": {"system": True, "user": False},
            ...
        }
    """
    results = {}
    for agent_name in REGISTERED_AGENTS:
        results[agent_name] = {
            "system": prompt_exists(agent_name, "system"),
            "user": prompt_exists(agent_name, "user"),
        }
    return results


def get_prompts_directory() -> Path:
    """
    Get the base directory for prompt files.
    
    Returns:
        Path to the prompts directory
    """
    return PROMPTS_DIR


# =============================================================================
# Registration Functions (for extending with custom agents)
# =============================================================================

def register_agent_prompts(
    agent_name: str,
    system_path: str,
    user_path: str,
) -> None:
    """
    Register prompts for a custom agent.
    
    This allows extending the prompt system with additional agents
    without modifying the core module.
    
    Args:
        agent_name: Name of the agent to register
        system_path: Relative path to system prompt file
        user_path: Relative path to user prompt file
        
    Example:
        >>> register_agent_prompts(
        ...     "custom_agent",
        ...     "custom_agent/system.txt",
        ...     "custom_agent/user.txt"
        ... )
    """
    REGISTERED_AGENTS[agent_name] = {
        "system": system_path,
        "user": user_path,
    }
    # Clear cache to ensure new agent prompts are loaded fresh
    clear_prompt_cache()


def unregister_agent(agent_name: str) -> bool:
    """
    Unregister an agent's prompts.
    
    Args:
        agent_name: Name of the agent to unregister
        
    Returns:
        True if agent was removed, False if it didn't exist
    """
    if agent_name in REGISTERED_AGENTS:
        del REGISTERED_AGENTS[agent_name]
        clear_prompt_cache()
        return True
    return False
