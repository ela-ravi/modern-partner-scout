-- ============================================================================
-- PartnerScout AI - Complete Database Setup
-- ============================================================================
-- Run this single file in Supabase SQL Editor to create all tables.
-- 
-- After running, refresh the Table Editor to see new tables.
-- ============================================================================

-- ============================================================================
-- STEP 1: Clean up any existing objects (for fresh install)
-- ============================================================================

-- Drop views first (they depend on tables)
DROP VIEW IF EXISTS v_suspicious_profiles CASCADE;
DROP VIEW IF EXISTS v_high_score_profiles CASCADE;
DROP VIEW IF EXISTS v_job_summary CASCADE;
DROP VIEW IF EXISTS v_complete_profiles CASCADE;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS profile_contacts CASCADE;
DROP TABLE IF EXISTS profile_scores CASCADE;
DROP TABLE IF EXISTS discovered_profiles CASCADE;
DROP TABLE IF EXISTS brand_dna CASCADE;
DROP TABLE IF EXISTS discovery_jobs CASCADE;

-- Drop enum types
DROP TYPE IF EXISTS profile_status CASCADE;
DROP TYPE IF EXISTS discovery_job_status CASCADE;

-- ============================================================================
-- STEP 2: Enable Extensions
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- STEP 3: Create Enum Types
-- ============================================================================

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

-- ============================================================================
-- STEP 4: Create Tables
-- ============================================================================

-- Main parent table
CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Brand DNA (1:1 with discovery_jobs)
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    competitors TEXT[] NOT NULL DEFAULT '{}',
    embedding vector(1536),
    analysis JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);

-- Discovered profiles (1:many with discovery_jobs)
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

-- Profile scores (1:1 with discovered_profiles)
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

-- Profile contacts (1:1 with discovered_profiles)
CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,
    confidence REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);

-- ============================================================================
-- STEP 5: Create Indexes
-- ============================================================================

CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);
CREATE INDEX idx_discovery_jobs_user_status ON discovery_jobs(user_id, status);

CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);

CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers DESC);
CREATE INDEX idx_discovered_profiles_job_status ON discovered_profiles(job_id, status);
CREATE INDEX idx_discovered_profiles_username ON discovered_profiles(username);

CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
CREATE INDEX idx_profile_scores_follower_quality ON profile_scores(follower_quality);

CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) WHERE email IS NOT NULL;

-- ============================================================================
-- STEP 6: Enable Row Level Security
-- ============================================================================

ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- Discovery jobs policies
CREATE POLICY "Users can view own discovery_jobs" 
    ON discovery_jobs FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own discovery_jobs" 
    ON discovery_jobs FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own discovery_jobs" 
    ON discovery_jobs FOR UPDATE 
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own discovery_jobs" 
    ON discovery_jobs FOR DELETE 
    USING (auth.uid() = user_id);

-- Brand DNA policies
CREATE POLICY "Users can access brand_dna for their jobs" 
    ON brand_dna FOR ALL 
    USING (job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid()));

-- Discovered profiles policies
CREATE POLICY "Users can access profiles for their jobs" 
    ON discovered_profiles FOR ALL 
    USING (job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid()));

-- Profile scores policies
CREATE POLICY "Users can access scores for their profiles" 
    ON profile_scores FOR ALL 
    USING (profile_id IN (
        SELECT id FROM discovered_profiles 
        WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    ));

-- Profile contacts policies
CREATE POLICY "Users can access contacts for their profiles" 
    ON profile_contacts FOR ALL 
    USING (profile_id IN (
        SELECT id FROM discovered_profiles 
        WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    ));

-- ============================================================================
-- STEP 7: Create Trigger Functions
-- ============================================================================

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

CREATE OR REPLACE FUNCTION update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = profiles_discovered + 1,
            updated_at = NOW()
        WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = GREATEST(0, profiles_discovered - 1),
            updated_at = NOW()
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

CREATE OR REPLACE FUNCTION update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE discovery_jobs 
        SET profiles_scored = profiles_scored + 1,
            updated_at = NOW()
        WHERE id = NEW.job_id;
    ELSIF OLD.status = 'done' AND NEW.status != 'done' THEN
        UPDATE discovery_jobs 
        SET profiles_scored = GREATEST(0, profiles_scored - 1),
            updated_at = NOW()
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_scored
    AFTER UPDATE OF status ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_scored();

