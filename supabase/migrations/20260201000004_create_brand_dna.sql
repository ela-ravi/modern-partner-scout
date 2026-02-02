-- Step 5: Create brand_dna Table
-- One-to-one with discovery_jobs: hashtags, keywords, embedding (Brand Analyzer output)

CREATE TABLE brand_dna (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    hashtags TEXT[] NOT NULL DEFAULT '{}',
    keywords TEXT[] NOT NULL DEFAULT '{}',
    embedding_vector vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_brand_dna UNIQUE (job_id)
);
