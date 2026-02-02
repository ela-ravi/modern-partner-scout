# PartnerScout AI - Database Implementation Step by Step

> A beginner-friendly, step-by-step guide for implementing the PartnerScout AI database on Supabase. Each step is small and actionable—acknowledge completion before moving to the next step.

**See also:** [Database_Implementation_Jira_Plan.md](Database_Implementation_Jira_Plan.md) (Jira EPIC/FEATURE/STORY/TASK/SUBTASK) · [Database_Implementation_Index.md](Database_Implementation_Index.md) (plan index and migration map)

---

## Table of Contents

1. [How This Works](#how-this-works)
2. [Step 1: Create Supabase Account and Project](#step-1-create-supabase-account-and-project)
3. [Step 2: Enable Required Extensions](#step-2-enable-required-extensions)
4. [Step 3: Create Enum Types](#step-3-create-enum-types)
5. [Step 4: Create discovery_jobs Table](#step-4-create-discovery_jobs-table)
6. [Step 5: Create brand_dna Table](#step-5-create-brand_dna-table)
7. [Step 6: Create discovered_profiles Table](#step-6-create-discovered_profiles-table)
8. [Step 7: Create profile_scores and profile_contacts Tables](#step-7-create-profile_scores-and-profile_contacts-tables)
9. [Step 8: Add Indexes](#step-8-add-indexes)
10. [Step 9: Add Triggers](#step-9-add-triggers)
11. [Step 10: Enable Row Level Security](#step-10-enable-row-level-security)
12. [Step 11: Enable Realtime](#step-11-enable-realtime)
13. [Summary](#summary)
14. [Next Phase](#next-phase)

---

## How This Works

- **One step at a time**: Complete each step, verify it works, then acknowledge before moving on.
- **Beginner-friendly**: Each step includes "What", "Why", and "How".
- **No code implementation until permission**: This document is a guide only. Do not run any implementation until you give permission.

This plan covers **Phase 1: Database** only. We will not proceed to backend, APIs, n8n, or frontend until you confirm the database phase is complete.

---

## Step 1: Create Supabase Account and Project

**What**: Sign up for Supabase and create your first project.

**Why**: Supabase hosts your PostgreSQL database. Every PartnerScout user has their own data isolated by `user_id`—Supabase provides the database, auth, and realtime features.

**How**:

1. Go to [supabase.com](https://supabase.com) and click **Start your project**
2. Sign in with GitHub, Google, or email
3. Click **New Project**
4. Fill in:
   - **Name**: `partner-scout` (or any name)
   - **Database Password**: Choose a strong password—**save it** (you need it for direct DB access)
   - **Region**: Pick one closest to you
5. Click **Create new project** (takes ~2 minutes)
6. Once ready, go to **Settings** (gear icon) → **API** and note:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public** key
   - **service_role** key (keep secret—for backend only)

**Verification**: You should see the Supabase dashboard with a project. The **Table Editor** will show "No tables yet".

**Acknowledge when done** → Proceed to Step 2.

---

## Step 2: Enable Required Extensions

**What**: Enable `vector` (for AI embeddings) and `uuid-ossp` (for UUID primary keys).

**Why**: PartnerScout stores brand "DNA" as a 1536-dimensional vector (OpenAI embeddings). UUIDs are used for all primary keys.

**How**:

1. In Supabase dashboard: **SQL Editor** (left sidebar)
2. Click **New query**
3. Paste and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

4. Click **Run** (or Ctrl+Enter)
5. You should see "Success. No rows returned"

**Verification**: In **Database** → **Extensions**, you should see `vector` and `uuid-ossp` listed.

**Acknowledge when done** → Proceed to Step 3.

---

## Step 3: Create Enum Types

**What**: Define the allowed values for `status` columns.

**Why**: Enums prevent invalid values (e.g., `"completed"` typo) and make queries clearer.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
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
```

3. **Run**

**Verification**: **Database** → **Types** should list `discovery_job_status` and `profile_status`.

**Acknowledge when done** → Proceed to Step 4.

---

## Step 4: Create discovery_jobs Table

**What**: Main parent table—each row = one discovery session.

**Why**: Users create "jobs" (sessions) with brand info. All profiles and scores belong to a job.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
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
```

3. **Run**

**Verification**: **Table Editor** → you should see `discovery_jobs` with columns: id, user_id, name, brand_description, reference_profiles, status, profiles_discovered, profiles_scored, created_at, updated_at.

**Acknowledge when done** → Proceed to Step 5.

---

## Step 5: Create brand_dna Table

**What**: Stores extracted brand identity (hashtags, keywords, embedding) per job.

**Why**: One-to-one with a job. The Brand Analyzer agent fills this after analyzing reference profiles.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    embedding_vector vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);
```

3. **Run**

**Verification**: `brand_dna` appears in **Table Editor**. It has `job_id` as a foreign key to `discovery_jobs`.

**Acknowledge when done** → Proceed to Step 6.

---

## Step 6: Create discovered_profiles Table

**What**: Stores Instagram profiles found during discovery—one row per profile per job.

**Why**: Profiles are inserted when the Discovery Agent runs. Later the Scorer Agent adds scores and contacts.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    followers INTEGER NOT NULL DEFAULT 0,
    following INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business BOOLEAN,
    external_url TEXT,
    business_email TEXT,
    business_category TEXT,
    following_ratio DECIMAL(5,2),
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, instagram_url)
);
```

3. **Run**

**Verification**: `discovered_profiles` exists with `job_id` FK to `discovery_jobs`.

**Acknowledge when done** → Proceed to Step 7.

---

## Step 7: Create profile_scores and profile_contacts Tables

**What**: Child tables for each discovered profile—scores (0–100) and contact email.

**Why**: One-to-one with each profile. Scorer Agent inserts scores and optional contact.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100),
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),
    reasoning JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);
```

3. **Run**

**Verification**: Both tables appear. Each has `profile_id` FK to `discovered_profiles`.

**Acknowledge when done** → Proceed to Step 8.

---

## Step 8: Add Indexes

**What**: Indexes speed up queries on foreign keys and common filters.

**Why**: Without indexes, listing jobs by user or profiles by job would scan entire tables.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers DESC);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);
```

3. **Run**

**Verification**: **Database** → **Tables** → select any table → **Indexes** tab shows the new indexes.

**Acknowledge when done** → Proceed to Step 9.

---

## Step 9: Add Triggers

**What**: Automatically update `updated_at` and maintain `profiles_discovered` / `profiles_scored`.

**Why**: Keeps counters correct without manual logic. Dashboard shows "Discovered 47 | Scored 23" in real time.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to discovery_jobs
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
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE discovery_jobs 
        SET profiles_scored = profiles_scored + 1
        WHERE id = NEW.job_id;
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

3. **Run**

**Verification**: **Database** → **Functions** shows the new functions. **Table Editor** → any table → **Triggers** tab shows the triggers.

**Acknowledge when done** → Proceed to Step 10.

---

## Step 10: Enable Row Level Security

**What**: RLS ensures users only see their own data.

**Why**: Without RLS, any authenticated user could read all jobs. RLS enforces `user_id = auth.uid()`.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

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

3. **Run**

**Verification**: **Authentication** → **Policies** (or **Database** → **Tables** → select table → **RLS** tab) shows RLS enabled and policies listed.

**Note for backend/n8n**: The backend and n8n use the **service_role** key, which bypasses RLS. Users accessing via the frontend (anon key) are protected by these policies.

**Acknowledge when done** → Proceed to Step 11.

---

## Step 11: Enable Realtime

**What**: Add tables to the Realtime publication so the frontend can subscribe to INSERT/UPDATE/DELETE.

**Why**: Dashboard updates live as profiles are discovered and scored—no manual refresh.

**How**:

1. **SQL Editor** → **New query**
2. Paste and run:

```sql
-- Add tables to realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;
```

3. **Run**

**Verification**: Run this query to verify tables are in the realtime publication:

```sql
SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
```

You should see `discovery_jobs`, `discovered_profiles`, `profile_scores`, and `profile_contacts` in the results.

**Acknowledge when done** → Database phase complete.

---

## Summary

| Step | Task |
|------|------|
| 1 | Create Supabase account and project |
| 2 | Enable extensions (vector, uuid-ossp) |
| 3 | Create enum types (discovery_job_status, profile_status) |
| 4 | Create discovery_jobs table |
| 5 | Create brand_dna table |
| 6 | Create discovered_profiles table |
| 7 | Create profile_scores and profile_contacts tables |
| 8 | Add indexes |
| 9 | Add triggers (updated_at, profiles_discovered, profiles_scored) |
| 10 | Enable RLS and create policies |
| 11 | Enable Realtime |

### Database Schema Overview

```
auth.users (Supabase Auth)
    └── discovery_jobs (1:many, user_id FK)
            ├── brand_dna (1:1, job_id FK)
            └── discovered_profiles (1:many, job_id FK)
                    ├── profile_scores (1:1, profile_id FK)
                    └── profile_contacts (1:1, profile_id FK)
```

---

## Next Phase

Once you confirm the database is complete, we will proceed to **Phase 2: Backend (FastAPI)**. We will not start the backend until you acknowledge.

---

*Last updated: February 2026*
