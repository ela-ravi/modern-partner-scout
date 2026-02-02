-- Step 3: Create Enum Types
-- discovery_job_status: job lifecycle; profile_status: profile processing state

CREATE TYPE discovery_job_status AS ENUM (
    'pending',
    'analyzing',
    'discovering',
    'scoring',
    'completed',
    'failed'
);

CREATE TYPE profile_status AS ENUM (
    'new',
    'processing',
    'done',
    'skipped'
);
