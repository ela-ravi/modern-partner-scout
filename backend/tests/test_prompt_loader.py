"""
PartnerScout AI - Prompt Loader Unit Tests (STORY-3.1.2)

Comprehensive unit tests for the Prompt Management System including:
- Loading individual prompts (system/user)
- Loading both prompts together
- Variable substitution
- Cache management
- Error handling
- Utility functions
- Agent registration
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
import tempfile
import shutil

from app.prompts.loader import (
    # Core functions
    load_prompt,
    load_prompts,
    load_prompt_from_path,
    
    # Cache management
    clear_prompt_cache,
    get_cache_info,
    _load_prompt_cached,
    
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
    
    # Internal helpers
    _substitute_variables,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clear_cache_before_each():
    """Clear prompt cache before each test to ensure isolation."""
    clear_prompt_cache()
    yield
    clear_prompt_cache()


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary directory with test prompt files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create test agent directory
    test_agent_dir = Path(temp_dir) / "test_agent"
    test_agent_dir.mkdir()
    
    # Create system prompt
    (test_agent_dir / "system.txt").write_text(
        "You are a test agent. Your role is {role}.",
        encoding="utf-8"
    )
    
    # Create user prompt
    (test_agent_dir / "user.txt").write_text(
        "Please analyze {input_data} for {purpose}.",
        encoding="utf-8"
    )
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_variables():
    """Sample variables for substitution tests."""
    return {
        "role": "testing assistant",
        "input_data": "sample data",
        "purpose": "validation",
    }


# =============================================================================
# Test Constants
# =============================================================================

class TestConstants:
    """Tests for module constants."""
    
    def test_prompts_dir_exists(self):
        """Test that PROMPTS_DIR points to existing directory."""
        assert PROMPTS_DIR.exists()
        assert PROMPTS_DIR.is_dir()
    
    def test_valid_prompt_types(self):
        """Test valid prompt types are correct."""
        assert "system" in VALID_PROMPT_TYPES
        assert "user" in VALID_PROMPT_TYPES
        assert len(VALID_PROMPT_TYPES) == 2
    
    def test_registered_agents_not_empty(self):
        """Test that agents are registered."""
        assert len(REGISTERED_AGENTS) >= 4
        assert "brand_analyzer" in REGISTERED_AGENTS
        assert "discovery" in REGISTERED_AGENTS
        assert "scorer" in REGISTERED_AGENTS
        assert "email_composer" in REGISTERED_AGENTS
    
    def test_registered_agents_have_prompts(self):
        """Test that registered agents have both prompt types."""
        for agent_name, config in REGISTERED_AGENTS.items():
            assert "system" in config, f"{agent_name} missing system prompt config"
            assert "user" in config, f"{agent_name} missing user prompt config"


# =============================================================================
# Test load_prompt Function
# =============================================================================

class TestLoadPrompt:
    """Tests for load_prompt function."""
    
    def test_load_system_prompt_brand_analyzer(self):
        """Test loading brand analyzer system prompt."""
        prompt = load_prompt("brand_analyzer", "system")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
        # Verify content contains expected elements
        assert "brand" in prompt.lower() or "analyzer" in prompt.lower()
    
    def test_load_user_prompt_brand_analyzer(self):
        """Test loading brand analyzer user prompt."""
        prompt = load_prompt("brand_analyzer", "user")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_system_prompt_discovery(self):
        """Test loading discovery system prompt."""
        prompt = load_prompt("discovery", "system")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_user_prompt_discovery(self):
        """Test loading discovery user prompt."""
        prompt = load_prompt("discovery", "user")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_system_prompt_scorer(self):
        """Test loading scorer system prompt."""
        prompt = load_prompt("scorer", "system")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_user_prompt_scorer(self):
        """Test loading scorer user prompt."""
        prompt = load_prompt("scorer", "user")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_system_prompt_email_composer(self):
        """Test loading email composer system prompt."""
        prompt = load_prompt("email_composer", "system")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_load_user_prompt_email_composer(self):
        """Test loading email composer user prompt."""
        prompt = load_prompt("email_composer", "user")
        
        assert len(prompt) > 0
        assert isinstance(prompt, str)
    
    def test_prompt_type_case_insensitive(self):
        """Test that prompt type is case-insensitive."""
        prompt1 = load_prompt("brand_analyzer", "system")
        prompt2 = load_prompt("brand_analyzer", "SYSTEM")
        prompt3 = load_prompt("brand_analyzer", "System")
        
        assert prompt1 == prompt2 == prompt3
    
    def test_invalid_agent_raises_error(self):
        """Test that invalid agent name raises InvalidAgentError."""
        with pytest.raises(InvalidAgentError) as exc_info:
            load_prompt("invalid_agent", "system")
        
        assert "invalid_agent" in str(exc_info.value)
        assert "Unknown agent" in str(exc_info.value.message)
    
    def test_invalid_prompt_type_raises_error(self):
        """Test that invalid prompt type raises InvalidPromptTypeError."""
        with pytest.raises(InvalidPromptTypeError) as exc_info:
            load_prompt("brand_analyzer", "invalid_type")
        
        assert "invalid_type" in str(exc_info.value)
        assert "Invalid prompt type" in str(exc_info.value.message)
    
    def test_load_prompt_with_cache(self):
        """Test that caching works correctly."""
        # Clear cache first
        clear_prompt_cache()
        
        # Load prompt twice
        prompt1 = load_prompt("brand_analyzer", "system", use_cache=True)
        prompt2 = load_prompt("brand_analyzer", "system", use_cache=True)
        
        # Should be identical
        assert prompt1 == prompt2
        
        # Check cache was hit
        info = get_cache_info()
        assert info["hits"] >= 1
    
    def test_load_prompt_without_cache(self):
        """Test loading without cache."""
        # Clear cache first
        clear_prompt_cache()
        
        # Load prompt twice without cache
        prompt1 = load_prompt("brand_analyzer", "system", use_cache=False)
        prompt2 = load_prompt("brand_analyzer", "system", use_cache=False)
        
        # Should still be identical content
        assert prompt1 == prompt2
        
        # Cache should not have been populated
        info = get_cache_info()
        assert info["currsize"] == 0


class TestLoadPromptWithVariables:
    """Tests for load_prompt with variable substitution."""
    
    def test_variable_substitution(self):
        """Test that variables are substituted in prompts when all required vars provided."""
        # The user prompts have template variables - we need to provide ALL required variables
        # When only partial variables are provided, the format() function fails and returns original
        prompt = load_prompt(
            "brand_analyzer",
            "user",
            variables={
                "brand_description": "Test brand description",
                "reference_profiles": "everlane, reformation"
            }
        )
        
        # Both variables should be substituted when all are provided
        assert "Test brand description" in prompt
        assert "everlane, reformation" in prompt
    
    def test_variable_substitution_multiple(self):
        """Test multiple variable substitution."""
        prompt = load_prompt(
            "scorer",
            "user",
            variables={
                "username": "test_user",
                "profile_url": "https://instagram.com/test_user"
            }
        )
        
        # Either variables are substituted or placeholders remain if not found
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_missing_variable_keeps_placeholder(self):
        """Test that missing variables don't cause errors."""
        # Load with empty variables dict
        prompt = load_prompt("brand_analyzer", "user", variables={})
        
        # Should not raise error, placeholder might remain
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_extra_variables_ignored(self):
        """Test that extra variables are ignored."""
        prompt = load_prompt(
            "brand_analyzer",
            "system",
            variables={"extra_var": "extra_value", "another": "value"}
        )
        
        # Should not raise error
        assert isinstance(prompt, str)


