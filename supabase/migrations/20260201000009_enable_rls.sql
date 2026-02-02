-- Step 10: Enable Row Level Security
-- Users see only their own data; backend/n8n use service_role (bypasses RLS)

-- Enable RLS on all tables
ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- discovery_jobs: Direct user_id check
CREATE POLICY "Users can view own discovery_jobs" ON discovery_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own discovery_jobs" ON discovery_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own discovery_jobs" ON discovery_jobs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own discovery_jobs" ON discovery_jobs
    FOR DELETE USING (auth.uid() = user_id);

-- brand_dna: Access via job ownership
CREATE POLICY "Users can access brand_dna for their jobs" ON brand_dna
    FOR ALL USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

-- discovered_profiles: Access via job ownership
CREATE POLICY "Users can access profiles for their jobs" ON discovered_profiles
    FOR ALL USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

-- profile_scores: Access via profile → job ownership
CREATE POLICY "Users can access scores for their profiles" ON profile_scores
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );

-- profile_contacts: Access via profile → job ownership
CREATE POLICY "Users can access contacts for their profiles" ON profile_contacts
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );
