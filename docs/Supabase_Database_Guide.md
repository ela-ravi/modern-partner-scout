# Supabase Database Setup Guide

> A comprehensive guide for setting up Supabase PostgreSQL database, including schema design, migrations, RLS policies, and common query patterns.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Setup](#2-project-setup)
3. [Database Schema Design](#3-database-schema-design)
4. [SQL Migrations](#4-sql-migrations)
5. [Common Query Patterns](#5-common-query-patterns)
6. [Seed Data](#6-seed-data)
7. [Maintenance & Cleanup](#7-maintenance--cleanup)
8. [Data Flow & Workflow](#8-data-flow--workflow)
9. [Integration: Backend (Python/FastAPI)](#9-integration-backend-pythonfastapi)
10. [Integration: Frontend (React/TypeScript)](#10-integration-frontend-reacttypescript)

---

## 1. Overview

### What is Supabase?

Supabase is an open-source Firebase alternative providing:
- **PostgreSQL Database** - Full SQL database with extensions
- **Authentication** - Built-in auth with social providers
- **Realtime** - Subscribe to database changes
- **Row Level Security** - Fine-grained access control at database level
- **Auto-generated APIs** - REST and GraphQL APIs from your schema

### Key Features Used

| Feature | Purpose |
|---------|---------|
| PostgreSQL | Primary data store with full SQL support |
| pgvector | Vector embeddings for AI/ML features |
| RLS Policies | User data isolation and security |
| Realtime | Live updates for dashboard |
| Auth | User authentication and JWT tokens |

---

## 2. Project Setup

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your credentials:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon Key**: Public key for client-side
   - **Service Role Key**: Private key for server-side (keep secret!)

### 2.2 Database Files Structure

```
supabase/
├── migrations/               # SQL migration files (run in order)
│   ├── 001_initial_schema.sql
│   ├── 002_enable_rls.sql
│   └── 003_enable_realtime.sql
├── seed.sql                  # Sample data for testing
└── README.md
```

### 2.3 Required Credentials

From your Supabase project dashboard, note these values:

| Credential | Location | Purpose |
|------------|----------|---------|
| Project URL | Settings → API | `https://xxxxx.supabase.co` |
| Anon Key | Settings → API | Public key for client-side |
| Service Role Key | Settings → API | Private key for server-side (keep secret!) |
| Database Password | Settings → Database | Direct PostgreSQL access |
| Connection String | Settings → Database | For migrations and CLI |

---

## 3. Database Schema Design

### 3.1 Entity Relationship Diagram

```
┌────────────────────────┐
│     discovery_jobs     │ (Parent table)
│────────────────────────│
│ id (PK)                │
│ user_id (FK)           │───────────┐
│ name                   │           │
│ brand_description      │           │
│ reference_profiles[]   │           │ 
│ status                 │           ▼
│ profiles_discovered    │    ┌────────────┐
│ profiles_scored        │    │ auth.users │
│ created_at             │    │ (Supabase) │
│ updated_at             │    └────────────┘
└───────────┬────────────┘
            │
       ┌────┴────┐
       │ 1:1     │ 1:many
       ▼         ▼
┌──────────────────┐  ┌────────────────────┐
│    brand_dna     │  │ discovered_profiles│
│──────────────────│  │────────────────────│
│ id (PK)          │  │ id (PK)            │
│ job_id (FK)      │  │ job_id (FK)        │
│ hashtags[]       │  │ instagram_url      │
│ keywords[]       │  │ username           │
│ embedding_vector │  │ followers          │
│ created_at       │  │ status             │
└──────────────────┘  │ created_at         │
                      └─────────┬──────────┘
                                │
                           ┌────┴────┐
                           │ 1:1     │ 1:1
                           ▼         ▼
                    ┌─────────────┐ ┌─────────────────┐
                    │profile_     │ │ profile_contacts│
                    │scores       │ │─────────────────│
                    │─────────────│ │ id (PK)         │
                    │ id (PK)     │ │ profile_id (FK) │
                    │ profile_id  │ │ email           │
                    │ score       │ │ source          │
                    │ aesthetic_  │ │ created_at      │
                    │   match     │ └─────────────────┘
                    │ engagement_ │
                    │   quality   │
                    │ content_    │
                    │   alignment │
                    │ audience_   │
                    │   fit       │
                    │ reasoning   │
                    │ created_at  │
                    └─────────────┘
```

### 3.2 Data Storage vs Runtime Fetching

Some profile data is stored in the database, while other data is fetched fresh from Apify at scoring time:

| Field | Storage | Source |
|-------|---------|--------|
| `instagram_url`, `username`, `followers` | `discovered_profiles` table | Stored at discovery |
| `bio`, `posts_count`, `engagement_rate`, `recent_posts` | Not stored | Fetched via Apify at scoring time |

**Why not store everything?**
- Profile data changes frequently (followers, engagement)
- Fresh data ensures accurate scoring
- Reduces storage costs
- Avoids stale data issues

**Apify Instagram Profile Scraper** provides these fields:
- `biography` → mapped to `bio`
- `postsCount` → mapped to `posts_count`
- `followersCount` → mapped to `followers`
- `latestPosts` → mapped to `recent_posts` (includes likes, comments, captions)
- `engagement_rate` → calculated as `(avg_likes + avg_comments) / followers * 100`

### 3.3 Relationship Types

| Relationship | Type | Constraint |
|--------------|------|------------|
| discovery_jobs → brand_dna | 1:1 | UNIQUE (job_id) |
| discovery_jobs → discovered_profiles | 1:many | FK with CASCADE |
| discovered_profiles → profile_scores | 1:1 | UNIQUE (profile_id) |
| discovered_profiles → profile_contacts | 1:1 | UNIQUE (profile_id) |

### 3.4 Scoring Dimensions

The `profile_scores` table stores 4 scoring dimensions from the Scorer Agent:

| Dimension | Description | Weight |
|-----------|-------------|--------|
| `aesthetic_match` | Visual style and content alignment | 25% |
| `engagement_quality` | Signs of authentic engagement vs fake followers | 25% |
| `content_alignment` | Topic, values, and messaging alignment | 25% |
| `audience_fit` | Target audience overlap potential | 15% |

The remaining 10% weight comes from embedding similarity calculated separately.

All scores are integers from 0-100, with the final `score` being a weighted average.

---

## 4. SQL Migrations

### 4.1 Migration 001: Initial Schema

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;      -- For AI embeddings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- For UUID generation

-- Create enum types
CREATE TYPE discovery_job_status AS ENUM (
    'pending',
    'analyzing',
    'discovering',
    'scoring',
    'completed',
    'failed'
);

CREATE TYPE profile_status AS ENUM (
    'new',
    'processing',
    'done',
    'skipped'
);

-- Main parent table
CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Child table with 1:1 relationship
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    embedding_vector vector(1536), -- OpenAI embedding dimension
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);

-- Child table with 1:many relationship
CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    followers INTEGER NOT NULL DEFAULT 0,
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, instagram_url)
);

-- Grandchild table (1:1 with discovered_profiles)
CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    aesthetic_match INTEGER CHECK (aesthetic_match >= 0 AND aesthetic_match <= 100),
    engagement_quality INTEGER CHECK (engagement_quality >= 0 AND engagement_quality <= 100),
    content_alignment INTEGER CHECK (content_alignment >= 0 AND content_alignment <= 100),
    audience_fit INTEGER CHECK (audience_fit >= 0 AND audience_fit <= 100),
    reasoning JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

-- Grandchild table (1:1 with discovered_profiles)
CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);
```

### 4.2 Indexes for Performance

```sql
-- Parent table indexes
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);

-- Foreign key indexes (always index FK columns!)
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);

-- Query-specific indexes
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) WHERE email IS NOT NULL;
```

### 4.3 Auto-updating Timestamps and Counts

```sql
-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER trigger_discovery_jobs_updated_at
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-update profiles_discovered count
CREATE OR REPLACE FUNCTION update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = profiles_discovered + 1
        WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = profiles_discovered - 1
        WHERE id = OLD.job_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_discovered
    AFTER INSERT OR DELETE ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_discovered();

-- Function to auto-update profiles_scored count when profile status changes to 'done'
CREATE OR REPLACE FUNCTION update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment when profile changes to 'done'
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE discovery_jobs 
        SET profiles_scored = profiles_scored + 1
        WHERE id = NEW.job_id;
    -- Decrement when profile changes from 'done' to something else
    ELSIF OLD.status = 'done' AND NEW.status != 'done' THEN
        UPDATE discovery_jobs 
        SET profiles_scored = profiles_scored - 1
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_scored
    AFTER UPDATE OF status ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_scored();
```

### 4.4 Convenience Views

```sql
-- Complete profile view with scores and contacts
CREATE VIEW v_complete_profiles AS
SELECT 
    dp.id,
    dp.job_id,
    dp.instagram_url,
    dp.username,
    dp.followers,
    dp.status,
    dp.created_at,
    ps.score,
    ps.aesthetic_match,
    ps.engagement_quality,
    ps.content_alignment,
    ps.audience_fit,
    ps.reasoning,
    pc.email,
    pc.source AS email_source
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

-- Job summary with statistics
CREATE VIEW v_job_summary AS
SELECT 
    dj.id AS job_id,
    dj.user_id,
    dj.name,
    dj.brand_description,
    dj.status,
    dj.profiles_discovered,
    dj.profiles_scored,
    dj.created_at,
    dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    AVG(ps.score)::INTEGER AS avg_score,
    MAX(ps.score) AS max_score,
    COUNT(pc.email) AS profiles_with_email
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id AND pc.email IS NOT NULL
GROUP BY dj.id;
```

### 4.5 Migration 002: Enable Row Level Security

```sql
-- Enable RLS on all tables
ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- discovery_jobs: Direct user_id check
CREATE POLICY "Users can view own discovery_jobs" ON discovery_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own discovery_jobs" ON discovery_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own discovery_jobs" ON discovery_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own discovery_jobs" ON discovery_jobs
    FOR DELETE USING (auth.uid() = user_id);

-- brand_dna: Access via job ownership
CREATE POLICY "Users can access brand_dna for their jobs" ON brand_dna
    FOR ALL USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

-- discovered_profiles: Access via job ownership
CREATE POLICY "Users can access profiles for their jobs" ON discovered_profiles
    FOR ALL USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

-- profile_scores: Access via profile → job ownership
CREATE POLICY "Users can access scores for their profiles" ON profile_scores
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );

-- profile_contacts: Access via profile → job ownership
CREATE POLICY "Users can access contacts for their profiles" ON profile_contacts
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );
```

### 4.6 Migration 003: Enable Realtime

```sql
-- Add tables to realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

-- Verify with:
-- SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

---

## 5. Common Query Patterns

### 5.1 Insert with Returning

```sql
INSERT INTO discovery_jobs (brand_description, reference_profiles, status)
VALUES ($1, $2, 'pending')
RETURNING *;
```

### 5.2 Upsert (Insert or Update)

```sql
INSERT INTO profile_scores (profile_id, score, reasoning)
VALUES ($1, $2, $3)
ON CONFLICT (profile_id) 
DO UPDATE SET
    score = EXCLUDED.score,
    reasoning = EXCLUDED.reasoning
RETURNING *;
```

### 5.3 Join Query

```sql
SELECT 
    dp.*,
    ps.score,
    ps.reasoning,
    pc.email
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
WHERE dp.job_id = $1
  AND dp.status = 'done'
ORDER BY ps.score DESC NULLS LAST;
```

### 5.4 Aggregation

```sql
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'done') AS done_count,
    AVG(ps.score)::INTEGER AS avg_score
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
WHERE dp.job_id = $1;
```

### 5.5 Batch Processing (FOR UPDATE SKIP LOCKED)

```sql
-- Get next batch of profiles to process (locks rows)
SELECT * FROM discovered_profiles
WHERE job_id = $1 AND status = 'new'
ORDER BY followers DESC
LIMIT 10
FOR UPDATE SKIP LOCKED;
```