CREATE OR REPLACE FUNCTION auto_complete_job()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.profiles_scored > 0 
       AND NEW.profiles_scored >= NEW.profiles_discovered 
       AND NEW.status = 'scoring' THEN
        NEW.status = 'completed';
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_complete_job
    BEFORE UPDATE OF profiles_scored ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION auto_complete_job();

-- ============================================================================
-- STEP 8: Enable Realtime
-- ============================================================================

ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

-- ============================================================================
-- STEP 9: Create Views
-- ============================================================================

CREATE VIEW v_complete_profiles AS
SELECT 
    dp.id,
    dp.job_id,
    dp.instagram_url,
    dp.username,
    dp.full_name,
    dp.profile_picture_url,
    dp.bio,
    dp.followers,
    dp.following,
    dp.posts_count,
    dp.engagement_rate,
    dp.is_verified,
    dp.is_business,
    dp.external_url,
    dp.business_email,
    dp.business_category,
    dp.following_ratio,
    dp.status,
    dp.created_at,
    ps.score,
    ps.visual_aesthetic_match,
    ps.content_theme_alignment,
    ps.engagement_rate_score,
    ps.follower_quality,
    ps.business_indicators,
    ps.activity_recency,
    ps.reasoning,
    pc.email,
    pc.source AS email_source
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

CREATE VIEW v_job_summary AS
SELECT 
    dj.id AS job_id,
    dj.user_id,
    dj.name,
    dj.brand_description,
    dj.reference_profiles,
    dj.status,
    dj.profiles_discovered,
    dj.profiles_scored,
    dj.created_at,
    dj.updated_at,
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    COALESCE(AVG(ps.score)::INTEGER, 0) AS avg_score,
    MAX(ps.score) AS max_score,
    MIN(ps.score) AS min_score,
    COUNT(CASE WHEN ps.score >= 80 THEN 1 END) AS excellent_count,
    COUNT(CASE WHEN ps.score >= 60 AND ps.score < 80 THEN 1 END) AS good_count,
    COUNT(CASE WHEN ps.score >= 40 AND ps.score < 60 THEN 1 END) AS moderate_count,
    COUNT(CASE WHEN ps.score < 40 THEN 1 END) AS poor_count,
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

CREATE VIEW v_high_score_profiles AS
SELECT 
    dp.*,
    ps.score,
    ps.reasoning,
    pc.email,
    dj.user_id
FROM discovered_profiles dp
INNER JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
INNER JOIN discovery_jobs dj ON dp.job_id = dj.id
WHERE ps.score >= 70
ORDER BY ps.score DESC;

CREATE VIEW v_suspicious_profiles AS
SELECT 
    dp.id,
    dp.job_id,
    dp.username,
    dp.followers,
    dp.following,
    dp.following_ratio,
    dp.posts_count,
    dp.engagement_rate,
    dp.is_business,
    dp.business_email,
    ps.score,
    ps.follower_quality,
    ps.reasoning,
    dj.user_id,
    CASE WHEN dp.following_ratio > 2.0 THEN true ELSE false END AS high_following_ratio,
    CASE WHEN dp.posts_count < 20 AND dp.followers > 5000 THEN true ELSE false END AS low_post_ratio,
    CASE WHEN dp.engagement_rate < 1.0 THEN true ELSE false END AS low_engagement,
    CASE WHEN dp.is_business = false THEN true ELSE false END AS not_business
FROM discovered_profiles dp
INNER JOIN profile_scores ps ON dp.id = ps.profile_id
INNER JOIN discovery_jobs dj ON dp.job_id = dj.id
WHERE ps.follower_quality < 50
ORDER BY ps.follower_quality ASC;

-- ============================================================================
-- VERIFICATION: Run this query to confirm tables were created
-- ============================================================================

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND table_name IN ('discovery_jobs', 'brand_dna', 'discovered_profiles', 'profile_scores', 'profile_contacts')
ORDER BY table_name;
