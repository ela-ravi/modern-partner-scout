# PartnerScout AI - Supabase Database Setup Guide

> **Purpose:** Step-by-step guide for team members to set up Supabase from scratch, create all database tables, apply migrations, seed test data, and configure credentials. Follow this guide after cloning the repository.

---

## Table of Contents

1. [Create Supabase Project](#1-create-supabase-project)
2. [Collect Credentials](#2-collect-credentials)
3. [Configure Environment Files](#3-configure-environment-files)
4. [Enable Required Extensions](#4-enable-required-extensions)
5. [Run Migrations](#5-run-migrations)
6. [Seed Test Data (Optional)](#6-seed-test-data-optional)
7. [Verify Setup](#7-verify-setup)
8. [Start the Application](#8-start-the-application)
9. [Database Schema Reference](#9-database-schema-reference)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up or log in
2. Click **"New Project"**
3. Fill in the project details:
   - **Organization:** Select or create one
   - **Name:** `partnerscout-ai` (or your preferred name)
   - **Database Password:** Generate a strong password and **save it securely** (you'll need it later)
   - **Region:** Choose the closest region to your team
   - **Pricing Plan:** Free tier is sufficient for development
4. Click **"Create new project"** and wait ~2 minutes for provisioning

---

## 2. Collect Credentials

Once your project is ready, you need 4 credentials from the Supabase Dashboard:

### 2.1 API Keys

Go to **Project Settings** > **API** (left sidebar):

| Credential | Where to Find | Description |
|------------|---------------|-------------|
| **Project URL** | Project URL section | `https://xxxxx.supabase.co` |
| **Anon Key** | Project API Keys > `anon` `public` | Public key for client-side (safe to expose) |
| **Service Role Key** | Project API Keys > `service_role` `secret` | **Private key** for server-side (**never expose!**) |

### 2.2 JWT Secret

Go to **Project Settings** > **API** > scroll down to **JWT Settings**:

| Credential | Where to Find |
|------------|---------------|
| **JWT Secret** | JWT Secret field | Used for token verification in the backend |

> **Security:** Never commit actual keys to version control. Only `.env.example` files should be committed.

---

## 3. Configure Environment Files

### 3.1 Backend Configuration

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` and fill in your Supabase credentials:

```env
# =============================================================================
# Supabase (Required)
# =============================================================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-anon-key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret-from-dashboard

# =============================================================================
# N8N Orchestration (for workflow triggering)
# =============================================================================
N8N_SERVICE_KEY=test-service-key-12345

# =============================================================================
# LLM Provider (choose one)
# =============================================================================
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# =============================================================================
# Apify (Instagram Scraping)
# =============================================================================
APIFY_API_KEY=apify_api_...
```

### 3.2 Frontend Configuration

```bash
cd frontend
cp .env.example .env
```

Edit `frontend/.env`:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-anon-key

# Backend API URL
VITE_API_URL=http://localhost:8000
```

> **Note:** The frontend uses the **Anon Key** (public), not the Service Role Key.

---

## 4. Enable Required Extensions

Open the **SQL Editor** in your Supabase Dashboard (left sidebar > SQL Editor).

Click **"New query"** and run the following:

```sql
-- ============================================================================
-- Migration 000: Enable Required Extensions
-- ============================================================================

-- Enable pgvector extension for AI embedding storage and similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation (usually enabled by default in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extensions are enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'pgvector extension is not installed';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        RAISE EXCEPTION 'uuid-ossp extension is not installed';
    END IF;

    RAISE NOTICE 'All required extensions are enabled successfully!';
END $$;
```

You should see: `All required extensions are enabled successfully!`

> **Alternative:** You can also enable pgvector from **Database** > **Extensions** > search "vector" > toggle ON.

---

## 5. Run Migrations

Run each migration **in order** in the Supabase SQL Editor. Create a new query for each migration, paste the SQL, and click **"Run"**.

### Migration 1: Create Tables (001_initial_schema.sql)

This creates all 5 core tables, indexes, triggers, and views.

```sql
-- ============================================================================
-- Migration 001: Initial Schema
-- Creates: discovery_jobs, brand_dna, discovered_profiles, profile_scores, profile_contacts
-- Plus: indexes, triggers, views (v_complete_profiles, v_job_summary)
-- ============================================================================

-- ENUM TYPES
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

-- TABLE: discovery_jobs (parent table)
CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    follower_range_min INTEGER DEFAULT 10000,
    follower_range_max INTEGER DEFAULT 500000,
    discovery_limit INTEGER DEFAULT 50,
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- TABLE: brand_dna (1:1 with discovery_jobs)
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    visual_themes TEXT[] DEFAULT '{}',
    content_pillars TEXT[] DEFAULT '{}',
    target_audience_description TEXT,
    embedding_vector vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);

-- TABLE: discovered_profiles (1:many with discovery_jobs)
CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    following_ratio DECIMAL(5,2),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business_account BOOLEAN,
    external_url TEXT,
    business_email TEXT,
    business_category TEXT,
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, username)
);

-- TABLE: profile_scores (1:1 with discovered_profiles)
CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100),
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),
    final_score INTEGER NOT NULL CHECK (final_score >= 0 AND final_score <= 100),
    recommendation TEXT CHECK (recommendation IN ('highly_recommended', 'recommended', 'consider', 'not_recommended')),
    reasoning JSONB NOT NULL DEFAULT '{}',
    is_fake_suspected BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

-- TABLE: profile_contacts (1:1 with discovered_profiles)
CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    email_source TEXT,
    phone TEXT,
    website TEXT,
    other_contacts JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);

-- INDEXES
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers_count DESC);
CREATE INDEX idx_discovered_profiles_username ON discovered_profiles(username);
CREATE INDEX idx_profile_scores_final_score ON profile_scores(final_score DESC);
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) WHERE email IS NOT NULL;

-- TRIGGER: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_discovery_jobs_updated_at
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- TRIGGER: Auto-increment profiles_discovered
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

-- TRIGGER: Auto-increment profiles_scored
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

-- VIEW: v_complete_profiles (profiles with scores and contacts)
CREATE VIEW v_complete_profiles AS
SELECT
    dp.id, dp.job_id, dp.instagram_url, dp.username,
    dp.full_name, dp.profile_picture_url, dp.bio,
    dp.followers_count, dp.following_count, dp.posts_count,
    dp.engagement_rate, dp.following_ratio,
    dp.is_verified, dp.is_business_account,
    dp.external_url, dp.business_email, dp.business_category,
    dp.status, dp.created_at,
    ps.final_score, ps.visual_aesthetic_match, ps.content_theme_alignment,
    ps.engagement_rate_score, ps.follower_quality,
    ps.business_indicators, ps.activity_recency,
    ps.recommendation, ps.reasoning, ps.is_fake_suspected,
    pc.email AS contact_email, pc.email_source,
    pc.phone AS contact_phone, pc.website AS contact_website
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

-- VIEW: v_job_summary (aggregated job statistics)
CREATE VIEW v_job_summary AS
SELECT
    dj.id AS job_id, dj.user_id, dj.name, dj.brand_description,
    dj.status, dj.profiles_discovered, dj.profiles_scored,
    dj.created_at, dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    AVG(ps.final_score)::INTEGER AS avg_score,
    MAX(ps.final_score) AS max_score,
    MIN(ps.final_score) AS min_score,
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

-- VERIFICATION
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('discovery_jobs', 'brand_dna', 'discovered_profiles', 'profile_scores', 'profile_contacts');

    IF table_count != 5 THEN
        RAISE EXCEPTION 'Expected 5 tables, found %', table_count;
    END IF;

    RAISE NOTICE 'Migration 001 complete! All 5 tables created successfully.';
END $$;
```

**Expected output:** `Migration 001 complete! All 5 tables created successfully.`

---

### Migration 2: Enable Row Level Security (002_enable_rls.sql)

```sql
-- ============================================================================
-- Migration 002: Enable RLS on all tables
-- ============================================================================

ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- discovery_jobs: Users can only access their own jobs
CREATE POLICY "Users can view own discovery_jobs" ON discovery_jobs
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own discovery_jobs" ON discovery_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own discovery_jobs" ON discovery_jobs
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own discovery_jobs" ON discovery_jobs
    FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Service role can access all discovery_jobs" ON discovery_jobs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- brand_dna: Access via job ownership
CREATE POLICY "Users can access brand_dna for their jobs" ON brand_dna
    FOR ALL USING (job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid()));
CREATE POLICY "Service role can access all brand_dna" ON brand_dna
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- discovered_profiles: Access via job ownership
CREATE POLICY "Users can access profiles for their jobs" ON discovered_profiles
    FOR ALL USING (job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid()));
CREATE POLICY "Service role can access all discovered_profiles" ON discovered_profiles
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- profile_scores: Access via profile -> job ownership
CREATE POLICY "Users can access scores for their profiles" ON profile_scores
    FOR ALL USING (profile_id IN (
        SELECT id FROM discovered_profiles
        WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    ));
CREATE POLICY "Service role can access all profile_scores" ON profile_scores
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- profile_contacts: Access via profile -> job ownership
CREATE POLICY "Users can access contacts for their profiles" ON profile_contacts
    FOR ALL USING (profile_id IN (
        SELECT id FROM discovered_profiles
        WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    ));
CREATE POLICY "Service role can access all profile_contacts" ON profile_contacts
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- VERIFICATION
DO $$
DECLARE
    rls_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO rls_count
    FROM pg_tables
    WHERE schemaname = 'public'
    AND tablename IN ('discovery_jobs', 'brand_dna', 'discovered_profiles', 'profile_scores', 'profile_contacts')
    AND rowsecurity = true;

    IF rls_count != 5 THEN
        RAISE EXCEPTION 'Expected RLS enabled on 5 tables, found %', rls_count;
    END IF;

    RAISE NOTICE 'Migration 002 complete! RLS enabled on all 5 tables.';
END $$;
```

**Expected output:** `Migration 002 complete! RLS enabled on all 5 tables.`

---

### Migration 3: Enable Realtime (003_enable_realtime.sql)

```sql
-- ============================================================================
-- Migration 003: Enable Supabase Realtime
-- ============================================================================

ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

DO $$
BEGIN
    RAISE NOTICE 'Migration 003 complete! Realtime enabled for all tables.';
END $$;
```

---

### Migration 4: Job Creation Enhancements (004_job_creation_enhancements.sql)

```sql
-- ============================================================================
-- Migration 004: Add keywords, hashtags, min_score_threshold to discovery_jobs
-- ============================================================================

ALTER TABLE discovery_jobs ADD COLUMN IF NOT EXISTS keywords TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE discovery_jobs ADD COLUMN IF NOT EXISTS hashtags TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE discovery_jobs ADD COLUMN IF NOT EXISTS min_score_threshold INTEGER NOT NULL DEFAULT 50
    CHECK (min_score_threshold >= 0 AND min_score_threshold <= 100);

-- Recreate v_job_summary with new fields
DROP VIEW IF EXISTS v_job_summary;
CREATE VIEW v_job_summary AS
SELECT
    dj.id AS job_id, dj.user_id, dj.name, dj.brand_description,
    dj.keywords, dj.hashtags, dj.min_score_threshold,
    dj.follower_range_min, dj.follower_range_max, dj.discovery_limit,
    dj.status, dj.profiles_discovered, dj.profiles_scored,
    dj.error_message, dj.created_at, dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    AVG(ps.final_score)::INTEGER AS avg_score,
    MAX(ps.final_score) AS max_score,
    MIN(ps.final_score) AS min_score,
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email,
    COUNT(ps.final_score) FILTER (WHERE ps.final_score >= 80) AS high_score_count
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

DO $$
BEGIN
    RAISE NOTICE 'Migration 004 complete! Added keywords, hashtags, min_score_threshold.';
END $$;
```

---

### Migration 5: Add Target Country (005_add_target_country.sql)

```sql
-- ============================================================================
-- Migration 005: Add target_country to discovery_jobs
-- ============================================================================

ALTER TABLE discovery_jobs ADD COLUMN IF NOT EXISTS target_country TEXT;

-- Recreate v_job_summary with target_country
DROP VIEW IF EXISTS v_job_summary;
CREATE VIEW v_job_summary AS
SELECT
    dj.id AS job_id, dj.user_id, dj.name, dj.brand_description,
    dj.keywords, dj.hashtags, dj.min_score_threshold, dj.target_country,
    dj.follower_range_min, dj.follower_range_max, dj.discovery_limit,
    dj.status, dj.profiles_discovered, dj.profiles_scored,
    dj.error_message, dj.created_at, dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    AVG(ps.final_score)::INTEGER AS avg_score,
    MAX(ps.final_score) AS max_score,
    MIN(ps.final_score) AS min_score,
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email,
    COUNT(ps.final_score) FILTER (WHERE ps.final_score >= 80) AS high_score_count
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

DO $$
BEGIN
    RAISE NOTICE 'Migration 005 complete! Added target_country column.';
END $$;
```

---

### Migration 6: Add Bookmarks (006_add_bookmarks.sql)

```sql
-- ============================================================================
-- Migration 006: Add bookmark support to discovered_profiles
-- ============================================================================

ALTER TABLE discovered_profiles
ADD COLUMN IF NOT EXISTS is_bookmarked BOOLEAN NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_discovered_profiles_bookmarked
ON discovered_profiles(is_bookmarked) WHERE is_bookmarked = true;

-- Recreate v_complete_profiles with is_bookmarked
DROP VIEW IF EXISTS v_complete_profiles;
CREATE VIEW v_complete_profiles AS
SELECT
    dp.id, dp.job_id, dp.instagram_url, dp.username,
    dp.full_name, dp.profile_picture_url, dp.bio,
    dp.followers_count, dp.following_count, dp.posts_count,
    dp.engagement_rate, dp.following_ratio,
    dp.is_verified, dp.is_business_account,
    dp.external_url, dp.business_email, dp.business_category,
    dp.status, dp.is_bookmarked, dp.created_at,
    ps.final_score, ps.visual_aesthetic_match, ps.content_theme_alignment,
    ps.engagement_rate_score, ps.follower_quality,
    ps.business_indicators, ps.activity_recency,
    ps.recommendation, ps.reasoning, ps.is_fake_suspected,
    pc.email AS contact_email, pc.email_source,
    pc.phone AS contact_phone, pc.website AS contact_website
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

DO $$
BEGIN
    RAISE NOTICE 'Migration 006 complete! Added is_bookmarked column and updated views.';
END $$;
```

---

### Migration 7: Add Cancelled Status (required)

The `cancelled` status is used by the job cancellation feature but is not in the original enum. Run this:

```sql
-- Add 'cancelled' to the job status enum if not already present
ALTER TYPE discovery_job_status ADD VALUE IF NOT EXISTS 'cancelled';
```

---

## 6. Seed Test Data (Optional)

To populate the database with sample data for development and testing, run this in the SQL Editor.

> **Note:** The seed data creates a job with `user_id = NULL` (no auth required). For authenticated testing, replace `NULL` with your actual user UUID from Supabase Auth.

```sql
-- ============================================================================
-- Seed Data: 1 job, 3 profiles, 3 scores, 2 contacts
-- ============================================================================

-- Sample discovery job
INSERT INTO discovery_jobs (
    id, user_id, name, brand_description, reference_profiles,
    follower_range_min, follower_range_max, discovery_limit,
    status, profiles_discovered, profiles_scored
) VALUES (
    '11111111-1111-1111-1111-111111111111',
    NULL,
    'Sustainable Fashion Discovery',
    'Sustainable fashion brand focused on eco-friendly materials and ethical production.',
    ARRAY['https://instagram.com/everlane', 'https://instagram.com/reformation', 'https://instagram.com/patagonia'],
    10000, 500000, 50, 'completed', 3, 3
) ON CONFLICT (id) DO NOTHING;

-- Brand DNA
INSERT INTO brand_dna (
    id, job_id, hashtags, keywords, visual_themes, content_pillars, target_audience_description
) VALUES (
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    ARRAY['#sustainablefashion', '#slowfashion', '#ethicalfashion', '#ecofriendly'],
    ARRAY['sustainable', 'ethical', 'eco-friendly', 'organic', 'fair trade'],
    ARRAY['minimalist aesthetic', 'earth tones', 'natural textures'],
    ARRAY['sustainability education', 'styling tips', 'brand values'],
    'Environmentally conscious millennials and Gen Z, primarily women aged 25-40'
) ON CONFLICT (job_id) DO NOTHING;

-- Profile 1: High score (88)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, bio, profile_picture_url,
    followers_count, following_count, posts_count, engagement_rate, following_ratio,
    is_verified, is_business_account, external_url, business_email, business_category, status
) VALUES (
    '33333333-3333-3333-3333-333333333333',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/eco_style_blogger', 'eco_style_blogger', 'Emma Green',
    'Sustainable fashion advocate | Slow fashion tips | emma@ecostyle.com',
    'https://example.com/avatars/emma.jpg',
    125000, 850, 320, 2.80, 0.007, false, true,
    'https://ecostyle.blog', 'emma@ecostyle.com', 'Blogger/Creator', 'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- Profile 2: Medium score (76)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, bio, profile_picture_url,
    followers_count, following_count, posts_count, engagement_rate, following_ratio,
    is_verified, is_business_account, external_url, business_email, business_category, status
) VALUES (
    '44444444-4444-4444-4444-444444444444',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/mindful_minimalist', 'mindful_minimalist', 'Sarah Chen',
    'Living with less | Capsule wardrobe tips | Sustainable living',
    'https://example.com/avatars/sarah.jpg',
    75000, 420, 180, 2.10, 0.006, false, true,
    'https://linktree.com/mindfulminimalist', NULL, 'Personal Blog', 'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- Profile 3: Lower score (61)
INSERT INTO discovered_profiles (
    id, job_id, instagram_url, username, full_name, bio, profile_picture_url,
    followers_count, following_count, posts_count, engagement_rate, following_ratio,
    is_verified, is_business_account, external_url, business_email, business_category, status
) VALUES (
    '55555555-5555-5555-5555-555555555555',
    '11111111-1111-1111-1111-111111111111',
    'https://instagram.com/green_lifestyle_tips', 'green_lifestyle_tips', 'Alex Martinez',
    'Eco-conscious living | Fashion | Home | Travel',
    'https://example.com/avatars/alex.jpg',
    45000, 1200, 450, 1.50, 0.027, false, false,
    NULL, NULL, NULL, 'done'
) ON CONFLICT (job_id, username) DO NOTHING;

-- Scores
INSERT INTO profile_scores (id, profile_id, visual_aesthetic_match, content_theme_alignment, engagement_rate_score, follower_quality, business_indicators, activity_recency, final_score, recommendation, reasoning, is_fake_suspected)
VALUES ('66666666-6666-6666-6666-666666666666', '33333333-3333-3333-3333-333333333333', 88, 92, 85, 78, 95, 90, 88, 'highly_recommended', '{"summary": "Excellent match. Strong alignment with brand values.", "recommendation": "Highly recommended for outreach."}'::jsonb, false)
ON CONFLICT (profile_id) DO NOTHING;

INSERT INTO profile_scores (id, profile_id, visual_aesthetic_match, content_theme_alignment, engagement_rate_score, follower_quality, business_indicators, activity_recency, final_score, recommendation, reasoning, is_fake_suspected)
VALUES ('77777777-7777-7777-7777-777777777777', '44444444-4444-4444-4444-444444444444', 75, 82, 70, 72, 80, 85, 76, 'recommended', '{"summary": "Good match with room for growth.", "recommendation": "Recommended for outreach."}'::jsonb, false)
ON CONFLICT (profile_id) DO NOTHING;

INSERT INTO profile_scores (id, profile_id, visual_aesthetic_match, content_theme_alignment, engagement_rate_score, follower_quality, business_indicators, activity_recency, final_score, recommendation, reasoning, is_fake_suspected)
VALUES ('88888888-8888-8888-8888-888888888888', '55555555-5555-5555-5555-555555555555', 62, 68, 55, 58, 50, 75, 61, 'consider', '{"summary": "Moderate match. Content relevant but not highly focused.", "recommendation": "Consider if other options are limited."}'::jsonb, false)
ON CONFLICT (profile_id) DO NOTHING;

-- Contacts
INSERT INTO profile_contacts (id, profile_id, email, email_source, website, other_contacts)
VALUES ('99999999-9999-9999-9999-999999999999', '33333333-3333-3333-3333-333333333333', 'emma@ecostyle.com', 'bio', 'https://ecostyle.blog', '{"instagram_dm": true}'::jsonb)
ON CONFLICT (profile_id) DO NOTHING;

INSERT INTO profile_contacts (id, profile_id, email, email_source, website, other_contacts)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-bbbbbbbbbbbb', '44444444-4444-4444-4444-444444444444', NULL, NULL, 'https://linktree.com/mindfulminimalist', '{"linktree": "https://linktree.com/mindfulminimalist"}'::jsonb)
ON CONFLICT (profile_id) DO NOTHING;
```

---

## 7. Verify Setup

Run these verification queries in the SQL Editor to confirm everything is set up correctly:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
-- Expected: brand_dna, discovered_profiles, discovery_jobs, profile_contacts, profile_scores

-- Check views exist
SELECT table_name FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;
-- Expected: v_complete_profiles, v_job_summary

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('discovery_jobs', 'brand_dna', 'discovered_profiles', 'profile_scores', 'profile_contacts');
-- Expected: All rows show rowsecurity = true

-- Check seed data (if you ran the seed)
SELECT COUNT(*) as jobs FROM discovery_jobs;               -- Expected: 1
SELECT COUNT(*) as profiles FROM discovered_profiles;       -- Expected: 3
SELECT COUNT(*) as scores FROM profile_scores;              -- Expected: 3

-- Test the views
SELECT username, final_score, recommendation, contact_email
FROM v_complete_profiles
WHERE job_id = '11111111-1111-1111-1111-111111111111'
ORDER BY final_score DESC;

-- Test job summary
SELECT job_id, total_profiles, done_profiles, avg_score, profiles_with_email
FROM v_job_summary
WHERE job_id = '11111111-1111-1111-1111-111111111111';
```

---

## 8. Start the Application

### 8.1 Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: Open http://localhost:8000/docs (Swagger UI)

### 8.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

Verify: Open http://localhost:5173

### 8.3 Quick Connection Test

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -c "
from app.db.supabase import get_supabase_client
db = get_supabase_client()
result = db.table('discovery_jobs').select('id, name, status').limit(5).execute()
print(f'Connected! Found {len(result.data)} jobs.')
for job in result.data:
    print(f'  - {job[\"name\"]} ({job[\"status\"]})')
"
```

---

## 9. Database Schema Reference

### Entity Relationships

```
auth.users (Supabase managed)
     │
     ▼ (1:many)
discovery_jobs
     │
     ├──▶ brand_dna (1:1)
     │
     └──▶ discovered_profiles (1:many)
              │
              ├──▶ profile_scores (1:1)
              │
              └──▶ profile_contacts (1:1)
```

### Tables Summary

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `discovery_jobs` | Discovery sessions | status, profiles_discovered, profiles_scored, keywords, hashtags, min_score_threshold, target_country |
| `brand_dna` | Extracted brand identity | hashtags, keywords, embedding_vector |
| `discovered_profiles` | Found Instagram profiles | username, followers_count, engagement_rate, status, is_bookmarked |
| `profile_scores` | AI scoring results | final_score (0-100), 6 dimension scores, recommendation, reasoning |
| `profile_contacts` | Extracted contact info | email, email_source, phone, website |

### Views Summary

| View | Purpose | Key Columns |
|------|---------|-------------|
| `v_complete_profiles` | Profiles + scores + contacts joined | All profile fields + final_score + contact_email + is_bookmarked |
| `v_job_summary` | Aggregated job stats | total_profiles, done_profiles, avg_score, profiles_with_email |

### Migration History

| # | File | What it does |
|---|------|-------------|
| 000 | `000_enable_extensions.sql` | Enables pgvector and uuid-ossp |
| 001 | `001_initial_schema.sql` | Creates 5 tables, indexes, triggers, views |
| 002 | `002_enable_rls.sql` | Enables Row Level Security with policies |
| 003 | `003_enable_realtime.sql` | Adds tables to realtime publication |
| 004 | `004_job_creation_enhancements.sql` | Adds keywords, hashtags, min_score_threshold |
| 005 | `005_add_target_country.sql` | Adds target_country column |
| 006 | `006_add_bookmarks.sql` | Adds is_bookmarked, updates v_complete_profiles |

---

## 10. Troubleshooting

### "relation does not exist" error
You missed a migration. Run them in order starting from 001.

### "type already exists" error
The migration was already run. This is safe to ignore, or skip that migration.

### "permission denied" on RLS
The backend must use the **Service Role Key** (not the Anon Key). Check `SUPABASE_SERVICE_ROLE_KEY` in `backend/.env`.

### "JWT expired" error
Generate a fresh test token:
```bash
cd backend && source venv/bin/activate
python -c "from app.guards.auth import create_test_token; print(create_test_token('YOUR_USER_ID'))"
```

### Foreign key violation on `user_id`
The `user_id` must exist in `auth.users`. Either:
- Create a user via Supabase Dashboard > Authentication > Users > "Add User"
- Or use the Demo endpoint (`POST /api/demo/start`) which creates jobs with `user_id = NULL`

### "publication does not exist" error on Migration 003
The `supabase_realtime` publication only exists in Supabase-hosted databases. If running PostgreSQL locally, skip Migration 003.

### pgvector extension not available
Go to **Database** > **Extensions** in the Supabase Dashboard, search for "vector", and toggle it ON.

### Stale profile counts on Sessions page
The trigger-based counters (`profiles_discovered`, `profiles_scored`) can drift during bulk operations. The backend automatically corrects this by using the `v_job_summary` view for accurate counts.

---

*Last updated: February 2026*