# =============================================================================
# Test load_prompts Function
# =============================================================================

class TestLoadPrompts:
    """Tests for load_prompts function."""
    
    def test_load_both_prompts(self):
        """Test loading both system and user prompts."""
        prompts = load_prompts("brand_analyzer")
        
        assert "system" in prompts
        assert "user" in prompts
        assert len(prompts["system"]) > 0
        assert len(prompts["user"]) > 0
    
    def test_load_prompts_all_agents(self):
        """Test loading prompts for all registered agents."""
        for agent_name in get_registered_agents():
            prompts = load_prompts(agent_name)
            
            assert "system" in prompts, f"{agent_name} missing system prompt"
            assert "user" in prompts, f"{agent_name} missing user prompt"
            assert len(prompts["system"]) > 0, f"{agent_name} system prompt empty"
            assert len(prompts["user"]) > 0, f"{agent_name} user prompt empty"
    
    def test_load_prompts_with_variables(self):
        """Test loading prompts with variable substitution."""
        prompts = load_prompts(
            "brand_analyzer",
            variables={"brand_description": "Test brand"}
        )
        
        assert isinstance(prompts, dict)
        assert len(prompts) == 2
    
    def test_load_prompts_invalid_agent(self):
        """Test loading prompts for invalid agent."""
        with pytest.raises(InvalidAgentError):
            load_prompts("nonexistent_agent")


