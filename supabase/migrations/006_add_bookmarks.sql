-- ============================================================================
-- Migration: 006_add_bookmarks.sql
-- Description: Add bookmark support to discovered_profiles
-- Purpose: Allow users to bookmark profiles for later review
-- ============================================================================

-- Add is_bookmarked column (defaults to false)
ALTER TABLE discovered_profiles
ADD COLUMN IF NOT EXISTS is_bookmarked BOOLEAN NOT NULL DEFAULT false;

-- Partial index for fast bookmark filtering
CREATE INDEX IF NOT EXISTS idx_discovered_profiles_bookmarked
ON discovered_profiles(is_bookmarked) WHERE is_bookmarked = true;

-- Add comment
COMMENT ON COLUMN discovered_profiles.is_bookmarked IS 'Whether the user has bookmarked this profile for later review';

-- ============================================================================
-- Recreate v_complete_profiles view to include is_bookmarked
-- ============================================================================

DROP VIEW IF EXISTS v_complete_profiles;
CREATE VIEW v_complete_profiles AS
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

COMMENT ON VIEW v_complete_profiles IS 'Complete profile view with scores, contacts, and bookmark status';

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
    AND table_name = 'discovered_profiles'
    AND column_name = 'is_bookmarked';

    IF col_count != 1 THEN
        RAISE EXCEPTION 'Expected is_bookmarked column, not found';
    END IF;

    RAISE NOTICE 'Migration 006 completed successfully! Added is_bookmarked column and updated views.';
END $$;
