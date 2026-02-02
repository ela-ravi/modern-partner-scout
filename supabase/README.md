# PartnerScout AI – Supabase Database

Phase 1 database migrations for PartnerScout AI. Canonical plan: **[docs/Database_Implementation_Jira_Plan.md](../docs/Database_Implementation_Jira_Plan.md)** (Jira: DB-EPIC-001). Same 11 steps as [docs/Database_Implementation_Step_By_Step.md](../docs/Database_Implementation_Step_By_Step.md). Run migrations after completing **Step 1** (Create Supabase project) — see Jira **DB-TASK-001** or Step-by-Step guide.

## Step → Task → Migration

| Step | Jira Task | Migration file |
|------|-----------|----------------|
| 1 | DB-TASK-001 | Manual (Supabase project creation) |
| 2 | DB-TASK-002 | `20260201000001_enable_extensions.sql` |
| 3 | DB-TASK-003 | `20260201000002_create_enum_types.sql` |
| 4 | DB-TASK-004 | `20260201000003_create_discovery_jobs.sql` |
| 5 | DB-TASK-005 | `20260201000004_create_brand_dna.sql` |
| 6 | DB-TASK-006 | `20260201000005_create_discovered_profiles.sql` |
| 7 | DB-TASK-007 | `20260201000006_create_profile_scores_and_contacts.sql` |
| 8 | DB-TASK-008 | `20260201000007_add_indexes.sql` |
| 9 | DB-TASK-009 | `20260201000008_add_triggers.sql` |
| 10 | DB-TASK-010 | `20260201000009_enable_rls.sql` |
| 11 | DB-TASK-011 | `20260201000010_enable_realtime.sql` |

## Running migrations

### Option A: Supabase SQL Editor (manual)

1. In the [Supabase Dashboard](https://supabase.com/dashboard), open your project.
2. Go to **SQL Editor** → **New query**.
3. Run each file in `migrations/` in order (oldest timestamp first):
   - `20260201000001_enable_extensions.sql`
   - `20260201000002_create_enum_types.sql`
   - … through `20260201000010_enable_realtime.sql`
4. After each file, confirm success (e.g. “Success. No rows returned” or table/object created).

### Option B: Supabase CLI (if linked)

From the project root:

```bash
supabase db push
```

Or run migrations manually with `supabase db execute` and the migration file paths.

## Verification

- **Step 2**: Database → Extensions → `vector`, `uuid-ossp`.
- **Step 3**: Database → Types → `discovery_job_status`, `profile_status`.
- **Steps 4–7**: Table Editor → all five tables and expected columns.
- **Step 8**: Each table → Indexes tab.
- **Step 9**: Database → Functions; each table → Triggers tab.
- **Step 10**: Tables → RLS tab; policies visible.
- **Step 11**: Run `SELECT * FROM pg_publication_tables WHERE pubname = 'supabase_realtime';` — should list `discovery_jobs`, `discovered_profiles`, `profile_scores`, `profile_contacts`.

## Schema

```
auth.users (Supabase Auth)
    └── discovery_jobs (1:many, user_id FK)
            ├── brand_dna (1:1, job_id FK)
            └── discovered_profiles (1:many, job_id FK)
                    ├── profile_scores (1:1, profile_id FK)
                    └── profile_contacts (1:1, profile_id FK)
```