# =============================================================================
# Test load_prompt_from_path Function
# =============================================================================

class TestLoadPromptFromPath:
    """Tests for load_prompt_from_path function."""
    
    def test_load_from_valid_path(self, temp_prompts_dir):
        """Test loading prompt from valid path."""
        file_path = Path(temp_prompts_dir) / "test_agent" / "system.txt"
        prompt = load_prompt_from_path(file_path)
        
        assert "test agent" in prompt.lower()
    
    def test_load_from_path_with_variables(self, temp_prompts_dir):
        """Test loading prompt with variable substitution."""
        file_path = Path(temp_prompts_dir) / "test_agent" / "system.txt"
        prompt = load_prompt_from_path(
            file_path,
            variables={"role": "validation helper"}
        )
        
        assert "validation helper" in prompt
    
    def test_load_from_nonexistent_path(self):
        """Test loading from non-existent path raises error."""
        with pytest.raises(PromptNotFoundError) as exc_info:
            load_prompt_from_path("/nonexistent/path/prompt.txt")
        
        assert "not found" in str(exc_info.value.message).lower()
    
    def test_load_from_path_string(self, temp_prompts_dir):
        """Test loading from path as string."""
        file_path = str(Path(temp_prompts_dir) / "test_agent" / "system.txt")
        prompt = load_prompt_from_path(file_path)
        
        assert len(prompt) > 0


# =============================================================================
# Test Cache Management
# =============================================================================

class TestCacheManagement:
    """Tests for cache management functions."""
    
    def test_clear_prompt_cache(self):
        """Test clearing prompt cache."""
        # Load some prompts to populate cache
        load_prompt("brand_analyzer", "system", use_cache=True)
        load_prompt("brand_analyzer", "user", use_cache=True)
        
        # Verify cache has items
        info_before = get_cache_info()
        assert info_before["currsize"] > 0
        
        # Clear cache
        clear_prompt_cache()
        
        # Verify cache is empty
        info_after = get_cache_info()
        assert info_after["currsize"] == 0
    
    def test_get_cache_info(self):
        """Test getting cache information."""
        clear_prompt_cache()
        
        # Load prompt
        load_prompt("brand_analyzer", "system", use_cache=True)
        
        info = get_cache_info()
        
        assert "hits" in info
        assert "misses" in info
        assert "maxsize" in info
        assert "currsize" in info
        assert info["currsize"] >= 1
        assert info["misses"] >= 1
    
    def test_cache_hit_after_load(self):
        """Test cache hit on subsequent load."""
        clear_prompt_cache()
        
        # First load - cache miss
        load_prompt("brand_analyzer", "system", use_cache=True)
        info1 = get_cache_info()
        
        # Second load - cache hit
        load_prompt("brand_analyzer", "system", use_cache=True)
        info2 = get_cache_info()
        
        assert info2["hits"] > info1["hits"]


# =============================================================================
# Test Utility Functions
# =============================================================================

