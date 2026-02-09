-- ============================================================================
-- Migration: 004_add_cover_and_posts_to_profiles.sql
-- Description: Add cover_image_url and recent_posts to discovered_profiles
-- ============================================================================

-- 1. Add new columns to discovered_profiles
ALTER TABLE discovered_profiles 
ADD COLUMN IF NOT EXISTS cover_image_url TEXT,
ADD COLUMN IF NOT EXISTS recent_posts JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN discovered_profiles.cover_image_url IS 'Instagram profile cover/header image URL';
COMMENT ON COLUMN discovered_profiles.recent_posts IS 'JSON array of recent posts (image_url, caption, engagement)';

-- 2. Refresh v_complete_profiles view to include new columns
OR REPLACE VIEW v_complete_profiles AS
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
    dp.cover_image_url, -- New column
    dp.recent_posts,    -- New column
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

COMMENT ON VIEW v_complete_profiles IS 'Complete profile view with scores, contacts, and UI visual assets';
