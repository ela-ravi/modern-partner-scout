-- Parent table indexes
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);

-- Foreign key indexes (always index FK columns)
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);

-- Query-specific indexes
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers DESC);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
CREATE INDEX idx_profile_scores_follower_quality ON profile_scores(follower_quality DESC);
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) WHERE email IS NOT NULL;
-- ============================================================================
-- Migration 002: Indexes for Performance
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Creates indexes for common query patterns and foreign key lookups.
-- Run after 001_initial_schema.sql
-- ============================================================================

-- ============================================================================
-- DISCOVERY_JOBS INDEXES
-- ============================================================================

-- User's jobs listing (most common query)
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);

-- Filter by status (dashboard tabs)
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);

-- Sort by creation date (newest first)
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);

-- Composite index for user's jobs by status
CREATE INDEX idx_discovery_jobs_user_status ON discovery_jobs(user_id, status);

-- ============================================================================
-- BRAND_DNA INDEXES
-- ============================================================================

-- Foreign key lookup
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);

-- ============================================================================
-- DISCOVERED_PROFILES INDEXES
-- ============================================================================

-- Foreign key lookup (most critical - used in all profile queries)
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);

-- Filter by status (NEW/PROCESSING/DONE tabs)
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);

-- Sort by followers (popular profiles first)
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers DESC);

-- Composite: job's profiles by status (dashboard query)
CREATE INDEX idx_discovered_profiles_job_status ON discovered_profiles(job_id, status);

-- Username lookup (deduplication)
CREATE INDEX idx_discovered_profiles_username ON discovered_profiles(username);

-- ============================================================================
-- PROFILE_SCORES INDEXES
-- ============================================================================

-- Foreign key lookup
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);

-- Sort by score (best matches first)
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);

-- Filter by follower quality (fake detection)
CREATE INDEX idx_profile_scores_follower_quality ON profile_scores(follower_quality);

-- ============================================================================
-- PROFILE_CONTACTS INDEXES
-- ============================================================================

-- Foreign key lookup
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);

-- Find profiles with email (for outreach)
CREATE INDEX idx_profile_contacts_email ON profile_contacts(email) 
    WHERE email IS NOT NULL;
