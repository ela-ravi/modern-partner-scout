-- ============================================================================
-- Migration: 005_add_target_country.sql
-- Description: Add optional target_country field to discovery_jobs
-- Purpose: Allow users to prioritize profiles from a specific country/region
-- ============================================================================

-- Add target_country column (nullable - optional field)
ALTER TABLE discovery_jobs
ADD COLUMN IF NOT EXISTS target_country TEXT;

-- Add comment
COMMENT ON COLUMN discovery_jobs.target_country IS 'Optional target country/region for score boosting (e.g., India, USA, Germany)';

-- ============================================================================
-- Update v_job_summary view to include target_country
-- ============================================================================

DROP VIEW IF EXISTS v_job_summary;
CREATE VIEW v_job_summary AS
SELECT
    dj.id AS job_id,
    dj.user_id,
    dj.name,
    dj.brand_description,
    dj.keywords,
    dj.hashtags,
    dj.min_score_threshold,
    dj.target_country,
    dj.follower_range_min,
    dj.follower_range_max,
    dj.discovery_limit,
    dj.status,
    dj.profiles_discovered,
    dj.profiles_scored,
    dj.error_message,
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
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email,
    COUNT(ps.final_score) FILTER (WHERE ps.final_score >= 80) AS high_score_count
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

COMMENT ON VIEW v_job_summary IS 'Job summary with aggregated statistics including target_country';

-- ============================================================================
-- Verification
-- ============================================================================

DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'discovery_jobs'
    AND column_name = 'target_country';

    IF col_count != 1 THEN
        RAISE EXCEPTION 'Expected target_country column, not found';
    END IF;

    RAISE NOTICE 'Migration 005 completed successfully! Added target_country column.';
END $$;
