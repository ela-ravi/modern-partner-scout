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

-- profile_scores: Access via profile -> job ownership
CREATE POLICY "Users can access scores for their profiles" ON profile_scores
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );

-- profile_contacts: Access via profile -> job ownership
CREATE POLICY "Users can access contacts for their profiles" ON profile_contacts
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );
-- ============================================================================
-- Migration 003: Row Level Security (RLS) Policies
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Implements user data isolation per PRD Section 6 and 10.1.2.
-- All data access flows through user_id ownership chain.
-- Run after 001_initial_schema.sql and 002_indexes.sql
-- ============================================================================

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================

ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- DISCOVERY_JOBS POLICIES
-- Direct user_id check - users can only access their own jobs
-- ============================================================================

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

-- ============================================================================
-- BRAND_DNA POLICIES
-- Access via job ownership chain: brand_dna → discovery_jobs → user_id
-- ============================================================================

CREATE POLICY "Users can access brand_dna for their jobs" 
    ON brand_dna FOR ALL 
    USING (
        job_id IN (
            SELECT id FROM discovery_jobs WHERE user_id = auth.uid()
        )
    );

-- ============================================================================
-- DISCOVERED_PROFILES POLICIES
-- Access via job ownership chain: discovered_profiles → discovery_jobs → user_id
-- ============================================================================

CREATE POLICY "Users can access profiles for their jobs" 
    ON discovered_profiles FOR ALL 
    USING (
        job_id IN (
            SELECT id FROM discovery_jobs WHERE user_id = auth.uid()
        )
    );

-- ============================================================================
-- PROFILE_SCORES POLICIES
-- Access via profile → job ownership chain
-- ============================================================================

CREATE POLICY "Users can access scores for their profiles" 
    ON profile_scores FOR ALL 
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (
                SELECT id FROM discovery_jobs WHERE user_id = auth.uid()
            )
        )
    );

-- ============================================================================
-- PROFILE_CONTACTS POLICIES
-- Access via profile → job ownership chain
-- ============================================================================

CREATE POLICY "Users can access contacts for their profiles" 
    ON profile_contacts FOR ALL 
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (
                SELECT id FROM discovery_jobs WHERE user_id = auth.uid()
            )
        )
    );

-- ============================================================================
-- SERVICE ROLE BYPASS
-- The service role (used by n8n and backend) bypasses RLS automatically.
-- This is the expected behavior for orchestration workflows.
-- ============================================================================

-- Note: Supabase service role key automatically bypasses RLS.
-- No additional policies needed for backend service operations.
