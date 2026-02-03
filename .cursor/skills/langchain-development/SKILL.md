---
name: langchain-development
description: Build LangChain AI agents with multi-provider LLM support for PartnerScout. Use this skill when implementing AI agents, LLM chains, prompt engineering, embeddings, or output parsing.
version: 1.0.0
---

# LangChain Development Skill

Patterns and templates for building LangChain AI agents in PartnerScout.

## When to Use

- Building AI agent chains (Brand Analyzer, Discovery, Scorer, Email Composer)
- Writing system and user prompts
- Configuring LLM providers (OpenAI, Gemini, Ollama)
- Generating embeddings
- Parsing structured JSON outputs

## Architecture

```
BaseAgent (Abstract)
  ├── BrandAnalyzerAgent
  ├── DiscoveryAgent
  ├── ScorerAgent
  └── EmailComposerAgent

Chain Pattern: prompt | llm | output_parser
LLM Factory: OpenAI | Gemini | Ollama
```

## Project Structure

```
backend/app/
├── agents/
│   ├── base.py              # BaseAgent abstract class
│   ├── brand_analyzer.py
│   ├── scorer.py
│   └── email_composer.py
├── prompts/
│   ├── loader.py
│   ├── brand_analyzer/
│   │   ├── system.txt
│   │   └── user.txt
│   └── scorer/
│       ├── system.txt
│       └── user.txt
└── core/
    └── llm.py               # LLM provider factory
```

## Guidelines

1. Store prompts in `.txt` files, not inline strings
2. Use `system.txt` for role, `user.txt` for task with `{placeholders}`
3. Use `LLM_PROVIDER` env var: `openai`, `gemini`, `ollama`
4. Use `JsonOutputParser` for structured responses
5. Implement retry logic for transient failures

---

## Code Templates

### BaseAgent

```python
from abc import ABC, abstractmethod
from langchain.prompts import ChatPromptTemplate
from app.prompts.loader import load_prompts
from app.core.llm import get_llm

class BaseAgent(ABC):
    AGENT_NAME: str = None
    
    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.system_prompt, self.user_prompt = load_prompts(self.AGENT_NAME)
        self.chain = self._build_chain()
    
    def _build_prompt_template(self):
        return ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", self.user_prompt)
        ])
    
    @abstractmethod
    def _build_chain(self): pass
    
    @abstractmethod
    async def run(self, **kwargs): pass
```

### Prompt Loader

```python
from pathlib import Path
PROMPTS_DIR = Path(__file__).parent

def load_prompt(agent_name: str, prompt_type: str) -> str:
    path = PROMPTS_DIR / agent_name / f"{prompt_type}.txt"
    return path.read_text().strip()

def load_prompts(agent_name: str) -> tuple[str, str]:
    return (load_prompt(agent_name, "system"), load_prompt(agent_name, "user"))
```

### LLM Factory

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from app.core.config import settings

def get_llm():
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    elif settings.LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, google_api_key=settings.GOOGLE_API_KEY)
    elif settings.LLM_PROVIDER == "ollama":
        return Ollama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
    raise ValueError(f"Unknown provider: {settings.LLM_PROVIDER}")
```

### Brand Analyzer Agent

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import OpenAIEmbeddings

class BrandAnalyzerAgent(BaseAgent):
    AGENT_NAME = "brand_analyzer"
    
    def __init__(self, llm=None):
        super().__init__(llm)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    def _build_chain(self):
        return self._build_prompt_template() | self.llm | JsonOutputParser()
    
    async def run(self, job_id: str, brand_description: str, reference_profiles: list[str]) -> dict:
        profile_data = await self.apify.scrape_profiles(reference_profiles)
        result = await self.chain.ainvoke({
            "brand_description": brand_description,
            "profile_data": self._format_profiles(profile_data)
        })
        embedding = await self.embeddings.aembed_query(f"{brand_description} {' '.join(result['keywords'])}")
        return {"hashtags": result["hashtags"], "keywords": result["keywords"], "embedding_vector": embedding}
```

### Scorer Agent

```python
class ScorerAgent(BaseAgent):
    AGENT_NAME = "scorer"
    
    def _build_chain(self):
        return self._build_prompt_template() | self.llm | JsonOutputParser()
    
    async def run(self, profile_id: str, job_id: str) -> dict:
        profile = await self.profile_repo.get_by_id(profile_id)
        brand_dna = await self.brand_repo.get_by_job(job_id)
        return await self.chain.ainvoke({
            "brand_hashtags": brand_dna.hashtags,
            "brand_keywords": brand_dna.keywords,
            "username": profile.username,
            "followers": profile.followers,
            "engagement_rate": profile.engagement_rate
        })
```

---

## Prompt Examples

### Scorer System Prompt
```text
You are an influencer partnership analyst.

Score profiles 0-100 on:
- visual_aesthetic_match (25%): Visual style alignment
- content_theme_alignment (20%): Topic fit
- engagement_rate_score (15%): Engagement quality
- follower_quality (15%): Authenticity signals
- business_indicators (15%): Business presence
- activity_recency (10%): Posting frequency

Fake signals: following_ratio > 2.0, posts < 20 with 5K+ followers, engagement < 1%

Return JSON with scores, summary, recommendation, email.
```

---

## Error Handling

```python
async def run_with_retry(self, **kwargs):
    for attempt in range(3):
        try:
            return await self.chain.ainvoke(kwargs)
        except Exception as e:
            if attempt == 2:
                raise AgentError(agent=self.AGENT_NAME, message=str(e))
            await asyncio.sleep(2 ** attempt)
```

## Environment Variables

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-pro
```

## Cross-References
- `docs/Agents_Documentation.md`
- `docs/Backend_Implementation_Guide.md`