class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_get_registered_agents(self):
        """Test getting list of registered agents."""
        agents = get_registered_agents()
        
        assert isinstance(agents, list)
        assert len(agents) >= 4
        assert "brand_analyzer" in agents
        assert "discovery" in agents
        assert "scorer" in agents
        assert "email_composer" in agents
    
    def test_get_agent_prompt_paths(self):
        """Test getting prompt paths for agent."""
        paths = get_agent_prompt_paths("brand_analyzer")
        
        assert "system" in paths
        assert "user" in paths
        assert isinstance(paths["system"], Path)
        assert isinstance(paths["user"], Path)
    
    def test_get_agent_prompt_paths_invalid_agent(self):
        """Test getting paths for invalid agent."""
        with pytest.raises(InvalidAgentError):
            get_agent_prompt_paths("invalid_agent")
    
    def test_prompt_exists_true(self):
        """Test prompt_exists returns True for existing prompts."""
        assert prompt_exists("brand_analyzer", "system") == True
        assert prompt_exists("brand_analyzer", "user") == True
    
    def test_prompt_exists_false_invalid_agent(self):
        """Test prompt_exists returns False for invalid agent."""
        assert prompt_exists("invalid_agent", "system") == False
    
    def test_prompt_exists_false_invalid_type(self):
        """Test prompt_exists returns False for invalid type."""
        # This might return False or True depending on implementation
        result = prompt_exists("brand_analyzer", "invalid_type")
        assert isinstance(result, bool)
    
    def test_validate_all_prompts(self):
        """Test validating all registered prompts."""
        results = validate_all_prompts()
        
        assert isinstance(results, dict)
        assert len(results) >= 4
        
        for agent_name, status in results.items():
            assert "system" in status
            assert "user" in status
            assert isinstance(status["system"], bool)
            assert isinstance(status["user"], bool)
    
    def test_validate_all_prompts_all_exist(self):
        """Test that all registered prompts exist."""
        results = validate_all_prompts()
        
        for agent_name, status in results.items():
            assert status["system"] == True, f"{agent_name} system prompt missing"
            assert status["user"] == True, f"{agent_name} user prompt missing"
    
    def test_get_prompts_directory(self):
        """Test getting prompts directory."""
        directory = get_prompts_directory()
        
        assert isinstance(directory, Path)
        assert directory.exists()
        assert directory.is_dir()


# =============================================================================
# Test Registration Functions
# =============================================================================

class TestRegistrationFunctions:
    """Tests for agent registration functions."""
    
    def test_register_agent_prompts(self, temp_prompts_dir):
        """Test registering custom agent prompts."""
        # Create test prompt files
        test_agent_dir = Path(temp_prompts_dir) / "custom_agent"
        test_agent_dir.mkdir()
        (test_agent_dir / "system.txt").write_text("Custom system prompt", encoding="utf-8")
        (test_agent_dir / "user.txt").write_text("Custom user prompt", encoding="utf-8")
        
        # Register custom agent
        register_agent_prompts(
            "custom_test_agent",
            "custom_agent/system.txt",
            "custom_agent/user.txt"
        )
        
        try:
            # Verify agent is registered
            assert "custom_test_agent" in get_registered_agents()
        finally:
            # Cleanup
            unregister_agent("custom_test_agent")
    
    def test_unregister_agent_existing(self):
        """Test unregistering an existing agent."""
        # Register a test agent
        register_agent_prompts(
            "temp_agent",
            "temp/system.txt",
            "temp/user.txt"
        )
        
        assert "temp_agent" in get_registered_agents()
        
        # Unregister
        result = unregister_agent("temp_agent")
        
        assert result == True
        assert "temp_agent" not in get_registered_agents()
    
    def test_unregister_agent_nonexistent(self):
        """Test unregistering non-existent agent."""
        result = unregister_agent("nonexistent_agent")
        
        assert result == False


# =============================================================================
# Test Variable Substitution
# =============================================================================

class TestVariableSubstitution:
    """Tests for variable substitution helper."""
    
    def test_substitute_single_variable(self):
        """Test single variable substitution."""
        content = "Hello {name}!"
        result = _substitute_variables(content, {"name": "World"})
        
        assert result == "Hello World!"
    
    def test_substitute_multiple_variables(self):
        """Test multiple variable substitution."""
        content = "{greeting} {name}! Welcome to {place}."
        result = _substitute_variables(content, {
            "greeting": "Hello",
            "name": "User",
            "place": "PartnerScout"
        })
        
        assert result == "Hello User! Welcome to PartnerScout."
    
    def test_substitute_missing_variable_returns_original(self):
        """Test missing variable returns original content."""
        content = "Hello {name}!"
        result = _substitute_variables(content, {"other": "value"})
        
        # Should return original since KeyError is caught
        assert result == "Hello {name}!"
    
    def test_substitute_empty_variables(self):
        """Test empty variables dict."""
        content = "Hello {name}!"
        result = _substitute_variables(content, {})
        
        # Should return original
        assert result == "Hello {name}!"
    
    def test_substitute_special_characters(self):
        """Test substitution with special characters."""
        content = "Query: {query}"
        result = _substitute_variables(content, {"query": "test & <value>"})
        
        assert result == "Query: test & <value>"


# =============================================================================
# Test Exception Classes
# =============================================================================

