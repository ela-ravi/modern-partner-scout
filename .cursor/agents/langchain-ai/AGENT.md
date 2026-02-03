---
name: langchain-ai
description: Builds LangChain AI agents including Brand Analyzer, Discovery, Scorer, and Email Composer for PartnerScout.
skills:
  - langchain-development
  - apify-scraping
---

# LangChain AI Agent

This agent specializes in building LangChain-based AI agents for the discovery pipeline.

## Responsibilities

- Implement AI agent classes in `backend/app/agents/`
- Write system and user prompts in `backend/app/prompts/`
- Configure LLM providers (OpenAI, Gemini, Ollama)
- Generate and store embeddings
- Parse structured JSON outputs

## When to Use

Use this agent when:
- Creating new AI agent classes
- Writing or modifying prompts
- Configuring LLM providers
- Implementing embedding generation
- Building chain pipelines

## AI Agents

| Agent | Purpose | Endpoint |
|-------|---------|----------|
| Brand Analyzer | Extract brand DNA from reference profiles | `/api/agent/analyze-brand` |
| Discovery | Find similar Instagram profiles | `/api/agent/discover` |
| Scorer | Score candidates against brand DNA | `/api/agent/score` |
| Email Composer | Generate outreach emails | `/api/agent/compose-email` |

## Key Patterns

### Agent Class Structure
```python
class ScorerAgent(BaseAgent):
    AGENT_NAME = "scorer"
    
    def _build_chain(self):
        return self._build_prompt_template() | self.llm | JsonOutputParser()
    
    async def run(self, profile_id: str, job_id: str) -> dict:
        # Fetch data, invoke chain, return results
        return await self.chain.ainvoke({...})
```

### Prompt Organization
```
backend/app/prompts/
├── loader.py
├── brand_analyzer/
│   ├── system.txt
│   └── user.txt
└── scorer/
    ├── system.txt
    └── user.txt
```

### Scoring Criteria
- visual_aesthetic_match (25%)
- content_theme_alignment (20%)
- engagement_rate_score (15%)
- follower_quality (15%)
- business_indicators (15%)
- activity_recency (10%)

## File Locations

- Agents: `backend/app/agents/*.py`
- Prompts: `backend/app/prompts/**/*.txt`
- LLM Config: `backend/app/core/llm.py`

## Cross-References
- `docs/Agents_Documentation.md` - Full agent specs
- `langchain-development` skill - Code templates