---

## 6. Seed Data

### 6.1 Sample Seed File

```sql
-- seed.sql
INSERT INTO discovery_jobs (id, brand_description, reference_profiles, status)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Sustainable fashion brand focused on minimalist aesthetics.',
    ARRAY['https://instagram.com/everlane', 'https://instagram.com/reformation'],
    'completed'
);

INSERT INTO brand_dna (job_id, hashtags, keywords)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    ARRAY['#sustainablefashion', '#slowfashion', '#ethicalfashion'],
    ARRAY['sustainable', 'minimalist', 'ethical', 'organic']
);

INSERT INTO discovered_profiles (id, job_id, instagram_url, username, followers, status)
VALUES (
    'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/the_sustainable_closet',
    'the_sustainable_closet',
    45200,
    'done'
);

INSERT INTO profile_scores (profile_id, score, aesthetic_match, engagement_quality, content_alignment, audience_fit, reasoning)
VALUES (
    'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    92, 95, 88, 93, 91,
    '{"summary": "Excellent match. Strong alignment with sustainable fashion values.", "recommendation": "Highly recommended for partnership outreach."}'::jsonb
);

INSERT INTO profile_contacts (profile_id, email, source)
VALUES (
    'aaaa1111-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'hello@sustainablecloset.com',
    'bio'
);
```

