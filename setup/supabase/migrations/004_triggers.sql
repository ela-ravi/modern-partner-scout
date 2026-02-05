-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_discovery_jobs_updated_at
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to auto-update profiles_discovered count
CREATE OR REPLACE FUNCTION update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE discovery_jobs
        SET profiles_discovered = profiles_discovered + 1
        WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE discovery_jobs
        SET profiles_discovered = profiles_discovered - 1
        WHERE id = OLD.job_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_discovered
    AFTER INSERT OR DELETE ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_discovered();

-- Function to auto-update profiles_scored count when status changes to 'done'
CREATE OR REPLACE FUNCTION update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE discovery_jobs
        SET profiles_scored = profiles_scored + 1
        WHERE id = NEW.job_id;
    ELSIF OLD.status = 'done' AND NEW.status != 'done' THEN
        UPDATE discovery_jobs
        SET profiles_scored = profiles_scored - 1
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_scored
    AFTER UPDATE OF status ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_scored();

-- Function to auto-complete job when all profiles scored
CREATE OR REPLACE FUNCTION auto_complete_job()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.profiles_discovered > 0
       AND NEW.profiles_scored >= NEW.profiles_discovered
       AND NEW.status != 'completed' THEN
        NEW.status = 'completed';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_complete_job
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION auto_complete_job();
-- ============================================================================
-- Migration 004: Triggers and Functions
-- PartnerScout AI - Supabase PostgreSQL Database
-- 
-- Auto-updating timestamps and denormalized counters.
-- Run after 001_initial_schema.sql
-- ============================================================================

-- ============================================================================
-- FUNCTION: Auto-update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Automatically updates updated_at on row modification';

-- Apply to discovery_jobs
CREATE TRIGGER trigger_discovery_jobs_updated_at
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FUNCTION: Auto-update profiles_discovered counter
-- Increments/decrements when profiles are added/removed
-- ============================================================================

CREATE OR REPLACE FUNCTION update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = profiles_discovered + 1,
            updated_at = NOW()
        WHERE id = NEW.job_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE discovery_jobs 
        SET profiles_discovered = GREATEST(0, profiles_discovered - 1),
            updated_at = NOW()
        WHERE id = OLD.job_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_profiles_discovered() IS 'Maintains denormalized profiles_discovered count';

CREATE TRIGGER trigger_update_profiles_discovered
    AFTER INSERT OR DELETE ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_discovered();

-- ============================================================================
-- FUNCTION: Auto-update profiles_scored counter
-- Increments when profile status changes to 'done'
-- ============================================================================

CREATE OR REPLACE FUNCTION update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment when profile changes to 'done'
    IF NEW.status = 'done' AND (OLD.status IS NULL OR OLD.status != 'done') THEN
        UPDATE discovery_jobs 
        SET profiles_scored = profiles_scored + 1,
            updated_at = NOW()
        WHERE id = NEW.job_id;
    -- Decrement when profile changes from 'done' to something else
    ELSIF OLD.status = 'done' AND NEW.status != 'done' THEN
        UPDATE discovery_jobs 
        SET profiles_scored = GREATEST(0, profiles_scored - 1),
            updated_at = NOW()
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_profiles_scored() IS 'Maintains denormalized profiles_scored count';

CREATE TRIGGER trigger_update_profiles_scored
    AFTER UPDATE OF status ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_scored();

-- ============================================================================
-- FUNCTION: Auto-complete job when all profiles scored
-- Updates job status to 'completed' when profiles_scored = profiles_discovered
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_complete_job()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if all profiles are scored
    IF NEW.profiles_scored > 0 
       AND NEW.profiles_scored >= NEW.profiles_discovered 
       AND NEW.status = 'scoring' THEN
        NEW.status = 'completed';
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION auto_complete_job() IS 'Auto-completes job when all profiles are scored';

CREATE TRIGGER trigger_auto_complete_job
    BEFORE UPDATE OF profiles_scored ON discovery_jobs
    FOR EACH ROW
    EXECUTE FUNCTION auto_complete_job();
