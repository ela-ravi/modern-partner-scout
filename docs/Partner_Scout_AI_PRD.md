# PartnerScout AI – Product Requirements Document (PRD)

## Version

**v1.0 – Hackathon Build (24 Hours)**

## Author

Team PartnerScout AI

## Last Updated

February 2026

---

## 1. Product Overview

### 1.1 Product Name

**PartnerScout AI**

### 1.2 Problem Statement

Brands spend **10–15 hours per week manually searching Instagram** to identify suitable boutique partners or influencers. This process is:

* Manual and time-consuming
* Subjective and inconsistent
* Hard to scale
* Poorly documented

### 1.3 Solution

PartnerScout AI automates partner discovery by:

* Learning a brand’s “DNA” from reference profiles
* Discovering similar Instagram profiles
* Scoring and ranking them using AI
* Extracting contact details
* Presenting results in a real-time dashboard

### 1.4 Target Users

* D2C Brand Founders
* Marketing Managers
* Influencer / Partnership Teams
* Growth Consultants

---

## 2. Goals & Success Metrics

### 2.1 Primary Goals

* Reduce partner discovery time from hours → minutes
* Deliver ranked, explainable partner recommendations
* Provide a working end-to-end demo within 24 hours

### 2.2 Success Metrics

| Metric                      | Target                |
| --------------------------- | --------------------- |
| Time to discover partners   | < 15 minutes          |
| Qualified profiles found    | ≥ 40                  |
| Match accuracy (subjective) | ≥ 70%                 |
| End-to-end workflow success | 100% demo reliability |

---

## 3. Scope

### 3.1 In Scope (Hackathon MVP)

* Brand DNA extraction from reference profiles
* Instagram profile discovery
* AI-based profile scoring
* Contact extraction (email)
* Real-time dashboard
* Manual email trigger
* n8n-based orchestration
* User authentication (Supabase Auth)
* Multi-user session management

### 3.2 Out of Scope

* Automated email sending (mock only)
* Multi-platform discovery (TikTok, LinkedIn)
* Billing or payments
* Production-grade scraping reliability

---

## 4. User Journey

1. User signs up / logs in (Supabase Auth)
2. User sees their dashboard with past discovery sessions
3. User creates new discovery:

   * Brand description
   * 2–10 reference Instagram profiles
4. User clicks **Start Discovery**
5. System:

   * Analyzes brand DNA
   * Discovers similar profiles
   * Scores and ranks them
6. User sees:

   * Profiles appearing in real-time
   * Match scores and reasoning
   * Contact email (if available)
7. User optionally:

   * Reviews profiles
   * Clicks "Send Email" (mock)
8. User can return later to view past sessions and results

---

## 5. Functional Requirements

### 5.1 Brand Analyzer Agent

**Purpose:** Learn brand identity

**Inputs:**

* Reference profile URLs
* Brand description text

**Outputs:**

* Visual features
* Keywords & hashtags
* Embedding vector (“Brand DNA”)

---

### 5.2 Profile Discovery Agent

**Purpose:** Find candidate profiles

**Inputs:**

* Hashtags / keywords
* Result limit (default: 50)

**Outputs:**

* Instagram profile URLs
* Basic metadata (username, followers_count)

---

### 5.3 Scorer Agent

**Purpose:** Rank candidates and detect fake/bot accounts

**Inputs:**

* Candidate profile (with business indicators)
* Brand DNA

**Outputs:**

* Score (0–100) with 6 scoring dimensions
* Follower authenticity assessment (fake detection)
* Reasoning breakdown (JSON)
* Contact email (if found)

**Scoring Dimensions:**

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Visual Aesthetic Match | 25% | Visual style alignment with brand |
| Content Theme Alignment | 20% | Topic, values, messaging match |
| Engagement Rate | 15% | Engagement metrics vs followers |
| Follower Quality | 15% | Authenticity (fake detection) |
| Business Indicators | 15% | Business account, email, website |
| Activity Recency | 10% | Posting frequency and recency |

---

### 5.3.1 Fake Profile Detection

**Purpose:** Filter out bot accounts and fake profiles to ensure quality partner recommendations

