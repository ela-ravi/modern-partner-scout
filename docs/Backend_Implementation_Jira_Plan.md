# PartnerScout AI - Backend Implementation Plan (Jira Structure)

> Enterprise-ready implementation plan structured for Jira product management. Use EPIC, FEATURE, STORY, TASK, and SUBTASK hierarchy for sprint planning and tracking.

---

## Table of Contents

1. [Jira Hierarchy Overview](#jira-hierarchy-overview)
2. [EPIC 1: PartnerScout Backend Foundation](#epic-1-partnerscout-backend-foundation)
3. [EPIC 2: Session Management API](#epic-2-session-management-api)
4. [EPIC 3: AI Agent Integration](#epic-3-ai-agent-integration)
5. [EPIC 4: Email & Outreach](#epic-4-email--outreach)
6. [EPIC 5: Orchestration & Integration](#epic-5-orchestration--integration)
7. [Jira Import Reference](#jira-import-reference)

---

## Jira Hierarchy Overview

### Hierarchy Definition

| Level | Description | Example | PRD Reference |
|-------|-------------|---------|---------------|
| **EPIC** | Large initiative spanning multiple sprints | PartnerScout Backend Foundation | Section 7 |
| **FEATURE** | Major capability or functional area | Session Management | Section 5.4 |
| **STORY** | User-facing deliverable (As a... I want... So that...) | Create discovery session | Section 8.1 |
| **TASK** | Concrete work item with acceptance criteria | Implement job repository | Section 7 |
| **SUBTASK** | Smallest trackable unit of work | Create job_repo.py | - |

### Implementation Order

EPICs should be implemented in numerical order. Within each EPIC, complete FEATURES in dependency order. STORIES can be parallelized where dependencies allow.

---

## EPIC 1: PartnerScout Backend Foundation

**Epic Key:** `BE-EPIC-001`  
**Summary:** Establish FastAPI backend structure, configuration, data layer, and core infrastructure.  
**PRD Reference:** Section 7 (Technical Architecture)  
**Sprint Estimate:** 2 sprints

---

### FEATURE 1.1: Project Setup & Structure

**Feature Key:** `BE-FEAT-001`  
**Summary:** Initialize backend project with proper folder structure and dependencies.

#### STORY 1.1.1: Backend Project Initialization

**Story Key:** `BE-STORY-001`  
**As a** developer  
**I want** a properly structured FastAPI backend project  
**So that** I can build PartnerScout API in a maintainable way

**Acceptance Criteria:**
- Backend folder exists at `backend/`
- Python 3.10+ virtual environment supported
- All layers (core, api, services, repositories, agents, db) have directory structure
- `main.py` entry point exists and starts FastAPI app

##### TASK 1.1.1.1: Create Backend Directory Structure

**Task Key:** `BE-TASK-001`  
**File:** `backend/app/` (directory structure)

**SUBTASKS:**
- **BE-SUB-001:** Create `backend/` root directory
- **BE-SUB-002:** Create `app/` package with `__init__.py`
- **BE-SUB-003:** Create `core/`, `guards/`, `api/`, `models/`, `services/`, `repositories/`, `agents/`, `prompts/`, `db/` directories
- **BE-SUB-004:** Add `__init__.py` to each package
- **BE-SUB-005:** Create `scripts/` and `tests/` directories

##### TASK 1.1.1.2: Create Dependencies File

**Task Key:** `BE-TASK-002`  
**File:** `backend/requirements.txt`

**SUBTASKS:**
- **BE-SUB-006:** Add FastAPI, uvicorn, pydantic, pydantic-settings
- **BE-SUB-007:** Add supabase client
- **BE-SUB-008:** Add LangChain, langchain-openai, langchain-google-genai, langchain-community
- **BE-SUB-009:** Add httpx, apify-client, pyyaml
- **BE-SUB-010:** Add PyJWT, python-jose for authentication
- **BE-SUB-011:** Add pytest, pytest-asyncio for testing

##### TASK 1.1.1.3: Create Environment Template

**Task Key:** `BE-TASK-003`  
**File:** `backend/.env.example`

**SUBTASKS:**
- **BE-SUB-012:** Document SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET
- **BE-SUB-013:** Document LLM_PROVIDER, OPENAI_API_KEY, GOOGLE_API_KEY
- **BE-SUB-014:** Document APIFY_API_KEY, N8N_SERVICE_KEY, N8N_WEBHOOK_URL
- **BE-SUB-015:** Add README section for environment setup

##### TASK 1.1.1.4: Create FastAPI Entry Point

**Task Key:** `BE-TASK-004`  
**File:** `backend/app/main.py`

**SUBTASKS:**
- **BE-SUB-016:** Create FastAPI app instance with title "PartnerScout API"
- **BE-SUB-017:** Add CORS middleware configuration
- **BE-SUB-018:** Add global exception handler for consistent error format
- **BE-SUB-019:** Add GET /api/health endpoint (public, no auth)
- **BE-SUB-020:** Create uvicorn run configuration

---

### FEATURE 1.2: Core Configuration

**Feature Key:** `BE-FEAT-002`  
**Summary:** Centralized configuration for environment variables, constants, and YAML settings.

#### STORY 1.2.1: Environment Configuration

**Story Key:** `BE-STORY-002`  
**As a** developer  
**I want** centralized configuration management  
**So that** secrets and settings are managed in one place

**Acceptance Criteria:**
- Settings loaded from environment variables
- All required env vars documented
- Settings cached for performance

##### TASK 1.2.1.1: Implement Config Module

**Task Key:** `BE-TASK-005`  
**File:** `backend/app/core/config.py`

**SUBTASKS:**
- **BE-SUB-021:** Create Settings class with Pydantic BaseSettings
- **BE-SUB-022:** Add database config (SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET)
- **BE-SUB-023:** Add LLM config (LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, GOOGLE_API_KEY, GEMINI_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL)
- **BE-SUB-024:** Add external services (APIFY_API_KEY, N8N_SERVICE_KEY, N8N_WEBHOOK_URL)
- **BE-SUB-025:** Implement get_settings() with lru_cache

##### TASK 1.2.1.2: Implement Constants Module

**Task Key:** `BE-TASK-006`  
**File:** `backend/app/core/constants.py`

**SUBTASKS:**
- **BE-SUB-026:** Define HttpStatus class with status codes (OK, CREATED, BAD_REQUEST, UNAUTHORIZED, FORBIDDEN, NOT_FOUND, etc.)
- **BE-SUB-027:** Define ErrorCodes class (UNAUTHORIZED, INVALID_TOKEN, JOB_NOT_FOUND, PROFILE_NOT_FOUND, INVALID_TRANSITION, etc.)
- **BE-SUB-028:** Define JobStatus enum (pending, analyzing, discovering, scoring, completed, failed)
- **BE-SUB-029:** Define ProfileStatus enum (new, processing, done, skipped)
- **BE-SUB-030:** Define VALID_JOB_TRANSITIONS and VALID_PROFILE_TRANSITIONS dicts
- **BE-SUB-031:** Define Defaults (DISCOVERY_LIMIT=50, MIN_REFERENCE_PROFILES=2, MAX_REFERENCE_PROFILES=10)
- **BE-SUB-032:** Define ScoringCategories and Tables constants

##### TASK 1.2.1.3: Implement Custom Exceptions

**Task Key:** `BE-TASK-007`  
**File:** `backend/app/core/exceptions.py`

**SUBTASKS:**
- **BE-SUB-033:** Create BusinessError extending HTTPException with code and message
- **BE-SUB-034:** Create NotFoundError for JOB_NOT_FOUND, PROFILE_NOT_FOUND
- **BE-SUB-035:** Create UnauthorizedError for authentication failures
- **BE-SUB-036:** Create ForbiddenError for authorization failures
- **BE-SUB-037:** Create AgentError for AI agent failures

##### TASK 1.2.1.4: Create YAML Configuration Files

**Task Key:** `BE-TASK-008`  
**Files:** `backend/app/core/settings/*.yaml`

**SUBTASKS:**
- **BE-SUB-038:** Create settings/__init__.py with load_yaml, get_agent_config, get_scoring_config, get_limits_config
- **BE-SUB-039:** Create agents.yaml (brand_analyzer, discovery, scorer config)
- **BE-SUB-040:** Create scoring.yaml (weights, thresholds, fake_detection, engagement_benchmarks)
- **BE-SUB-041:** Create limits.yaml (rate_limits, timeouts, retry config)

---

### FEATURE 1.3: Data Layer

**Feature Key:** `BE-FEAT-003`  
**Summary:** Database client and connection management for Supabase.

#### STORY 1.3.1: Supabase Database Integration

**Story Key:** `BE-STORY-003`  
**As a** backend service  
**I want** to connect to Supabase PostgreSQL  
**So that** I can persist and retrieve discovery data

**Acceptance Criteria:**
- Supabase client initializes with project URL and service role key
- Client available via dependency injection
- Connection errors handled gracefully

##### TASK 1.3.1.1: Implement Supabase Client

**Task Key:** `BE-TASK-009`  
**File:** `backend/app/db/supabase.py`

**SUBTASKS:**
- **BE-SUB-042:** Create get_supabase_client() function
- **BE-SUB-043:** Use SUPABASE_SERVICE_ROLE_KEY for server-side operations (bypasses RLS)
- **BE-SUB-044:** Implement get_db() dependency for FastAPI Depends()
- **BE-SUB-045:** Add connection validation on startup

---

### FEATURE 1.4: Pydantic Models

**Feature Key:** `BE-FEAT-004`  
**Summary:** Request/response models for API validation and serialization.

#### STORY 1.4.1: Data Models for API Contracts

**Story Key:** `BE-STORY-004`  
**As a** API consumer  
**I want** validated request and response schemas  
**So that** API contracts are consistent and type-safe

**Acceptance Criteria:**
- All API endpoints have request/response models
- Models align with PRD Section 8 API contracts
- Validation rules match business rules (2-10 reference profiles, etc.)

##### TASK 1.4.1.1: Job Models

**Task Key:** `BE-TASK-010`  
**File:** `backend/app/models/job.py`

**SUBTASKS:**
- **BE-SUB-046:** Create DiscoveryJob model (matches discovery_jobs table)
- **BE-SUB-047:** Create CreateJobRequest (brand_description, reference_profiles, name)
- **BE-SUB-048:** Create UpdateJobRequest (name)
- **BE-SUB-049:** Create JobWithProfiles (extends Job with profiles, brand_dna)
- **BE-SUB-050:** Add validators for reference_profiles count (2-10)

##### TASK 1.4.1.2: Profile Models

**Task Key:** `BE-TASK-011`  
**File:** `backend/app/models/profile.py`

**SUBTASKS:**
- **BE-SUB-051:** Create DiscoveredProfile model (matches discovered_profiles table)
- **BE-SUB-052:** Create ProfileScore model (matches profile_scores table)
- **BE-SUB-053:** Create ProfileContact model (matches profile_contacts table)
- **BE-SUB-054:** Create CompleteProfile (profile + score + contact)

##### TASK 1.4.1.3: Brand DNA Model

**Task Key:** `BE-TASK-012`  
**File:** `backend/app/models/brand.py`

**SUBTASKS:**
- **BE-SUB-055:** Create BrandDNA model (hashtags, keywords, embedding_vector)

##### TASK 1.4.1.4: Agent Request/Response Models

**Task Key:** `BE-TASK-013`  
**File:** `backend/app/models/agent.py`

**SUBTASKS:**
- **BE-SUB-056:** Create AnalyzeBrandRequest (job_id)
- **BE-SUB-057:** Create AnalyzeBrandResponse (brand_dna)
- **BE-SUB-058:** Create DiscoverRequest (job_id, hashtags, keywords, limit)
- **BE-SUB-059:** Create DiscoverResponse (profiles, total_discovered, deduplicated)
- **BE-SUB-060:** Create ScoreRequest (profile_id, job_id)
- **BE-SUB-061:** Create ScoreResponse (score, reasoning, contact)

##### TASK 1.4.1.5: Email Models

**Task Key:** `BE-TASK-014`  
**File:** `backend/app/models/email.py`

**SUBTASKS:**
- **BE-SUB-062:** Create GenerateEmailRequest (profile_id, job_id, tone)
- **BE-SUB-063:** Create GenerateEmailResponse (subject, body, profile, metadata)
- **BE-SUB-064:** Create SendEmailRequest (profile_id, subject, body, to_email)
- **BE-SUB-065:** Create SendEmailResponse (status, message, email_id, sent_at)

##### TASK 1.4.1.6: Status Models

**Task Key:** `BE-TASK-015`  
**File:** `backend/app/models/status.py`

**SUBTASKS:**
- **BE-SUB-066:** Create UpdateJobStatusRequest (status, error_message)
- **BE-SUB-067:** Create UpdateProfileStatusRequest (status)
- **BE-SUB-068:** Create BatchUpdateProfileStatusRequest (profile_ids, status)
- **BE-SUB-069:** Create JobStatusResponse, ProfileStatusResponse

---

## EPIC 2: Session Management API

**Epic Key:** `BE-EPIC-002`  
**Summary:** Full CRUD and lifecycle management for discovery sessions (jobs).  
**PRD Reference:** Section 5.4 (Session Management), Section 8.1 (Session Management APIs)  
**Sprint Estimate:** 2 sprints

---

### FEATURE 2.1: Repository Layer

**Feature Key:** `BE-FEAT-005`  
**Summary:** Data access layer for database operations.

#### STORY 2.1.1: Job Repository

**Story Key:** `BE-STORY-005`  
**As a** service layer  
**I want** to access job data without SQL logic  
**So that** business logic remains decoupled from data access

**Acceptance Criteria:**
- All job CRUD operations available
- Queries filter by user_id for isolation
- Async operations throughout

##### TASK 2.1.1.1: Base Repository

**Task Key:** `BE-TASK-016`  
**File:** `backend/app/repositories/base_repo.py`

**SUBTASKS:**
- **BE-SUB-070:** Create BaseRepository generic class
- **BE-SUB-071:** Implement get_by_id, list_all, delete
- **BE-SUB-072:** Use Supabase client via Depends()

##### TASK 2.1.1.2: Job Repository

**Task Key:** `BE-TASK-017`  
**File:** `backend/app/repositories/job_repo.py`

**SUBTASKS:**
- **BE-SUB-073:** Implement create(user_id, brand_description, reference_profiles, name)
- **BE-SUB-074:** Implement list_by_user(user_id) ordered by created_at DESC
- **BE-SUB-075:** Implement get_by_id(job_id)
- **BE-SUB-076:** Implement update_status(job_id, status, error_message)
- **BE-SUB-077:** Implement update(job_id, name)
- **BE-SUB-078:** Implement delete(job_id)
- **BE-SUB-079:** Implement count_user_jobs_today(user_id)

##### TASK 2.1.1.3: Profile Repository

**Task Key:** `BE-TASK-018`  
**File:** `backend/app/repositories/profile_repo.py`

**SUBTASKS:**
- **BE-SUB-080:** Implement list_by_job(job_id, filters)
- **BE-SUB-081:** Implement list_by_job_with_scores(job_id) with joins
- **BE-SUB-082:** Implement get_by_id(profile_id)
- **BE-SUB-083:** Implement get_by_id_with_score(profile_id)
- **BE-SUB-084:** Implement batch_insert(job_id, profiles)
- **BE-SUB-085:** Implement update_status(profile_id, status)
- **BE-SUB-086:** Implement batch_update_status(profile_ids, status)

##### TASK 2.1.1.4: Brand DNA Repository

**Task Key:** `BE-TASK-019`  
**File:** `backend/app/repositories/brand_repo.py`

**SUBTASKS:**
- **BE-SUB-087:** Implement create(job_id, hashtags, keywords, embedding_vector)
- **BE-SUB-088:** Implement get_by_job(job_id)
- **BE-SUB-089:** Implement upsert for idempotent brand_dna creation

##### TASK 2.1.1.5: Score Repository

**Task Key:** `BE-TASK-020`  
**File:** `backend/app/repositories/score_repo.py`

**SUBTASKS:**
- **BE-SUB-090:** Implement create_score(profile_id, score, reasoning fields)
- **BE-SUB-091:** Implement upsert_score for idempotent scoring
- **BE-SUB-092:** Implement create_contact(profile_id, email, source)
- **BE-SUB-093:** Implement upsert_contact

---

### FEATURE 2.2: Authentication Guards

**Feature Key:** `BE-FEAT-006`  
**Summary:** Request validation and authentication before processing.

#### STORY 2.2.1: User Authentication

**Story Key:** `BE-STORY-006`  
**As a** authenticated user  
**I want** my requests validated by JWT  
**So that** only I can access my discovery sessions

**Acceptance Criteria:**
- JWT validation for /api/jobs/* endpoints
- User ID extracted from token
- 401 returned for invalid/expired tokens (PRD 8.0)

##### TASK 2.2.1.1: Auth Guards

**Task Key:** `BE-TASK-021`  
**File:** `backend/app/guards/auth.py`

**SUBTASKS:**
- **BE-SUB-094:** Create UserGuard - validate Bearer token, decode Supabase JWT
- **BE-SUB-095:** Extract user_id (sub) and email from payload
- **BE-SUB-096:** Handle ExpiredSignatureError, InvalidTokenError with 401
- **BE-SUB-097:** Create ServiceKeyGuard - validate X-Service-Key header
- **BE-SUB-098:** Compare against N8N_SERVICE_KEY from config
- **BE-SUB-099:** Return UNAUTHORIZED error format per PRD 8.0

##### TASK 2.2.1.2: Ownership Guards

**Task Key:** `BE-TASK-022`  
**File:** `backend/app/guards/ownership.py`

**SUBTASKS:**
- **BE-SUB-100:** Create JobOwnerGuard - verify user owns job_id
- **BE-SUB-101:** Fetch job, check user_id == auth.uid()
- **BE-SUB-102:** Return 404 if job not found (JOB_NOT_FOUND)
- **BE-SUB-103:** Return 403 if wrong user (FORBIDDEN per PRD 8.0)
- **BE-SUB-104:** Create ProfileOwnerGuard - verify profile belongs to user's job

##### TASK 2.2.1.3: Validation Guards

**Task Key:** `BE-TASK-023`  
**File:** `backend/app/guards/validation.py`

**SUBTASKS:**
- **BE-SUB-105:** Create StatusTransitionGuard for job status
- **BE-SUB-106:** Validate new status in VALID_JOB_TRANSITIONS[current_status]
- **BE-SUB-107:** Create StatusTransitionGuard for profile status
- **BE-SUB-108:** Return INVALID_TRANSITION error per PRD

---

### FEATURE 2.3: Job Service

**Feature Key:** `BE-FEAT-007`  
**Summary:** Business logic for discovery session lifecycle.

#### STORY 2.3.1: Create Discovery Session

**Story Key:** `BE-STORY-007`  
**As a** user  
**I want** to create a new discovery session with brand description and reference profiles  
**So that** I can start finding partner profiles

**Acceptance Criteria:**
- POST /api/jobs creates job with status=pending
- 2-10 reference profiles required (PRD 5.4)
- Daily job limit enforced
- Returns job with id

##### TASK 2.3.1.1: Job Service - Create & List

**Task Key:** `BE-TASK-024`  
**File:** `backend/app/services/job_service.py`

**SUBTASKS:**
- **BE-SUB-109:** Implement create_job(user_id, CreateJobRequest)
- **BE-SUB-110:** Validate 2-10 reference profiles (raise INSUFFICIENT_PROFILES or INVALID_INPUT)
- **BE-SUB-111:** Check daily limit (count_user_jobs_today, raise DAILY_LIMIT_EXCEEDED)
- **BE-SUB-112:** Call job_repo.create, return Job
- **BE-SUB-113:** Implement list_user_jobs(user_id) - return jobs ordered by created_at DESC

##### TASK 2.3.1.2: Job Service - Get & Update

**Task Key:** `BE-TASK-025`  
**File:** `backend/app/services/job_service.py`

**SUBTASKS:**
- **BE-SUB-114:** Implement get_job_with_profiles(job) - join profiles, scores, contacts
- **BE-SUB-115:** Support min_score, sort, order, status query params
- **BE-SUB-116:** Implement update_job(job, UpdateJobRequest) - update name
- **BE-SUB-117:** Implement delete_job(job) - cascade delete

##### TASK 2.3.1.3: Job Service - Start & Retry

**Task Key:** `BE-TASK-026`  
**File:** `backend/app/services/job_service.py`

**SUBTASKS:**
- **BE-SUB-118:** Implement trigger_discovery(job) - POST to N8N_WEBHOOK_URL with job_id, user_id
- **BE-SUB-119:** Validate job.status == PENDING (raise JOB_ALREADY_STARTED)
- **BE-SUB-120:** Return 202 Accepted with job_id
- **BE-SUB-121:** Implement retry_job(job) - validate status=FAILED, reset to PENDING, trigger_discovery

##### TASK 2.3.1.4: Job Service - Analytics

**Task Key:** `BE-TASK-027`  
**File:** `backend/app/services/job_service.py`

**SUBTASKS:**
- **BE-SUB-122:** Implement get_analytics(job) - profiles_discovered, profiles_scored, profiles_with_email
- **BE-SUB-123:** Calculate average_score, score_distribution (excellent, good, moderate, poor)
- **BE-SUB-124:** Calculate status_distribution (new, processing, done, skipped)
- **BE-SUB-125:** Return structure matching PRD GET /api/jobs/{id}/analytics

---

### FEATURE 2.4: Job API Routes

**Feature Key:** `BE-FEAT-008`  
**Summary:** HTTP endpoints for session management.

#### STORY 2.4.1: Session Management Endpoints

**Story Key:** `BE-STORY-008`  
**As a** frontend developer  
**I want** RESTful APIs for session CRUD  
**So that** I can build the dashboard

**Acceptance Criteria:**
- All 8 session endpoints implemented per PRD 8.1
- User JWT required for all
- Responses match PRD contract

##### TASK 2.4.1.1: Job Routes Implementation

**Task Key:** `BE-TASK-028`  
**File:** `backend/app/api/routes/jobs.py`

**SUBTASKS:**
- **BE-SUB-126:** GET /api/jobs - list_user_jobs, require UserGuard
- **BE-SUB-127:** POST /api/jobs - create_job, require UserGuard, return 201
- **BE-SUB-128:** GET /api/jobs/{id} - get_job_with_profiles, require JobOwnerGuard
- **BE-SUB-129:** GET /api/jobs/{id}/analytics - get_analytics, require JobOwnerGuard
- **BE-SUB-130:** POST /api/jobs/{id}/start - trigger_discovery, require JobOwnerGuard, return 202
- **BE-SUB-131:** POST /api/jobs/{id}/retry - retry_job, require JobOwnerGuard, return 202
- **BE-SUB-132:** PATCH /api/jobs/{id} - update_job, require JobOwnerGuard
- **BE-SUB-133:** DELETE /api/jobs/{id} - delete_job, require JobOwnerGuard
- **BE-SUB-134:** Register router in main.py

---

### FEATURE 2.5: Status Update API

**Feature Key:** `BE-FEAT-009`  
**Summary:** Endpoints for n8n to update job and profile status.

#### STORY 2.4.2: Status Update Endpoints for Orchestration

**Story Key:** `BE-STORY-009`  
**As a** n8n orchestrator  
**I want** to update job and profile status  
**So that** the frontend shows real-time progress

**Acceptance Criteria:**
- PATCH /api/jobs/{id}/status (Service Key)
- PATCH /api/profiles/{id}/status (Service Key)
- PATCH /api/jobs/{id}/profiles/status batch (Service Key)
- Status transition validation enforced

##### TASK 2.5.1.1: Status Routes Implementation

**Task Key:** `BE-TASK-029`  
**File:** `backend/app/api/routes/status.py`

**SUBTASKS:**
- **BE-SUB-135:** PATCH /api/jobs/{job_id}/status - require ServiceKeyGuard
- **BE-SUB-136:** Validate status transition via StatusTransitionGuard
- **BE-SUB-137:** Update job, return JobStatusResponse
- **BE-SUB-138:** PATCH /api/profiles/{profile_id}/status - require ServiceKeyGuard
- **BE-SUB-139:** Validate profile status transition
- **BE-SUB-140:** PATCH /api/jobs/{job_id}/profiles/status - batch update, require ServiceKeyGuard
- **BE-SUB-141:** Validate all profile_ids belong to job_id
- **BE-SUB-142:** Register status router in main.py

---

## EPIC 3: AI Agent Integration

**Epic Key:** `BE-EPIC-003`  
**Summary:** Brand Analyzer, Discovery, and Scorer AI agents using LangChain.  
**PRD Reference:** Section 5.1, 5.2, 5.3 (Agents), Section 8.2, 8.3, 8.4 (Agent APIs)  
**Sprint Estimate:** 3 sprints

---

### FEATURE 3.1: LLM & External Services

**Feature Key:** `BE-FEAT-010`  
**Summary:** LLM provider abstraction and Apify Instagram scraping.

#### STORY 3.1.1: LLM Provider Abstraction

**Story Key:** `BE-STORY-010`  
**As a** agent developer  
**I want** a unified LLM interface  
**So that** I can switch between OpenAI, Gemini, and Ollama

**Acceptance Criteria:**
- LLM_PROVIDER env var selects provider
- OpenAI, Gemini, Ollama supported
- Same interface for all agents

##### TASK 3.1.1.1: LLM Service

**Task Key:** `BE-TASK-030`  
**File:** `backend/app/services/llm_service.py`

**SUBTASKS:**
- **BE-SUB-143:** Create get_llm() factory function
- **BE-SUB-144:** Implement OpenAI ChatOpenAI when LLM_PROVIDER=openai
- **BE-SUB-145:** Implement Gemini ChatGoogleGenerativeAI when LLM_PROVIDER=gemini
- **BE-SUB-146:** Implement Ollama when LLM_PROVIDER=ollama
- **BE-SUB-147:** Create get_embeddings() for OpenAI text-embedding-3-small

##### TASK 3.1.1.2: Apify Service

**Task Key:** `BE-TASK-031`  
**File:** `backend/app/services/apify_service.py`

**SUBTASKS:**
- **BE-SUB-148:** Create ApifyClient instance with APIFY_API_KEY
- **BE-SUB-149:** Implement scrape_instagram_profile(url) - profile data
- **BE-SUB-150:** Implement scrape_instagram_hashtag(hashtag, limit) - posts with profiles
- **BE-SUB-151:** Map Apify fields to discovered_profiles schema (PRD, Supabase_Database_Guide)
- **BE-SUB-152:** Calculate engagement_rate, following_ratio
- **BE-SUB-153:** Implement scrape_recent_posts(username) for Scorer Agent

---

### FEATURE 3.2: Prompt Management

**Feature Key:** `BE-FEAT-011`  
**Summary:** Loadable prompt templates for each agent.

#### STORY 3.1.2: Agent Prompts

**Story Key:** `BE-STORY-011`  
**As a** agent  
**I want** prompts loaded from files  
**So that** prompts can be updated without code changes

##### TASK 3.1.2.1: Prompt Loader

**Task Key:** `BE-TASK-032`  
**Files:** `backend/app/prompts/loader.py`, `**/system.txt`, `**/user.txt`

**SUBTASKS:**
- **BE-SUB-154:** Create load_prompt(agent_name, prompt_type) from prompts/{agent}/{system|user}.txt
- **BE-SUB-155:** Create load_prompts(agent_name) returns (system, user)
- **BE-SUB-156:** Create brand_analyzer/system.txt, brand_analyzer/user.txt
- **BE-SUB-157:** Create discovery/system.txt, discovery/user.txt
- **BE-SUB-158:** Create scorer/system.txt, scorer/user.txt (include fake detection rules)
- **BE-SUB-159:** Create email_composer/system.txt, email_composer/user.txt

---

### FEATURE 3.3: Brand Analyzer Agent

**Feature Key:** `BE-FEAT-012`  
**Summary:** Extract brand DNA from reference profiles.

#### STORY 3.2.1: Brand DNA Extraction

**Story Key:** `BE-STORY-012`  
**As a** n8n workflow  
**I want** to call Brand Analyzer API  
**So that** I get hashtags, keywords, and embedding for discovery

**Acceptance Criteria:**
- POST /api/agent/analyze-brand with job_id
- Fetches job, scrapes reference profiles via Apify
- Returns brand_dna per PRD 8.2
- Stores in brand_dna table

##### TASK 3.2.1.1: Base Agent Class

**Task Key:** `BE-TASK-033`  
**File:** `backend/app/agents/base.py`

**SUBTASKS:**
- **BE-SUB-160:** Create BaseAgent abstract class
- **BE-SUB-161:** _load_prompts(), _build_prompt_template(), _get_default_llm()
- **BE-SUB-162:** Abstract _build_chain(), run()

##### TASK 3.2.1.2: Brand Analyzer Agent

**Task Key:** `BE-TASK-034`  
**File:** `backend/app/agents/brand_analyzer.py`

**SUBTASKS:**
- **BE-SUB-163:** Extend BaseAgent, AGENT_NAME=brand_analyzer
- **BE-SUB-164:** Build chain with JsonOutputParser
- **BE-SUB-165:** run(job_id): fetch job, reference_profiles, brand_description
- **BE-SUB-166:** Scrape each reference profile via Apify
- **BE-SUB-167:** Invoke LLM with aggregated profile data
- **BE-SUB-168:** Generate embedding from keywords + brand_description
- **BE-SUB-169:** Store brand_dna in database (brand_repo.create)
- **BE-SUB-170:** Return brand_dna response

##### TASK 3.2.1.3: Brand Analyzer Route

**Task Key:** `BE-TASK-035`  
**File:** `backend/app/api/routes/agents.py`

**SUBTASKS:**
- **BE-SUB-171:** POST /api/agent/analyze-brand - require ServiceKeyGuard
- **BE-SUB-172:** Accept AnalyzeBrandRequest (job_id from body)
- **BE-SUB-173:** Call brand_analyzer.run(job_id)
- **BE-SUB-174:** Return AnalyzeBrandResponse
- **BE-SUB-175:** Handle AgentError, return 500 with AGENT_ERROR

---

### FEATURE 3.4: Discovery Agent

**Feature Key:** `BE-FEAT-013`  
**Summary:** Find Instagram profiles matching brand DNA.

#### STORY 3.3.1: Profile Discovery

**Story Key:** `BE-STORY-013`  
**As a** n8n workflow  
**I want** to call Discovery API  
**So that** I get candidate profiles for scoring

**Acceptance Criteria:**
- POST /api/agent/discover with job_id, hashtags, keywords, limit
- Searches hashtags via Apify, deduplicates by username
- Inserts into discovered_profiles with status=new
- Returns profiles with ids per PRD 8.3

##### TASK 3.3.1.1: Discovery Agent

**Task Key:** `BE-TASK-036`  
**File:** `backend/app/agents/discovery.py`

**SUBTASKS:**
- **BE-SUB-176:** Extend BaseAgent, AGENT_NAME=discovery
- **BE-SUB-177:** run(job_id, hashtags, keywords, limit): search each hashtag
- **BE-SUB-178:** Filter by follower range (min 10K, max 500K from config)
- **BE-SUB-179:** Deduplicate by username
- **BE-SUB-180:** Batch insert into discovered_profiles via profile_repo
- **BE-SUB-181:** Return profiles with generated ids, total_discovered, deduplicated

##### TASK 3.3.1.2: Discovery Route

**Task Key:** `BE-TASK-037`  
**File:** `backend/app/api/routes/agents.py`

**SUBTASKS:**
- **BE-SUB-182:** POST /api/agent/discover - require ServiceKeyGuard
- **BE-SUB-183:** Accept DiscoverRequest
- **BE-SUB-184:** Call discovery_agent.run()
- **BE-SUB-185:** Return DiscoverResponse

---

### FEATURE 3.5: Scorer Agent

**Feature Key:** `BE-FEAT-014`  
**Summary:** Score profiles against brand DNA, extract contacts.

#### STORY 3.4.1: Profile Scoring

**Story Key:** `BE-STORY-014`  
**As a** n8n workflow  
**I want** to call Scorer API  
**So that** I get ranked profiles with reasoning and contacts

**Acceptance Criteria:**
- POST /api/agent/score with profile_id, job_id
- Fetches profile from DB, brand_dna from DB, recent_posts from Apify
- Returns score (0-100), 6 dimension reasoning, contact per PRD 8.4
- Implements fake detection per PRD 5.3.1

##### TASK 3.4.1.1: Scoring Service

**Task Key:** `BE-TASK-038`  
**File:** `backend/app/services/scoring_service.py`

**SUBTASKS:**
- **BE-SUB-186:** calculate_final_score() with weights from scoring.yaml
- **BE-SUB-187:** get_recommendation(score) from thresholds
- **BE-SUB-188:** evaluate_engagement(engagement_rate, followers) by tier
- **BE-SUB-189:** calculate_follower_quality() - fake detection heuristics per PRD 5.3.1

##### TASK 3.4.1.2: Scorer Agent

**Task Key:** `BE-TASK-039`  
**File:** `backend/app/agents/scorer.py`

**SUBTASKS:**
- **BE-SUB-190:** Extend BaseAgent, AGENT_NAME=scorer
- **BE-SUB-191:** run(profile_id, job_id): fetch profile, brand_dna from DB
- **BE-SUB-192:** Fetch recent_posts from Apify for engagement analysis
- **BE-SUB-193:** Invoke LLM with profile + brand_dna
- **BE-SUB-194:** Parse 6 dimension scores, summary, recommendation
- **BE-SUB-195:** Calculate final weighted score via ScoringService
- **BE-SUB-196:** Extract email (LLM or regex from bio)
- **BE-SUB-197:** Store profile_scores, profile_contacts via score_repo
- **BE-SUB-198:** Update profile status to done
- **BE-SUB-199:** Return ScoreResponse

##### TASK 3.4.1.3: Scorer Route

**Task Key:** `BE-TASK-040`  
**File:** `backend/app/api/routes/agents.py`

**SUBTASKS:**
- **BE-SUB-200:** POST /api/agent/score - require ServiceKeyGuard
- **BE-SUB-201:** Accept ScoreRequest (profile_id, job_id)
- **BE-SUB-202:** Call scorer_agent.run()
- **BE-SUB-203:** Return ScoreResponse
- **BE-SUB-204:** Register agents router in main.py

---

## EPIC 4: Email & Outreach

**Epic Key:** `BE-EPIC-004`  
**Summary:** AI email generation and mock send.  
**PRD Reference:** Section 8.1.1 (Email Endpoints)  
**Sprint Estimate:** 1 sprint

---

### FEATURE 4.1: Email Composer Agent

**Feature Key:** `BE-FEAT-015`  
**Summary:** Generate AI-drafted partnership outreach emails.

#### STORY 4.1.1: Email Generation

**Story Key:** `BE-STORY-015`  
**As a** user  
**I want** to generate a personalized outreach email for a profile  
**So that** I can quickly contact potential partners

**Acceptance Criteria:**
- POST /api/email/generate with profile_id, job_id, tone
- Returns subject, body, profile metadata
- User JWT required

##### TASK 4.1.1.1: Email Composer Agent

**Task Key:** `BE-TASK-041`  
**File:** `backend/app/agents/email_composer.py`

**SUBTASKS:**
- **BE-SUB-205:** Extend BaseAgent, AGENT_NAME=email_composer
- **BE-SUB-206:** compose(profile, brand_dna, brand_description, tone)
- **BE-SUB-207:** Build prompt with profile username, bio, score, brand context
- **BE-SUB-208:** Return subject, body

##### TASK 4.1.1.2: Email Service

**Task Key:** `BE-TASK-042`  
**File:** `backend/app/services/email_service.py`

**SUBTASKS:**
- **BE-SUB-209:** generate_email(profile_id, job_id, tone, user_id) - fetch profile, brand, job
- **BE-SUB-210:** Call email_composer.compose()
- **BE-SUB-211:** Return subject, body, profile metadata, generated_at
- **BE-SUB-212:** send_email_mock() - return demo success response

##### TASK 4.1.1.3: Email Routes

**Task Key:** `BE-TASK-043`  
**File:** `backend/app/api/routes/email.py`

**SUBTASKS:**
- **BE-SUB-213:** POST /api/email/generate - require UserGuard
- **BE-SUB-214:** Validate profile belongs to user's job (ProfileOwnerGuard)
- **BE-SUB-215:** POST /api/email/send - require UserGuard, mock implementation
- **BE-SUB-216:** Register email router in main.py

---

## EPIC 5: Orchestration & Integration

**Epic Key:** `BE-EPIC-005`  
**Summary:** Python fallback orchestrator and integration testing.  
**PRD Reference:** Section 5.5 (Orchestration), Orchestration.md  
**Sprint Estimate:** 1 sprint

---

### FEATURE 5.1: Python Fallback Orchestrator

**Feature Key:** `BE-FEAT-016`  
**Summary:** Run discovery workflow when n8n unavailable.

#### STORY 5.1.1: Fallback Orchestrator

**Story Key:** `BE-STORY-016`  
**As a** developer  
**I want** a Python script to run discovery when n8n is down  
**So that** demos and local dev work without n8n

**Acceptance Criteria:**
- python -m scripts.run_discovery <job_id> runs full workflow
- Calls same APIs as n8n (analyze-brand, discover, score)
- Updates status via PATCH endpoints
- Handles errors, sets job failed

##### TASK 5.1.1.1: Python Orchestrator Script

**Task Key:** `BE-TASK-044`  
**File:** `backend/scripts/run_discovery.py`

**SUBTASKS:**
- **BE-SUB-217:** Implement update_job_status(), update_profile_status() via httpx
- **BE-SUB-218:** Implement call_brand_analyzer(), call_discovery_agent(), call_scorer_agent()
- **BE-SUB-219:** Implement run_discovery(job_id) - sequential phases
- **BE-SUB-220:** Phase 1: analyzing -> Brand Analyzer
- **BE-SUB-221:** Phase 2: discovering -> Discovery Agent
- **BE-SUB-222:** Phase 3: scoring -> loop profiles, Scorer Agent, update status
- **BE-SUB-223:** Phase 4: completed
- **BE-SUB-224:** Error handling: set job failed
- **BE-SUB-225:** CLI entry point: python -m scripts.run_discovery <job_id>

---

### FEATURE 5.2: Testing & Documentation

**Feature Key:** `BE-FEAT-017`  
**Summary:** Unit tests, integration tests, README.

#### STORY 5.2.1: Test Coverage

**Story Key:** `BE-STORY-017`  
**As a** developer  
**I want** test coverage for critical paths  
**So that** regressions are caught

##### TASK 5.2.1.1: Test Setup

**Task Key:** `BE-TASK-045`  
**Files:** `backend/tests/conftest.py`, `backend/tests/fixtures/`

**SUBTASKS:**
- **BE-SUB-226:** Create conftest.py with FastAPI TestClient, mock Supabase
- **BE-SUB-227:** Create mock_data.py with sample job, profile, brand_dna
- **BE-SUB-228:** Create pytest fixtures for auth headers, service key headers

##### TASK 5.2.1.2: Integration Tests

**Task Key:** `BE-TASK-046`  
**File:** `backend/tests/integration/test_api.py`

**SUBTASKS:**
- **BE-SUB-229:** Test GET /api/health returns 200
- **BE-SUB-230:** Test POST /api/jobs without auth returns 401
- **BE-SUB-231:** Test POST /api/jobs with auth creates job
- **BE-SUB-232:** Test GET /api/jobs/{id} returns job with profiles
- **BE-SUB-233:** Test POST /api/agent/* with invalid service key returns 401

##### TASK 5.2.1.3: Backend README

**Task Key:** `BE-TASK-047`  
**File:** `backend/README.md`

**SUBTASKS:**
- **BE-SUB-234:** Document setup (venv, pip install, .env)
- **BE-SUB-235:** Document run commands (uvicorn, run_discovery script)
- **BE-SUB-236:** Document API overview and auth requirements
- **BE-SUB-237:** Link to PRD, Backend_Implementation_Guide

---

## Jira Import Reference

### Epic Template

| Field | Value |
|-------|-------|
| Issue Type | Epic |
| Summary | [Epic Name] |
| Description | PRD Reference: [Section]. [Brief description]. Sprint Estimate: [N] sprints. |
| Custom Field: Sprint Estimate | [N] |

### Feature Template

| Field | Value |
|-------|-------|
| Issue Type | Feature |
| Parent | [Epic Key] |
| Summary | [Feature Name] |
| Description | [Capability description]. Links to [Story Keys]. |

### Story Template

| Field | Value |
|-------|-------|
| Issue Type | Story |
| Parent | [Feature Key] |
| Summary | [Story Name] |
| Description | As a [role] I want [goal] So that [benefit]. Acceptance Criteria: [list]. |
| Story Points | [1-8] |

### Task Template

| Field | Value |
|-------|-------|
| Issue Type | Task |
| Parent | [Story Key] |
| Summary | [Task Name] |
| Description | File: [path]. Subtasks: [list]. |
| Acceptance Criteria | [Technical criteria] |

### Subtask Template

| Field | Value |
|-------|-------|
| Issue Type | Sub-task |
| Parent | [Task Key] |
| Summary | [Specific action] |
| Description | [Implementation detail]. |

---

## Summary Statistics

| Level | Count |
|-------|-------|
| EPICs | 5 |
| FEATURES | 17 |
| STORIES | 17 |
| TASKS | 47 |
| SUBTASKS | 237 |
| **Total Work Items** | **323** |

---

## PRD Validation Checklist

- [ ] Section 5.1 Brand Analyzer - EPIC 3, FEATURE 3.3
- [ ] Section 5.2 Discovery Agent - EPIC 3, FEATURE 3.4
- [ ] Section 5.3 Scorer Agent - EPIC 3, FEATURE 3.5
- [ ] Section 5.3.1 Fake Detection - TASK 3.4.1.1, SUB-189
- [ ] Section 5.4 Session Management - EPIC 2
- [ ] Section 8.0 Authentication - FEATURE 2.2
- [ ] Section 8.1 Session APIs - FEATURE 2.4
- [ ] Section 8.1.1 Email APIs - EPIC 4
- [ ] Section 8.2 Brand Analyzer API - FEATURE 3.3
- [ ] Section 8.3 Discovery API - FEATURE 3.4
- [ ] Section 8.4 Scorer API - FEATURE 3.5
- [ ] Section 6 NFRs (Auth, RLS, Multi-user) - Guards, Repository user_id filtering

---

*Last updated: February 2026*
*Document: Backend Implementation Jira Plan*
*Validated against: Partner_Scout_AI_PRD.md v1.0*
