-- Step 4: Create discovery_jobs Table
-- Parent table: one row per discovery session, linked to auth.users

CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
