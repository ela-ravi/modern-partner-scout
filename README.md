# PartnerScout AI

> Automated Instagram partner discovery platform for D2C brands

PartnerScout AI uses AI agents to analyze brand identity, discover similar Instagram profiles, score candidates, and extract contact information for partnership outreach.

---

## Features

- **Brand DNA Extraction** - Analyze reference profiles to extract hashtags, keywords, and brand identity
- **Profile Discovery** - Find similar Instagram profiles using AI-powered similarity search
- **6-Dimension Scoring** - Score candidates on visual aesthetics, content alignment, engagement, authenticity, business indicators, and activity
- **Fake Detection** - Identify suspicious accounts using PRD-defined authenticity signals
- **Contact Extraction** - Extract emails from business profiles, bios, and linked websites
- **Real-time Dashboard** - Live updates as profiles are discovered and scored

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Tailwind CSS, React Query |
| Backend | Python 3.10+, FastAPI, Pydantic |
| AI | LangChain (OpenAI, Gemini, Ollama) |
| Database | Supabase (PostgreSQL) with SQLite fallback |
| Auth | Supabase Auth |
| Scraping | Apify (Instagram) |
| Orchestration | n8n workflows |

---

## Quick Start

### 1. Clone and Setup Backend

```bash
git clone https://github.com/your-org/partner-scout.git
cd partner-scout/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env.local`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
LLM_PROVIDER=openai
```

### 3. Setup Database

**Option A: Supabase (Production)**

1. Open Supabase SQL Editor
2. Copy `setup/supabase/all_migrations.sql`
3. Paste and execute

**Option B: SQLite (Local Development)**

Set in `.env.local`:
```env
USE_SQLITE_FALLBACK=true
```

### 4. Seed Test Data (Optional)

```bash
cd backend
python ../setup/scripts/seed_database.py --reset
```

### 5. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## Project Structure

```
partner-scout/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── agents/           # AI agent implementations
│   │   ├── api/              # API route handlers
│   │   ├── core/             # Config, logging, exceptions
│   │   ├── db/               # Database clients (Supabase/SQLite)
│   │   ├── models/           # Pydantic models
│   │   ├── repositories/     # Data access layer
│   │   └── services/         # Business logic
│   └── tests/
├── frontend/                 # React TypeScript app (coming soon)
├── setup/                    # Setup scripts and migrations
│   ├── scripts/              # Validation and seeding scripts
│   └── supabase/             # SQL migrations
├── docs/                     # Documentation
├── designs/                  # HTML design mockups
└── n8n/                      # n8n workflow exports
```

---

## Database Schema

```
discovery_jobs (1) ─┬─ (1) brand_dna
                    └─ (many) discovered_profiles ─┬─ (1) profile_scores
                                                   └─ (1) profile_contacts
```

| Table | Description |
|-------|-------------|
| `discovery_jobs` | Discovery sessions per user |
| `brand_dna` | Extracted brand identity (hashtags, keywords, embedding) |
| `discovered_profiles` | Candidate Instagram profiles |
| `profile_scores` | AI scoring with 6 dimensions (0-100) |
| `profile_contacts` | Extracted contact emails |

---

## AI Agents

| Agent | Endpoint | Purpose |
|-------|----------|---------|
| Brand Analyzer | `POST /api/agent/analyze-brand` | Extract brand DNA from reference profiles |
| Discovery Agent | `POST /api/agent/discover` | Find similar Instagram profiles |
| Scorer Agent | `POST /api/agent/score` | Score candidates with 6 dimensions |

---

## Development

### Run Tests

```bash
cd backend
pytest                          # All tests
pytest tests/unit               # Unit tests only
pytest tests/integration        # Integration tests only
pytest -v --tb=short            # Verbose with short traceback
```

### Type Checking

```bash
cd backend
mypy app --follow-imports=skip
```

### Validate Implementation

```bash
cd backend
python ../setup/scripts/validate_epic2.py
```

---

## Environment Variables

### Backend

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes* |
| `SUPABASE_KEY` | Supabase anon key | Yes* |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Yes* |
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI provider |
| `GOOGLE_API_KEY` | Google API key | For Gemini provider |
| `LLM_PROVIDER` | `openai` \| `gemini` \| `ollama` | Default: `openai` |
| `USE_SQLITE_FALLBACK` | Use local SQLite | Default: `false` |
| `APIFY_API_KEY` | Apify API key | For Instagram scraping |

\* Not required if `USE_SQLITE_FALLBACK=true`

---

## Documentation

- [PRD](docs/Partner_Scout_AI_PRD.md) - Product Requirements Document
- [Backend Guide](docs/Backend_Implementation_Guide.md) - Implementation details
- [Database Guide](docs/Supabase_Database_Guide.md) - Schema and queries
- [Agents](docs/Agents_Documentation.md) - AI agent specifications
- [Setup Guide](setup/README.md) - Detailed setup instructions

---

## Contributing

1. Create a feature branch from `main`
2. Make changes following project conventions
3. Ensure tests pass: `pytest`
4. Ensure types check: `mypy app`
5. Submit a pull request

---

## License

MIT License - see LICENSE file for details.
