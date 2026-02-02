# PartnerScout AI - Database Implementation Plan (Jira Structure)

> Enterprise-ready implementation plan for Supabase database. Structured for Jira product management with EPIC, FEATURE, STORY, TASK, and SUBTASK hierarchy.

---

## Table of Contents

1. [Jira Hierarchy Overview](#jira-hierarchy-overview)
2. [EPIC 1: PartnerScout Database Foundation](#epic-1-partnerscout-database-foundation)
3. [Jira Import Reference](#jira-import-reference)
4. [PRD Validation Checklist](#prd-validation-checklist)
5. [Summary Statistics](#summary-statistics)

---

## Jira Hierarchy Overview

### Hierarchy Definition

| Level | Description | Example | PRD Reference |
|-------|-------------|---------|---------------|
| **EPIC** | Large initiative spanning multiple sprints | PartnerScout Database Foundation | Section 10 |
| **FEATURE** | Major capability or functional area | Supabase Project Setup | Section 10 |
| **STORY** | User-facing deliverable (As a... I want... So that...) | Create database tables | Section 10 |
| **TASK** | Concrete work item with acceptance criteria | Create discovery_jobs table | Section 10.3 |
| **SUBTASK** | Smallest trackable unit of work | Run CREATE TABLE SQL | - |

### Implementation Order

All work must follow **Step 1 → Step 11** due to dependencies (enums before tables, tables before indexes/triggers/RLS/realtime).

### Phase Boundary

**Phase 1: Database only.** Backend (FastAPI), APIs, n8n, and frontend are out of scope until the database phase is confirmed complete. No SQL or setup should be run until you give permission.

---

## EPIC 1: PartnerScout Database Foundation

**Epic Key:** `DB-EPIC-001`  
**Summary:** Implement PartnerScout AI database on Supabase with full schema, RLS, and Realtime.  
**PRD Reference:** Section 10 (Database Schema)  
**Sprint Estimate:** 1 sprint  
**Document Reference:** [Database_Implementation_Step_By_Step.md](Database_Implementation_Step_By_Step.md)

**See also:** [Database_Implementation_Index.md](Database_Implementation_Index.md) (plan index, step–task–migration map) · [supabase/migrations/](../supabase/migrations/) (SQL migration files)

### Schema Overview

```
auth.users (Supabase Auth)
    └── discovery_jobs (1:many, user_id FK)
            ├── brand_dna (1:1, job_id FK)
            └── discovered_profiles (1:many, job_id FK)
                    ├── profile_scores (1:1, profile_id FK)
                    └── profile_contacts (1:1, profile_id FK)
```

---

### FEATURE 1.1: Supabase Project Setup

**Feature Key:** `DB-FEAT-001`  
**Summary:** Create Supabase account and project for PartnerScout.

#### STORY 1.1.1: Supabase Project Creation

**Story Key:** `DB-STORY-001`  
**As a** developer  
**I want** a Supabase project for PartnerScout  
**So that** I can store discovery sessions and profile data

**Acceptance Criteria:**
- Supabase project created and accessible
- Project URL, anon key, service_role key saved
- Table Editor shows "No tables yet"

##### TASK 1.1.1.1: Create Supabase Account and Project (Step 1)

**Task Key:** `DB-TASK-001`  
**What:** Sign up for Supabase and create project.  
**Why:** Supabase hosts PostgreSQL database. Data isolated by user_id.

**SUBTASKS:**
- **DB-SUB-001:** Go to supabase.com, sign in (GitHub/Google/email)
- **DB-SUB-002:** Click New Project
- **DB-SUB-003:** Enter name (e.g., partner-scout), database password, region
- **DB-SUB-004:** Save database password for direct DB access
- **DB-SUB-005:** Wait for project creation (~2 minutes)
- **DB-SUB-006:** Navigate to Settings → API, note Project URL, anon key, service_role key

**Verification:** Dashboard visible; Table Editor shows "No tables yet".

---

### FEATURE 1.2: Database Extensions & Types

**Feature Key:** `DB-FEAT-002`  
**Summary:** Enable required extensions and define enum types.

#### STORY 1.2.1: Extensions for AI and UUID Support

**Story Key:** `DB-STORY-002`  
**As a** backend  
**I want** vector and uuid-ossp extensions enabled  
**So that** I can store embeddings and use UUID primary keys

**Acceptance Criteria:**
- vector extension enabled (for AI embeddings)
- uuid-ossp extension enabled (for UUID generation)

##### TASK 1.2.1.1: Enable Extensions (Step 2)

**Task Key:** `DB-TASK-002`  
**What:** Enable vector and uuid-ossp extensions.  
**Why:** PartnerScout stores brand DNA as 1536-dim vector; UUIDs for all PKs.

**SUBTASKS:**
- **DB-SUB-007:** Open SQL Editor in Supabase dashboard
- **DB-SUB-008:** Run CREATE EXTENSION IF NOT EXISTS vector;
- **DB-SUB-009:** Run CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
- **DB-SUB-010:** Verify "Success. No rows returned"

**Verification:** Database → Extensions lists vector, uuid-ossp.

##### TASK 1.2.1.2: Create Enum Types (Step 3)

**Task Key:** `DB-TASK-003`  
**What:** Define discovery_job_status and profile_status enums.  
**Why:** Prevent invalid status values; make queries clearer.

**SUBTASKS:**
- **DB-SUB-011:** Run CREATE TYPE discovery_job_status AS ENUM (pending, analyzing, discovering, scoring, completed, failed);
- **DB-SUB-012:** Run CREATE TYPE profile_status AS ENUM (new, processing, done, skipped);

**Verification:** Database → Types lists both enums.

---

### FEATURE 1.3: Core Schema - Tables

**Feature Key:** `DB-FEAT-003`  
**Summary:** Create all database tables per PRD Section 10.

#### STORY 1.3.1: Parent Table - discovery_jobs

**Story Key:** `DB-STORY-003`  
**As a** user  
**I want** discovery sessions stored in the database  
**So that** I can track and manage multiple discovery jobs

**Acceptance Criteria:**
- discovery_jobs table exists
- Columns: id, user_id, name, brand_description, reference_profiles, status, profiles_discovered, profiles_scored, created_at, updated_at
- user_id references auth.users(id) ON DELETE CASCADE

##### TASK 1.3.1.1: Create discovery_jobs Table (Step 4)

**Task Key:** `DB-TASK-004`  
**File:** Supabase SQL Editor

**SUBTASKS:**
- **DB-SUB-013:** Run CREATE TABLE discovery_jobs with all columns per PRD 10.3
- **DB-SUB-014:** Verify user_id FK to auth.users(id) ON DELETE CASCADE
- **DB-SUB-015:** Verify status uses discovery_job_status enum, default 'pending'

**Verification:** Table Editor shows discovery_jobs with expected columns.

##### TASK 1.3.1.2: Create brand_dna Table (Step 5)

**Task Key:** `DB-TASK-005`  
**What:** 1:1 table for extracted brand identity per job.

**SUBTASKS:**
- **DB-SUB-016:** Run CREATE TABLE brand_dna
- **DB-SUB-017:** Include job_id FK, hashtags[], keywords[], embedding_vector vector(1536)
- **DB-SUB-018:** Add UNIQUE(job_id) constraint

**Verification:** brand_dna in Table Editor with job_id FK.

##### TASK 1.3.1.3: Create discovered_profiles Table (Step 6)

**Task Key:** `DB-TASK-006`  
**What:** 1:many table for Instagram profiles per job.

**SUBTASKS:**
- **DB-SUB-019:** Run CREATE TABLE discovered_profiles
- **DB-SUB-020:** Include all columns per PRD 10.5 (instagram_url, username, full_name, profile_picture_url, bio, followers, following, posts_count, engagement_rate, is_verified, is_business, external_url, business_email, business_category, following_ratio, status)
- **DB-SUB-021:** Add UNIQUE(job_id, instagram_url)
- **DB-SUB-022:** Verify status uses profile_status enum, default 'new'

**Verification:** discovered_profiles in Table Editor with job_id FK.

##### TASK 1.3.1.4: Create profile_scores and profile_contacts Tables (Step 7)

**Task Key:** `DB-TASK-007`  
**What:** 1:1 tables for scores and contacts per profile.

**SUBTASKS:**
- **DB-SUB-023:** Run CREATE TABLE profile_scores with score, 6 dimension columns, reasoning JSONB
- **DB-SUB-024:** Add CHECK constraints for score 0-100 on all score columns
- **DB-SUB-025:** Add UNIQUE(profile_id)
- **DB-SUB-026:** Run CREATE TABLE profile_contacts with profile_id, email, source
- **DB-SUB-027:** Add UNIQUE(profile_id)

**Verification:** Both tables in Table Editor with profile_id FKs.

---

### FEATURE 1.4: Performance & Automation

**Feature Key:** `DB-FEAT-004`  
**Summary:** Indexes and triggers for performance and counter maintenance.

#### STORY 1.4.1: Database Performance Optimization

**Story Key:** `DB-STORY-004`  
**As a** backend  
**I want** indexes on foreign keys and filters  
**So that** queries are fast

**Acceptance Criteria:**
- Indexes on user_id, job_id, profile_id, status, created_at, followers, score

##### TASK 1.4.1.1: Add Indexes (Step 8)

**Task Key:** `DB-TASK-008`  
**What:** Create indexes for FK lookups and common filters.

**SUBTASKS:**
- **DB-SUB-028:** idx_discovery_jobs_user_id
- **DB-SUB-029:** idx_discovery_jobs_status, idx_discovery_jobs_created_at DESC
- **DB-SUB-030:** idx_brand_dna_job_id
- **DB-SUB-031:** idx_discovered_profiles_job_id, idx_discovered_profiles_status, idx_discovered_profiles_followers DESC
- **DB-SUB-032:** idx_profile_scores_profile_id, idx_profile_scores_score DESC
- **DB-SUB-033:** idx_profile_contacts_profile_id

**Verification:** Each table's Indexes tab shows new indexes.

##### TASK 1.4.1.2: Add Triggers (Step 9)

**Task Key:** `DB-TASK-009`  
**What:** Auto-update updated_at, profiles_discovered, profiles_scored.

**SUBTASKS:**
- **DB-SUB-034:** Create update_updated_at_column() function
- **DB-SUB-035:** Create trigger trigger_discovery_jobs_updated_at on discovery_jobs
- **DB-SUB-036:** Create update_profiles_discovered() function (INSERT +1, DELETE -1)
- **DB-SUB-037:** Create trigger trigger_update_profiles_discovered on discovered_profiles
- **DB-SUB-038:** Create update_profiles_scored() function (status→done: +1; done→other: -1)
- **DB-SUB-039:** Create trigger trigger_update_profiles_scored on discovered_profiles

**Verification:** Database → Functions; each table's Triggers tab.

---

### FEATURE 1.5: Security & Realtime

**Feature Key:** `DB-FEAT-005`  
**Summary:** Row Level Security and Realtime publication.

#### STORY 1.5.1: User Data Isolation

**Story Key:** `DB-STORY-005`  
**As a** user  
**I want** my data isolated from other users  
**So that** only I can access my discovery sessions

**Acceptance Criteria:**
- RLS enabled on all 5 tables
- Policies enforce user_id = auth.uid() or ownership chain

##### TASK 1.5.1.1: Enable Row Level Security (Step 10)

**Task Key:** `DB-TASK-010`  
**What:** RLS policies for multi-tenant data isolation.

**SUBTASKS:**
- **DB-SUB-040:** ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY
- **DB-SUB-041:** Create 4 policies on discovery_jobs (SELECT, INSERT, UPDATE, DELETE) USING user_id = auth.uid()
- **DB-SUB-042:** ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY
- **DB-SUB-043:** Create policy on brand_dna FOR ALL USING job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
- **DB-SUB-044:** ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY
- **DB-SUB-045:** Create policy on discovered_profiles FOR ALL USING job ownership chain
- **DB-SUB-046:** ALTER TABLE profile_scores, profile_contacts ENABLE ROW LEVEL SECURITY
- **DB-SUB-047:** Create policies on profile_scores, profile_contacts via profile→job ownership chain

**Verification:** RLS enabled; policies visible in Authentication → Policies or table RLS tab.

##### TASK 1.5.1.2: Enable Realtime (Step 11)

**Task Key:** `DB-TASK-011`  
**What:** Add tables to supabase_realtime publication for live dashboard updates.

**SUBTASKS:**
- **DB-SUB-048:** ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs
- **DB-SUB-049:** ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles
- **DB-SUB-050:** ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores
- **DB-SUB-051:** ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts

**Verification:** SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime'; returns 4 tables.

---

## Jira Import Reference

### Epic Template

| Field | Value |
|-------|-------|
| Issue Type | Epic |
| Summary | PartnerScout Database Foundation |
| Description | Implement PartnerScout AI database on Supabase. PRD Section 10. Sprint Estimate: 1 sprint. |
| Custom Field: Sprint Estimate | 1 |

### Feature Template

| Field | Value |
|-------|-------|
| Issue Type | Feature |
| Parent | DB-EPIC-001 |
| Summary | [Feature Name] |
| Description | [Capability description]. Links to [Story Keys]. |

### Story Template

| Field | Value |
|-------|-------|
| Issue Type | Story |
| Parent | [Feature Key] |
| Summary | [Story Name] |
| Description | As a [role] I want [goal] So that [benefit]. Acceptance Criteria: [list]. |
| Story Points | [1-3] |

### Task Template

| Field | Value |
|-------|-------|
| Issue Type | Task |
| Parent | [Story Key] |
| Summary | [Task Name] |
| Description | Step [N]. What: []. Why: []. Subtasks: [list]. Verification: []. |

### Subtask Template

| Field | Value |
|-------|-------|
| Issue Type | Sub-task |
| Parent | [Task Key] |
| Summary | [Specific action] |
| Description | [Implementation detail]. |

---

## PRD Validation Checklist

- [ ] Section 10.1 Tables Overview - FEATURE 1.3
- [ ] Section 10.1.1 Data Isolation Chain - FEATURE 1.5, RLS policies
- [ ] Section 10.1.2 RLS Policies - TASK 1.5.1.1
- [ ] Section 10.2 users (Supabase Auth) - Pre-existing
- [ ] Section 10.3 discovery_jobs - TASK 1.3.1.1
- [ ] Section 10.4 brand_dna - TASK 1.3.1.2
- [ ] Section 10.5 discovered_profiles - TASK 1.3.1.3
- [ ] Section 10.6 profile_scores - TASK 1.3.1.4
- [ ] Section 10.7 profile_contacts - TASK 1.3.1.4
- [ ] Realtime for dashboard - TASK 1.5.1.2

---

## Summary Statistics

| Level | Count |
|-------|-------|
| EPICs | 1 |
| FEATURES | 5 |
| STORIES | 5 |
| TASKS | 11 |
| SUBTASKS | 51 |
| **Total Work Items** | **73** |

### Step-to-Task Mapping

| Step | Task Key | Feature |
|------|----------|---------|
| 1 | DB-TASK-001 | Supabase Project Setup |
| 2 | DB-TASK-002 | Extensions |
| 3 | DB-TASK-003 | Enum Types |
| 4 | DB-TASK-004 | discovery_jobs |
| 5 | DB-TASK-005 | brand_dna |
| 6 | DB-TASK-006 | discovered_profiles |
| 7 | DB-TASK-007 | profile_scores, profile_contacts |
| 8 | DB-TASK-008 | Indexes |
| 9 | DB-TASK-009 | Triggers |
| 10 | DB-TASK-010 | RLS |
| 11 | DB-TASK-011 | Realtime |

---

## Next Phase

After you confirm the database phase is complete, the next phase is **Phase 2: Backend (FastAPI)**. See [Backend_Implementation_Jira_Plan.md](Backend_Implementation_Jira_Plan.md).

---

*Last updated: February 2026*  
*Document: Database Implementation Jira Plan*  
*Validated against: Partner_Scout_AI_PRD.md v1.0, Database_Implementation_Step_By_Step.md*
