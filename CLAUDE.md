# PartnerScout AI - Claude Code Project Instructions

## Project Overview

PartnerScout AI is an automated Instagram partner discovery platform for D2C brands. It uses AI agents to analyze brand identity, discover similar profiles, score candidates, and extract contact information.

## Tech Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **Routing**: React Router v6

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **AI Framework**: LangChain (multi-provider: OpenAI, Gemini, Ollama)
- **Database**: Supabase (PostgreSQL) with SQLite fallback
- **Auth**: Supabase Auth

### Orchestration
- **Workflow Engine**: n8n
- **Scraping**: Apify (Instagram)

## Project Structure

```
partner-scout/
├── frontend/                 # React TypeScript app
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Route pages
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client services
│   │   ├── types/            # TypeScript type definitions
│   │   └── utils/            # Helper utilities
│   └── ...
├── backend/                  # FastAPI Python app
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   ├── agents/           # AI agent implementations
│   │   ├── models/           # Pydantic models
│   │   ├── services/         # Business logic
│   │   └── db/               # Database utilities
│   └── ...
├── n8n/                      # n8n workflow exports
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

## Coding Conventions

### Python (Backend)
- Use type hints everywhere
- Follow PEP 8 style guide
- Use Pydantic for all data validation
- Async functions for all I/O operations
- Docstrings for all public functions

### TypeScript (Frontend)
- Strict TypeScript - no `any` types
- Functional components with hooks
- Use interfaces over types where possible
- Destructure props in function parameters

### API Design
- RESTful endpoints under `/api/`
- Agent endpoints under `/api/agent/`
- Use consistent error response format:
  ```json
  { "error": { "code": "ERROR_CODE", "message": "Human readable message" } }
  ```

## Database Schema

### Core Tables
- `users` - Supabase Auth managed
- `discovery_jobs` - Discovery sessions (status: pending -> analyzing -> discovering -> scoring -> completed/failed)
- `brand_dna` - Extracted brand identity (hashtags, keywords, embedding)
- `discovered_profiles` - Found Instagram profiles (status: new -> processing -> done/skipped)
- `profile_scores` - AI scoring results (0-100 with reasoning)
- `profile_contacts` - Extracted emails

### Relationships
```
users (1) -> (many) discovery_jobs
discovery_jobs (1) -> (1) brand_dna
discovery_jobs (1) -> (many) discovered_profiles
discovered_profiles (1) -> (1) profile_scores
discovered_profiles (1) -> (1) profile_contacts
```

## AI Agents

### Brand Analyzer Agent
- **Endpoint**: `POST /api/agent/analyze-brand`
- **Purpose**: Extract brand DNA from reference profiles
- **Output**: hashtags, keywords, embedding vector

### Discovery Agent
- **Endpoint**: `POST /api/agent/discover`
- **Purpose**: Find similar Instagram profiles
- **Output**: Profile URLs with basic metadata

### Scorer Agent
- **Endpoint**: `POST /api/agent/score`
- **Purpose**: Score candidate profiles against brand DNA
- **Output**: Score (0-100), reasoning breakdown, contact email

## Environment Variables

### Backend
```
SUPABASE_URL=
SUPABASE_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
APIFY_API_KEY=
LLM_PROVIDER=openai  # openai | gemini | ollama
```

### Frontend
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_URL=
```

## Key Principles

1. **Demo-first**: Everything must work reliably for demos
2. **Real-time UX**: Profiles appear incrementally as discovered
3. **Explainable AI**: All scores must include reasoning
4. **Graceful degradation**: Use fallbacks (SQLite, mock data) when services fail
5. **Modular agents**: Each agent is independent and testable

## Common Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database migrations
cd backend
alembic upgrade head
```

## Testing

- Backend: pytest with async support
- Frontend: Vitest + React Testing Library
- E2E: Playwright

## Performance Targets

- Process 50 profiles in < 10 minutes
- Dashboard updates in real-time (polling every 2s or webhooks)
- Demo completes in under 5 minutes

## Frontend Design Guidelines

When building or modifying frontend interfaces, follow these principles:

- **Typography**: Choose distinctive, beautiful fonts. Avoid generic defaults like Arial, Inter, Roboto.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Bold dominant colors with sharp accents over timid, evenly-distributed palettes.
- **Motion**: Use animations for micro-interactions. Prioritize CSS-only solutions. Use staggered reveals and scroll-triggered effects.
- **Spatial Composition**: Embrace asymmetry, overlap, and grid-breaking elements. Use generous negative space or controlled density.
- **Backgrounds & Visual Details**: Create depth with gradient meshes, noise textures, geometric patterns, layered transparencies, and grain overlays.
- Avoid generic AI-generated aesthetics: no overused font families, no cliched purple-gradient-on-white color schemes, no cookie-cutter layouts.