---

## 7. Maintenance & Cleanup

### 7.1 Delete Old Data

```sql
-- Delete jobs older than 30 days
DELETE FROM discovery_jobs
WHERE created_at < NOW() - INTERVAL '30 days';
```

### 7.2 Reset Job for Reprocessing

```sql
-- Delete scores and contacts
DELETE FROM profile_scores WHERE profile_id IN (
    SELECT id FROM discovered_profiles WHERE job_id = $1
);
DELETE FROM profile_contacts WHERE profile_id IN (
    SELECT id FROM discovered_profiles WHERE job_id = $1
);

-- Reset profile statuses
UPDATE discovered_profiles SET status = 'new' WHERE job_id = $1;

-- Reset job status
UPDATE discovery_jobs SET status = 'pending' WHERE id = $1;
```

### 7.3 Cleanup Old Jobs (SQL)

```sql
-- Keep only N most recent jobs per user, delete the rest
WITH ranked_jobs AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) as rn
    FROM discovery_jobs
)
DELETE FROM discovery_jobs
WHERE id IN (
    SELECT id FROM ranked_jobs WHERE rn > 10  -- Keep 10 most recent per user
);
```

---

## 8. Data Flow & Workflow

This section describes how data flows through the database during a discovery session.

### 8.1 Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER ACTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Sign Up/Login → Create Session → Add Brand Info → Start Discovery          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: BRAND ANALYSIS                                                     │
│  ─────────────────────────────────────────────────────────────────────────  │
│  1. INSERT discovery_jobs (status: 'pending' → 'analyzing')                  │
│  2. Brand Analyzer Agent extracts brand DNA                                  │
│  3. INSERT brand_dna (hashtags, keywords, embedding_vector)                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: PROFILE DISCOVERY                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  1. UPDATE discovery_jobs (status: 'discovering')                            │
│  2. Discovery Agent finds similar Instagram profiles                         │
│  3. INSERT discovered_profiles (status: 'new')                               │
│  4. TRIGGER: profiles_discovered counter increments                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: SCORING (per profile)                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  1. UPDATE discovery_jobs (status: 'scoring')                                │
│  2. UPDATE discovered_profiles (status: 'processing')                        │
│  3. Scorer Agent calculates match score                                      │
│  4. INSERT profile_scores (score, reasoning)                                 │
│  5. INSERT profile_contacts (email if found)                                 │
│  6. UPDATE discovered_profiles (status: 'done')                              │
│  7. TRIGGER: profiles_scored counter increments                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: COMPLETE                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  1. UPDATE discovery_jobs (status: 'completed')                              │
│  2. Dashboard displays ranked results with scores and contacts               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Status State Machines

**discovery_jobs.status**

```
┌─────────┐    ┌───────────┐    ┌─────────────┐    ┌─────────┐    ┌───────────┐
│ pending │───▶│ analyzing │───▶│ discovering │───▶│ scoring │───▶│ completed │
└─────────┘    └───────────┘    └─────────────┘    └─────────┘    └───────────┘
                    │                  │                │
                    └──────────────────┴────────────────┴──────▶ ┌────────┐
                                                                 │ failed │
                                                                 └────────┘
```

**discovered_profiles.status**

```
┌─────┐    ┌────────────┐    ┌──────┐
│ new │───▶│ processing │───▶│ done │
└─────┘    └────────────┘    └──────┘
                │
                └───────────────────▶ ┌─────────┐
                                      │ skipped │
                                      └─────────┘
```

### 8.3 Database Operations by Phase

| Phase | Table | Operation | Key Fields |
|-------|-------|-----------|------------|
| 1 | `discovery_jobs` | INSERT | user_id, brand_description, reference_profiles |
| 1 | `discovery_jobs` | UPDATE | status → 'analyzing' |
| 1 | `brand_dna` | INSERT | job_id, hashtags, keywords, embedding_vector |
| 2 | `discovery_jobs` | UPDATE | status → 'discovering' |
| 2 | `discovered_profiles` | INSERT (batch) | job_id, instagram_url, username, followers |
| 3 | `discovery_jobs` | UPDATE | status → 'scoring' |
| 3 | `discovered_profiles` | UPDATE | status → 'processing' |
| 3 | `profile_scores` | INSERT | profile_id, score, aesthetic_match, engagement_quality, content_alignment, audience_fit, reasoning |
| 3 | `profile_contacts` | INSERT | profile_id, email, source |
| 3 | `discovered_profiles` | UPDATE | status → 'done' |
| 4 | `discovery_jobs` | UPDATE | status → 'completed' |

