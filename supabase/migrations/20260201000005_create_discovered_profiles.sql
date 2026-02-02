-- Step 6: Create discovered_profiles Table
-- One row per Instagram profile per job (Discovery Agent output)

CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    followers INTEGER NOT NULL DEFAULT 0,
    following INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business BOOLEAN,
    external_url TEXT,
    business_email TEXT,
    business_category TEXT,
    following_ratio DECIMAL(5,2),
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, instagram_url)
);