**Why It Matters:**

* Fake accounts waste outreach efforts
* Low-quality followers don't convert to sales
* Bot accounts damage brand reputation

**Detection Signals:**

| Signal | Genuine | Suspicious | Likely Fake |
|--------|---------|------------|-------------|
| Following/Follower Ratio | < 1.0 | 1.0 – 2.0 | > 2.0 |
| Posts vs Followers | 50+ posts for 5K | 20–50 posts | < 20 posts for 5K+ |
| Business Account | Yes | – | No |
| Email Available | Yes | – | No |
| Website Linked | Yes | – | No |
| Engagement Rate | > 2% | 1–2% | < 1% |

**Scoring Impact:**

* High following ratio (> 2.0): -30 points
* Too few posts for followers: -25 points
* Business account verified: +5 points
* Email available: +5 points
* Website linked: +5 points

Profiles scoring below 50 on follower quality are flagged as potentially fake.

---

### 5.4 Session Management

**Purpose:** Enable users to manage multiple discovery sessions

#### Capabilities

* **Create Sessions** – Users can run multiple discovery jobs (different brands, campaigns, or iterations)
* **List Sessions** – Dashboard shows all past and active sessions with status indicators
* **Switch Sessions** – Users can navigate between sessions without losing data
* **Session Isolation** – Each session maintains its own brand DNA, discovered profiles, and scores
* **Concurrent Sessions** – Multiple sessions can run simultaneously (queued processing)
* **Session Persistence** – All session data persists across logins and browser sessions

#### Session States

| State | Description |
|-------|-------------|
| `pending` | Created but not started |
| `analyzing` | Brand DNA extraction in progress |
| `discovering` | Finding candidate profiles |
| `scoring` | AI scoring in progress |
| `completed` | All profiles scored, results ready |
| `failed` | Error occurred, can be retried |

#### Session List View

* Session name/description
* Creation date
* Current status with progress indicator
* Profile count (discovered / scored)
* Quick actions (View, Resume, Delete)

---

### 5.5 Dashboard (Frontend)

#### Tabs

* **NEW** – Freshly discovered profiles
* **PROCESSING** – Profiles being scored
* **DONE** – Final ranked profiles

#### Features

* Real-time updates (polling/webhooks)
* Profile cards with score
* Score breakdown
* Email preview modal
* Basic analytics summary
* **Session selector** – Switch between discovery sessions
* **Session history** – View and compare past sessions

---

### 5.5 Orchestration (n8n)

* Webhook-triggered workflow
* Sequential and parallel agent execution
* Retry and error handling
* Database updates
* UI notification hooks

---

## 6. Non-Functional Requirements

| Category        | Requirement                                          |
| --------------- | ---------------------------------------------------- |
| Performance     | Process 50 profiles in < 10 minutes                  |
| Reliability     | Demo-safe, deterministic flow                        |
| Scalability     | Modular, agent-based                                 |
| Explainability  | Score reasoning required                             |
| Maintainability | Clear API contracts                                  |
| Multi-session   | Users can run and manage multiple concurrent sessions |
| Data Isolation  | Sessions are isolated per user; no cross-user access |
| Persistence     | All session data survives restarts and re-logins     |
| Multi-user      | System supports unlimited concurrent users           |
| Authentication  | All user-facing endpoints require valid JWT          |
| Authorization   | RLS policies enforce data access at database level   |

### 6.1 Multi-User Scaling

| Aspect | MVP (Hackathon) | Production |
|--------|-----------------|------------|
| Concurrent Users | 10-20 | Unlimited (Supabase scales) |
| Sessions per User | Unlimited | Unlimited |
| Jobs in Queue | Sequential per user | Parallel with rate limiting |
| Rate Limiting | None | Per-user API limits |
| Data Retention | Indefinite | Configurable per plan |

**Queue Management:**

When multiple users submit jobs simultaneously:

1. Each user's job enters the n8n queue
2. n8n processes jobs in FIFO order (or parallel if resources allow)
3. Users see real-time status updates for their own jobs only
4. No user can impact another user's job performance (fair scheduling)