### 8.4 Trigger-Updated Counters

The `discovery_jobs` table maintains denormalized counts for dashboard performance:

| Counter | Trigger Event | Purpose |
|---------|---------------|---------|
| `profiles_discovered` | INSERT/DELETE on `discovered_profiles` | Shows discovery progress |
| `profiles_scored` | UPDATE status → 'done' on `discovered_profiles` | Shows scoring progress |

**Dashboard Display Example:**
```
Discovery Progress: Discovered 47 profiles | Scored 23/47 (49%)
```

### 8.5 Real-time Event Flow

With realtime enabled, the frontend receives live database changes:

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Database        │     │  Supabase Realtime  │     │  Frontend        │
│  (PostgreSQL)    │────▶│  (WebSocket)        │────▶│  (React)         │
└──────────────────┘     └─────────────────────┘     └──────────────────┘

Events Published:
  • discovered_profiles INSERT  → New profile card appears
  • discovered_profiles UPDATE  → Profile status/score updates
  • profile_scores INSERT       → Score badge appears on card
  • discovery_jobs UPDATE       → Progress bar updates
```

### 8.6 Data Isolation Chain

All data access flows through the user ownership chain enforced by RLS:

```
auth.users.id (JWT auth.uid())
     │
     ▼
discovery_jobs.user_id = auth.uid()
     │
     ├──▶ brand_dna.job_id
     │
     └──▶ discovered_profiles.job_id
              │
              ├──▶ profile_scores.profile_id
              │
              └──▶ profile_contacts.profile_id
```

**Rule:** Users can ONLY access data where the foreign key chain traces back to their `user_id`.

---

## 9. Integration: Backend (Python/FastAPI)

### 8.1 Python Client Setup

```python
# backend/app/db/supabase.py
from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """Create and return Supabase client"""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be configured")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Global client instance
_supabase: Client = None

def get_db() -> Client:
    """Get database client (for dependency injection)"""
    global _supabase
    if _supabase is None:
        _supabase = get_supabase_client()
    return _supabase
```

### 8.2 FastAPI Dependency Injection

```python
from fastapi import APIRouter, Depends
from supabase import Client
from app.db.supabase import get_db

router = APIRouter()

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: Client = Depends(get_db)):
    result = db.table("discovery_jobs").select("*").eq("id", job_id).single().execute()
    return result.data
```

### 8.3 CRUD Operations

```python
# CREATE
result = db.table("discovery_jobs").insert({
    "brand_description": "My brand",
    "reference_profiles": ["https://instagram.com/example"],
    "status": "pending",
}).execute()
job = result.data[0]

# READ with joins
result = db.table("discovered_profiles").select(
    "*, profile_scores(*), profile_contacts(*)"
).eq("job_id", job_id).execute()

# UPDATE
db.table("discovery_jobs").update({
    "status": "completed"
}).eq("id", job_id).execute()

# DELETE
db.table("discovery_jobs").delete().eq("id", job_id).execute()

# UPSERT (insert or update)
db.table("profile_scores").upsert({
    "profile_id": profile_id,
    "score": 85,
    "reasoning": {"summary": "Good match"},
}).execute()
```

### 8.4 Requirements

```txt
# backend/requirements.txt
supabase>=2.0.0
python-dotenv>=1.0.0
```

### 8.5 Environment Variables

```bash
# backend/.env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# Use service role key for backend operations
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 10. Integration: Frontend (React/TypeScript)

### 10.1 TypeScript Types

