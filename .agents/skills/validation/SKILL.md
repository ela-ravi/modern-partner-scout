# Validation Agent

## Purpose
Validate all implementations against PRD and documentation requirements.

## Before Starting
Read these files in order:
1. `PROJECT_CONTEXT.md` - Project overview
2. `docs/Partner_Scout_AI_PRD.md` - Source of truth
3. `docs/PartnerScout_AI_Agile_Development_Plan.md` - Task definitions
4. `docs/Frontend_Functionalities.md` - 79 UI requirements

## Validation Checklist

### Database Validation
Compare against `docs/Supabase_Database_Guide.md`:
- [ ] All 5 tables exist
- [ ] All columns match schema
- [ ] RLS policies enabled
- [ ] Realtime enabled
- [ ] Indexes created
- [ ] Triggers working

### Backend API Validation
Compare against `docs/Backend_Implementation_Guide.md`:
- [ ] All 18 endpoints respond correctly
- [ ] Request/response schemas match
- [ ] Error codes consistent
- [ ] Auth guards working
- [ ] Service key authentication working

### Agent Validation
Compare against `docs/Agents_Documentation.md`:
- [ ] Brand Analyzer extracts hashtags, keywords, embedding
- [ ] Discovery finds profiles via Apify
- [ ] Scorer returns 6-dimension scores
- [ ] Contact extraction works

### Frontend Validation
Compare against `docs/Frontend_Functionalities.md`:
- [ ] All 79 functionalities implemented
- [ ] Designs match `designs/` mockups
- [ ] Realtime updates working
- [ ] Error states handled

### Orchestration Validation
Compare against `docs/Orchestration.md`:
- [ ] n8n workflow has all 21 nodes
- [ ] Python fallback script works
- [ ] Status transitions correct
- [ ] End-to-end flow completes

## Validation Commands

### Quick Health Check
```bash
curl http://localhost:8001/api/health
```

### Test All Endpoints
```bash
# Jobs
curl http://localhost:8001/api/jobs -H "Authorization: Bearer TOKEN"

# Agents (use service key)
curl -X POST http://localhost:8001/api/agent/status \
  -H "X-Service-Key: ks-partnerscout-n8n-2026-secure"
```

### Database Verification
```sql
-- Run in Supabase SQL Editor
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

## Validation Report Format
After validating, create report in `docs/validations/`:
```markdown
# Validation Report: [Component Name]
**Date:** YYYY-MM-DD
**Validator:** [Agent Name]

## Summary
| Category | Total | Pass | Fail |
|----------|-------|------|------|
| ...      | ...   | ...  | ...  |

## Details
### ✅ Passed
- Item 1
- Item 2

### ❌ Failed
- Item 1: [Reason]
- Item 2: [Reason]

## Recommendations
1. ...
2. ...
```