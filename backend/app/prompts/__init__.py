"""
PartnerScout AI - Prompts Module

This module provides prompt management functionality for AI agents.
Prompts are stored as external text files and loaded at runtime,
allowing for easy modification without code changes.

Usage:
    from app.prompts import load_prompt, load_prompts
    
    # Load a single prompt
    system_prompt = load_prompt("brand_analyzer", "system")
    
    # Load both system and user prompts
    prompts = load_prompts("brand_analyzer")
    
    # Load with variable substitution
    user_prompt = load_prompt("scorer", "user", variables={"username": "everlane"})
    
Available Agents:
    - brand_analyzer: Analyzes brand identity and extracts hashtags/keywords
    - discovery: Discovers and filters Instagram profiles
    - scorer: Scores profiles across 6 dimensions
    - email_composer: Generates personalized outreach emails
"""

from app.prompts.loader import (
    # Core functions
    load_prompt,
    load_prompts,
    load_prompt_from_path,
    
    # Cache management
    clear_prompt_cache,
    get_cache_info,
    
    # Utility functions
    get_registered_agents,
    get_agent_prompt_paths,
    prompt_exists,
    validate_all_prompts,
    get_prompts_directory,
    
    # Registration functions
    register_agent_prompts,
    unregister_agent,
    
    # Exceptions
    PromptLoadError,
    PromptNotFoundError,
    InvalidPromptTypeError,
    InvalidAgentError,
    
    # Constants
    PROMPTS_DIR,
    REGISTERED_AGENTS,
    VALID_PROMPT_TYPES,
)

__all__ = [
    # Core functions
    "load_prompt",
    "load_prompts",
    "load_prompt_from_path",
    
    # Cache management
    "clear_prompt_cache",
    "get_cache_info",
    
    # Utility functions
    "get_registered_agents",
    "get_agent_prompt_paths",
    "prompt_exists",
    "validate_all_prompts",
    "get_prompts_directory",
    
    # Registration functions
    "register_agent_prompts",
    "unregister_agent",
    
    # Exceptions
    "PromptLoadError",
    "PromptNotFoundError",
    "InvalidPromptTypeError",
    "InvalidAgentError",
    
    # Constants
    "PROMPTS_DIR",
    "REGISTERED_AGENTS",
    "VALID_PROMPT_TYPES",
]
