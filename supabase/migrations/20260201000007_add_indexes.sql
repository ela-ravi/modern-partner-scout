-- Step 8: Add Indexes
-- Speed up queries on FKs and common filters (user, job, status, created_at, score, followers)

CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovery_jobs_created_at ON discovery_jobs(created_at DESC);
CREATE INDEX idx_brand_dna_job_id ON brand_dna(job_id);
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_discovered_profiles_followers ON discovered_profiles(followers DESC);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
CREATE INDEX idx_profile_contacts_profile_id ON profile_contacts(profile_id);
