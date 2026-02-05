# Supabase Migrations

These SQL files set up the PartnerScout AI schema in Supabase.

## Order
Run the migrations in order:

1. `001_initial_schema.sql`
2. `002_indexes.sql`
3. `003_rls_policies.sql`
4. `004_triggers.sql`
5. `005_realtime.sql`
6. `006_views.sql`
7. `007_seed.sql` (optional for demo data)

## Running in Supabase
Use the Supabase SQL Editor and run each file in order. The seed file is optional
and intended for demo/testing data.

## Notes
- Requires `vector`, `uuid-ossp`, and `pgcrypto` extensions.
- RLS is enabled for all tables. Use the service role key for backend operations.
# Supabase Migrations

SQL migration files for PartnerScout AI PostgreSQL database.

## Migration Order

Run these migrations in order in your Supabase SQL Editor:

| # | File | Description |
|---|------|-------------|
| 1 | `001_initial_schema.sql` | Tables, enums, constraints |
| 2 | `002_indexes.sql` | Performance indexes |
| 3 | `003_rls_policies.sql` | Row Level Security |
| 4 | `004_triggers.sql` | Auto-update timestamps & counters |
| 5 | `005_realtime.sql` | Enable realtime subscriptions |
| 6 | `006_views.sql` | Convenience views |
| 7 | `007_seed.sql` | Demo/test data (optional) |

## Quick Start

### Option 1: Supabase Dashboard

1. Go to your Supabase project → SQL Editor
2. Copy & paste each migration file in order
3. Run each one

### Option 2: Supabase CLI

```bash
# Install CLI
npm install -g supabase

# Login and link project
supabase login
supabase link --project-ref YOUR_PROJECT_REF

# Push all migrations
supabase db push
```

### Option 3: Direct PostgreSQL

```bash
# Concatenate all migrations
cat 001_initial_schema.sql 002_indexes.sql 003_rls_policies.sql \
    004_triggers.sql 005_realtime.sql 006_views.sql > all_migrations.sql

# Run against your database
psql $DATABASE_URL -f all_migrations.sql
```

## Tables Created

```
discovery_jobs          # Parent table - user sessions
├── brand_dna          # 1:1 - extracted brand identity
└── discovered_profiles # 1:many - found Instagram profiles
    ├── profile_scores # 1:1 - AI scoring (6 dimensions)
    └── profile_contacts # 1:1 - extracted emails
```

## PRD Reference

- **PRD 10.3**: discovery_jobs schema
- **PRD 10.4**: brand_dna schema
- **PRD 10.5**: discovered_profiles schema
- **PRD 10.6**: profile_scores (6 scoring dimensions)
- **PRD 10.7**: profile_contacts schema
- **PRD 5.3**: Scoring dimensions and weights
- **PRD 5.3.1**: Fake detection signals
- **PRD 6**: Multi-user data isolation (RLS)

## Seed Data

The `007_seed.sql` file contains demo data matching the PRD:

- 1 completed job with 5 profiles
- 3 additional jobs (pending, scoring, failed)
- Mix of genuine and fake profiles for testing
- All 6 scoring dimensions populated
- Contact emails for genuine profiles

**Note**: Update the `user_id` in seed data to match a real auth.users UUID from your Supabase Auth.

## Verification Queries

After running migrations, verify with:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public';

-- Check realtime is enabled
SELECT * FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime';

-- Test views
SELECT * FROM v_job_summary LIMIT 5;
SELECT * FROM v_complete_profiles LIMIT 5;
```

## Rollback

To reset the database:

```sql
-- Drop all tables (cascades to dependent objects)
DROP TABLE IF EXISTS profile_contacts CASCADE;
DROP TABLE IF EXISTS profile_scores CASCADE;
DROP TABLE IF EXISTS discovered_profiles CASCADE;
DROP TABLE IF EXISTS brand_dna CASCADE;
DROP TABLE IF EXISTS discovery_jobs CASCADE;

-- Drop enums
DROP TYPE IF EXISTS discovery_job_status CASCADE;
DROP TYPE IF EXISTS profile_status CASCADE;

-- Drop views
DROP VIEW IF EXISTS v_complete_profiles CASCADE;
DROP VIEW IF EXISTS v_job_summary CASCADE;
DROP VIEW IF EXISTS v_high_score_profiles CASCADE;
DROP VIEW IF EXISTS v_suspicious_profiles CASCADE;
```
