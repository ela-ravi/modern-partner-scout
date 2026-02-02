-- ============================================================================
-- Migration: 000_enable_extensions.sql
-- Description: Enable required PostgreSQL extensions for PartnerScout AI
-- ============================================================================

-- Enable pgvector extension for AI embedding storage and similarity search
-- This must be run before creating tables with vector columns
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation (usually enabled by default in Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extensions are enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'pgvector extension is not installed';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        RAISE EXCEPTION 'uuid-ossp extension is not installed';
    END IF;
    
    RAISE NOTICE 'All required extensions are enabled successfully!';
END $$;
