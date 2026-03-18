-- ============================================================================
-- Migration: 007_fix_security_issues.sql
-- Description: Fix security issues flagged by Supabase Security Advisor
-- Issues addressed:
--   1. v_job_summary view uses SECURITY DEFINER (should be SECURITY INVOKER)
--   2. v_complete_profiles view uses SECURITY DEFINER (should be SECURITY INVOKER)
--   3. update_profiles_scored() has mutable search_path
--   4. update_profiles_discovered() has mutable search_path
--   5. update_updated_at_column() has mutable search_path
--   6. vector extension installed in public schema
-- Note: Issue #7 (leaked password protection) must be enabled manually
--       in Supabase Dashboard > Authentication > Settings
-- ============================================================================

-- ============================================================================
-- FIX 1: Move vector extension to dedicated 'extensions' schema
-- ============================================================================

-- Create extensions schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS extensions;

-- Move vector extension to extensions schema
ALTER EXTENSION vector SET SCHEMA extensions;

-- Move uuid-ossp extension to extensions schema (if in public)
ALTER EXTENSION "uuid-ossp" SET SCHEMA extensions;

-- Grant usage on extensions schema to authenticated users
GRANT USAGE ON SCHEMA extensions TO authenticated;
GRANT USAGE ON SCHEMA extensions TO service_role;

-- ============================================================================
-- FIX 2: Recreate functions with SET search_path = ''
-- ============================================================================

-- Fix update_updated_at_column() — add SET search_path
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = '';

-- Fix update_profiles_discovered() — add SET search_path
CREATE OR REPLACE FUNCTION public.update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.discovery_jobs
        SET profiles_discovered = profiles_discovered + 1
        WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.discovery_jobs
        SET profiles_discovered = profiles_discovered - 1
        WHERE id = OLD.job_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql
SET search_path = '';

-- Fix update_profiles_scored() — add SET search_path
CREATE OR REPLACE FUNCTION public.update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment when profile changes to 'done'
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE public.discovery_jobs
        SET profiles_scored = profiles_scored + 1
        WHERE id = NEW.job_id;
    -- Decrement when profile changes from 'done' to something else
    ELSIF OLD.status = 'done' AND NEW.status != 'done' THEN
        UPDATE public.discovery_jobs
        SET profiles_scored = profiles_scored - 1
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql
SET search_path = '';

-- ============================================================================
-- FIX 3: Recreate views with security_invoker = true
-- ============================================================================

-- Recreate v_complete_profiles with SECURITY INVOKER
-- (Uses the version from 006_add_bookmarks.sql which includes is_bookmarked)
DROP VIEW IF EXISTS v_complete_profiles;
CREATE VIEW v_complete_profiles
WITH (security_invoker = true)
AS
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
    dp.is_bookmarked,
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

COMMENT ON VIEW v_complete_profiles IS 'Complete profile view with scores, contacts, and bookmark status (SECURITY INVOKER)';

-- Recreate v_job_summary with SECURITY INVOKER
DROP VIEW IF EXISTS v_job_summary;
CREATE VIEW v_job_summary
WITH (security_invoker = true)
AS
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

COMMENT ON VIEW v_job_summary IS 'Job summary with aggregated statistics (SECURITY INVOKER)';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    ext_schema TEXT;
    func_path TEXT;
    view_security TEXT;
BEGIN
    -- Verify vector extension moved out of public
    SELECT n.nspname INTO ext_schema
    FROM pg_extension e
    JOIN pg_namespace n ON e.extnamespace = n.oid
    WHERE e.extname = 'vector';

    IF ext_schema = 'public' THEN
        RAISE WARNING 'vector extension is still in public schema (got: %)', ext_schema;
    ELSE
        RAISE NOTICE 'OK: vector extension is in % schema', ext_schema;
    END IF;

    -- Verify functions have search_path set
    SELECT proconfig::TEXT INTO func_path
    FROM pg_proc
    WHERE proname = 'update_updated_at_column';

    IF func_path IS NOT NULL AND func_path LIKE '%search_path%' THEN
        RAISE NOTICE 'OK: update_updated_at_column has search_path set';
    ELSE
        RAISE WARNING 'update_updated_at_column may not have search_path set';
    END IF;

    SELECT proconfig::TEXT INTO func_path
    FROM pg_proc
    WHERE proname = 'update_profiles_discovered';

    IF func_path IS NOT NULL AND func_path LIKE '%search_path%' THEN
        RAISE NOTICE 'OK: update_profiles_discovered has search_path set';
    ELSE
        RAISE WARNING 'update_profiles_discovered may not have search_path set';
    END IF;

    SELECT proconfig::TEXT INTO func_path
    FROM pg_proc
    WHERE proname = 'update_profiles_scored';

    IF func_path IS NOT NULL AND func_path LIKE '%search_path%' THEN
        RAISE NOTICE 'OK: update_profiles_scored has search_path set';
    ELSE
        RAISE WARNING 'update_profiles_scored may not have search_path set';
    END IF;

    RAISE NOTICE 'Migration 007 completed! Security issues addressed.';
    RAISE NOTICE 'MANUAL ACTION REQUIRED: Enable leaked password protection in Supabase Dashboard > Authentication > Settings';
END $$;
