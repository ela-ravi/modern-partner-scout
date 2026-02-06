-- ============================================================================
-- Migration: 004_job_creation_enhancements.sql
-- Description: Add keywords, hashtags, and min_score_threshold to discovery_jobs
-- Part of: Item 5 - Job Creation Enhancements
-- ============================================================================

-- Add keywords array (user-provided target keywords for discovery)
ALTER TABLE discovery_jobs 
ADD COLUMN IF NOT EXISTS keywords TEXT[] NOT NULL DEFAULT '{}';

-- Add hashtags array (user-provided target hashtags for discovery)
ALTER TABLE discovery_jobs 
ADD COLUMN IF NOT EXISTS hashtags TEXT[] NOT NULL DEFAULT '{}';

-- Add min_score_threshold (minimum score filter, 0-100)
ALTER TABLE discovery_jobs 
ADD COLUMN IF NOT EXISTS min_score_threshold INTEGER NOT NULL DEFAULT 50 
    CHECK (min_score_threshold >= 0 AND min_score_threshold <= 100);

-- Add comments
COMMENT ON COLUMN discovery_jobs.keywords IS 'User-provided target keywords for discovery';
COMMENT ON COLUMN discovery_jobs.hashtags IS 'User-provided target hashtags for discovery';
COMMENT ON COLUMN discovery_jobs.min_score_threshold IS 'Minimum score filter threshold (0-100)';

-- ============================================================================
-- Update v_job_summary view to include new fields
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

COMMENT ON VIEW v_job_summary IS 'Job summary with aggregated statistics including enhancement fields';

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
    AND column_name IN ('keywords', 'hashtags', 'min_score_threshold');
    
    IF col_count != 3 THEN
        RAISE EXCEPTION 'Expected 3 new columns, found %', col_count;
    END IF;
    
    RAISE NOTICE 'Migration 004 completed successfully! Added keywords, hashtags, min_score_threshold columns.';
END $$;
