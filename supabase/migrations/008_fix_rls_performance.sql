-- ============================================================================
-- Migration: 008_fix_rls_performance.sql
-- Description: Fix RLS performance warnings and overlapping permissive policies
-- Issues addressed:
--   1. auth.uid() and auth.jwt() re-evaluated per row → wrap in (select ...)
--   2. Service role policies overlap with user policies for all roles
--      → scope user policies to 'authenticated' and service policies to 'service_role'
-- ============================================================================

-- ============================================================================
-- DISCOVERY_JOBS: Drop and recreate all policies
-- ============================================================================

DROP POLICY IF EXISTS "Users can view own discovery_jobs" ON discovery_jobs;
DROP POLICY IF EXISTS "Users can insert own discovery_jobs" ON discovery_jobs;
DROP POLICY IF EXISTS "Users can update own discovery_jobs" ON discovery_jobs;
DROP POLICY IF EXISTS "Users can delete own discovery_jobs" ON discovery_jobs;
DROP POLICY IF EXISTS "Service role can access all discovery_jobs" ON discovery_jobs;

-- User policies: scoped to 'authenticated' role, auth.uid() wrapped in (select ...)
CREATE POLICY "Users can view own discovery_jobs"
    ON discovery_jobs
    FOR SELECT
    TO authenticated
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can insert own discovery_jobs"
    ON discovery_jobs
    FOR INSERT
    TO authenticated
    WITH CHECK ((select auth.uid()) = user_id);

CREATE POLICY "Users can update own discovery_jobs"
    ON discovery_jobs
    FOR UPDATE
    TO authenticated
    USING ((select auth.uid()) = user_id);

CREATE POLICY "Users can delete own discovery_jobs"
    ON discovery_jobs
    FOR DELETE
    TO authenticated
    USING ((select auth.uid()) = user_id);

-- Service role policy: scoped to 'service_role' only
CREATE POLICY "Service role can access all discovery_jobs"
    ON discovery_jobs
    FOR ALL
    TO service_role
    USING (true);

-- ============================================================================
-- BRAND_DNA: Drop and recreate all policies
-- ============================================================================

DROP POLICY IF EXISTS "Users can access brand_dna for their jobs" ON brand_dna;
DROP POLICY IF EXISTS "Service role can access all brand_dna" ON brand_dna;

CREATE POLICY "Users can access brand_dna for their jobs"
    ON brand_dna
    FOR ALL
    TO authenticated
    USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = (select auth.uid()))
    );

CREATE POLICY "Service role can access all brand_dna"
    ON brand_dna
    FOR ALL
    TO service_role
    USING (true);

-- ============================================================================
-- DISCOVERED_PROFILES: Drop and recreate all policies
-- ============================================================================

DROP POLICY IF EXISTS "Users can access profiles for their jobs" ON discovered_profiles;
DROP POLICY IF EXISTS "Service role can access all discovered_profiles" ON discovered_profiles;

CREATE POLICY "Users can access profiles for their jobs"
    ON discovered_profiles
    FOR ALL
    TO authenticated
    USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = (select auth.uid()))
    );

CREATE POLICY "Service role can access all discovered_profiles"
    ON discovered_profiles
    FOR ALL
    TO service_role
    USING (true);

-- ============================================================================
-- PROFILE_SCORES: Drop and recreate all policies
-- ============================================================================

DROP POLICY IF EXISTS "Users can access scores for their profiles" ON profile_scores;
DROP POLICY IF EXISTS "Service role can access all profile_scores" ON profile_scores;

CREATE POLICY "Users can access scores for their profiles"
    ON profile_scores
    FOR ALL
    TO authenticated
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = (select auth.uid()))
        )
    );

CREATE POLICY "Service role can access all profile_scores"
    ON profile_scores
    FOR ALL
    TO service_role
    USING (true);

-- ============================================================================
-- PROFILE_CONTACTS: Drop and recreate all policies
-- ============================================================================

DROP POLICY IF EXISTS "Users can access contacts for their profiles" ON profile_contacts;
DROP POLICY IF EXISTS "Service role can access all profile_contacts" ON profile_contacts;

CREATE POLICY "Users can access contacts for their profiles"
    ON profile_contacts
    FOR ALL
    TO authenticated
    USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = (select auth.uid()))
        )
    );

CREATE POLICY "Service role can access all profile_contacts"
    ON profile_contacts
    FOR ALL
    TO service_role
    USING (true);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    policy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO policy_count
    FROM pg_policies
    WHERE schemaname = 'public';

    RAISE NOTICE 'Migration 008 completed! Total RLS policies: %', policy_count;
    RAISE NOTICE 'All auth.uid()/auth.jwt() calls wrapped in (select ...) for per-query evaluation';
    RAISE NOTICE 'Service role policies scoped to service_role only — no more overlapping permissive policies';
END $$;
