-- Step 11: Enable Realtime
-- Frontend can subscribe to INSERT/UPDATE/DELETE on these tables for live dashboard updates

ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;
