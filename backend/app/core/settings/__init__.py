"""
PartnerScout AI - YAML Configuration Loader

Provides functions to load and access YAML configuration files
for agents, scoring, and rate limits.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml


# Get the directory where this module is located
SETTINGS_DIR = Path(__file__).parent


class ConfigurationError(Exception):
    """Raised when a configuration file cannot be loaded."""
    pass


def _load_yaml_file(filename: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file from the settings directory.
    
    Args:
        filename: Name of the YAML file (with extension)
        
    Returns:
        Dict containing the parsed YAML content
        
    Raises:
        ConfigurationError: If the file cannot be loaded or parsed
    """
    filepath = SETTINGS_DIR / filename
    
    if not filepath.exists():
        raise ConfigurationError(f"Configuration file not found: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Failed to parse YAML file {filename}: {e}")
    except IOError as e:
        raise ConfigurationError(f"Failed to read file {filename}: {e}")


@lru_cache()
def get_agents_config() -> Dict[str, Any]:
    """
    Get the agents configuration.
    
    Returns:
        Dict containing agent configurations including prompts,
        models, and behavior settings.
    """
    return _load_yaml_file("agents.yaml")


@lru_cache()
def get_scoring_config() -> Dict[str, Any]:
    """
    Get the scoring configuration.
    
    Returns:
        Dict containing scoring weights, thresholds, and
        dimension configurations.
    """
    return _load_yaml_file("scoring.yaml")


@lru_cache()
def get_limits_config() -> Dict[str, Any]:
    """
    Get the rate limits and timeout configuration.
    
    Returns:
        Dict containing rate limits, quotas, timeouts,
        and retry configurations.
    """
    return _load_yaml_file("limits.yaml")


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'brand_analyzer', 'discovery')
        
    Returns:
        Dict containing the agent's configuration
        
    Raises:
        ConfigurationError: If the agent is not found in configuration
    """
    config = get_agents_config()
    agents = config.get("agents", {})
    
    if agent_name not in agents:
        raise ConfigurationError(f"Agent not found in configuration: {agent_name}")
    
    return agents[agent_name]


def get_scoring_weights() -> Dict[str, float]:
    """
    Get the scoring dimension weights.
    
    Returns:
        Dict mapping dimension names to their weights (should sum to 1.0)
    """
    config = get_scoring_config()
    return config.get("weights", {})


def get_scoring_thresholds() -> Dict[str, int]:
    """
    Get the scoring thresholds.
    
    Returns:
        Dict containing threshold values (e.g., min_score, high_score)
    """
    config = get_scoring_config()
    return config.get("thresholds", {})


def get_rate_limits() -> Dict[str, Any]:
    """
    Get rate limit configuration.
    
    Returns:
        Dict containing rate limit values
    """
    config = get_limits_config()
    return config.get("rate_limits", {})


def get_timeouts() -> Dict[str, int]:
    """
    Get timeout configuration.
    
    Returns:
        Dict mapping operation names to timeout values in seconds
    """
    config = get_limits_config()
    return config.get("timeouts", {})


def get_retry_config() -> Dict[str, Any]:
    """
    Get retry configuration.
    
    Returns:
        Dict containing retry settings (max_retries, delay, etc.)
    """
    config = get_limits_config()
    return config.get("retry", {})


def reload_configs() -> None:
    """
    Clear the configuration cache and reload all configs.
    
    Use this when configurations have been modified and need to be reloaded.
    """
    get_agents_config.cache_clear()
    get_scoring_config.cache_clear()
    get_limits_config.cache_clear()


def validate_scoring_weights() -> bool:
    """
    Validate that scoring weights sum to 1.0.
    
    Returns:
        True if weights are valid
        
    Raises:
        ConfigurationError: If weights don't sum to 1.0
    """
    weights = get_scoring_weights()
    total = sum(weights.values())
    
    # Allow for small floating point errors
    if not (0.99 <= total <= 1.01):
        raise ConfigurationError(
            f"Scoring weights must sum to 1.0, but got {total}"
        )
    
    return True


# Convenience function for importing all configs at once
def get_all_configs() -> Dict[str, Dict[str, Any]]:
    """
    Get all configuration files as a single dictionary.
    
    Returns:
        Dict with keys 'agents', 'scoring', 'limits'
    """
    return {
        "agents": get_agents_config(),
        "scoring": get_scoring_config(),
        "limits": get_limits_config(),
    }
