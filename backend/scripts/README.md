# Python Orchestrator - Quick Reference

Run discovery agents via CLI. Requires backend server running on `localhost:8000`.

---

## Setup

```bash
cd /Volumes/Development/Practise/partner-scout/backend
source venv/bin/activate
```

---

## LLM Providers

Set in `.env`:

| Provider | Env Var | Example Model |
|----------|---------|---------------|
| `openai` | `OPENAI_API_KEY` | gpt-4-turbo-preview |
| `gemini` | `GEMINI_API_KEY` | gemini-pro |
| `openrouter` | `OPENROUTER_API_KEY` | anthropic/claude-3.5-sonnet |
| `huggingface` | `HUGGINGFACE_API_KEY` | mistralai/Mistral-7B-Instruct-v0.2 |
| `ollama` | (local) | llama2 |

```bash
LLM_PROVIDER=huggingface
EMBEDDING_PROVIDER=huggingface
```

---

## Create a New Job

```bash
curl -s -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $(python -c "from app.guards.auth import create_test_token; print(create_test_token('5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9'))")" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Job",
    "brand_description": "A boutique coffee roastery specializing in single-origin beans.",
    "reference_profiles": ["https://instagram.com/bluebottlecoffee", "https://instagram.com/stumptowncoffee"],
    "follower_range_min": 5000,
    "follower_range_max": 100000,
    "discovery_limit": 10
  }' | python -m json.tool | grep '"id"'
```

---

## Run Agents

### Individual Phases
```bash
python -m scripts.run_discovery <job_id> --phase analyze-only   # Phase 1
python -m scripts.run_discovery <job_id> --phase discover-only  # Phase 1+2
python -m scripts.run_discovery <job_id> --phase score-only     # Phase 3 only
```

### Full Workflow
```bash
python -m scripts.run_discovery <job_id> --phase full
```

This runs: Analyze → Discover → Score → Complete
