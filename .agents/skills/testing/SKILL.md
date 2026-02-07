# Testing Agent

## Purpose
Implement EPIC-6: Comprehensive Testing & Quality Assurance.

## Before Starting
Read these files in order:
1. `PROJECT_CONTEXT.md` - Project overview
2. `docs/Partner_Scout_AI_PRD.md` - Section 13 (Demo Acceptance Criteria)
3. `docs/PartnerScout_AI_Agile_Development_Plan.md` - EPIC-6 section
4. `docs/Backend_Implementation_Guide.md` - Section 12 (Mock Data)
5. `backend/tests/` - Existing test structure

## Current Status
- Backend has `tests/` folder with pytest configured
- `pytest.ini` exists in backend folder
- All 18 API endpoints need test coverage

## Test Categories

### 1. Backend Unit Tests
- Guards: `tests/test_guards.py`
- Repositories: `tests/test_repositories.py`
- Services: `tests/test_services.py`
- Agents: `tests/test_agents.py`

### 2. API Integration Tests
- Health: `tests/test_api_health.py`
- Jobs: `tests/test_api_jobs.py`
- Status: `tests/test_api_status.py`
- Agents: `tests/test_api_agents.py`
- Email: `tests/test_api_email.py`

### 3. Frontend Tests (Vitest)
- Components: `frontend/src/__tests__/`
- Hooks: `frontend/src/hooks/__tests__/`

## Mock Data
Use consistent test UUIDs:
```python
TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_JOB_ID = "22222222-2222-2222-2222-222222222222"
TEST_PROFILE_ID = "33333333-3333-3333-3333-333333333333"
```

## Test Commands
```bash
# Run all backend tests
cd backend
pytest

# Run specific test file
pytest tests/test_api_jobs.py -v

# Run with coverage
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm run test
```

## Demo Acceptance Criteria (Must Pass)
1. ✅ Create discovery session with brand description
2. ✅ Add 2-10 reference Instagram URLs
3. ✅ Start discovery and see status updates
4. ✅ View discovered profiles in real-time
5. ✅ See scores with 6-dimension breakdown
6. ✅ Filter profiles by score threshold
7. ✅ View profile details with AI reasoning
8. ✅ Generate outreach email
9. ✅ Complete flow in < 5 minutes demo

## Validation
```bash
# Health check
curl http://localhost:8001/api/health

# Full test suite
cd backend && pytest -v

# Coverage report
pytest --cov=app --cov-report=term-missing
```