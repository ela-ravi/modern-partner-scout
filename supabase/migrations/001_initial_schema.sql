-- ============================================================================
-- Migration: 001_initial_schema.sql
-- Description: Create initial database schema for PartnerScout AI
-- ============================================================================

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Status enum for discovery jobs
CREATE TYPE discovery_job_status AS ENUM (
    'pending',      -- Job created, waiting to start
    'analyzing',    -- Brand Analyzer Agent is extracting brand DNA
    'discovering',  -- Discovery Agent is finding similar profiles
    'scoring',      -- Scorer Agent is evaluating profiles
    'completed',    -- All processing finished successfully
    'failed'        -- An error occurred during processing
);

-- Status enum for discovered profiles
CREATE TYPE profile_status AS ENUM (
    'new',          -- Profile discovered, not yet scored
    'processing',   -- Scorer Agent is currently evaluating
    'done',         -- Scoring complete
    'skipped'       -- Profile was skipped (e.g., private account)
);

-- ============================================================================
-- TABLES
-- ============================================================================

-- Main parent table: Discovery Jobs
-- Each job represents a discovery session initiated by a user
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

COMMENT ON TABLE discovery_jobs IS 'Main table storing discovery session information';
COMMENT ON COLUMN discovery_jobs.reference_profiles IS 'Array of Instagram URLs used as reference for brand analysis';
COMMENT ON COLUMN discovery_jobs.profiles_discovered IS 'Denormalized count updated by trigger';
COMMENT ON COLUMN discovery_jobs.profiles_scored IS 'Denormalized count updated by trigger';

-- Brand DNA table: Extracted brand characteristics
-- 1:1 relationship with discovery_jobs
CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    visual_themes TEXT[] DEFAULT '{}',
    content_pillars TEXT[] DEFAULT '{}',
    target_audience_description TEXT,
    embedding_vector vector(1536),  -- OpenAI text-embedding-ada-002 dimension
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);

COMMENT ON TABLE brand_dna IS 'Extracted brand characteristics from reference profiles';
COMMENT ON COLUMN brand_dna.embedding_vector IS 'Vector embedding for semantic similarity search (1536 dims for OpenAI)';

-- Discovered Profiles table: Instagram profiles found by Discovery Agent
-- 1:many relationship with discovery_jobs
CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    
    -- Core Instagram data
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    
    -- Metrics
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    following_ratio DECIMAL(5,2),  -- Calculated: following / followers
    
    -- Account flags
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business_account BOOLEAN,
    
    -- Business account info
    external_url TEXT,          -- Website link from bio
    business_email TEXT,        -- Email from business account
    business_category TEXT,     -- Business category name
    
    -- Processing status
    status profile_status NOT NULL DEFAULT 'new',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Prevent duplicate profiles per job
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, username)
);

COMMENT ON TABLE discovered_profiles IS 'Instagram profiles discovered for a job';
COMMENT ON COLUMN discovered_profiles.following_ratio IS 'Calculated as following_count / followers_count for fake detection';

-- Profile Scores table: AI-generated scores with 6 dimensions
-- 1:1 relationship with discovered_profiles
CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    
    -- Individual dimension scores (0-100)
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100),
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),
    
    -- Final weighted score
    final_score INTEGER NOT NULL CHECK (final_score >= 0 AND final_score <= 100),
    
    -- AI recommendation
    recommendation TEXT CHECK (recommendation IN ('highly_recommended', 'recommended', 'consider', 'not_recommended')),
    
    -- Detailed reasoning from AI
    reasoning JSONB NOT NULL DEFAULT '{}',
    
    -- Fake/bot detection flag
    is_fake_suspected BOOLEAN NOT NULL DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

COMMENT ON TABLE profile_scores IS 'AI-generated scores with 6 dimensions for each profile';
COMMENT ON COLUMN profile_scores.reasoning IS 'JSON containing detailed AI reasoning for each dimension';

-- Profile Contacts table: Extracted contact information
-- 1:1 relationship with discovered_profiles
CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    
    -- Contact info
    email TEXT,
    email_source TEXT,  -- 'bio', 'business_email', 'website', 'extracted'
    phone TEXT,
    website TEXT,
    
    -- Additional contact methods
    other_contacts JSONB DEFAULT '{}',  -- {"linktree": "...", "twitter": "...", etc}
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);

COMMENT ON TABLE profile_contacts IS 'Contact information extracted from profiles';
COMMENT ON COLUMN profile_contacts.email_source IS 'Where the email was found: bio, business_email, website, or extracted';

-- ============================================================================
-- INDEXES
-- ============================================================================

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
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers_count DESC);
CREATE INDEX idx_discovered_profiles_username ON discovered_profiles(username);
CREATE INDEX idx_profile_scores_final_score ON profile_scores(final_score DESC);
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) WHERE email IS NOT NULL;

-- ============================================================================
-- TRIGGERS: Auto-update timestamps
-- ============================================================================

-- Function to auto-update updated_at column
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

-- ============================================================================
-- TRIGGERS: Auto-update counters
-- ============================================================================

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

-- ============================================================================
-- CONVENIENCE VIEWS
-- ============================================================================

-- Complete profile view with scores and contacts
CREATE VIEW v_complete_profiles AS
SELECT 
    dp.id,
    dp.job_id,
    dp.instagram_url,
    dp.username,
    dp.full_name,
    dp.profile_picture_url,
    dp.bio,
    dp.followers_count,
    dp.following_count,
    dp.posts_count,
    dp.engagement_rate,
    dp.following_ratio,
    dp.is_verified,
    dp.is_business_account,
    dp.external_url,
    dp.business_email,
    dp.business_category,
    dp.status,
    dp.created_at,
    ps.final_score,
    ps.visual_aesthetic_match,
    ps.content_theme_alignment,
    ps.engagement_rate_score,
    ps.follower_quality,
    ps.business_indicators,
    ps.activity_recency,
    ps.recommendation,
    ps.reasoning,
    ps.is_fake_suspected,
    pc.email AS contact_email,
    pc.email_source,
    pc.phone AS contact_phone,
    pc.website AS contact_website
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

COMMENT ON VIEW v_complete_profiles IS 'Complete profile view with scores and contacts joined';

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

COMMENT ON VIEW v_job_summary IS 'Job summary with aggregated statistics';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify all tables were created
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
    
    RAISE NOTICE 'Schema created successfully! All 5 tables exist.';
END $$;
