-- Step 7: Create profile_scores and profile_contacts Tables
-- One-to-one per discovered profile (Scorer Agent output)

CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100),
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),
    reasoning JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);

CREATE TABLE profile_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    email TEXT,
    source TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_contact UNIQUE (profile_id)
);
