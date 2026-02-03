---
name: supabase-operations
description: Design and operate Supabase PostgreSQL database with proper schema, RLS policies, and client operations. Use this skill when working with database tables, migrations, queries, realtime subscriptions, or TypeScript/Python clients for PartnerScout.
---

This skill guides Supabase database operations for PartnerScout, including schema design, RLS policies, triggers, and client usage.

## Database Schema

### Entity Relationships

```
discovery_jobs (Parent)
    │
    ├── brand_dna (1:1)
    │
    └── discovered_profiles (1:many)
            │
            ├── profile_scores (1:1)
            │
            └── profile_contacts (1:1)
```

### Core Tables

**discovery_jobs** - Discovery sessions
```sql
CREATE TABLE discovery_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    brand_description TEXT NOT NULL,
    reference_profiles TEXT[] NOT NULL DEFAULT '{}',
    status discovery_job_status NOT NULL DEFAULT 'pending',
    profiles_discovered INTEGER NOT NULL DEFAULT 0,
    profiles_scored INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE discovery_job_status AS ENUM (
    'pending', 'analyzing', 'discovering', 'scoring', 'completed', 'failed'
);
```

**discovered_profiles** - Found Instagram profiles
```sql
CREATE TABLE discovered_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES discovery_jobs(id) ON DELETE CASCADE,
    instagram_url TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT,
    profile_picture_url TEXT,
    bio TEXT,
    followers INTEGER NOT NULL DEFAULT 0,
    following INTEGER,
    posts_count INTEGER,
    engagement_rate DECIMAL(5,2),
    is_verified BOOLEAN NOT NULL DEFAULT false,
    is_business BOOLEAN,
    external_url TEXT,
    business_email TEXT,
    business_category TEXT,
    following_ratio DECIMAL(5,2),
    status profile_status NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_per_job UNIQUE (job_id, instagram_url)
);

CREATE TYPE profile_status AS ENUM ('new', 'processing', 'done', 'skipped');
```

**profile_scores** - AI scoring results
```sql
CREATE TABLE profile_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES discovered_profiles(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    visual_aesthetic_match INTEGER CHECK (visual_aesthetic_match >= 0 AND visual_aesthetic_match <= 100),
    content_theme_alignment INTEGER CHECK (content_theme_alignment >= 0 AND content_theme_alignment <= 100),
    engagement_rate_score INTEGER CHECK (engagement_rate_score >= 0 AND engagement_rate_score <= 100),
    follower_quality INTEGER CHECK (follower_quality >= 0 AND follower_quality <= 100),
    business_indicators INTEGER CHECK (business_indicators >= 0 AND business_indicators <= 100),
    activity_recency INTEGER CHECK (activity_recency >= 0 AND activity_recency <= 100),
    reasoning JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_profile_score UNIQUE (profile_id)
);
```

## Indexes

Always index foreign keys and common query columns:

```sql
-- Foreign key indexes
CREATE INDEX idx_discovered_profiles_job_id ON discovered_profiles(job_id);
CREATE INDEX idx_profile_scores_profile_id ON profile_scores(profile_id);

-- Query indexes
CREATE INDEX idx_discovery_jobs_user_id ON discovery_jobs(user_id);
CREATE INDEX idx_discovery_jobs_status ON discovery_jobs(status);
CREATE INDEX idx_discovered_profiles_status ON discovered_profiles(status);
CREATE INDEX idx_profile_scores_score ON profile_scores(score DESC);
```

## Row Level Security (RLS)

Enable RLS and create policies for user isolation:

```sql
-- Enable RLS
ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- Direct user_id check
CREATE POLICY "Users can access own jobs" ON discovery_jobs
    FOR ALL USING (auth.uid() = user_id);

-- Access via job ownership
CREATE POLICY "Users can access profiles for their jobs" ON discovered_profiles
    FOR ALL USING (
        job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
    );

-- Access via profile -> job ownership
CREATE POLICY "Users can access scores for their profiles" ON profile_scores
    FOR ALL USING (
        profile_id IN (
            SELECT id FROM discovered_profiles 
            WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
        )
    );
```

## Triggers

Auto-update timestamps and counters:

```sql
-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_discovery_jobs_updated_at
    BEFORE UPDATE ON discovery_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-increment profiles_discovered
CREATE OR REPLACE FUNCTION update_profiles_discovered()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE discovery_jobs SET profiles_discovered = profiles_discovered + 1
        WHERE id = NEW.job_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE discovery_jobs SET profiles_discovered = profiles_discovered - 1
        WHERE id = OLD.job_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_profiles_discovered
    AFTER INSERT OR DELETE ON discovered_profiles
    FOR EACH ROW EXECUTE FUNCTION update_profiles_discovered();
```

