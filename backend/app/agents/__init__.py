"""
PartnerScout AI - Agents Module

AI agents for brand analysis, profile discovery, scoring, and email composition.
All agents inherit from BaseAgent to ensure consistent behavior.

Available Agents:
- BaseAgent: Abstract base class with common functionality
- BrandAnalyzerAgent: Analyzes brand identity (STORY-3.3.2)
- DiscoveryAgent: Discovers similar profiles (STORY-3.3.3)
- ScorerAgent: Scores discovered profiles (STORY-3.3.4)
- EmailComposerAgent: Generates outreach emails (STORY-3.3.5)

Usage:
    from app.agents import BaseAgent, AgentConfig, AgentResult
    
    # Subclass BaseAgent to create custom agents
    class MyAgent(BaseAgent[MyInput, MyOutput]):
        agent_name = "my_agent"
        
        async def run(self, input_data: MyInput) -> MyOutput:
            # Implementation
            pass
"""

from app.agents.base import (
    # Main classes
    BaseAgent,
    
    # Configuration and result models
    AgentConfig,
    AgentMetrics,
    AgentResult,
    
    # Type variables for generic typing
    InputT,
    OutputT,
)

# Implemented agents
from app.agents.brand_analyzer import BrandAnalyzerAgent, get_brand_analyzer_agent
from app.agents.discovery import DiscoveryAgent, get_discovery_agent
from app.agents.scorer import ScorerAgent, get_scorer_agent
from app.agents.email_composer import (
    EmailComposerAgent,
    EmailComposerRequest,
    EmailComposerResponse,
    get_email_composer_agent,
)


__all__ = [
    # Base classes
    "BaseAgent",
    
    # Configuration models
    "AgentConfig",
    "AgentMetrics",
    "AgentResult",
    
    # Type variables
    "InputT",
    "OutputT",
    
    # Implemented agents
    "BrandAnalyzerAgent",
    "get_brand_analyzer_agent",
    "DiscoveryAgent",
    "get_discovery_agent",
    "ScorerAgent",
    "get_scorer_agent",
    "EmailComposerAgent",
    "EmailComposerRequest",
    "EmailComposerResponse",
    "get_email_composer_agent",
]
