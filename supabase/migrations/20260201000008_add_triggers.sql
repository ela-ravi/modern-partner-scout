-- Step 9: Add Triggers
-- Auto-update updated_at on jobs; maintain profiles_discovered and profiles_scored counters

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to discovery_jobs
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

-- Function to auto-update profiles_scored count when profile status changes to 'done'
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