---

## 7. Technical Architecture

### 7.1 High-Level Architecture

```
Frontend (React + TypeScript)
    ↓
Webhook Trigger
    ↓
n8n Orchestration
    ↓
Agent APIs (FastAPI)
    ↓
Database (Supabase / SQLite)
```

---

### 7.2 Orchestration Flow (n8n)

```
Webhook Trigger
  ↓
Brand Analyzer Agent
  ↓
Discovery Agent
  ↓
Split Profiles (Batch)
  ↓
Scorer Agent (Parallel)
  ↓
Filter (Score ≥ 50)
  ↓
Deduplicate
  ↓
Database Insert
  ↓
Frontend Update
```

---

## 8. API Contracts

### 8.0 Authentication Requirements

**All API endpoints require authentication** via Supabase Auth JWT token.

```
Authorization: Bearer <supabase_jwt_token>
```

| Endpoint Pattern | Auth Required | User Scope |
|------------------|---------------|------------|
| `/api/jobs/*` | ✅ Yes (User JWT) | User's own jobs only |
| `/api/agent/*` | ✅ Yes (Service Key) | Called by n8n with service key |
| `/api/health` | ❌ No | Public |

**Service Key Authentication (for n8n):**

Agent endpoints are called by n8n, not directly by users. They use a service key:

```
X-Service-Key: <N8N_SERVICE_KEY>
```

The service key is validated server-side and grants access to process any job. The `job_id` in the request determines which user's data is being processed.

**Unauthorized Access Response:**

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Valid authentication token required"
  }
}
```

**Forbidden Access Response (accessing another user's data):**

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have access to this resource"
  }
}
```

---

### 8.1 Session Management

```
GET    /api/jobs              # List all sessions for current user
POST   /api/jobs              # Create new discovery session
GET    /api/jobs/{id}         # Get session details with results
GET    /api/jobs/{id}/analytics  # Get session analytics
POST   /api/jobs/{id}/start   # Start/resume discovery
POST   /api/jobs/{id}/retry   # Retry a failed session
PATCH  /api/jobs/{id}         # Update session metadata (name)
DELETE /api/jobs/{id}         # Delete session and all related data
```

### 8.1.1 Email Endpoints

```
POST   /api/email/generate    # Generate AI-drafted outreach email
POST   /api/email/send        # Send email (mock for demo)
```

**Note:** All session endpoints automatically filter by `user_id` from the JWT token. Users cannot access other users' sessions.

**Create Session Request**

```json
POST /api/jobs
{
  "brand_description": "Sustainable fashion brand...",
  "reference_profiles": [
    "https://instagram.com/brand1",
    "https://instagram.com/brand2"
  ]
}
```

**List Sessions Response**

```json
GET /api/jobs
{
  "sessions": [
    {
      "id": "uuid",
      "brand_description": "...",
      "status": "completed",
      "profiles_discovered": 47,
      "profiles_scored": 47,
      "created_at": "2026-01-31T10:00:00Z",
      "updated_at": "2026-01-31T10:15:00Z"
    }
  ]
}
```

---

### 8.2 Brand Analyzer

```json
POST /api/agent/analyze-brand
```

**Response**

```json
{
  "brand_dna": {
    "hashtags": [],
    "keywords": [],
    "embedding_vector": []
  }
}
```

---

### 8.3 Discovery Agent

```json
POST /api/agent/discover
```

**Response**

```json
{
  "profiles": [
    {
      "id": "uuid",
      "instagram_url": "https://instagram.com/example",
      "username": "example",
      "full_name": "Example Account",
      "profile_picture_url": "https://...",
      "bio": "Account bio text",
      "followers_count": 45000,
      "following_count": 1200,
      "posts_count": 500,
      "engagement_rate": 3.5,
      "is_verified": false,
      "is_business_account": true,
      "external_url": "https://example.com",
      "business_email": "hello@example.com",
      "business_category": "Clothing Store",
      "following_ratio": 0.03
    }
  ],
  "total_discovered": 1,
  "deduplicated": 0
}
```

---

### 8.4 Scorer Agent

```json
POST /api/agent/score
```

