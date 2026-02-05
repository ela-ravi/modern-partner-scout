-- Add tables to realtime publication
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

-- Verify with:
-- SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
-- ============================================================================
-- Migration 005: Enable Realtime Subscriptions
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Adds tables to Supabase realtime publication for live dashboard updates.
-- Run after all other migrations.
-- ============================================================================

-- ============================================================================
-- ENABLE REALTIME FOR DASHBOARD TABLES
-- These tables will broadcast changes via WebSocket to connected clients.
-- ============================================================================

-- Discovery jobs - for status updates and progress
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;

-- Discovered profiles - for real-time profile appearance
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;

-- Profile scores - for score updates as they complete
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;

-- Profile contacts - for email extraction notifications
ALTER PUBLICATION supabase_realtime ADD TABLE profile_contacts;

-- ============================================================================
-- VERIFICATION QUERY
-- Run this to verify tables are in the realtime publication:
-- 
-- SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';
-- ============================================================================

-- ============================================================================
-- NOTES ON REALTIME USAGE
-- ============================================================================

-- Frontend subscription example:
--
-- const channel = supabase
--   .channel('profiles-changes')
--   .on(
--     'postgres_changes',
--     {
--       event: '*',
--       schema: 'public',
--       table: 'discovered_profiles',
--       filter: `job_id=eq.${jobId}`,
--     },
--     (payload) => {
--       // Handle INSERT, UPDATE, DELETE events
--     }
--   )
--   .subscribe()
--
-- Remember to unsubscribe when component unmounts:
-- supabase.removeChannel(channel)
