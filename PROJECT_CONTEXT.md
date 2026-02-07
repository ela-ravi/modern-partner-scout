# PartnerScout AI - Project Context

## 🎯 Project Overview
PartnerScout AI is a B2B partner discovery system for luxury/niche brands. It automates the process of finding Instagram boutiques and distributors that match a brand's aesthetic.

## 🏗️ Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Database:** Supabase (PostgreSQL + pgvector + Realtime)
- **AI/LLM:** Google Gemini (primary), OpenAI (backup)
- **Scraping:** Apify (Instagram Profile Scraper)
- **Orchestration:** n8n (self-hosted) + Python fallback

## 📁 Project Structure
```
modern-partner-scout/
├── backend/
│   ├── app/
│   │   ├── agents/        # AI Agents (Brand Analyzer, Discovery, Scorer)
│   │   ├── api/routes/    # FastAPI endpoints
│   │   ├── core/          # Config, constants, exceptions
│   │   ├── db/            # Supabase client
│   │   ├── guards/        # Auth, validation, ownership
│   │   ├── models/        # Pydantic models
│   │   ├── prompts/       # LLM prompt templates
│   │   ├── repositories/  # Database operations
│   │   └── services/      # Business logic
│   └── scripts/           # Python fallback orchestrator
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities, Supabase client
│   │   └── types/         # TypeScript types
├── docs/                  # All documentation
├── designs/               # HTML mockups
├── supabase/migrations/   # Database migrations
└── n8n/                   # n8n workflow configs
```

## 📋 Development Status

### ✅ COMPLETED (EPIC 1-3)
| EPIC | Description | Status |
|------|-------------|--------|
| EPIC-1 | Project Foundation & Infrastructure | ✅ DONE |
| EPIC-2 | Backend Core Services & API Layer | ✅ DONE |
| EPIC-3 | AI Agents & LLM Integration (up to STORY-3.3.4) | ✅ DONE |

### ❌ REMAINING (EPIC 4-7)
| EPIC | Description | Status |
|------|-------------|--------|
| EPIC-4 | Workflow Orchestration (n8n + Python) | 🔄 NEXT |
| EPIC-5 | Frontend Application Development | ⏳ PENDING |
| EPIC-6 | Comprehensive Testing & QA | ⏳ PENDING |
| EPIC-7 | Deployment & Production Readiness | ⏳ PENDING |

## 🔧 Current Configuration

### Backend (.env)
- Port: 8001
- LLM: Gemini (gemini-2.5-flash-lite)
- Database: Supabase (sojwzibebggyezzsxpgv)
- n8n: https://n8n.srv824552.hstgr.cloud

### Frontend (.env)
- API URL: http://localhost:8001/api
- Supabase: Same project as backend

## 📚 Key Documentation Files
- `docs/Partner_Scout_AI_PRD.md` - Product Requirements
- `docs/PartnerScout_AI_Agile_Development_Plan.md` - Full JIRA-style plan
- `docs/Backend_Implementation_Guide.md` - Backend architecture
- `docs/Orchestration.md` - n8n workflow details
- `docs/Frontend_Functionalities.md` - UI requirements
- `docs/Supabase_Database_Guide.md` - Database schema
- `docs/Agents_Documentation.md` - AI agent specs

## 🔌 API Endpoints (18 total, all working)
- Health: 2 endpoints
- Jobs: 6 endpoints  
- Status: 3 endpoints
- Email: 3 endpoints
- Agents: 4 endpoints

## ⚠️ Important Rules
1. Always read relevant docs before implementing
2. Follow the JIRA structure (EPIC → FEATURE → STORY → TASK)
3. Validate each implementation against PRD
4. Don't modify completed EPIC 1-3 code unless fixing bugs
5. Use existing patterns from backend code
6. Test each endpoint after implementation