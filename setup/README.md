# PartnerScout AI - Setup Guide

This folder contains all setup-related assets for PartnerScout AI.

## Contents

```
setup/
├── scripts/
│   ├── seed_database.py      # Seed database with mock data
│   ├── validate_epic1.py     # Validate Epic 1 (Foundation)
│   └── validate_epic2.py     # Validate Epic 2 (Database Layer)
├── supabase/
│   ├── migrations/           # Individual SQL migration files
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_indexes.sql
│   │   ├── 003_rls_policies.sql
│   │   ├── 004_triggers.sql
│   │   ├── 005_realtime.sql
│   │   ├── 006_views.sql
│   │   └── 007_seed.sql
│   └── all_migrations.sql    # Single consolidated file (recommended)
├── sync_env.sh               # Environment sync helper
└── README.md                 # This file
```

---

## 1. Environment Setup

### Backend Environment

1. Create `.env.local` in the `backend/` directory:

```bash
cd backend
cat > .env.local << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM Provider (openai | gemini | ollama)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key

# Optional: Use SQLite for local development without Supabase
USE_SQLITE_FALLBACK=false
EOF
```

2. Install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

---

## 2. Database Setup (Supabase)

### Option A: Single File (Recommended)

1. Open your Supabase project's SQL Editor
2. Copy the contents of `setup/supabase/all_migrations.sql`
3. Paste and run in the SQL Editor
4. All tables, indexes, RLS policies, triggers, and views will be created

### Option B: Individual Migrations

Run each file in order in the SQL Editor:

1. `001_initial_schema.sql` - Tables and types
2. `002_indexes.sql` - Performance indexes
3. `003_rls_policies.sql` - Row Level Security
4. `004_triggers.sql` - Auto-update triggers
5. `005_realtime.sql` - WebSocket subscriptions
6. `006_views.sql` - Convenience views
7. `007_seed.sql` - Demo data (optional)

### Verify Setup

Run these queries in Supabase SQL Editor:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' AND rowsecurity = true;

-- Check views
SELECT * FROM v_job_summary LIMIT 5;
```

---

## 3. Local SQLite Fallback

For development without Supabase:

1. Set `USE_SQLITE_FALLBACK=true` in `.env.local`
2. The database will be created at `backend/data/partner_scout.db`

---

## 4. Seed Database

Populate the database with test data:

```bash
cd backend

# Seed all tables
python ../setup/scripts/seed_database.py

# Clear and reseed
python ../setup/scripts/seed_database.py --reset

# Seed specific tables only
python ../setup/scripts/seed_database.py --tables users,discovery_jobs

# Verify seeded data
python ../setup/scripts/seed_database.py --verify
```

---

## 5. Validation Scripts

### Validate Epic 1 (Foundation)

```bash
cd backend
python ../setup/scripts/validate_epic1.py
```

Checks:
- Project structure
- Configuration loading
- Exception handling
- Logging setup

### Validate Epic 2 (Database Layer)

```bash
cd backend
python ../setup/scripts/validate_epic2.py
```

Checks:
- Database client (Supabase/SQLite)
- Pydantic models
- Repository pattern
- Unit and integration tests
- Type checking (mypy)
- Mock data fixtures

---

## 6. Running the Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

---

## 7. Troubleshooting

### "Cannot connect to Supabase"
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`
- Ensure your IP is not blocked in Supabase network settings

### "Module not found" errors
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "RLS policy violation"
- Ensure you're using the service role key (bypasses RLS) for backend operations
- For frontend, ensure the user is authenticated

### SQLite "table has no column" errors
- Delete `backend/data/partner_scout.db` and restart
- The schema will be recreated automatically

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start backend | `cd backend && uvicorn app.main:app --reload` |
| Run tests | `cd backend && pytest` |
| Type check | `cd backend && mypy app` |
| Seed database | `python setup/scripts/seed_database.py --reset` |
| Validate Epic 2 | `python setup/scripts/validate_epic2.py` |
