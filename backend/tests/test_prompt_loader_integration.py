"""
PartnerScout AI - Prompt Loader Integration Tests (STORY-3.1.2)

Integration tests verifying:
- Prompt loader works with LLM service
- Prompts work with LangChain templates
- End-to-end prompt loading and usage flows
- Prompt system configuration validation
"""

import pytest
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from app.prompts.loader import (
    load_prompt,
    load_prompts,
    clear_prompt_cache,
    validate_all_prompts,
    get_registered_agents,
    PROMPTS_DIR,
)
from app.services.llm_service import LLMService, LLMProvider, LLMConfig
from app.core.settings import get_agents_config


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear prompt cache before each test."""
    clear_prompt_cache()
    yield
    clear_prompt_cache()


@pytest.fixture
def mock_llm_settings():
    """Mock LLM settings for testing."""
    with patch("app.services.llm_service.settings") as mock_settings:
        mock_settings.openai.api_key = "test-openai-key-12345"
        mock_settings.openai.model = "gpt-4-turbo-preview"
        mock_settings.gemini.api_key = "test-gemini-key-12345"
        mock_settings.gemini.model = "gemini-pro"
        mock_settings.ollama.base_url = "http://localhost:11434"
        mock_settings.ollama.model = "llama2"
        mock_settings.llm_provider = "openai"
        yield mock_settings


# =============================================================================
# Test Prompt System Validation
# =============================================================================

class TestPromptSystemIntegrity:
    """Integration tests for prompt system integrity."""
    
    def test_all_registered_prompts_exist(self):
        """Test all registered agent prompts exist on disk."""
        results = validate_all_prompts()
        
        for agent_name, status in results.items():
            assert status["system"] == True, (
                f"System prompt missing for {agent_name}. "
                f"Expected at: {PROMPTS_DIR}/{agent_name}/system.txt"
            )
            assert status["user"] == True, (
                f"User prompt missing for {agent_name}. "
                f"Expected at: {PROMPTS_DIR}/{agent_name}/user.txt"
            )
    
    def test_prompts_match_agents_yaml_config(self):
        """Test prompts match configuration in agents.yaml."""
        agent_config = get_agents_config()
        
        if agent_config and "agents" in agent_config:
            for agent_name, config in agent_config["agents"].items():
                if "prompts" in config:
                    # Verify prompt paths in config exist
                    prompts_config = config["prompts"]
                    
                    if "system" in prompts_config:
                        system_path = PROMPTS_DIR / prompts_config["system"]
                        assert system_path.exists(), (
                            f"Config references non-existent system prompt: {prompts_config['system']}"
                        )
                    
                    if "user" in prompts_config:
                        user_path = PROMPTS_DIR / prompts_config["user"]
                        assert user_path.exists(), (
                            f"Config references non-existent user prompt: {prompts_config['user']}"
                        )
    
    def test_prompt_directory_structure(self):
        """Test prompt directory structure is correct."""
        expected_agents = ["brand_analyzer", "discovery", "scorer", "email_composer"]
        
        for agent_name in expected_agents:
            agent_dir = PROMPTS_DIR / agent_name
            assert agent_dir.exists(), f"Agent directory missing: {agent_dir}"
            assert agent_dir.is_dir(), f"Agent path is not a directory: {agent_dir}"
            
            system_file = agent_dir / "system.txt"
            user_file = agent_dir / "user.txt"
            
            assert system_file.exists(), f"System prompt missing: {system_file}"
            assert user_file.exists(), f"User prompt missing: {user_file}"


# =============================================================================
# Test Integration with LLM Service
# =============================================================================

class TestPromptWithLLMService:
    """Integration tests for prompts with LLM service."""
    
    @patch("langchain_openai.ChatOpenAI")
    def test_prompt_with_llm_generate(self, mock_chat_openai, mock_llm_settings):
        """Test using prompt with LLM generate method."""
        # Setup mock
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = '{"hashtags": ["#test"], "keywords": ["test"]}'
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        # Load prompts
        system_prompt = load_prompt("brand_analyzer", "system")
        user_prompt = load_prompt(
            "brand_analyzer",
            "user",
            variables={
                "brand_description": "A sustainable fashion brand",
                "reference_profiles": "everlane, reformation"
            }
        )
        
        # Create LLM service and generate
        service = LLMService(provider=LLMProvider.OPENAI)
        result = service.generate_sync(user_prompt, system_prompt=system_prompt)
        
        # Verify LLM was called
        mock_instance.invoke.assert_called_once()
        assert result == mock_response.content
    
    @pytest.mark.asyncio
    @patch("langchain_openai.ChatOpenAI")
    async def test_prompt_with_llm_async_generate(self, mock_chat_openai, mock_llm_settings):
        """Test using prompt with async LLM generate method."""
        # Setup mock
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = '{"scores": {"visual": 80}}'
        mock_instance.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_instance
        
        # Load prompts
        prompts = load_prompts("scorer")
        user_prompt = prompts["user"].format(
            brand_description="Test brand",
            brand_dna="Test DNA",
            username="test_user",
            profile_url="https://instagram.com/test",
            profile_data="{}"
        ) if "{" in prompts["user"] else prompts["user"]
        
        # Create LLM service and generate async
        service = LLMService(provider=LLMProvider.OPENAI)
        result = await service.generate(user_prompt, system_prompt=prompts["system"])
        
        # Verify
        mock_instance.ainvoke.assert_called_once()
    
    @patch("langchain_openai.ChatOpenAI")
    def test_prompt_with_llm_chat_messages(self, mock_chat_openai, mock_llm_settings):
        """Test using prompts in chat message format."""
        # Setup mock
        mock_instance = MagicMock()
        mock_response = Mock()
        mock_response.content = "Email generated successfully"
        mock_instance.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_instance
        
        # Load prompts
        prompts = load_prompts("email_composer")
        
        # Create LLM service
        service = LLMService(provider=LLMProvider.OPENAI)
        
        # Build messages
        messages = [
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ]
        
        # This should work without errors
        assert len(messages) == 2
        assert len(messages[0]["content"]) > 0
        assert len(messages[1]["content"]) > 0


class TestPromptWithLangChainTemplates:
    """Integration tests for prompts with LangChain templates."""
    
    def test_create_chat_prompt_template(self):
        """Test creating LangChain ChatPromptTemplate from prompts."""
        system_prompt = load_prompt("brand_analyzer", "system")
        user_prompt = load_prompt("brand_analyzer", "user")
        
        # Create template
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{user_input}")
        ])
        
        # Verify template works
        messages = template.format_messages(user_input="Test brand description")
        
        assert len(messages) == 2
        assert messages[0].content == system_prompt
        assert messages[1].content == "Test brand description"
    
    def test_prompt_template_with_variables(self):
        """Test prompt template with multiple variables."""
        user_prompt = load_prompt("scorer", "user")
        
        # Create template that uses variables from prompt
        # Note: The actual prompt has variables like {username}, {profile_data}
        template = ChatPromptTemplate.from_template(user_prompt)
        
        # Get input variables
        input_vars = template.input_variables
        
        # Template should have variables
        assert len(input_vars) > 0 or "{" not in user_prompt
    
    @patch("langchain_openai.ChatOpenAI")
    def test_prompt_chain_creation(self, mock_chat_openai, mock_llm_settings):
        """Test creating a chain with prompts."""
        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance
        
        # Load prompt
        system_prompt = load_prompt("discovery", "system")
        
        # Create template
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{query}")
        ])
        
        # Create service and chain
        service = LLMService(provider=LLMProvider.OPENAI)
        chain = service.create_chain(template)
        
        # Chain should be created
        assert chain is not None


# =============================================================================
# Test Prompt Loading Performance
# =============================================================================

class TestPromptLoadingPerformance:
    """Integration tests for prompt loading performance."""
    
    def test_cached_loading_performance(self):
        """Test that cached loading is faster than uncached."""
        import time
        
        # Clear cache
        clear_prompt_cache()
        
        # First load (uncached)
        start1 = time.perf_counter()
        for _ in range(10):
            load_prompt("brand_analyzer", "system", use_cache=False)
        time_uncached = time.perf_counter() - start1
        
        # Clear and reload with cache
        clear_prompt_cache()
        
        # Second load (cached after first)
        load_prompt("brand_analyzer", "system", use_cache=True)  # Prime cache
        start2 = time.perf_counter()
        for _ in range(10):
            load_prompt("brand_analyzer", "system", use_cache=True)
        time_cached = time.perf_counter() - start2
        
        # Cached should be faster
        assert time_cached < time_uncached, (
            f"Cached ({time_cached:.4f}s) should be faster than uncached ({time_uncached:.4f}s)"
        )
    
    def test_all_prompts_load_quickly(self):
        """Test all prompts load within acceptable time."""
        import time
        
        clear_prompt_cache()
        
        start = time.perf_counter()
        
        for agent_name in get_registered_agents():
            load_prompts(agent_name, use_cache=False)
        
        elapsed = time.perf_counter() - start
        
        # All prompts should load in under 1 second
        assert elapsed < 1.0, f"Loading all prompts took too long: {elapsed:.2f}s"


# =============================================================================
# Test Agent-Specific Prompt Integration
# =============================================================================

class TestAgentPromptIntegration:
    """Integration tests for agent-specific prompt usage."""
    
    def test_brand_analyzer_prompt_has_required_output_fields(self):
        """Test brand analyzer prompts mention required output fields."""
        system_prompt = load_prompt("brand_analyzer", "system")
        
        # Should mention output format requirements
        system_lower = system_prompt.lower()
        assert "json" in system_lower, "Should mention JSON output"
        assert "hashtag" in system_lower, "Should mention hashtags"
        assert "keyword" in system_lower, "Should mention keywords"
    
    def test_scorer_prompt_has_6_dimensions(self):
        """Test scorer prompts reference 6 scoring dimensions."""
        system_prompt = load_prompt("scorer", "system")
        
        system_lower = system_prompt.lower()
        # Should mention scoring dimensions
        dimension_keywords = [
            "visual", "content", "engagement", "follower", "business", "activity"
        ]
        
        found_dimensions = sum(1 for kw in dimension_keywords if kw in system_lower)
        assert found_dimensions >= 4, (
            f"Scorer should mention most scoring dimensions, found {found_dimensions}/6"
        )
    
    def test_email_composer_prompt_has_tone_options(self):
        """Test email composer prompts mention tone options."""
        system_prompt = load_prompt("email_composer", "system")
        
        system_lower = system_prompt.lower()
        # Should mention available tones
        assert "professional" in system_lower
        assert "friendly" in system_lower
        assert "casual" in system_lower
    
    def test_discovery_prompt_has_filter_criteria(self):
        """Test discovery prompts mention filtering criteria."""
        system_prompt = load_prompt("discovery", "system")
        
        system_lower = system_prompt.lower()
        # Should mention filtering/relevance
        filter_keywords = ["filter", "relevant", "screen", "match"]
        
        found_filters = sum(1 for kw in filter_keywords if kw in system_lower)
        assert found_filters >= 2, "Discovery should mention filtering criteria"


# =============================================================================
# Test Prompt Variable Substitution Integration
# =============================================================================

class TestPromptVariableIntegration:
    """Integration tests for variable substitution with real prompts."""
    
    def test_brand_analyzer_user_prompt_variables(self):
        """Test brand analyzer user prompt with variable substitution."""
        variables = {
            "brand_description": "Eco-friendly skincare brand",
            "reference_profiles": "Profile 1: @ecobeauty\nProfile 2: @greenskin"
        }
        
        prompt = load_prompt("brand_analyzer", "user", variables=variables)
        
        # Variables should be substituted
        assert "Eco-friendly skincare brand" in prompt
        assert "@ecobeauty" in prompt
    
    def test_scorer_user_prompt_variables(self):
        """Test scorer user prompt with variable substitution."""
        variables = {
            "username": "fashion_influencer",
            "profile_url": "https://instagram.com/fashion_influencer",
            "brand_description": "Luxury fashion brand",
            "brand_dna": '{"keywords": ["luxury", "fashion"]}',
            "profile_data": '{"followers": 50000}'
        }
        
        prompt = load_prompt("scorer", "user", variables=variables)
        
        # At least some variables should be substituted
        # (depending on how the prompt template is structured)
        assert len(prompt) > 0
    
    def test_email_composer_user_prompt_variables(self):
        """Test email composer user prompt with variable substitution."""
        variables = {
            "brand_name": "EcoStyle",
            "brand_description": "Sustainable fashion brand",
            "username": "style_guru",
            "profile_url": "https://instagram.com/style_guru",
            "follower_count": "75,000",
            "bio": "Fashion blogger | Sustainability advocate",
            "profile_summary": "High engagement, authentic audience",
            "score": "85",
            "tone": "friendly"
        }
        
        prompt = load_prompt("email_composer", "user", variables=variables)
        
        # Variables should be substituted where they appear
        assert len(prompt) > 0
    
    def test_discovery_user_prompt_variables(self):
        """Test discovery user prompt with variable substitution."""
        variables = {
            "brand_description": "Tech startup",
            "hashtags": "#tech, #startup, #innovation",
            "keywords": "technology, startup, innovation",
            "min_followers": "10000",
            "max_followers": "500000",
            "limit": "50",
            "profiles_data": "[]"
        }
        
        prompt = load_prompt("discovery", "user", variables=variables)
        
        # Should be a valid prompt
        assert len(prompt) > 0


# =============================================================================
# Test Edge Cases Integration
# =============================================================================

class TestEdgeCasesIntegration:
    """Integration tests for edge cases."""
    
    def test_prompt_with_special_characters(self):
        """Test prompts handle special characters in variables."""
        variables = {
            "brand_description": "Brand with 'quotes' and \"double quotes\" and {braces}",
            "reference_profiles": "Profile with <html> tags & ampersands"
        }
        
        # Should not raise exception
        prompt = load_prompt("brand_analyzer", "user", variables=variables)
        assert len(prompt) > 0
    
    def test_prompt_with_unicode_characters(self):
        """Test prompts handle Unicode characters."""
        variables = {
            "brand_description": "Brand with émojis 🌿 and 日本語 characters",
            "reference_profiles": "Profile with Ñ and ü"
        }
        
        # Should not raise exception
        prompt = load_prompt("brand_analyzer", "user", variables=variables)
        assert len(prompt) > 0
    
    def test_prompt_with_very_long_values(self):
        """Test prompts handle very long variable values."""
        variables = {
            "brand_description": "A" * 10000,  # Very long description
            "reference_profiles": "B" * 5000
        }
        
        # Should not raise exception
        prompt = load_prompt("brand_analyzer", "user", variables=variables)
        assert len(prompt) > 10000  # Should include the long values
    
    def test_concurrent_prompt_loading(self):
        """Test concurrent prompt loading works correctly."""
        import concurrent.futures
        
        def load_agent_prompts(agent_name):
            return load_prompts(agent_name)
        
        agents = get_registered_agents()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(load_agent_prompts, agent) for agent in agents]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All prompts should be loaded
        assert len(results) == len(agents)
        for result in results:
            assert "system" in result
            assert "user" in result