**Response**

```json
{
  "score": 78,
  "reasoning": {
    "visual_aesthetic_match": 85,
    "content_theme_alignment": 80,
    "engagement_rate_score": 72,
    "follower_quality": 90,
    "business_indicators": 75,
    "activity_recency": 80,
    "summary": "Good match with strong visual alignment. Genuine profile with healthy engagement.",
    "recommendation": "Recommended for partnership."
  },
  "contact": {
    "email": "hello@example.com",
    "source": "business_email"
  }
}
```

---

## 9. Tech Stack

### Frontend

* React
* TypeScript
* Tailwind CSS

### Backend

* Python 3.10+
* FastAPI

### AI

* LangChain (multi-provider abstraction)
* OpenAI GPT-4o (high-quality, demos)
* Google Gemini (cost-effective production)
* Ollama (local dev, free testing)

### Orchestration

* n8n

### Database

* Supabase (primary)
* SQLite (fallback)

### Scraping

* Apify (Instagram)

---

## 10. Database Schema (Supabase)

### 10.1 Tables Overview

```
users (Supabase Auth)
    └── discovery_jobs (1:many, user_id FK)
            ├── brand_dna (1:1, job_id FK)
            └── discovered_profiles (1:many, job_id FK)
                    ├── profile_scores (1:1, profile_id FK)
                    └── profile_contacts (1:1, profile_id FK)
```

### 10.1.1 Data Isolation Chain

All data is isolated per user through foreign key chains:

```
users.id
    ↓ (user_id)
discovery_jobs.id
    ↓ (job_id)
discovered_profiles.id / brand_dna.id
    ↓ (profile_id)
profile_scores.id / profile_contacts.id
```

**Rule:** Users can ONLY access data where the chain leads back to their `user_id`.

### 10.1.2 Row-Level Security (RLS) Policies

All tables have RLS enabled. Policies enforce user isolation at the database level.

```sql
-- Enable RLS on all tables
ALTER TABLE discovery_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_dna ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_contacts ENABLE ROW LEVEL SECURITY;

-- discovery_jobs: Direct user_id check
CREATE POLICY "Users can only access their own jobs"
ON discovery_jobs FOR ALL
USING (user_id = auth.uid());

-- brand_dna: Access via job ownership
CREATE POLICY "Users can only access brand_dna for their jobs"
ON brand_dna FOR ALL
USING (
  job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
);

-- discovered_profiles: Access via job ownership
CREATE POLICY "Users can only access profiles for their jobs"
ON discovered_profiles FOR ALL
USING (
  job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
);

-- profile_scores: Access via profile → job ownership
CREATE POLICY "Users can only access scores for their profiles"
ON profile_scores FOR ALL
USING (
  profile_id IN (
    SELECT id FROM discovered_profiles 
    WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
  )
);

-- profile_contacts: Access via profile → job ownership
CREATE POLICY "Users can only access contacts for their profiles"
ON profile_contacts FOR ALL
USING (
  profile_id IN (
    SELECT id FROM discovered_profiles 
    WHERE job_id IN (SELECT id FROM discovery_jobs WHERE user_id = auth.uid())
  )
);
```

---

### 10.2 `users` (Supabase Auth)

Managed by Supabase Auth. Extended with profile data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Supabase Auth user ID |
| `email` | text | User email |
| `full_name` | text | Display name |
| `avatar_url` | text | Profile picture URL |
| `created_at` | timestamptz | Registration time |

---

### 10.3 `discovery_jobs`

Tracks each discovery session initiated by a user. Supports multiple concurrent sessions per user.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Unique job ID |
| `user_id` | uuid (FK) | Reference to users (Supabase Auth) |
| `name` | text | User-friendly session name (auto-generated or custom) |
| `brand_description` | text | User-provided brand description |
| `reference_profiles` | text[] | Array of reference Instagram URLs |
| `status` | enum | `pending`, `analyzing`, `discovering`, `scoring`, `completed`, `failed` |
| `profiles_discovered` | integer | Count of discovered profiles (denormalized for quick access) |
| `profiles_scored` | integer | Count of scored profiles (denormalized for quick access) |
| `created_at` | timestamptz | Job creation time |
| `updated_at` | timestamptz | Last update time |

