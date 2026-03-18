# Supabase Setup Guide for PartnerScout AI

This guide walks you through setting up Supabase for the PartnerScout AI project.

## Step 1: Create Supabase Account & Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click **"New Project"**
3. Fill in the project details:
   - **Name:** `partnerscout-ai` (or your preferred name)
   - **Database Password:** Generate a strong password (save this!)
   - **Region:** Choose the closest region to your users
   - **Pricing Plan:** Free tier is sufficient for development
4. Click **"Create new project"** and wait for provisioning (~2 minutes)

## Step 2: Get Your Project Credentials

Once your project is ready, go to **Project Settings** > **API** to find:

| Credential | Location | Description |
|------------|----------|-------------|
| **Project URL** | Project URL | `https://xxxxx.supabase.co` |
| **Anon Key** | Project API Keys > anon public | Public key for client-side |
| **Service Role Key** | Project API Keys > service_role | Private key for server-side (keep secret!) |

Go to **Project Settings** > **API** > **JWT Settings** to find:
| Credential | Location | Description |
|------------|----------|-------------|
| **JWT Secret** | JWT Secret | Used for token verification |

## Step 3: Enable pgvector Extension

1. Go to **Database** > **Extensions** in your Supabase dashboard
2. Search for `vector`
3. Toggle **ON** the `vector` extension
4. This enables vector similarity search for AI embeddings

Or run this SQL in the **SQL Editor**:

```sql
-- Enable pgvector extension for embedding storage
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 4: Update Environment Files

### Backend (.env)

Update `backend/.env` with your credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### Frontend (.env)

Update `frontend/.env` with your credentials:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## Step 5: Apply Database Migrations

After configuring credentials, run the migrations in order:

1. Go to **SQL Editor** in Supabase dashboard
2. Run each migration file in the `migrations/` folder in order:
   - `001_initial_schema.sql` - Creates all tables
   - `002_enable_rls.sql` - Enables Row Level Security
   - `003_enable_realtime.sql` - Enables realtime subscriptions
   - `004_job_creation_enhancements.sql` - Adds keywords, hashtags, min_score_threshold
   - `005_add_target_country.sql` - Adds target_country, enhanced v_job_summary view
   - `006_add_bookmarks.sql` - Adds is_bookmarked to discovered_profiles, updates views

## Step 6: (Optional) Seed Development Data

For development/testing, run the seed file:

```sql
-- Run in SQL Editor
-- Contents of seed.sql
```

## Security Notes

- **NEVER** commit `.env` files to version control
- **NEVER** expose the `service_role` key in client-side code
- The `anon` key is safe for client-side use (with RLS enabled)
- Always use RLS policies to protect data

## Verification

After setup, verify your connection:

### Backend Test
```bash
cd backend
.\venv\Scripts\Activate.ps1
python -c "from supabase import create_client; import os; print(create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY')))"
```

### Frontend Test
The app should connect automatically when you run `npm run dev`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if URL is correct and project is active |
| 401 Unauthorized | Verify API keys are correct |
| RLS policy error | Ensure user is authenticated for protected tables |
| pgvector not found | Enable the vector extension in dashboard |

---

For more information, see the [Supabase Documentation](https://supabase.com/docs).
