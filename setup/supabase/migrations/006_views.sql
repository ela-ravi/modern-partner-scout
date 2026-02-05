-- Complete profile view with scores and contacts
CREATE OR REPLACE VIEW v_complete_profiles AS
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
    pc.source AS email_source,
    pc.confidence AS email_confidence
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

-- Job summary with statistics
CREATE OR REPLACE VIEW v_job_summary AS
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
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    AVG(ps.score)::INTEGER AS avg_score,
    MAX(ps.score) AS max_score,
    COUNT(pc.email) AS profiles_with_email
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id AND pc.email IS NOT NULL
GROUP BY dj.id;

-- High score profiles (score >= 70)
CREATE OR REPLACE VIEW v_high_score_profiles AS
SELECT *
FROM v_complete_profiles
WHERE score >= 70;

-- Suspicious profiles (low follower_quality)
CREATE OR REPLACE VIEW v_suspicious_profiles AS
SELECT *
FROM v_complete_profiles
WHERE follower_quality IS NOT NULL AND follower_quality < 30;
-- ============================================================================
-- Migration 006: Convenience Views
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Creates views for common query patterns to simplify frontend/backend code.
-- Run after all table migrations.
-- ============================================================================

-- ============================================================================
-- VIEW: v_complete_profiles
-- Complete profile with score and contact info joined
-- ============================================================================

CREATE OR REPLACE VIEW v_complete_profiles AS
SELECT 
    -- Profile fields
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
    
    -- Score fields
    ps.score,
    ps.visual_aesthetic_match,
    ps.content_theme_alignment,
    ps.engagement_rate_score,
    ps.follower_quality,
    ps.business_indicators,
    ps.activity_recency,
    ps.reasoning,
    
    -- Contact fields
    pc.email,
    pc.source AS email_source
    
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;

COMMENT ON VIEW v_complete_profiles IS 'Complete profile with score and contact for dashboard display';

-- ============================================================================
-- VIEW: v_job_summary
-- Job with aggregated statistics
-- ============================================================================

CREATE OR REPLACE VIEW v_job_summary AS
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
    
    -- Aggregated stats
    COUNT(dp.id) AS total_profiles,
    COUNT(CASE WHEN dp.status = 'new' THEN 1 END) AS new_profiles,
    COUNT(CASE WHEN dp.status = 'processing' THEN 1 END) AS processing_profiles,
    COUNT(CASE WHEN dp.status = 'done' THEN 1 END) AS done_profiles,
    COUNT(CASE WHEN dp.status = 'skipped' THEN 1 END) AS skipped_profiles,
    
    -- Score stats
    COALESCE(AVG(ps.score)::INTEGER, 0) AS avg_score,
    MAX(ps.score) AS max_score,
    MIN(ps.score) AS min_score,
    
    -- Score distribution
    COUNT(CASE WHEN ps.score >= 80 THEN 1 END) AS excellent_count,
    COUNT(CASE WHEN ps.score >= 60 AND ps.score < 80 THEN 1 END) AS good_count,
    COUNT(CASE WHEN ps.score >= 40 AND ps.score < 60 THEN 1 END) AS moderate_count,
    COUNT(CASE WHEN ps.score < 40 THEN 1 END) AS poor_count,
    
    -- Contact stats
    COUNT(pc.email) FILTER (WHERE pc.email IS NOT NULL) AS profiles_with_email
    
FROM discovery_jobs dj
LEFT JOIN discovered_profiles dp ON dj.id = dp.job_id
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
GROUP BY dj.id;

COMMENT ON VIEW v_job_summary IS 'Job with aggregated statistics for dashboard';

-- ============================================================================
-- VIEW: v_high_score_profiles
-- Profiles with score >= 70 (recommended for outreach)
-- ============================================================================

CREATE OR REPLACE VIEW v_high_score_profiles AS
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

COMMENT ON VIEW v_high_score_profiles IS 'High-quality profiles (score >= 70) for outreach';

-- ============================================================================
-- VIEW: v_suspicious_profiles
-- Profiles with low follower_quality (potential fakes per PRD 5.3.1)
-- ============================================================================

CREATE OR REPLACE VIEW v_suspicious_profiles AS
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
    
    -- Fake detection flags (PRD 5.3.1)
    CASE WHEN dp.following_ratio > 2.0 THEN true ELSE false END AS high_following_ratio,
    CASE WHEN dp.posts_count < 20 AND dp.followers > 5000 THEN true ELSE false END AS low_post_ratio,
    CASE WHEN dp.engagement_rate < 1.0 THEN true ELSE false END AS low_engagement,
    CASE WHEN dp.is_business = false THEN true ELSE false END AS not_business
    
FROM discovered_profiles dp
INNER JOIN profile_scores ps ON dp.id = ps.profile_id
INNER JOIN discovery_jobs dj ON dp.job_id = dj.id
WHERE ps.follower_quality < 50
ORDER BY ps.follower_quality ASC;

COMMENT ON VIEW v_suspicious_profiles IS 'Profiles flagged as potentially fake (PRD 5.3.1)';
