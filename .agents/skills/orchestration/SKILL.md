# Orchestration Agent

## Purpose
Implement EPIC-4: Workflow Orchestration using n8n and Python fallback.

## Before Starting
Read these files in order:
1. `PROJECT_CONTEXT.md` - Project overview
2. `docs/Orchestration.md` - Complete orchestration guide
3. `docs/PartnerScout_AI_Agile_Development_Plan.md` - EPIC-4 section
4. `docs/Partner_Scout_AI_PRD.md` - Section 5.5 (Orchestration), 7.2 (Flow)
5. `backend/app/api/routes/` - Understand existing API structure

## Current Status
- All backend APIs are working (18 endpoints on port 8001)
- All 3 AI agents implemented (Brand Analyzer, Discovery, Scorer)
- Database ready with all tables, RLS, and Realtime enabled
- n8n URL: https://n8n.srv824552.hstgr.cloud

## Your Tasks (EPIC-4)

### FEAT-4.1: n8n Workflow Implementation
- Configure n8n workflow with 21 nodes
- Set up webhook trigger
- Connect to backend APIs
- Handle status transitions

### FEAT-4.2: Python Fallback Orchestrator
- Implement `scripts/run_discovery.py`
- Status update functions
- Agent call functions
- Main orchestration loop
- CLI entry point

## Key Configuration
```
N8N_SERVICE_KEY=ks-partnerscout-n8n-2026-secure
N8N_WEBHOOK_URL=https://n8n.srv824552.hstgr.cloud/webhook/partner-discovery
Backend API: http://localhost:8001/api
```

## API Endpoints to Orchestrate
1. `POST /api/jobs` - Create job
2. `PATCH /api/jobs/{id}/status` - Update job status
3. `POST /api/agent/analyze-brand` - Run Brand Analyzer
4. `POST /api/agent/discover` - Run Discovery
5. `POST /api/agent/score` - Run Scorer (per profile)
6. `PATCH /api/profiles/{id}/status` - Update profile status

## Workflow Sequence
```
1. Webhook receives job_id
2. Update job status → "analyzing"
3. Call Brand Analyzer API
4. Update job status → "discovering"
5. Call Discovery API
6. Update job status → "scoring"
7. For each profile: Call Scorer API
8. Update job status → "completed"
```

## Validation
After implementation, test with:
```bash
# Test Python fallback
cd backend
python -m scripts.run_discovery <job_id>
```