## Enable Realtime

```sql
ALTER PUBLICATION supabase_realtime ADD TABLE discovered_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE profile_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE discovery_jobs;
```

## Python Client (Backend)

```python
# backend/app/db/supabase.py
from supabase import create_client, Client
from app.core.config import settings

_supabase: Client = None

def get_db() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _supabase
```

**CRUD Operations:**
```python
# CREATE
result = db.table("discovery_jobs").insert({
    "user_id": user_id,
    "brand_description": "...",
    "reference_profiles": ["url1", "url2"],
    "status": "pending"
}).execute()
job = result.data[0]

# READ with joins
result = db.table("discovered_profiles").select(
    "*, profile_scores(*), profile_contacts(*)"
).eq("job_id", job_id).execute()

# UPDATE
db.table("discovery_jobs").update({
    "status": "completed"
}).eq("id", job_id).execute()

# DELETE (cascades to children)
db.table("discovery_jobs").delete().eq("id", job_id).execute()

# UPSERT
db.table("profile_scores").upsert({
    "profile_id": profile_id,
    "score": 85,
    "reasoning": {"summary": "Good match"}
}).execute()
```

## TypeScript Client (Frontend)

```typescript
// frontend/src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

**TypeScript Types:**
```typescript
// frontend/src/types/database.types.ts
export type JobStatus = 'pending' | 'analyzing' | 'discovering' | 'scoring' | 'completed' | 'failed';
export type ProfileStatus = 'new' | 'processing' | 'done' | 'skipped';

export interface DiscoveryJob {
  id: string;
  user_id: string;
  name: string | null;
  brand_description: string;
  status: JobStatus;
  profiles_discovered: number;
  profiles_scored: number;
  created_at: string;
  updated_at: string;
}

export interface DiscoveredProfile {
  id: string;
  job_id: string;
  instagram_url: string;
  username: string;
  full_name: string | null;
  profile_picture_url: string | null;
  bio: string | null;
  followers: number;
  following: number | null;
  engagement_rate: number | null;
  is_business: boolean | null;
  status: ProfileStatus;
}

export interface ProfileScore {
  id: string;
  profile_id: string;
  score: number;
  visual_aesthetic_match: number | null;
  content_theme_alignment: number | null;
  follower_quality: number | null;
  reasoning: { summary: string; recommendation: string };
}
```

## Realtime Subscriptions

```typescript
// frontend/src/hooks/useRealtimeProfiles.ts
import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { DiscoveredProfile } from '../types/database.types'

export function useRealtimeProfiles(jobId: string) {
  const [profiles, setProfiles] = useState<DiscoveredProfile[]>([])

  useEffect(() => {
    // Initial fetch
    const fetchProfiles = async () => {
      const { data } = await supabase
        .from('discovered_profiles')
        .select('*')
        .eq('job_id', jobId)
      if (data) setProfiles(data)
    }
    fetchProfiles()

    // Subscribe to changes
    const channel = supabase
      .channel(`profiles-${jobId}`)
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'discovered_profiles',
        filter: `job_id=eq.${jobId}`
      }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setProfiles(prev => [...prev, payload.new as DiscoveredProfile])
        } else if (payload.eventType === 'UPDATE') {
          setProfiles(prev => prev.map(p => 
            p.id === payload.new.id ? payload.new as DiscoveredProfile : p
          ))
        }
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [jobId])

  return profiles
}
```

## Common Query Patterns

```sql
-- Get profiles with scores, sorted by score
SELECT dp.*, ps.score, ps.reasoning, pc.email
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id
WHERE dp.job_id = $1 AND dp.status = 'done'
ORDER BY ps.score DESC NULLS LAST;

-- Job analytics
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'done') AS done_count,
    AVG(ps.score)::INTEGER AS avg_score
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
WHERE dp.job_id = $1;
```

## Dependencies

Backend:
```
supabase>=2.0.0
```

Frontend:
```
@supabase/supabase-js
```

## Best Practices

1. **Always index FKs**: PostgreSQL doesn't auto-index foreign keys
2. **Use CASCADE**: ON DELETE CASCADE for child tables
3. **Enable RLS before production**: Data is public without it
4. **Add to realtime publication**: Required for subscriptions
5. **Use service role key server-side**: Anon key is limited by RLS
6. **Denormalize counters**: Use triggers for fast dashboard queries