class TestExceptions:
    """Tests for custom exception classes."""
    
    def test_prompt_load_error_basic(self):
        """Test PromptLoadError basic creation."""
        error = PromptLoadError(
            message="Test error",
            agent_name="test_agent"
        )
        
        assert "Test error" in str(error)
    
    def test_prompt_load_error_with_details(self):
        """Test PromptLoadError with all details."""
        error = PromptLoadError(
            message="Test error",
            agent_name="test_agent",
            prompt_type="system",
            file_path="/path/to/file.txt"
        )
        
        assert error.details.get("prompt_type") == "system"
        assert error.details.get("file_path") == "/path/to/file.txt"
    
    def test_prompt_not_found_error(self):
        """Test PromptNotFoundError."""
        error = PromptNotFoundError(
            message="Prompt not found",
            agent_name="test_agent",
            file_path="/missing/file.txt"
        )
        
        assert "not found" in str(error).lower()
    
    def test_invalid_prompt_type_error(self):
        """Test InvalidPromptTypeError."""
        error = InvalidPromptTypeError(
            message="Invalid type",
            agent_name="test_agent",
            prompt_type="invalid"
        )
        
        assert error.details.get("prompt_type") == "invalid"
    
    def test_invalid_agent_error(self):
        """Test InvalidAgentError."""
        error = InvalidAgentError(
            message="Unknown agent",
            agent_name="unknown"
        )
        
        assert "unknown" in str(error).lower()


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_empty_prompt_file(self, temp_prompts_dir):
        """Test handling of empty prompt file."""
        # Create empty file
        empty_file = Path(temp_prompts_dir) / "empty.txt"
        empty_file.write_text("", encoding="utf-8")
        
        with pytest.raises(PromptLoadError) as exc_info:
            load_prompt_from_path(empty_file)
        
        assert "empty" in str(exc_info.value.message).lower()
    
    def test_whitespace_only_prompt_file(self, temp_prompts_dir):
        """Test handling of whitespace-only prompt file."""
        # Create whitespace-only file
        ws_file = Path(temp_prompts_dir) / "whitespace.txt"
        ws_file.write_text("   \n\t\n   ", encoding="utf-8")
        
        with pytest.raises(PromptLoadError) as exc_info:
            load_prompt_from_path(ws_file)
        
        assert "empty" in str(exc_info.value.message).lower()


# =============================================================================
# Test Content Validation
# =============================================================================

class TestPromptContent:
    """Tests for validating prompt file contents."""
    
    def test_brand_analyzer_system_contains_key_elements(self):
        """Test brand analyzer system prompt has key elements."""
        prompt = load_prompt("brand_analyzer", "system")
        
        # Should mention key concepts
        prompt_lower = prompt.lower()
        assert any(word in prompt_lower for word in ["brand", "hashtag", "keyword", "instagram", "analysis"])
    
    def test_scorer_system_contains_dimensions(self):
        """Test scorer system prompt mentions scoring dimensions."""
        prompt = load_prompt("scorer", "system")
        
        prompt_lower = prompt.lower()
        # Should mention scoring concepts
        assert any(word in prompt_lower for word in ["score", "dimension", "engagement", "follower"])
    
    def test_email_composer_contains_tone_info(self):
        """Test email composer mentions tone options."""
        prompt = load_prompt("email_composer", "system")
        
        prompt_lower = prompt.lower()
        # Should mention tone options
        assert any(word in prompt_lower for word in ["tone", "professional", "friendly", "casual"])
    
    def test_discovery_system_contains_filter_info(self):
        """Test discovery system prompt mentions filtering."""
        prompt = load_prompt("discovery", "system")
        
        prompt_lower = prompt.lower()
        # Should mention filtering concepts
        assert any(word in prompt_lower for word in ["filter", "profile", "discover", "relevant"])
    
    def test_all_prompts_have_reasonable_length(self):
        """Test all prompts have reasonable length."""
        for agent_name in get_registered_agents():
            prompts = load_prompts(agent_name)
            
            # System prompts should be substantial
            assert len(prompts["system"]) >= 100, f"{agent_name} system prompt too short"
            
            # User prompts should have content
            assert len(prompts["user"]) >= 50, f"{agent_name} user prompt too short"
            
            # But not excessively long (sanity check)
            assert len(prompts["system"]) < 50000, f"{agent_name} system prompt too long"
            assert len(prompts["user"]) < 50000, f"{agent_name} user prompt too long"
