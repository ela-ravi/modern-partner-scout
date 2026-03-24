# PartnerScout AI - Agile Development Plan

Complete development plan structured for Agile project management tools (Jira, Azure DevOps, Trello, etc.) with Epic > Feature > Story > Task > Subtask hierarchy, including validation steps with curl/Swagger and comprehensive testing.

---

## Table of Contents

1. [Agile Hierarchy Legend](#agile-hierarchy-legend)
2. [EPIC-1: Project Foundation & Infrastructure Setup](#epic-1-project-foundation--infrastructure-setup)
3. [EPIC-2: Backend Core Services & API Layer](#epic-2-backend-core-services--api-layer)
4. [EPIC-3: AI Agents & LLM Integration](#epic-3-ai-agents--llm-integration)
5. [EPIC-4: Workflow Orchestration (Python Pipeline)](#epic-4-workflow-orchestration-python-pipeline)
6. [EPIC-5: Frontend Application Development](#epic-5-frontend-application-development)
7. [EPIC-6: Comprehensive Testing & Quality Assurance](#epic-6-comprehensive-testing--quality-assurance)
8. [EPIC-7: Deployment & Production Readiness](#epic-7-deployment--production-readiness)
9. [Appendix: Validation Commands Reference](#appendix-validation-commands-reference)
10. [Test Coverage Summary](#test-coverage-summary)

---

## Agile Hierarchy Legend

| Level | Format | Description |
|-------|--------|-------------|
| **Epic** | EPIC-X | Large body of work spanning multiple sprints |
| **Feature** | FEAT-X.Y | Distinct functionality within an Epic |
| **Story** | STORY-X.Y.Z | User-facing deliverable |
| **Task** | TASK-X.Y.Z.N | Technical implementation work |
| **Subtask** | SUB-X.Y.Z.N.M | Granular work item within a Task |

---

## Epics Overview

| Epic | Description | Features | Stories |
|------|-------------|----------|---------|
| **EPIC-1** | Project Foundation & Infrastructure Setup | 2 | 8 |
| **EPIC-2** | Backend Core Services & API Layer | 4 | 13 |
| **EPIC-3** | AI Agents & LLM Integration | 3 | 8 |
| **EPIC-4** | Workflow Orchestration (Python Pipeline) | 2 | 4 |
| **EPIC-5** | Frontend Application Development | 7 | 12 |
| **EPIC-6** | Comprehensive Testing & QA | 3 | 6 |
| **EPIC-7** | Deployment & Production Readiness | 3 | 3 |

---

# EPIC-1: Project Foundation & Infrastructure Setup

**Description:** Set up project structure, development environments, and database infrastructure.

**Acceptance Criteria:** All environments running, database schema deployed, team can start development.

---

## FEAT-1.1: Project Structure & Environment Setup

### STORY-1.1.1: Initialize Project Repository Structure

**As a** developer, **I want** a well-organized project structure **so that** the team can collaborate efficiently.

#### TASK-1.1.1.1: Create Backend Project Structure

| Subtask | Description |
|---------|-------------|
| SUB-1.1.1.1.1 | Create `backend/` directory with FastAPI structure |
| SUB-1.1.1.1.2 | Create `app/core/`, `app/guards/`, `app/api/routes/` directories |
| SUB-1.1.1.1.3 | Create `app/models/`, `app/services/`, `app/repositories/` directories |
| SUB-1.1.1.1.4 | Create `app/agents/`, `app/prompts/`, `app/db/` directories |
| SUB-1.1.1.1.5 | Create `scripts/` and `tests/` directories |
| SUB-1.1.1.1.6 | Create `requirements.txt` with all dependencies |
| SUB-1.1.1.1.7 | Create `.env.example` template |

#### TASK-1.1.1.2: Create Frontend Project Structure

| Subtask | Description |
|---------|-------------|
| SUB-1.1.1.2.1 | Initialize Vite + React + TypeScript project |
| SUB-1.1.1.2.2 | Create `src/components/`, `src/pages/`, `src/hooks/` directories |
| SUB-1.1.1.2.3 | Create `src/lib/`, `src/types/`, `src/styles/` directories |
| SUB-1.1.1.2.4 | Configure Tailwind CSS |
| SUB-1.1.1.2.5 | Create `.env.example` template |

#### TASK-1.1.1.3: Create Supabase & Orchestration Structure

| Subtask | Description |
|---------|-------------|
| SUB-1.1.1.3.1 | Create `supabase/migrations/` directory |
| SUB-1.1.1.3.2 | Create `supabase/seed.sql` file |
| SUB-1.1.1.3.3 | Create `backend/scripts/` directory for orchestration scripts |

**Validation:** Run `tree` or `ls -R` to verify all directories exist.

---

### STORY-1.1.2: Configure Backend Development Environment

**As a** backend developer, **I want** a working Python environment **so that** I can develop FastAPI services.

#### TASK-1.1.2.1: Setup Python Virtual Environment

| Subtask | Description |
|---------|-------------|
| SUB-1.1.2.1.1 | Install Python 3.10+ |
| SUB-1.1.2.1.2 | Create virtual environment: `python -m venv venv` |
| SUB-1.1.2.1.3 | Activate and install dependencies: `pip install -r requirements.txt` |

#### TASK-1.1.2.2: Configure Environment Variables

| Subtask | Description |
|---------|-------------|
| SUB-1.1.2.2.1 | Copy `.env.example` to `.env` |
| SUB-1.1.2.2.2 | Configure Supabase credentials |
| SUB-1.1.2.2.3 | Configure LLM provider keys (OpenAI/Gemini) |
| SUB-1.1.2.2.4 | Configure Apify API key |
| SUB-1.1.2.2.5 | Configure orchestration service key |

#### TASK-1.1.2.3: Create Minimal FastAPI App

| Subtask | Description |
|---------|-------------|
| SUB-1.1.2.3.1 | Create `app/__init__.py` |
| SUB-1.1.2.3.2 | Create minimal `app/main.py` with health endpoint |

**Validation - curl:**

```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Test health endpoint
curl -X GET http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

**Validation - Swagger:** Open http://localhost:8000/docs, verify Swagger UI loads.

---

### STORY-1.1.3: Configure Frontend Development Environment

**As a** frontend developer, **I want** a working React environment **so that** I can develop the dashboard.

#### TASK-1.1.3.1: Setup Node.js Environment

| Subtask | Description |
|---------|-------------|
| SUB-1.1.3.1.1 | Install Node.js 18+ |
| SUB-1.1.3.1.2 | Install dependencies: `npm install` |
| SUB-1.1.3.1.3 | Configure Supabase environment variables |

#### TASK-1.1.3.2: Verify Development Server

| Subtask | Description |
|---------|-------------|
| SUB-1.1.3.2.1 | Run `npm run dev` |
| SUB-1.1.3.2.2 | Verify app loads at http://localhost:5173 |

**Validation:** Open http://localhost:5173, verify React app loads without errors.

---

## FEAT-1.2: Supabase Database Setup

### STORY-1.2.1: Create Supabase Project & Configure Access

**As a** developer, **I want** a Supabase project **so that** I have a production-ready PostgreSQL database.

#### TASK-1.2.1.1: Create Supabase Project

| Subtask | Description |
|---------|-------------|
| SUB-1.2.1.1.1 | Create account at supabase.com |
| SUB-1.2.1.1.2 | Create new project |
| SUB-1.2.1.1.3 | Document Project URL, Anon Key, Service Role Key, JWT Secret |
| SUB-1.2.1.1.4 | Enable pgvector extension |

**Validation:** Log into Supabase dashboard, verify project is created.

---

### STORY-1.2.2: Deploy Database Schema

**As a** developer, **I want** the database schema deployed **so that** I can persist application data.

#### TASK-1.2.2.1: Create Initial Schema Migration

| Subtask | Description |
|---------|-------------|
| SUB-1.2.2.1.1 | Create `001_initial_schema.sql` with all tables |
| SUB-1.2.2.1.2 | Define `discovery_jobs` table |
| SUB-1.2.2.1.3 | Define `brand_dna` table with vector column |
| SUB-1.2.2.1.4 | Define `discovered_profiles` table |
| SUB-1.2.2.1.5 | Define `profile_scores` table with 6 dimensions |
| SUB-1.2.2.1.6 | Define `profile_contacts` table |
| SUB-1.2.2.1.7 | Create enum types for status values |

#### TASK-1.2.2.2: Create Indexes & Triggers

| Subtask | Description |
|---------|-------------|
| SUB-1.2.2.2.1 | Create indexes on foreign keys and frequently queried columns |
| SUB-1.2.2.2.2 | Create `updated_at` auto-update trigger |
| SUB-1.2.2.2.3 | Create `profiles_discovered` counter trigger |
| SUB-1.2.2.2.4 | Create `profiles_scored` counter trigger |

#### TASK-1.2.2.3: Create Convenience Views

| Subtask | Description |
|---------|-------------|
| SUB-1.2.2.3.1 | Create `v_complete_profiles` view |
| SUB-1.2.2.3.2 | Create `v_job_summary` view |

**Validation - Supabase SQL Editor:**

```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
-- Expected: discovery_jobs, brand_dna, discovered_profiles, profile_scores, profile_contacts
```

---

### STORY-1.2.3: Enable Row Level Security

**As a** security engineer, **I want** RLS policies **so that** users can only access their own data.

#### TASK-1.2.3.1: Create RLS Policies

| Subtask | Description |
|---------|-------------|
| SUB-1.2.3.1.1 | Create `002_enable_rls.sql` migration |
| SUB-1.2.3.1.2 | Enable RLS on all tables |
| SUB-1.2.3.1.3 | Create policy for `discovery_jobs` (user_id check) |
| SUB-1.2.3.1.4 | Create policy for `brand_dna` (via job ownership) |
| SUB-1.2.3.1.5 | Create policy for `discovered_profiles` (via job ownership) |
| SUB-1.2.3.1.6 | Create policy for `profile_scores` (via profile ownership) |
| SUB-1.2.3.1.7 | Create policy for `profile_contacts` (via profile ownership) |

**Validation:**

```sql
SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
```

---

### STORY-1.2.4: Enable Realtime & Seed Data

**As a** developer, **I want** realtime enabled and test data seeded **so that** I can develop with realistic data.

#### TASK-1.2.4.1: Enable Realtime

| Subtask | Description |
|---------|-------------|
| SUB-1.2.4.1.1 | Create `003_enable_realtime.sql` migration |
| SUB-1.2.4.1.2 | Add tables to realtime publication |

#### TASK-1.2.4.2: Create Seed Data

| Subtask | Description |
|---------|-------------|
| SUB-1.2.4.2.1 | Create `seed.sql` with sample job |
| SUB-1.2.4.2.2 | Add sample brand_dna entry |
| SUB-1.2.4.2.3 | Add 3 sample discovered_profiles |
| SUB-1.2.4.2.4 | Add sample scores and contacts |

**Validation:**

```sql
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
SELECT COUNT(*) FROM discovery_jobs; -- Expected: >= 1
```

---

### Testing Summary for FEAT-1.2

| Test Type | Description | Tool |
|-----------|-------------|------|
| Schema Validation | All tables created correctly | Supabase SQL Editor |
| RLS Unit Test | Policies reject unauthorized access | Supabase SQL with different roles |
| Trigger Test | Counters update automatically | INSERT/DELETE and verify counts |
| Realtime Test | Changes broadcast to subscribers | Supabase Realtime inspector |

---

# EPIC-2: Backend Core Services & API Layer

**Description:** Implement backend infrastructure including configuration, guards, services, and API routes.

**Acceptance Criteria:** All API endpoints functional, properly authenticated, and tested.

---

## FEAT-2.1: Core Configuration & Infrastructure

### STORY-2.1.1: Implement Configuration Management

**As a** developer, **I want** centralized configuration **so that** I can easily manage environment-specific settings.

#### TASK-2.1.1.1: Create Environment Config

| Subtask | Description |
|---------|-------------|
| SUB-2.1.1.1.1 | Create `app/core/config.py` with pydantic-settings |
| SUB-2.1.1.1.2 | Define Supabase settings |
| SUB-2.1.1.1.3 | Define LLM provider settings |
| SUB-2.1.1.1.4 | Define Apify settings |
| SUB-2.1.1.1.5 | Define orchestration settings |

#### TASK-2.1.1.2: Create Constants & Enums

| Subtask | Description |
|---------|-------------|
| SUB-2.1.1.2.1 | Create `app/core/constants.py` |
| SUB-2.1.1.2.2 | Define `HttpStatus` class |
| SUB-2.1.1.2.3 | Define `ErrorCodes` class |
| SUB-2.1.1.2.4 | Define `JobStatus` and `ProfileStatus` enums |
| SUB-2.1.1.2.5 | Define `VALID_JOB_TRANSITIONS` and `VALID_PROFILE_TRANSITIONS` |
| SUB-2.1.1.2.6 | Define `Tables`, `Routes`, `Defaults` classes |

#### TASK-2.1.1.3: Create Custom Exceptions

| Subtask | Description |
|---------|-------------|
| SUB-2.1.1.3.1 | Create `app/core/exceptions.py` |
| SUB-2.1.1.3.2 | Implement `BusinessError` base class |
| SUB-2.1.1.3.3 | Implement `NotFoundError`, `UnauthorizedError`, `ForbiddenError` |
| SUB-2.1.1.3.4 | Implement `AgentError` for AI failures |

#### TASK-2.1.1.4: Create YAML Config Loader

| Subtask | Description |
|---------|-------------|
| SUB-2.1.1.4.1 | Create `app/core/settings/__init__.py` with loader |
| SUB-2.1.1.4.2 | Create `agents.yaml` configuration |
| SUB-2.1.1.4.3 | Create `scoring.yaml` with weights and thresholds |
| SUB-2.1.1.4.4 | Create `limits.yaml` with rate limits and timeouts |

**Validation - Unit Test:**

```python
def test_config_loads():
    from app.core.config import settings
    assert settings.SUPABASE_URL is not None
    
def test_yaml_config_loads():
    from app.core.settings import get_scoring_config
    config = get_scoring_config()
    assert sum(config["weights"].values()) == 1.0
```

---

### STORY-2.1.2: Implement Database Layer

**As a** developer, **I want** a database abstraction layer **so that** I can interact with Supabase consistently.

#### TASK-2.1.2.1: Create Supabase Client

| Subtask | Description |
|---------|-------------|
| SUB-2.1.2.1.1 | Create `app/db/supabase.py` |
| SUB-2.1.2.1.2 | Implement client factory function |
| SUB-2.1.2.1.3 | Implement `get_db()` dependency for FastAPI |

**Validation - Unit Test:**

```python
def test_supabase_connection():
    from app.db.supabase import get_db
    db = get_db()
    result = db.table("discovery_jobs").select("id").limit(1).execute()
    assert result is not None
```

---

### STORY-2.1.3: Implement Repository Layer

**As a** developer, **I want** repository classes **so that** database operations are encapsulated.

#### TASK-2.1.3.1: Create Base Repository

| Subtask | Description |
|---------|-------------|
| SUB-2.1.3.1.1 | Create `app/repositories/base_repo.py` |
| SUB-2.1.3.1.2 | Implement generic `get_by_id()`, `list_all()`, `delete()` methods |

#### TASK-2.1.3.2: Create Job Repository

| Subtask | Description |
|---------|-------------|
| SUB-2.1.3.2.1 | Create `app/repositories/job_repo.py` |
| SUB-2.1.3.2.2 | Implement `create()` method |
| SUB-2.1.3.2.3 | Implement `list_by_user()` method |
| SUB-2.1.3.2.4 | Implement `count_user_jobs_today()` method |
| SUB-2.1.3.2.5 | Implement `update_status()` method |

#### TASK-2.1.3.3: Create Profile Repository

| Subtask | Description |
|---------|-------------|
| SUB-2.1.3.3.1 | Create `app/repositories/profile_repo.py` |
| SUB-2.1.3.3.2 | Implement `list_by_job_with_scores()` method |
| SUB-2.1.3.3.3 | Implement `update_status()` method |

#### TASK-2.1.3.4: Create Brand & Score Repositories

| Subtask | Description |
|---------|-------------|
| SUB-2.1.3.4.1 | Create `app/repositories/brand_repo.py` |
| SUB-2.1.3.4.2 | Create `app/repositories/score_repo.py` |

**Validation - Unit Test:**

```python
def test_job_repo_create():
    from app.repositories.job_repo import JobRepository
    repo = JobRepository()
    job = await repo.create(user_id="test", brand_description="Test", reference_profiles=["url1", "url2"])
    assert job.id is not None
```

---

### STORY-2.1.4: Implement Pydantic Models

**As a** developer, **I want** Pydantic models **so that** request/response validation is automatic.

#### TASK-2.1.4.1: Create Job Models

| Subtask | Description |
|---------|-------------|
| SUB-2.1.4.1.1 | Create `app/models/job.py` |
| SUB-2.1.4.1.2 | Define `CreateJobRequest`, `UpdateJobRequest` |
| SUB-2.1.4.1.3 | Define `Job`, `JobWithProfiles` response models |

#### TASK-2.1.4.2: Create Profile Models

| Subtask | Description |
|---------|-------------|
| SUB-2.1.4.2.1 | Create `app/models/profile.py` |
| SUB-2.1.4.2.2 | Define `Profile`, `ProfileScore`, `ProfileContact` |
| SUB-2.1.4.2.3 | Define `CompleteProfile` (profile + score + contact) |

#### TASK-2.1.4.3: Create Agent & Status Models

| Subtask | Description |
|---------|-------------|
| SUB-2.1.4.3.1 | Create `app/models/brand.py` with `BrandDNA` |
| SUB-2.1.4.3.2 | Create `app/models/agent.py` with request/response models |
| SUB-2.1.4.3.3 | Create `app/models/email.py` with email models |
| SUB-2.1.4.3.4 | Create `app/models/status.py` with status update models |

**Validation - Unit Test:**

```python
def test_create_job_request_validation():
    from app.models.job import CreateJobRequest
    # Should raise ValidationError - too few profiles
    with pytest.raises(ValidationError):
        CreateJobRequest(brand_description="Test", reference_profiles=["url1"])
```

---

## FEAT-2.2: Authentication & Guards Layer

### STORY-2.2.1: Implement Authentication Guards

**As a** security engineer, **I want** authentication guards **so that** only authorized users access the API.

#### TASK-2.2.1.1: Create Auth Guards

| Subtask | Description |
|---------|-------------|
| SUB-2.2.1.1.1 | Create `app/guards/auth.py` |
| SUB-2.2.1.1.2 | Implement `AuthGuard` base class |
| SUB-2.2.1.1.3 | Implement `UserGuard` with JWT validation |
| SUB-2.2.1.1.4 | Implement `ServiceKeyGuard` for orchestration pipeline |

**Validation - curl (Unauthorized):**

```bash
# Test without auth header - should return 401
curl -X GET http://localhost:8000/api/jobs
# Expected: {"error": {"code": "UNAUTHORIZED", "message": "Authorization header required"}}
```

---

### STORY-2.2.2: Implement Ownership Guards

**As a** security engineer, **I want** ownership guards **so that** users can only access their own resources.

#### TASK-2.2.2.1: Create Ownership Guards

| Subtask | Description |
|---------|-------------|
| SUB-2.2.2.1.1 | Create `app/guards/ownership.py` |
| SUB-2.2.2.1.2 | Implement `JobOwnerGuard` |
| SUB-2.2.2.1.3 | Implement `ProfileOwnerGuard` |

**Validation - curl (Forbidden):**

```bash
# Test accessing another user's job - should return 403
curl -X GET http://localhost:8000/api/jobs/other-user-job-id \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"error": {"code": "FORBIDDEN", "message": "You do not have access to this job"}}
```

---

### STORY-2.2.3: Implement Validation Guards

**As a** developer, **I want** validation guards **so that** invalid state transitions are prevented.

#### TASK-2.2.3.1: Create Validation Guards

| Subtask | Description |
|---------|-------------|
| SUB-2.2.3.1.1 | Create `app/guards/validation.py` |
| SUB-2.2.3.1.2 | Implement `StatusTransitionGuard` |
| SUB-2.2.3.1.3 | Implement input sanitization |

**Validation - curl (Invalid Transition):**

```bash
# Test invalid status transition - should return 400
curl -X PATCH http://localhost:8000/api/jobs/$JOB_ID/status \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
# Expected: {"error": {"code": "INVALID_TRANSITION", "message": "Cannot transition from 'pending' to 'completed'"}}
```

---

### Testing Summary for FEAT-2.2

| Test Type | Description | Tool |
|-----------|-------------|------|
| Unit Test | Guards reject invalid tokens | pytest |
| Unit Test | Guards extract user correctly | pytest |
| Integration Test | Guards work with FastAPI DI | pytest + TestClient |
| Security Test | JWT tampering rejected | pytest |
| Security Test | Cross-user access blocked | pytest |

---

## FEAT-2.3: Service Layer

### STORY-2.3.1: Implement Job Service

**As a** developer, **I want** a job service **so that** business logic is separated from routes.

#### TASK-2.3.1.1: Create Job Service

| Subtask | Description |
|---------|-------------|
| SUB-2.3.1.1.1 | Create `app/services/job_service.py` |
| SUB-2.3.1.1.2 | Implement `create_job()` with daily limit check |
| SUB-2.3.1.1.3 | Implement `list_user_jobs()` |
| SUB-2.3.1.1.4 | Implement `get_job_with_profiles()` |
| SUB-2.3.1.1.5 | Implement `trigger_discovery()` to call orchestration pipeline |
| SUB-2.3.1.1.6 | Implement `update_status()` |
| SUB-2.3.1.1.7 | Implement `delete_job()`, `retry_job()` |
| SUB-2.3.1.1.8 | Implement `get_analytics()` |

**Validation - Unit Test:**

```python
def test_create_job_daily_limit():
    # Create 10 jobs, then verify 11th raises BusinessError
    for i in range(10):
        await job_service.create_job(user_id, data)
    with pytest.raises(BusinessError) as exc:
        await job_service.create_job(user_id, data)
    assert exc.value.code == "DAILY_LIMIT_EXCEEDED"
```

---

### STORY-2.3.2: Implement Scoring & Email Services

**As a** developer, **I want** scoring and email services **so that** AI-powered features work correctly.

#### TASK-2.3.2.1: Create Scoring Service

| Subtask | Description |
|---------|-------------|
| SUB-2.3.2.1.1 | Create `app/services/scoring_service.py` |
| SUB-2.3.2.1.2 | Implement weighted score calculation |
| SUB-2.3.2.1.3 | Implement recommendation logic based on thresholds |

#### TASK-2.3.2.2: Create Email Service

| Subtask | Description |
|---------|-------------|
| SUB-2.3.2.2.1 | Create `app/services/email_service.py` |
| SUB-2.3.2.2.2 | Implement `generate_email()` method |
| SUB-2.3.2.2.3 | Implement `send_email_mock()` method |

**Validation - Unit Test:**

```python
def test_scoring_weights_sum_to_100():
    service = ScoringService()
    score = service.calculate_final_score(
        visual_aesthetic_match=100,
        content_theme_alignment=100,
        engagement_rate_score=100,
        follower_quality=100,
        business_indicators=100,
        activity_recency=100
    )
    assert score == 100
```

---

## FEAT-2.4: API Routes Implementation

### STORY-2.4.1: Implement Health & Job Endpoints

**As a** user, **I want** job management endpoints **so that** I can create and manage discovery sessions.

#### TASK-2.4.1.1: Create Health Route

| Subtask | Description |
|---------|-------------|
| SUB-2.4.1.1.1 | Create `app/api/routes/health.py` |
| SUB-2.4.1.1.2 | Implement `GET /api/health` |

**Validation - curl:**

```bash
curl -X GET http://localhost:8000/api/health
# Expected: {"status": "healthy"}
```

#### TASK-2.4.1.2: Create Job Routes

| Subtask | Description |
|---------|-------------|
| SUB-2.4.1.2.1 | Create `app/api/routes/jobs.py` |
| SUB-2.4.1.2.2 | Implement `POST /api/jobs` - Create session |
| SUB-2.4.1.2.3 | Implement `GET /api/jobs` - List sessions |
| SUB-2.4.1.2.4 | Implement `GET /api/jobs/{id}` - Get session with profiles |
| SUB-2.4.1.2.5 | Implement `POST /api/jobs/{id}/start` - Start discovery |
| SUB-2.4.1.2.6 | Implement `DELETE /api/jobs/{id}` - Delete session |
| SUB-2.4.1.2.7 | Implement `POST /api/jobs/{id}/retry` - Retry failed |
| SUB-2.4.1.2.8 | Implement `PATCH /api/jobs/{id}` - Update metadata |
| SUB-2.4.1.2.9 | Implement `GET /api/jobs/{id}/analytics` - Get analytics |

**Validation - curl (Create Job):**

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_description": "Sustainable fashion brand",
    "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/reformation"]
  }'
# Expected: {"id": "uuid", "status": "pending", ...}
```

**Validation - curl (List Jobs):**

```bash
curl -X GET http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"jobs": [...]}
```

**Validation - curl (Get Job Details):**

```bash
curl -X GET http://localhost:8000/api/jobs/$JOB_ID \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"id": "...", "profiles": [...], ...}
```

**Validation - curl (Start Discovery):**

```bash
curl -X POST http://localhost:8000/api/jobs/$JOB_ID/start \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"status": "accepted", "job_id": "..."}
```

**Validation - curl (Delete Job):**

```bash
curl -X DELETE http://localhost:8000/api/jobs/$JOB_ID \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"deleted": true, "job_id": "..."}
```

**Validation - curl (Get Analytics):**

```bash
curl -X GET http://localhost:8000/api/jobs/$JOB_ID/analytics \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: {"profiles_discovered": 47, "average_score": 68.5, ...}
```

**Validation - Swagger:** Open http://localhost:8000/docs, test all job endpoints.

---

### STORY-2.4.2: Implement Status Update Endpoints

**As an** orchestration pipeline, **I want** status update endpoints **so that** I can track workflow progress.

#### TASK-2.4.2.1: Create Status Routes

| Subtask | Description |
|---------|-------------|
| SUB-2.4.2.1.1 | Create `app/api/routes/status.py` |
| SUB-2.4.2.1.2 | Implement `PATCH /api/jobs/{id}/status` |
| SUB-2.4.2.1.3 | Implement `PATCH /api/profiles/{id}/status` |
| SUB-2.4.2.1.4 | Implement `PATCH /api/jobs/{id}/profiles/status` (batch) |

**Validation - curl (Update Job Status):**

```bash
curl -X PATCH http://localhost:8000/api/jobs/$JOB_ID/status \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "analyzing"}'
# Expected: {"id": "...", "status": "analyzing", "updated_at": "..."}
```

**Validation - curl (Update Profile Status):**

```bash
curl -X PATCH http://localhost:8000/api/profiles/$PROFILE_ID/status \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "processing"}'
# Expected: {"id": "...", "status": "processing", "updated_at": "..."}
```

---

### STORY-2.4.3: Implement Email Endpoints

**As a** user, **I want** email generation endpoints **so that** I can create outreach emails.

#### TASK-2.4.3.1: Create Email Routes

| Subtask | Description |
|---------|-------------|
| SUB-2.4.3.1.1 | Create `app/api/routes/email.py` |
| SUB-2.4.3.1.2 | Implement `POST /api/email/generate` |
| SUB-2.4.3.1.3 | Implement `POST /api/email/send` |

**Validation - curl (Generate Email):**

```bash
curl -X POST http://localhost:8000/api/email/generate \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "'$PROFILE_ID'", "job_id": "'$JOB_ID'", "tone": "friendly"}'
# Expected: {"subject": "...", "body": "...", "metadata": {...}}
```

---

### STORY-2.4.4: Register All Routes in Main App

**As a** developer, **I want** all routes registered **so that** the API is fully functional.

#### TASK-2.4.4.1: Create Main Application

| Subtask | Description |
|---------|-------------|
| SUB-2.4.4.1.1 | Update `app/main.py` with all routers |
| SUB-2.4.4.1.2 | Configure CORS |
| SUB-2.4.4.1.3 | Add exception handlers |

**Validation - Swagger:** Open http://localhost:8000/docs, verify all endpoints listed.

---

### Testing Summary for FEAT-2.4

| Test Type | Description | Tool |
|-----------|-------------|------|
| Unit Test | Route handlers call services correctly | pytest + mock |
| Integration Test | Full request/response cycle | pytest + TestClient |
| Contract Test | Response matches Pydantic model | pytest |
| Negative Test | Invalid inputs return proper errors | pytest |
| Authorization Test | Protected routes require auth | curl/pytest |

---

# EPIC-3: AI Agents & LLM Integration

**Description:** Implement AI agents for brand analysis, profile discovery, scoring, and email generation.

**Acceptance Criteria:** All agents functional, tested with mock data, integrated with Apify.

---

## FEAT-3.1: LLM Service & Prompt Management

### STORY-3.1.1: Implement LLM Provider Abstraction

**As a** developer, **I want** an LLM abstraction layer **so that** I can switch between providers easily.

#### TASK-3.1.1.1: Create LLM Service

| Subtask | Description |
|---------|-------------|
| SUB-3.1.1.1.1 | Create `app/services/llm_service.py` |
| SUB-3.1.1.1.2 | Implement factory function for OpenAI |
| SUB-3.1.1.1.3 | Implement factory function for Gemini |
| SUB-3.1.1.1.4 | Implement factory function for Ollama |
| SUB-3.1.1.1.5 | Add provider selection via env var |

**Validation - Unit Test:**

```python
def test_llm_provider_openai():
    os.environ["LLM_PROVIDER"] = "openai"
    llm = get_llm()
    assert isinstance(llm, ChatOpenAI)
```

---

### STORY-3.1.2: Implement Prompt Management

**As a** developer, **I want** prompts loaded from files **so that** I can modify them without code changes.

#### TASK-3.1.2.1: Create Prompt Loader

| Subtask | Description |
|---------|-------------|
| SUB-3.1.2.1.1 | Create `app/prompts/loader.py` |
| SUB-3.1.2.1.2 | Implement `load_prompt()` function |
| SUB-3.1.2.1.3 | Implement `load_prompts()` for both system and user |

#### TASK-3.1.2.2: Create Agent Prompts

| Subtask | Description |
|---------|-------------|
| SUB-3.1.2.2.1 | Create `app/prompts/brand_analyzer/system.txt` |
| SUB-3.1.2.2.2 | Create `app/prompts/brand_analyzer/user.txt` |
| SUB-3.1.2.2.3 | Create `app/prompts/discovery/system.txt` and `user.txt` |
| SUB-3.1.2.2.4 | Create `app/prompts/scorer/system.txt` and `user.txt` |
| SUB-3.1.2.2.5 | Create `app/prompts/email_composer/system.txt` and `user.txt` |

**Validation - Unit Test:**

```python
def test_prompt_loader():
    from app.prompts.loader import load_prompt
    system = load_prompt("brand_analyzer", "system")
    assert len(system) > 0
```

---

## FEAT-3.2: Apify Integration

### STORY-3.2.1: Implement Apify Service

**As a** developer, **I want** an Apify service **so that** I can scrape Instagram profiles.

#### TASK-3.2.1.1: Create Apify Service

| Subtask | Description |
|---------|-------------|
| SUB-3.2.1.1.1 | Create `app/services/apify_service.py` |
| SUB-3.2.1.1.2 | Implement Instagram Profile Scraper integration |
| SUB-3.2.1.1.3 | Implement Hashtag Scraper integration |
| SUB-3.2.1.1.4 | Implement rate limiting and retry logic |
| SUB-3.2.1.1.5 | Implement error handling |

**Validation - Integration Test:**

```python
@pytest.mark.integration
async def test_apify_profile_scraper():
    service = ApifyService()
    result = await service.scrape_profile("everlane")
    assert result["username"] == "everlane"
    assert result["followersCount"] > 0
```

---

## FEAT-3.3: AI Agents Implementation

### STORY-3.3.1: Implement Base Agent Class

**As a** developer, **I want** a base agent class **so that** all agents share common functionality.

#### TASK-3.3.1.1: Create Base Agent

| Subtask | Description |
|---------|-------------|
| SUB-3.3.1.1.1 | Create `app/agents/base.py` |
| SUB-3.3.1.1.2 | Implement `BaseAgent` abstract class |
| SUB-3.3.1.1.3 | Implement prompt loading in constructor |
| SUB-3.3.1.1.4 | Implement chain building method |
| SUB-3.3.1.1.5 | Implement abstract `run()` method |

---

### STORY-3.3.2: Implement Brand Analyzer Agent

**As a** user, **I want** my brand analyzed **so that** I get relevant partner recommendations.

#### TASK-3.3.2.1: Create Brand Analyzer

| Subtask | Description |
|---------|-------------|
| SUB-3.3.2.1.1 | Create `app/agents/brand_analyzer.py` |
| SUB-3.3.2.1.2 | Implement profile fetching via Apify |
| SUB-3.3.2.1.3 | Implement LLM chain for hashtag/keyword extraction |
| SUB-3.3.2.1.4 | Implement embedding generation |
| SUB-3.3.2.1.5 | Implement database storage in `brand_dna` table |

**Validation - curl:**

```bash
curl -X POST http://localhost:8000/api/agent/analyze-brand \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "'$JOB_ID'"}'
# Expected: {"brand_dna": {"hashtags": [...], "keywords": [...], "embedding_vector": [...]}}
```

**Validation - Unit Test:**

```python
@pytest.mark.asyncio
async def test_brand_analyzer():
    agent = BrandAnalyzerAgent()
    result = await agent.run(job_id, brand_description, reference_profiles)
    assert len(result["hashtags"]) >= 5
    assert len(result["keywords"]) >= 5
    assert len(result["embedding_vector"]) == 1536
```

---

### STORY-3.3.3: Implement Discovery Agent

**As a** user, **I want** similar profiles discovered **so that** I have partnership candidates.

#### TASK-3.3.3.1: Create Discovery Agent

| Subtask | Description |
|---------|-------------|
| SUB-3.3.3.1.1 | Create `app/agents/discovery.py` |
| SUB-3.3.3.1.2 | Implement hashtag search via Apify |
| SUB-3.3.3.1.3 | Implement follower range filtering |
| SUB-3.3.3.1.4 | Implement deduplication by username |
| SUB-3.3.3.1.5 | Implement database storage in `discovered_profiles` table |

**Validation - curl:**

```bash
curl -X POST http://localhost:8000/api/agent/discover \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "'$JOB_ID'",
    "hashtags": ["#sustainablefashion", "#slowfashion"],
    "keywords": ["sustainable", "ethical"],
    "limit": 10
  }'
# Expected: {"profiles": [...], "total_discovered": 10, "deduplicated": 0}
```

---

### STORY-3.3.4: Implement Scorer Agent

**As a** user, **I want** profiles scored **so that** I can identify the best partners.

#### TASK-3.3.4.1: Create Scorer Agent

| Subtask | Description |
|---------|-------------|
| SUB-3.3.4.1.1 | Create `app/agents/scorer.py` |
| SUB-3.3.4.1.2 | Implement 6-dimension scoring with LLM |
| SUB-3.3.4.1.3 | Implement fake profile detection logic |
| SUB-3.3.4.1.4 | Implement email extraction (bio, business_email, website) |
| SUB-3.3.4.1.5 | Implement weighted final score calculation |
| SUB-3.3.4.1.6 | Implement database storage in `profile_scores` and `profile_contacts` |

**Validation - curl:**

```bash
curl -X POST http://localhost:8000/api/agent/score \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "'$PROFILE_ID'", "job_id": "'$JOB_ID'"}'
# Expected: {"score": 85, "reasoning": {...}, "contact": {"email": "...", "source": "..."}}
```

---

### STORY-3.3.5: Implement Email Composer Agent

**As a** user, **I want** AI-generated emails **so that** I can reach out to partners easily.

#### TASK-3.3.5.1: Create Email Composer

| Subtask | Description |
|---------|-------------|
| SUB-3.3.5.1.1 | Create `app/agents/email_composer.py` |
| SUB-3.3.5.1.2 | Implement email generation with LLM |
| SUB-3.3.5.1.3 | Support multiple tones (professional, friendly, casual) |

**Validation - Unit Test:**

```python
@pytest.mark.asyncio
async def test_email_composer():
    agent = EmailComposerAgent()
    result = await agent.compose(profile, brand_dna, brand_description, "friendly")
    assert "subject" in result
    assert "body" in result
    assert len(result["body"]) > 50
```

---

### STORY-3.3.6: Create Agent API Routes

**As an** orchestrator, **I want** agent endpoints **so that** I can call agents via HTTP.

#### TASK-3.3.6.1: Create Agent Routes

| Subtask | Description |
|---------|-------------|
| SUB-3.3.6.1.1 | Create `app/api/routes/agents.py` |
| SUB-3.3.6.1.2 | Implement `POST /api/agent/analyze-brand` |
| SUB-3.3.6.1.3 | Implement `POST /api/agent/discover` |
| SUB-3.3.6.1.4 | Implement `POST /api/agent/score` |

**Validation - Swagger:** Open http://localhost:8000/docs, test all agent endpoints.

---

### Testing Summary for EPIC-3

| Test Type | Description | Tool |
|-----------|-------------|------|
| Unit Test | Agent chain builds correctly | pytest |
| Unit Test | Score calculation is correct | pytest |
| Unit Test | Fake detection flags suspicious profiles | pytest |
| Integration Test | Agent calls LLM successfully | pytest (with mock) |
| Integration Test | Apify scraper returns data | pytest (real API) |
| Contract Test | Agent response matches schema | pytest |
| Performance Test | Agent completes within timeout | pytest |

---

# EPIC-4: Workflow Orchestration (Python Pipeline)

**Description:** Implement workflow orchestration using the internal Python orchestration pipeline.

**Acceptance Criteria:** Complete discovery workflow runs end-to-end via the Python orchestration pipeline.

---

## FEAT-4.1: Orchestration Pipeline Implementation

### STORY-4.1.1: Setup Orchestration Environment

**As a** developer, **I want** the orchestration pipeline configured **so that** the full discovery workflow runs automatically.

#### TASK-4.1.1.1: Configure Orchestration Pipeline

| Subtask | Description |
|---------|-------------|
| SUB-4.1.1.1.1 | Create `backend/scripts/run_orchestration.py` |
| SUB-4.1.1.1.2 | Configure `FASTAPI_BASE_URL` environment variable |
| SUB-4.1.1.1.3 | Configure `SERVICE_KEY` environment variable |

**Validation:** Run the orchestration script and verify it connects to FastAPI.

---

### STORY-4.1.2: Build Discovery Pipeline Steps

**As a** developer, **I want** the discovery pipeline **so that** the full workflow runs automatically.

#### TASK-4.1.2.1: Implement Pipeline Steps

| Subtask | Description |
|---------|-------------|
| SUB-4.1.2.1.1 | Implement webhook trigger handler |
| SUB-4.1.2.1.2 | Implement input validation step |
| SUB-4.1.2.1.3 | Implement brand analysis step (calls `/api/agent/analyze-brand`) |
| SUB-4.1.2.1.4 | Implement discovery step (calls `/api/agent/discover`) |
| SUB-4.1.2.1.5 | Implement scoring loop with parallel execution |
| SUB-4.1.2.1.6 | Implement score filtering (>= 50) |
| SUB-4.1.2.1.7 | Implement completion and status update step |
| SUB-4.1.2.1.8 | Implement error handling and job failure reporting |

**Validation:**

1. Run the pipeline script with a test job ID
2. Verify all steps execute successfully
3. Check database for inserted profiles and scores

---

## FEAT-4.2: Python Orchestrator Script

### STORY-4.2.1: Implement Python Orchestrator Script

**As a** developer, **I want** a Python orchestrator **so that** discovery runs end-to-end.

#### TASK-4.2.1.1: Create Fallback Script

| Subtask | Description |
|---------|-------------|
| SUB-4.2.1.1.1 | Create `backend/scripts/run_discovery.py` |
| SUB-4.2.1.1.2 | Implement `update_job_status()` function |
| SUB-4.2.1.1.3 | Implement `update_profile_status()` function |
| SUB-4.2.1.1.4 | Implement `call_brand_analyzer()` function |
| SUB-4.2.1.1.5 | Implement `call_discovery_agent()` function |
| SUB-4.2.1.1.6 | Implement `call_scorer_agent()` function |
| SUB-4.2.1.1.7 | Implement `run_discovery()` main function |
| SUB-4.2.1.1.8 | Implement CLI entry point |

**Validation - CLI:**

```bash
python -m scripts.run_discovery 11111111-1111-1111-1111-111111111111

# Expected output:
# [Orchestrator] Starting discovery for job: 11111111-1111-1111-1111-111111111111
# [Phase 1] Analyzing brand...
# [Phase 2] Discovering profiles...
# [Phase 3] Scoring profiles...
# [Complete] Discovery completed successfully!
```

---

### Testing Summary for EPIC-4

| Test Type | Description | Tool |
|-----------|-------------|------|
| Unit Test | Each workflow step calls correct API | pytest |
| Integration Test | Full pipeline completes end-to-end | pytest |
| Smoke Test | Python orchestrator completes | CLI |
| Error Recovery Test | Failed jobs can be retried | pytest |
| Performance Test | 50 profiles in < 10 minutes | pytest |

---

# EPIC-5: Frontend Application Development

**Description:** Implement React frontend with authentication, dashboard, and real-time updates.

**Acceptance Criteria:** Fully functional UI matching all design mockups.

---

## FEAT-5.1: Frontend Core Setup

### STORY-5.1.1: Configure React Project

**As a** frontend developer, **I want** a configured React project **so that** I can start building components.

#### TASK-5.1.1.1: Initialize Project

| Subtask | Description |
|---------|-------------|
| SUB-5.1.1.1.1 | Create Vite + React + TypeScript project |
| SUB-5.1.1.1.2 | Configure Tailwind CSS with Apple-inspired theme |
| SUB-5.1.1.1.3 | Configure path aliases |
| SUB-5.1.1.1.4 | Setup ESLint and Prettier |

#### TASK-5.1.1.2: Create Supabase Client

| Subtask | Description |
|---------|-------------|
| SUB-5.1.1.2.1 | Create `src/lib/supabase.ts` |
| SUB-5.1.1.2.2 | Configure environment variables |

#### TASK-5.1.1.3: Create TypeScript Types

| Subtask | Description |
|---------|-------------|
| SUB-5.1.1.3.1 | Create `src/types/database.types.ts` |
| SUB-5.1.1.3.2 | Define all entity types matching backend models |

#### TASK-5.1.1.4: Create API Client

| Subtask | Description |
|---------|-------------|
| SUB-5.1.1.4.1 | Create `src/lib/api.ts` with fetch wrappers |
| SUB-5.1.1.4.2 | Implement auth header injection |

**Validation:** Run `npm run dev`, verify app loads without errors.

---

## FEAT-5.2: Authentication

### STORY-5.2.1: Implement Login/Signup Pages

**As a** user, **I want** to sign up and log in **so that** I can access my discovery sessions.

#### TASK-5.2.1.1: Create Auth Pages

| Subtask | Description |
|---------|-------------|
| SUB-5.2.1.1.1 | Create `src/pages/LoginPage.tsx` based on `designs/login.html` |
| SUB-5.2.1.1.2 | Implement Sign In tab |
| SUB-5.2.1.1.3 | Implement Sign Up tab |
| SUB-5.2.1.1.4 | Implement form validation |
| SUB-5.2.1.1.5 | Integrate Supabase Auth |

#### TASK-5.2.1.2: Create Auth Context

| Subtask | Description |
|---------|-------------|
| SUB-5.2.1.2.1 | Create `src/context/AuthContext.tsx` |
| SUB-5.2.1.2.2 | Implement user state management |
| SUB-5.2.1.2.3 | Implement sign out function |
| SUB-5.2.1.2.4 | Create `ProtectedRoute` component |

**Validation - Manual Test:**

1. Sign up with new email
2. Receive confirmation email
3. Sign in with credentials
4. Verify redirect to dashboard
5. Sign out and verify redirect to login

---

## FEAT-5.3: Session Management

### STORY-5.3.1: Implement Session List Page

**As a** user, **I want** to see my discovery sessions **so that** I can manage them.

#### TASK-5.3.1.1: Create Session List Page

| Subtask | Description |
|---------|-------------|
| SUB-5.3.1.1.1 | Create `src/pages/SessionListPage.tsx` based on `designs/session-list.html` |
| SUB-5.3.1.1.2 | Implement session card component |
| SUB-5.3.1.1.3 | Display status badges (pending, analyzing, etc.) |
| SUB-5.3.1.1.4 | Implement delete session functionality |
| SUB-5.3.1.1.5 | Implement retry failed session |
| SUB-5.3.1.1.6 | Implement navigation to session detail |

---

### STORY-5.3.2: Implement Empty Dashboard

**As a** new user, **I want** an onboarding screen **so that** I know how to start.

#### TASK-5.3.2.1: Create Empty State

| Subtask | Description |
|---------|-------------|
| SUB-5.3.2.1.1 | Create `src/pages/EmptyDashboard.tsx` based on `designs/empty-dashboard.html` |
| SUB-5.3.2.1.2 | Add CTA to create first session |

---

### STORY-5.3.3: Implement Discovery Engine Steps

**As a** user, **I want** to create a discovery session **so that** I can find partners.

#### TASK-5.3.3.1: Create Discovery Step 1

| Subtask | Description |
|---------|-------------|
| SUB-5.3.3.1.1 | Create `src/pages/DiscoveryStep1.tsx` based on `designs/discovery-engine-step1.html` |
| SUB-5.3.3.1.2 | Implement brand description textarea |
| SUB-5.3.3.1.3 | Implement reference profiles input (2-10 URLs) |
| SUB-5.3.3.1.4 | Implement follower range slider |
| SUB-5.3.3.1.5 | Implement discovery limit input |
| SUB-5.3.3.1.6 | Implement form validation |

#### TASK-5.3.3.2: Create Discovery Step 2

| Subtask | Description |
|---------|-------------|
| SUB-5.3.3.2.1 | Create `src/pages/DiscoveryStep2.tsx` based on `designs/discovery-engine-step2.html` |
| SUB-5.3.3.2.2 | Display configuration summary |
| SUB-5.3.3.2.3 | Implement "Start Discovery" button |
| SUB-5.3.3.2.4 | Call `POST /api/jobs/{id}/start` |

**Validation - Manual Test:**

1. Navigate to create session
2. Enter brand description
3. Add 3 reference profile URLs
4. Proceed to step 2
5. Launch discovery
6. Verify session appears in list

---

## FEAT-5.4: Main Dashboard

### STORY-5.4.1: Implement Dashboard Layout

**As a** user, **I want** a dashboard **so that** I can see discovered profiles.

#### TASK-5.4.1.1: Create Dashboard Page

| Subtask | Description |
|---------|-------------|
| SUB-5.4.1.1.1 | Create `src/pages/DashboardPage.tsx` based on `designs/main-discovery-dashboard.html` |
| SUB-5.4.1.1.2 | Implement session selector dropdown |
| SUB-5.4.1.1.3 | Implement statistics summary bar |
| SUB-5.4.1.1.4 | Implement tab navigation (New, Processing, Done) |

#### TASK-5.4.1.2: Create Profile Card Component

| Subtask | Description |
|---------|-------------|
| SUB-5.4.1.2.1 | Create `src/components/ProfileCard.tsx` |
| SUB-5.4.1.2.2 | Display avatar, username, follower count |
| SUB-5.4.1.2.3 | Display score ring/badge |
| SUB-5.4.1.2.4 | Display email availability icon |
| SUB-5.4.1.2.5 | Implement click to open detail modal |

#### TASK-5.4.1.3: Implement Sorting & Filtering

| Subtask | Description |
|---------|-------------|
| SUB-5.4.1.3.1 | Add sort dropdown (score, followers, created_at) |
| SUB-5.4.1.3.2 | Add minimum score filter |

**Validation - Manual Test:**

1. Open dashboard with completed session
2. Verify profiles display in grid
3. Switch between tabs
4. Sort by score
5. Click profile card to open detail

---

## FEAT-5.5: Real-time Updates

### STORY-5.5.1: Implement Supabase Realtime Subscriptions

**As a** user, **I want** live updates **so that** I see profiles appear in real-time.

#### TASK-5.5.1.1: Create Realtime Hooks

| Subtask | Description |
|---------|-------------|
| SUB-5.5.1.1.1 | Create `src/hooks/useRealtimeProfiles.ts` |
| SUB-5.5.1.1.2 | Subscribe to `discovered_profiles` changes |
| SUB-5.5.1.1.3 | Subscribe to `profile_scores` inserts |
| SUB-5.5.1.1.4 | Subscribe to `discovery_jobs` status updates |

#### TASK-5.5.1.2: Create Processing Pipeline View

| Subtask | Description |
|---------|-------------|
| SUB-5.5.1.2.1 | Create `src/pages/ProcessingPipeline.tsx` based on `designs/ai-agent-processing-pipeline.html` |
| SUB-5.5.1.2.2 | Display live step progress |
| SUB-5.5.1.2.3 | Display processing log with timestamps |
| SUB-5.5.1.2.4 | Handle errors with retry option |

**Validation - Manual Test:**

1. Start a new discovery
2. Watch profiles appear incrementally
3. See score badges update
4. See email icons appear
5. See job status progress

---

## FEAT-5.6: Profile Detail & Email Composer

### STORY-5.6.1: Implement Profile Detail Modal

**As a** user, **I want** to see profile details **so that** I can evaluate potential partners.

#### TASK-5.6.1.1: Create Profile Detail Modal

| Subtask | Description |
|---------|-------------|
| SUB-5.6.1.1.1 | Create `src/components/ProfileDetailModal.tsx` based on `designs/profile-detail-model-view.html` |
| SUB-5.6.1.1.2 | Display full profile info (bio, stats) |
| SUB-5.6.1.1.3 | Display score breakdown (6 dimensions) |
| SUB-5.6.1.1.4 | Display AI reasoning and recommendation |
| SUB-5.6.1.1.5 | Display contact info with copy button |
| SUB-5.6.1.1.6 | Add "View on Instagram" link |
| SUB-5.6.1.1.7 | Add "Compose Email" button |

---

### STORY-5.6.2: Implement Email Composer Modal

**As a** user, **I want** to compose outreach emails **so that** I can contact partners.

#### TASK-5.6.2.1: Create Email Composer Modal

| Subtask | Description |
|---------|-------------|
| SUB-5.6.2.1.1 | Create `src/components/EmailComposerModal.tsx` based on `designs/ai-email-composer.html` |
| SUB-5.6.2.1.2 | Implement AI email generation |
| SUB-5.6.2.1.3 | Add tone selector (professional, friendly, casual) |
| SUB-5.6.2.1.4 | Add regenerate button |
| SUB-5.6.2.1.5 | Add edit capability |
| SUB-5.6.2.1.6 | Add send button (mock) |

**Validation - Manual Test:**

1. Open profile detail
2. Click "Compose Email"
3. Select tone
4. View generated email
5. Edit and send

---

## FEAT-5.7: UI Components & Polish

### STORY-5.7.1: Implement Component Library

**As a** developer, **I want** reusable components **so that** the UI is consistent.

#### TASK-5.7.1.1: Create Toast Components

| Subtask | Description |
|---------|-------------|
| SUB-5.7.1.1.1 | Create `src/components/Toast.tsx` |
| SUB-5.7.1.1.2 | Implement success, error, warning variants |

#### TASK-5.7.1.2: Create Loading Components

| Subtask | Description |
|---------|-------------|
| SUB-5.7.1.2.1 | Create `src/components/Spinner.tsx` |
| SUB-5.7.1.2.2 | Create `src/components/SkeletonCard.tsx` |
| SUB-5.7.1.2.3 | Create `src/components/PageLoading.tsx` |

#### TASK-5.7.1.3: Create Modal Components

| Subtask | Description |
|---------|-------------|
| SUB-5.7.1.3.1 | Create base `src/components/Modal.tsx` |
| SUB-5.7.1.3.2 | Create `DailyLimitModal` |
| SUB-5.7.1.3.3 | Create `ServiceUnavailableModal` |

#### TASK-5.7.1.4: Add Animations

| Subtask | Description |
|---------|-------------|
| SUB-5.7.1.4.1 | Add fade-in transitions |
| SUB-5.7.1.4.2 | Add slide-up transitions |
| SUB-5.7.1.4.3 | Add score ring animations |
| SUB-5.7.1.4.4 | Add card hover effects |

---

### Testing Summary for EPIC-5

| Test Type | Description | Tool |
|-----------|-------------|------|
| Unit Test | Component renders correctly | Jest + React Testing Library |
| Unit Test | Hooks return expected data | Jest |
| Integration Test | Pages call API correctly | Cypress |
| E2E Test | Full user flows work | Cypress |
| Visual Test | UI matches designs | Percy or manual |
| Accessibility Test | WCAG compliance | axe-core |
| Responsive Test | Works on mobile/tablet | Manual |

---

# EPIC-6: Comprehensive Testing & Quality Assurance

**Description:** Implement all testing types to ensure quality and reliability.

**Acceptance Criteria:** All tests passing, code coverage > 80%.

---

## FEAT-6.1: Backend Testing

### STORY-6.1.1: Implement Unit Tests

**As a** developer, **I want** unit tests **so that** individual components work correctly.

#### TASK-6.1.1.1: Test Configuration Layer

| Subtask | Description |
|---------|-------------|
| SUB-6.1.1.1.1 | Test config loads environment variables |
| SUB-6.1.1.1.2 | Test YAML configs load correctly |
| SUB-6.1.1.1.3 | Test constants have correct values |

#### TASK-6.1.1.2: Test Repository Layer

| Subtask | Description |
|---------|-------------|
| SUB-6.1.1.2.1 | Test CRUD operations with mock DB |
| SUB-6.1.1.2.2 | Test query methods return expected results |

#### TASK-6.1.1.3: Test Service Layer

| Subtask | Description |
|---------|-------------|
| SUB-6.1.1.3.1 | Test business logic with mocked repos |
| SUB-6.1.1.3.2 | Test daily limit enforcement |
| SUB-6.1.1.3.3 | Test status transition validation |

#### TASK-6.1.1.4: Test Guards

| Subtask | Description |
|---------|-------------|
| SUB-6.1.1.4.1 | Test JWT validation |
| SUB-6.1.1.4.2 | Test service key validation |
| SUB-6.1.1.4.3 | Test ownership validation |
| SUB-6.1.1.4.4 | Test status transition guard |

---

### STORY-6.1.2: Implement Integration Tests

**As a** developer, **I want** integration tests **so that** components work together.

#### TASK-6.1.2.1: Test API Endpoints

| Subtask | Description |
|---------|-------------|
| SUB-6.1.2.1.1 | Test all job endpoints with TestClient |
| SUB-6.1.2.1.2 | Test all status endpoints with TestClient |
| SUB-6.1.2.1.3 | Test all agent endpoints with TestClient |

#### TASK-6.1.2.2: Test Database Integration

| Subtask | Description |
|---------|-------------|
| SUB-6.1.2.2.1 | Test repositories with real Supabase |
| SUB-6.1.2.2.2 | Test RLS policies work correctly |
| SUB-6.1.2.2.3 | Test triggers update counters |

---

### STORY-6.1.3: Implement Security Tests

**As a** security engineer, **I want** security tests **so that** the API is secure.

#### TASK-6.1.3.1: Test Authentication

| Subtask | Description |
|---------|-------------|
| SUB-6.1.3.1.1 | Test invalid JWT rejected |
| SUB-6.1.3.1.2 | Test expired JWT rejected |
| SUB-6.1.3.1.3 | Test tampered JWT rejected |

#### TASK-6.1.3.2: Test Authorization

| Subtask | Description |
|---------|-------------|
| SUB-6.1.3.2.1 | Test cross-user access blocked |
| SUB-6.1.3.2.2 | Test missing service key rejected |
| SUB-6.1.3.2.3 | Test invalid service key rejected |

#### TASK-6.1.3.3: Test Input Validation

| Subtask | Description |
|---------|-------------|
| SUB-6.1.3.3.1 | Test SQL injection blocked |
| SUB-6.1.3.3.2 | Test XSS blocked |
| SUB-6.1.3.3.3 | Test oversized payloads rejected |

---

## FEAT-6.2: Frontend Testing

### STORY-6.2.1: Implement Component Tests

**As a** frontend developer, **I want** component tests **so that** UI components work correctly.

#### TASK-6.2.1.1: Test Core Components

| Subtask | Description |
|---------|-------------|
| SUB-6.2.1.1.1 | Test Toast component |
| SUB-6.2.1.1.2 | Test Modal component |
| SUB-6.2.1.1.3 | Test ProfileCard component |
| SUB-6.2.1.1.4 | Test form components |

#### TASK-6.2.1.2: Test Hooks

| Subtask | Description |
|---------|-------------|
| SUB-6.2.1.2.1 | Test useRealtimeProfiles hook |
| SUB-6.2.1.2.2 | Test useAuth hook |

---

### STORY-6.2.2: Implement E2E Tests

**As a** QA engineer, **I want** E2E tests **so that** user flows work correctly.

#### TASK-6.2.2.1: Test Authentication Flow

| Subtask | Description |
|---------|-------------|
| SUB-6.2.2.1.1 | Test sign up flow |
| SUB-6.2.2.1.2 | Test sign in flow |
| SUB-6.2.2.1.3 | Test sign out flow |

#### TASK-6.2.2.2: Test Discovery Flow

| Subtask | Description |
|---------|-------------|
| SUB-6.2.2.2.1 | Test create session flow |
| SUB-6.2.2.2.2 | Test start discovery flow |
| SUB-6.2.2.2.3 | Test view results flow |
| SUB-6.2.2.2.4 | Test email composer flow |

---

## FEAT-6.3: Performance & Load Testing

### STORY-6.3.1: Implement Performance Tests

**As a** performance engineer, **I want** performance tests **so that** the system handles load.

#### TASK-6.3.1.1: Backend Performance

| Subtask | Description |
|---------|-------------|
| SUB-6.3.1.1.1 | Test API response times < 500ms |
| SUB-6.3.1.1.2 | Test 50 profiles scored in < 10 minutes |
| SUB-6.3.1.1.3 | Test concurrent user handling |

#### TASK-6.3.1.2: Frontend Performance

| Subtask | Description |
|---------|-------------|
| SUB-6.3.1.2.1 | Test Lighthouse score > 90 |
| SUB-6.3.1.2.2 | Test First Contentful Paint < 1.5s |
| SUB-6.3.1.2.3 | Test Time to Interactive < 3s |

---

# EPIC-7: Deployment & Production Readiness

**Description:** Prepare for production deployment with documentation and demo readiness.

**Acceptance Criteria:** System deployable, demo completes in < 5 minutes.

---

## FEAT-7.1: Environment Configuration

### STORY-7.1.1: Configure Production Environment

**As a** DevOps engineer, **I want** production config **so that** the system runs in production.

#### TASK-7.1.1.1: Configure Backend Production

| Subtask | Description |
|---------|-------------|
| SUB-7.1.1.1.1 | Set production environment variables |
| SUB-7.1.1.1.2 | Configure production Supabase project |
| SUB-7.1.1.1.3 | Configure production orchestration pipeline |

#### TASK-7.1.1.2: Configure Frontend Production

| Subtask | Description |
|---------|-------------|
| SUB-7.1.1.2.1 | Set production environment variables |
| SUB-7.1.1.2.2 | Build production bundle |
| SUB-7.1.1.2.3 | Configure CDN/hosting |

---

## FEAT-7.2: Documentation

### STORY-7.2.1: Create Setup Documentation

**As a** developer, **I want** documentation **so that** I can set up the project.

#### TASK-7.2.1.1: Create README Files

| Subtask | Description |
|---------|-------------|
| SUB-7.2.1.1.1 | Create main `README.md` with overview |
| SUB-7.2.1.1.2 | Create `backend/README.md` with setup |
| SUB-7.2.1.1.3 | Create `frontend/README.md` with setup |

#### TASK-7.2.1.2: Create API Documentation

| Subtask | Description |
|---------|-------------|
| SUB-7.2.1.2.1 | Ensure Swagger/OpenAPI is complete |
| SUB-7.2.1.2.2 | Document all endpoints with examples |

---

## FEAT-7.3: Demo Preparation

### STORY-7.3.1: Prepare Demo Environment

**As a** presenter, **I want** a demo-ready environment **so that** the demo runs smoothly.

#### TASK-7.3.1.1: Create Demo Data

| Subtask | Description |
|---------|-------------|
| SUB-7.3.1.1.1 | Create demo user account |
| SUB-7.3.1.1.2 | Pre-populate sample brand data |
| SUB-7.3.1.1.3 | Have pre-scraped backup data |

#### TASK-7.3.1.2: Create Demo Script

| Subtask | Description |
|---------|-------------|
| SUB-7.3.1.2.1 | Document demo flow step by step |
| SUB-7.3.1.2.2 | Prepare talking points for each phase |
| SUB-7.3.1.2.3 | Create backup plan for failures |

---

# Appendix: Validation Commands Reference

## Backend Health Check

```bash
# Health endpoint
curl http://localhost:8000/api/health

# Swagger UI
open http://localhost:8000/docs
```

## Authentication

```bash
# Get JWT token (via Supabase)
TOKEN=$(curl -X POST 'https://your-project.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq -r '.access_token')
```

## Job API Testing

```bash
# Create job
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"brand_description":"Test","reference_profiles":["url1","url2"]}'

# List jobs
curl http://localhost:8000/api/jobs -H "Authorization: Bearer $TOKEN"

# Get job
curl http://localhost:8000/api/jobs/$JOB_ID -H "Authorization: Bearer $TOKEN"

# Start discovery
curl -X POST http://localhost:8000/api/jobs/$JOB_ID/start -H "Authorization: Bearer $TOKEN"

# Get analytics
curl http://localhost:8000/api/jobs/$JOB_ID/analytics -H "Authorization: Bearer $TOKEN"

# Delete job
curl -X DELETE http://localhost:8000/api/jobs/$JOB_ID -H "Authorization: Bearer $TOKEN"
```

## Agent API Testing

```bash
# Brand Analyzer
curl -X POST http://localhost:8000/api/agent/analyze-brand \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"'$JOB_ID'"}'

# Discovery
curl -X POST http://localhost:8000/api/agent/discover \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"job_id":"'$JOB_ID'","hashtags":["#test"],"keywords":["test"],"limit":5}'

# Scorer
curl -X POST http://localhost:8000/api/agent/score \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"'$PROFILE_ID'","job_id":"'$JOB_ID'"}'
```

## Status API Testing

```bash
# Update job status
curl -X PATCH http://localhost:8000/api/jobs/$JOB_ID/status \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"analyzing"}'

# Update profile status
curl -X PATCH http://localhost:8000/api/profiles/$PROFILE_ID/status \
  -H "X-Service-Key: $SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"processing"}'
```

## Python Fallback Testing

```bash
python -m scripts.run_discovery $JOB_ID
```

---

# Test Coverage Summary

| Area | Unit | Integration | E2E | Security | Performance |
|------|------|-------------|-----|----------|-------------|
| Configuration | Yes | - | - | - | - |
| Repositories | Yes | Yes | - | - | - |
| Services | Yes | Yes | - | - | - |
| Guards | Yes | Yes | - | Yes | - |
| API Routes | Yes | Yes | Yes | Yes | Yes |
| AI Agents | Yes | Yes | - | - | Yes |
| Orchestration Pipeline | - | Yes | Yes | - | Yes |
| Frontend Components | Yes | - | - | - | - |
| Frontend Pages | - | - | Yes | - | Yes |
| Full System | - | - | Yes | Yes | Yes |

---

# Work Item Count Summary

| Level | Count |
|-------|-------|
| Epics | 7 |
| Features | 24 |
| Stories | 54 |
| Tasks | ~120 |
| Subtasks | ~350 |

---

# Development Order

| Phase | Epic | Description |
|-------|------|-------------|
| 1 | EPIC-1 | Project Foundation & Infrastructure |
| 2 | EPIC-2 | Backend Core Services & API |
| 3 | EPIC-3 | AI Agents & LLM Integration |
| 4 | EPIC-4 | Workflow Orchestration |
| 5 | EPIC-5 | Frontend Application |
| 6 | EPIC-6 | Testing & QA |
| 7 | EPIC-7 | Deployment & Production |

---

*Generated for PartnerScout AI Project*