**Indexes:**
- `idx_discovery_jobs_user_id` on `user_id` for fast session listing
- `idx_discovery_jobs_status` on `status` for filtering active jobs

---

### 10.4 `brand_dna`

Stores extracted brand identity from reference profiles.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Unique ID |
| `job_id` | uuid (FK) | Reference to discovery_jobs |
| `hashtags` | text[] | Extracted hashtags |
| `keywords` | text[] | Extracted keywords |
| `embedding_vector` | vector(1536) | Brand embedding for similarity |
| `created_at` | timestamptz | Creation time |

---

### 10.5 `discovered_profiles`

Stores candidate profiles found during discovery.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Unique ID |
| `job_id` | uuid (FK) | Reference to discovery_jobs |
| `instagram_url` | text | Profile URL |
| `username` | text | Instagram handle |
| `full_name` | text | Display name |
| `profile_picture_url` | text | Avatar URL |
| `bio` | text | Profile bio/description |
| `followers_count` | integer | Follower count |
| `following_count` | integer | Following count |
| `posts_count` | integer | Total posts |
| `engagement_rate` | decimal(5,2) | Calculated engagement rate |
| `is_verified` | boolean | Blue checkmark status |
| `is_business_account` | boolean | Business account flag |
| `external_url` | text | Website link from bio |
| `business_email` | text | Email for business accounts |
| `business_category` | text | Business category name |
| `following_ratio` | decimal(5,2) | Calculated: following / followers |
| `status` | enum | `new`, `processing`, `done`, `skipped` |
| `created_at` | timestamptz | Discovery time |

---

### 10.6 `profile_scores`

Stores AI scoring results for each profile.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Unique ID |
| `profile_id` | uuid (FK) | Reference to discovered_profiles |
| `score` | integer | Match score (0-100) |
| `visual_aesthetic_match` | integer | Visual style alignment (0-100, 25% weight) |
| `content_theme_alignment` | integer | Topic/messaging alignment (0-100, 20% weight) |
| `engagement_rate_score` | integer | Engagement metrics (0-100, 15% weight) |
| `follower_quality` | integer | Authenticity/fake detection (0-100, 15% weight) |
| `business_indicators` | integer | Business presence (0-100, 15% weight) |
| `activity_recency` | integer | Posting frequency (0-100, 10% weight) |
| `reasoning` | jsonb | Full reasoning breakdown (summary, recommendation) |
| `created_at` | timestamptz | Scoring time |

---

### 10.7 `profile_contacts`

Stores extracted contact information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid (PK) | Unique ID |
| `profile_id` | uuid (FK) | Reference to discovered_profiles |
| `email` | text | Extracted email (nullable) |
| `source` | text | Where email was found (bio, website, etc.) |
| `created_at` | timestamptz | Extraction time |

---

## 11. Team Responsibilities

### Member 1 – Frontend & Database

* UI dashboard
* Database schema
* API integration

### Member 2 – AI Agents

* Brand Analyzer
* Discovery Agent
* Scorer Agent

### Member 3 – Orchestration

* n8n workflow
* Error handling
* Demo pipeline

---

## 12. Risks & Mitigation

| Risk                     | Mitigation            |
| ------------------------ | --------------------- |
| Instagram scraping fails | Pre-scraped demo data |
| Agent latency            | Use GPT-4o-mini       |
| Workflow failure         | Python fallback       |
| Time overrun             | Mock APIs early       |

---

## 13. Demo Acceptance Criteria

* End-to-end flow runs live
* Profiles appear incrementally
* Scores & reasoning visible
* No manual backend steps
* Demo completes under 5 minutes

---

## 14. Future Enhancements

* TikTok & LinkedIn discovery
* Auto email campaigns
* CRM integrations
* Team collaboration
* Paid plans
* Mobile app

---

## 15. Final Recommendation

**Use n8n-based orchestration for the hackathon MVP** due to:

* Faster development
* Visual debugging
* Deterministic execution
* Strong demo storytelling

---