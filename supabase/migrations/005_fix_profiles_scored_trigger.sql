-- Migration: Fix profiles_scored trigger to use 'scored' status instead of 'done'
-- The Python code uses ProfileStatus.SCORED = 'scored', but the trigger was looking for 'done'

-- Drop old trigger and function
DROP TRIGGER IF EXISTS trigger_update_profiles_scored ON discovered_profiles;
DROP FUNCTION IF EXISTS update_profiles_scored();

-- Recreate with correct status value 'scored'
CREATE OR REPLACE FUNCTION update_profiles_scored()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment when status changes to 'scored'
    IF NEW.status = 'scored' AND (OLD.status IS NULL OR OLD.status != 'scored') THEN
        UPDATE discovery_jobs
        SET profiles_scored = profiles_scored + 1
        WHERE id = NEW.job_id;
    -- Decrement if status changes away from 'scored'
    ELSIF OLD.status = 'scored' AND NEW.status != 'scored' THEN
        UPDATE discovery_jobs
        SET profiles_scored = profiles_scored - 1
        WHERE id = NEW.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Recreate trigger
CREATE TRIGGER trigger_update_profiles_scored
    AFTER INSERT OR UPDATE OF status ON discovered_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_profiles_scored();

-- Also fix existing data: Count profiles that are already scored but weren't counted
UPDATE discovery_jobs dj
SET profiles_scored = (
    SELECT COUNT(*)
    FROM discovered_profiles dp
    WHERE dp.job_id = dj.id
    AND dp.status = 'scored'
);
