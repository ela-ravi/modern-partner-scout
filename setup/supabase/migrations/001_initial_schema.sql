-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Child table with 1:1 relationship
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

-- Child table with 1:many relationship
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

-- Grandchild table (1:1 with discovered_profiles)
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

-- Grandchild table (1:1 with discovered_profiles)
CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,
    confidence REAL NOT NULL DEFAULT 0.0,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);
-- ============================================================================
-- Migration 001: Initial Schema
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- This migration creates the core tables for the partner discovery platform.
-- Reference: docs/Partner_Scout_AI_PRD.md Section 10
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;      -- For AI embeddings (pgvector)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; -- For UUID generation

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

-- Discovery job status (PRD Section 5.4)
CREATE TYPE discovery_job_status AS ENUM (
    'pending',      -- Created but not started
    'analyzing',    -- Brand DNA extraction in progress
    'discovering',  -- Finding candidate profiles
    'scoring',      -- AI scoring in progress
    'completed',    -- All profiles scored, results ready
    'failed'        -- Error occurred, can be retried
);

-- Profile processing status (PRD Section 10.5)
CREATE TYPE profile_status AS ENUM (
    'new',          -- Freshly discovered
    'processing',   -- Being scored
    'done',         -- Scoring complete
    'skipped'       -- Filtered out (fake/low quality)
);

-- ============================================================================
-- TABLE: discovery_jobs (PRD Section 10.3)
-- Parent table for discovery sessions
-- ============================================================================

CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE discovery_jobs IS 'Discovery sessions initiated by users (PRD 10.3)';
COMMENT ON COLUMN discovery_jobs.user_id IS 'Reference to Supabase auth.users';
COMMENT ON COLUMN discovery_jobs.reference_profiles IS 'Array of Instagram profile URLs to analyze';
COMMENT ON COLUMN discovery_jobs.profiles_discovered IS 'Denormalized count for dashboard performance';
COMMENT ON COLUMN discovery_jobs.profiles_scored IS 'Denormalized count for dashboard performance';

-- ============================================================================
-- TABLE: brand_dna (PRD Section 10.4)
-- Extracted brand identity from reference profiles (1:1 with discovery_jobs)
-- ============================================================================

CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    competitors TEXT[] NOT NULL DEFAULT '{}',
    embedding_vector vector(1536), -- OpenAI text-embedding-3-small dimension
    analysis JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);

COMMENT ON TABLE brand_dna IS 'Brand identity extracted from reference profiles (PRD 10.4)';
COMMENT ON COLUMN brand_dna.embedding_vector IS 'Vector embedding for similarity search (1536 dims for OpenAI)';
COMMENT ON COLUMN brand_dna.analysis IS 'Full analysis JSON from Brand Analyzer agent';

-- ============================================================================
-- TABLE: discovered_profiles (PRD Section 10.5)
-- Candidate Instagram profiles found during discovery (1:many with discovery_jobs)
-- ============================================================================

CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    
    -- Instagram profile data (from Apify scraper)
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    
    -- Metrics
    followers INTEGER NOT NULL DEFAULT 0,
    following INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    
    -- Business indicators (PRD 5.3.1 - Fake Detection)
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business BOOLEAN,
    external_url TEXT,                    -- Website link from bio
    business_email TEXT,                  -- Email from business account
    business_category TEXT,               -- Business category name
    following_ratio DECIMAL(5,2),         -- Calculated: following / followers
    
    -- Processing status
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, instagram_url)
);

COMMENT ON TABLE discovered_profiles IS 'Instagram profiles found during discovery (PRD 10.5)';
COMMENT ON COLUMN discovered_profiles.following_ratio IS 'following/followers - high ratio indicates potential fake (PRD 5.3.1)';
COMMENT ON COLUMN discovered_profiles.engagement_rate IS 'Calculated: (avg_likes + avg_comments) / followers * 100';

-- ============================================================================
-- TABLE: profile_scores (PRD Section 10.6)
-- AI scoring results with 6 dimensions (1:1 with discovered_profiles)
-- ============================================================================

CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    
    -- Overall weighted score (0-100)
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    
    -- 6 Scoring Dimensions (PRD 5.3)
    -- Each dimension is 0-100, weighted to calculate final score
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),     -- 25% weight
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100), -- 20% weight
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),       -- 15% weight
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),                       -- 15% weight (fake detection)
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),             -- 15% weight
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),                       -- 10% weight
    
    -- Explanation
    reasoning JSONB NOT NULL DEFAULT '{}',
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

COMMENT ON TABLE profile_scores IS 'AI scoring with 6 dimensions (PRD 5.3, 10.6)';
COMMENT ON COLUMN profile_scores.follower_quality IS 'Authenticity score - low = likely fake (PRD 5.3.1)';
COMMENT ON COLUMN profile_scores.reasoning IS 'JSON with summary, recommendation, dimension notes';

-- ============================================================================
-- TABLE: profile_contacts (PRD Section 10.7)
-- Extracted contact information (1:1 with discovered_profiles)
-- ============================================================================

CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,  -- Where email was found: 'business_email', 'bio', 'website', etc.
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);

COMMENT ON TABLE profile_contacts IS 'Extracted contact information (PRD 10.7)';
COMMENT ON COLUMN profile_contacts.source IS 'Origin of email: business_email, bio, website, etc.';