```typescript
// frontend/src/types/database.types.ts

export type DiscoveryJobStatus =
  | 'pending'
  | 'analyzing'
  | 'discovering'
  | 'scoring'
  | 'completed'
  | 'failed';

export type ProfileStatus = 'new' | 'processing' | 'done' | 'skipped';

export interface DiscoveryJob {
  id: string;
  user_id: string | null;
  name: string | null;
  brand_description: string;
  reference_profiles: string[];
  status: DiscoveryJobStatus;
  profiles_discovered: number;
  profiles_scored: number;
  created_at: string;
  updated_at: string;
}

export interface DiscoveredProfile {
  id: string;
  job_id: string;
  instagram_url: string;
  username: string;
  followers: number;
  status: ProfileStatus;
  created_at: string;
}

export interface ProfileScore {
  id: string;
  profile_id: string;
  score: number;
  aesthetic_match: number | null;
  engagement_quality: number | null;
  content_alignment: number | null;
  audience_fit: number | null;
  reasoning: {
    summary: string;
    recommendation: string;
  };
  created_at: string;
}

export interface ProfileContact {
  id: string;
  profile_id: string;
  email: string | null;
  source: string | null;
  created_at: string;
}

// Combined type for complete profile with score and contact
export interface CompleteProfile extends DiscoveredProfile {
  profile_scores: ProfileScore | null;
  profile_contacts: ProfileContact | null;
}
```

### 10.2 Supabase Client Setup

```typescript
// frontend/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### 10.3 CRUD Operations

```typescript
import { supabase } from '../lib/supabase'

// CREATE
const { data, error } = await supabase
  .from('discovery_jobs')
  .insert({
    brand_description: 'My brand description',
    reference_profiles: ['https://instagram.com/example'],
    user_id: user.id,
  })
  .select()
  .single()

// READ (single)
const { data: job } = await supabase
  .from('discovery_jobs')
  .select('*')
  .eq('id', jobId)
  .single()

// READ (with joins)
const { data: profiles } = await supabase
  .from('discovered_profiles')
  .select(`
    *,
    profile_scores (*),
    profile_contacts (*)
  `)
  .eq('job_id', jobId)
  .order('created_at', { ascending: false })

// UPDATE
await supabase
  .from('discovery_jobs')
  .update({ status: 'completed' })
  .eq('id', jobId)

// DELETE
await supabase
  .from('discovery_jobs')
  .delete()
  .eq('id', jobId)
```

### 10.4 Real-time Subscriptions

```typescript
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { DiscoveredProfile } from '../types/database.types'

function useRealtimeProfiles(jobId: string) {
  const [profiles, setProfiles] = useState<DiscoveredProfile[]>([])

  useEffect(() => {
    // Initial fetch
    const fetchProfiles = async () => {
      const { data } = await supabase
        .from('discovered_profiles')
        .select('*')
        .eq('job_id', jobId)
      if (data) setProfiles(data)
    }
    fetchProfiles()

    // Subscribe to changes
    const channel = supabase
      .channel(`profiles-${jobId}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'discovered_profiles',
          filter: `job_id=eq.${jobId}`,
        },
        (payload) => {
          if (payload.eventType === 'INSERT') {
            setProfiles((prev) => [...prev, payload.new as DiscoveredProfile])
          } else if (payload.eventType === 'UPDATE') {
            setProfiles((prev) =>
              prev.map((p) =>
                p.id === payload.new.id ? (payload.new as DiscoveredProfile) : p
              )
            )
          } else if (payload.eventType === 'DELETE') {
            setProfiles((prev) => prev.filter((p) => p.id !== payload.old.id))
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [jobId])

  return profiles
}
```

### 10.5 Using Views

```typescript
// Query a view just like a table
const { data: completeProfiles } = await supabase
  .from('v_complete_profiles')
  .select('*')
  .eq('job_id', jobId)
  .gte('score', 50)
  .order('score', { ascending: false })
```

### 10.6 Environment Variables

```bash
# frontend/.env
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 10.7 Auto-generate Types (Recommended)

```bash
# Install Supabase CLI
npm install -g supabase

# Generate types from your project
npx supabase gen types typescript --project-id YOUR_PROJECT_ID > src/types/database.types.ts
```

---

## Quick Reference

### Supabase CLI Commands

```bash
# Login
supabase login

# Link to project
supabase link --project-ref YOUR_PROJECT_REF

# Run migrations
supabase db push

# Generate types
supabase gen types typescript --project-id YOUR_PROJECT_ID > types.ts

# Local development
supabase start
supabase stop
supabase db reset  # Reapply all migrations
```

### Common Gotchas

1. **Always index foreign key columns** - PostgreSQL doesn't auto-index FKs
2. **Use CASCADE on delete** - Prevents orphaned records
3. **Enable RLS before production** - Data is public without it!
4. **Add tables to realtime publication** - Required for subscriptions
5. **Use service role key server-side** - Anon key is limited by RLS

---

*Last updated: January 2026*
