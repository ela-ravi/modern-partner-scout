-- ============================================================================
-- Migration: 003_enable_realtime.sql
-- Description: Enable Supabase Realtime for live updates
-- ============================================================================

-- ============================================================================
-- ADD TABLES TO REALTIME PUBLICATION
-- ============================================================================

-- Note: supabase_realtime publication is created by default in Supabase
-- We add our tables to it for real-time subscriptions

-- Discovery jobs - for status updates
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;

-- Discovered profiles - for new profiles appearing
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;

-- Profile scores - for score updates
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;

-- Profile contacts - for contact info updates
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify tables are added to realtime publication
-- Run this query to check:
-- SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';

DO $$
BEGIN
    RAISE NOTICE 'Realtime enabled for: discovery_jobs, discovered_profiles, profile_scores, profile_contacts';
    RAISE NOTICE 'Frontend can now subscribe to real-time changes on these tables.';
END $$;
