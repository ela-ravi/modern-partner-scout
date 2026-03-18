-- ============================================================================
-- Migration: 002_enable_rls.sql
-- Description: Enable Row Level Security policies for all tables
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
-- Users can only access their own jobs
-- ============================================================================

CREATE POLICY "Users can view own discovery_jobs" 
    ON discovery_jobs
    FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own discovery_jobs" 
    ON discovery_jobs
    FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own discovery_jobs" 
    ON discovery_jobs
    FOR UPDATE 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own discovery_jobs" 
    ON discovery_jobs
    FOR DELETE 
    USING (auth.uid() = user_id);

-- Service role can access all jobs (for backend operations)
CREATE POLICY "Service role can access all discovery_jobs"
    ON discovery_jobs
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- BRAND_DNA POLICIES
-- Access via job ownership
-- ============================================================================

CREATE POLICY "Users can access brand_dna for their jobs" 
    ON brand_dna
    FOR ALL 
    USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

CREATE POLICY "Service role can access all brand_dna"
    ON brand_dna
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- DISCOVERED_PROFILES POLICIES
-- Access via job ownership
-- ============================================================================

CREATE POLICY "Users can access profiles for their jobs" 
    ON discovered_profiles
    FOR ALL 
    USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

CREATE POLICY "Service role can access all discovered_profiles"
    ON discovered_profiles
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- PROFILE_SCORES POLICIES
-- Access via profile → job ownership chain
-- ============================================================================

CREATE POLICY "Users can access scores for their profiles" 
    ON profile_scores
    FOR ALL 
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );

CREATE POLICY "Service role can access all profile_scores"
    ON profile_scores
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- PROFILE_CONTACTS POLICIES
-- Access via profile → job ownership chain
-- ============================================================================

CREATE POLICY "Users can access contacts for their profiles" 
    ON profile_contacts
    FOR ALL 
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );

CREATE POLICY "Service role can access all profile_contacts"
    ON profile_contacts
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify RLS is enabled on all tables
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
    
    RAISE NOTICE 'RLS enabled successfully on all 5 tables!';
END $$;

-- List all policies for verification
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
