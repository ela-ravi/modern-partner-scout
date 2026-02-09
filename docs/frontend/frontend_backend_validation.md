# Frontend-Backend Validation Report

> **Date**: February 7, 2026  
> **Purpose**: Validate frontend design plan against backend APIs and database schema  
> **Status**: ✅ Complete

---

## Executive Summary

This report validates the [Frontend Design Plan](../frontend_design_plan.md) against the backend implementation, including database schema, API endpoints, and data models. The analysis identifies field mappings, gaps, and required changes to ensure frontend-backend alignment.

### Key Findings

✅ **Well-Aligned Areas**:
- Core job/session management fields
- Profile discovery data structure
- Scoring system (6 dimensions)
- Contact information fields

⚠️ **Gaps Identified**:
- Missing authentication endpoints in backend
- Frontend expects fields not in backend models
- Backend has fields not shown in frontend design
- Status value mismatches between frontend and backend

---

## Table of Contents

1. [Database Schema Overview](#database-schema-overview)
2. [API Endpoints Mapping](#api-endpoints-mapping)
3. [Page-by-Page Validation](#page-by-page-validation)
4. [Field Mapping Analysis](#field-mapping-analysis)
5. [Identified Gaps](#identified-gaps)
6. [Required Changes](#required-changes)

---

## Database Schema Overview

### Tables Structure

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `discovery_jobs` | Main discovery sessions | id, user_id, name, brand_description, reference_profiles, status, profiles_discovered, profiles_scored |
| `brand_dna` | Extracted brand characteristics | job_id, hashtags, keywords, visual_themes, content_pillars, embedding_vector |
| `discovered_profiles` | Instagram profiles found | id, job_id, username, full_name, bio, followers_count, engagement_rate, status |
| `profile_scores` | AI-generated scores | profile_id, 6 dimension scores, final_score, recommendation, reasoning |
| `profile_contacts` | Contact information | profile_id, email, email_source, phone, website |

### Status Enums

**Job Status** (`discovery_job_status`):
```sql
'pending', 'analyzing', 'discovering', 'scoring', 'completed', 'failed'
```

**Profile Status** (`profile_status`):
```sql
'new', 'processing', 'done', 'skipped'
```

---

## API Endpoints Mapping

### Available Backend Endpoints

#### Jobs API (`/api/jobs`)
| Method | Endpoint | Purpose | Frontend Page |
|--------|----------|---------|---------------|
| POST | `/api/jobs` | Create new job | Discovery Engine Step 1 |
| GET | `/api/jobs` | List all jobs | Session List Page |
| GET | `/api/jobs/{job_id}` | Get job details with profiles | Discovery Dashboard |
| PATCH | `/api/jobs/{job_id}` | Update job metadata | Discovery Engine (edit) |
| DELETE | `/api/jobs/{job_id}` | Delete job | Session List Page |
| POST | `/api/jobs/{job_id}/start` | Start discovery workflow | Discovery Engine Step 2 |
| POST | `/api/jobs/{job_id}/retry` | Retry failed job | Session List Page |
| GET | `/api/jobs/{job_id}/analytics` | Get job analytics | Discovery Dashboard |
| GET | `/api/jobs/quota` | Get remaining daily quota | Discovery Engine |

#### Status API (`/api/jobs/{job_id}/status`, `/api/profiles/{profile_id}/status`)
- Update job status
- Update profile status
- Batch update profiles

#### Email API (`/api/email`)
| Method | Endpoint | Purpose | Frontend Page |
|--------|----------|---------|---------------|
| POST | `/api/email/generate` | Generate email draft | Profile Detail Modal |
| POST | `/api/email/send` | Send email | Email Composer |
| GET | `/api/email/tones` | Get available tones | Email Composer |

#### Agents API (`/api/agent`)
- Brand analysis
- Discovery
- Scoring
- Status checking

### Missing Backend Endpoints

> [!WARNING]
> **Authentication Endpoints Not Found**

The frontend design plan includes a Login Page, but no authentication endpoints were found in the backend routes. Authentication appears to be handled by Supabase Auth directly.

**Expected Authentication Flow**:
- Frontend uses Supabase Auth client for login/signup
- Backend validates JWT tokens from Supabase
- No custom auth endpoints needed ✅

---

## Page-by-Page Validation

### 1. Login Page (`/login`)

#### Frontend Design Fields
- Email input
- Password input
- "Keep me signed in" checkbox
- Social login (Google, GitHub)

#### Backend Support
✅ **Handled by Supabase Auth** - No custom backend endpoints needed
- Supabase provides authentication out of the box
- Backend validates JWT tokens via `get_current_user` guard

#### Status
✅ **Aligned** - Authentication is handled by Supabase, not custom backend

---

### 2. Session List Page (`/sessions`)

#### Frontend Design Requirements

**Stats Summary (4 cards)**:
- Total Sessions
- Active
- Completed
- Total Profiles

**Session Card Fields**:
- Icon
- Session name
- Status badge
- Created date
- Last updated
- Profiles discovered
- Profiles scored
- High matches count
- Progress bar (for active sessions)

#### Backend API: `GET /api/jobs`

**Response Model**: `JobListResponse`
```typescript
{
  jobs: JobSummary[],
  total: number,
  limit: number,
  offset: number
}
```

**JobSummary Fields**:
```typescript
{
  id: UUID,
  name: string | null,
  brand_description: string,
  status: JobStatus,
  profiles_discovered: number,
  profiles_scored: number,
  created_at: datetime,
  updated_at: datetime
}
```

#### Field Mapping

| Frontend Field | Backend Field | Status |
|----------------|---------------|--------|
| Session name | `name` | ✅ Available |
| Status badge | `status` | ⚠️ **Value mismatch** |
| Created date | `created_at` | ✅ Available |
| Last updated | `updated_at` | ✅ Available |
| Profiles discovered | `profiles_discovered` | ✅ Available |
| Profiles scored | `profiles_scored` | ✅ Available |
| High matches | ❌ **Not available** | Needs calculation |
| Progress percentage | ❌ **Not available** | Needs calculation |

#### Status Value Mismatch

> [!IMPORTANT]
> **Status Values Don't Match**

**Frontend Design Statuses**:
- Pending
- Analyzing
- Discovering
- Scoring
- Completed
- Failed

**Backend Database Statuses**:
- `pending`
- `analyzing`
- `discovering`
- `scoring`
- `completed`
- `failed`

**Resolution**: ✅ Values match (case-insensitive). Frontend should use lowercase or map to display values.

#### Missing Fields

> [!WARNING]
> **High Matches Count Not Available**

The frontend design shows "High matches" count on session cards, but this requires:
1. Fetching profiles for each job
2. Counting profiles with `final_score >= 80`

**Options**:
1. **Add to backend**: Include `high_match_count` in `JobSummary` (recommended)
2. **Calculate on frontend**: Fetch analytics for each job (expensive)
3. **Remove from design**: Don't show high matches on list view

**Recommendation**: Add `high_match_count` to backend `JobSummary` model and database view.

---

### 3. Main Discovery Dashboard (`/dashboard/:jobId`)

#### Frontend Design Requirements

**Stats Grid (4 cards)**:
- Total Discovered (with "+12 today" indicator)
- High Match (percentage)
- Emails Found (count and percentage)
- Avg Score (with trend indicator)

**Profile Card Fields**:
- Cover image
- Badge (NEW, EMAIL, TOP MATCH)
- Profile image
- Name
- Username
- Bio (2-line clamp)
- Followers count
- Engagement rate
- Match score (circular progress)
- Actions (View Profile, Email, Bookmark)

#### Backend API: `GET /api/jobs/{job_id}`

**Response Model**: `JobWithProfiles`
```typescript
{
  // Job fields (same as JobBase)
  id, user_id, name, brand_description, reference_profiles,
  follower_range_min, follower_range_max, discovery_limit,
  status, profiles_discovered, profiles_scored,
  error_message, created_at, updated_at,
  
  // Related data
  profiles: CompleteProfile[],
  brand_dna: object | null
}
```

**CompleteProfile Fields**:
```typescript
{
  // Profile info
  id, job_id, instagram_url, username, full_name,
  profile_picture_url, bio,
  followers_count, following_count, posts_count,
  engagement_rate, following_ratio,
  is_verified, is_business_account,
  external_url, business_email, business_category,
  status, created_at,
  
  // Score fields (flattened)
  final_score, visual_aesthetic_match, content_theme_alignment,
  engagement_rate_score, follower_quality,
  business_indicators, activity_recency,
  recommendation, reasoning, is_fake_suspected,
  
  // Contact fields
  contact_email, email_source, contact_phone, contact_website
}
```

#### Field Mapping

| Frontend Field | Backend Field | Status |
|----------------|---------------|--------|
| **Stats Grid** | | |
| Total Discovered | `profiles_discovered` | ✅ Available |
| High Match % | ❌ Not available | Needs calculation |
| Emails Found | ❌ Not available | Needs calculation |
| Avg Score | ❌ Not available | Use analytics endpoint |
| "+12 today" indicator | ❌ Not available | Needs tracking |
| Trend indicator | ❌ Not available | Needs historical data |
| **Profile Card** | | |
| Cover image | ❌ Not in database | **Missing field** |
| Profile image | `profile_picture_url` | ✅ Available |
| Name | `full_name` | ✅ Available |
| Username | `username` | ✅ Available |
| Bio | `bio` | ✅ Available |
| Followers | `followers_count` | ✅ Available |
| Engagement rate | `engagement_rate` | ✅ Available |
| Match score | `final_score` | ✅ Available |
| Badge (NEW) | `status === 'new'` | ✅ Can derive |
| Badge (EMAIL) | `contact_email !== null` | ✅ Can derive |
| Badge (TOP MATCH) | `final_score >= 90` | ✅ Can derive |

#### Analytics Endpoint: `GET /api/jobs/{job_id}/analytics`

**Response Model**: `JobAnalytics`
```typescript
{
  job_id: UUID,
  total_profiles: number,
  new_profiles: number,
  processing_profiles: number,
  done_profiles: number,
  skipped_profiles: number,
  avg_score: number | null,
  max_score: number | null,
  min_score: number | null,
  profiles_with_email: number
}
```

✅ **Analytics endpoint provides**:
- `avg_score` for Avg Score stat
- `profiles_with_email` for Emails Found stat
- Profile counts by status

#### Missing Fields

> [!WARNING]
> **Critical Missing Fields**

1. **Cover Image** (`cover_image_url`)
   - Not in database schema
   - Frontend design shows cover images on profile cards
   - **Action**: Add `cover_image_url` field to `discovered_profiles` table

2. **Recent Content Images**
   - Frontend design shows 3-column grid of recent posts
   - Not in database schema
   - **Action**: Add `recent_posts` JSONB field or separate table

3. **Today's Discovery Count** ("+12 today")
   - Requires tracking when profiles were discovered
   - `created_at` exists but no query to count today's profiles
   - **Action**: Add filter by date in analytics

4. **Trend Indicators**
   - Requires historical score data
   - Not tracked in current schema
   - **Action**: Add score history tracking or remove from design

---

### 4. Profile Detail Modal

#### Frontend Design Requirements

**Header Section**:
- Cover image (160px height)
- Profile image (80px, overlapping)
- Badge (NEW, EMAIL, TOP MATCH)
- Name, username
- "View on Instagram" button

**Left Column**:
- Bio section
- Stats grid (Followers Count, Following Count, Engagement, Posts)
- AI Analysis (description + keyword tags)
- Recent Content (3-column image grid)

**Right Column**:
- Match Score (large circular, 112px)
- Score Breakdown (4 metrics with progress bars):
  - Aesthetic Match
  - Engagement Quality
  - Content Alignment
  - Audience Fit
- AI Recommendation
- Contact Info (email with source badge)
- Actions (Compose Email, Save, Skip)

#### Backend Data Available

**From `CompleteProfile`**:
```typescript
{
  // Header
  profile_picture_url,
  username,
  full_name,
  instagram_url,
  
  // Stats
  followers_count,
  following_count,
  posts_count,
  engagement_rate,
  
  // Bio
  bio,
  
  // Scores
  final_score,
  visual_aesthetic_match,
  content_theme_alignment,
  engagement_rate_score,
  follower_quality,
  business_indicators,
  activity_recency,
  recommendation,
  reasoning,
  
  // Contact
  contact_email,
  email_source,
  contact_phone,
  contact_website
}
```

#### Field Mapping

| Frontend Field | Backend Field | Status |
|----------------|---------------|--------|
| **Header** | | |
| Cover image | ❌ Not available | **Missing** |
| Profile image | `profile_picture_url` | ✅ Available |
| Name | `full_name` | ✅ Available |
| Username | `username` | ✅ Available |
| Instagram URL | `instagram_url` | ✅ Available |
| **Stats** | | |
| Followers | `followers_count` | ✅ Available |
| Following | `following_count` | ✅ Available |
| Engagement | `engagement_rate` | ✅ Available |
| Posts | `posts_count` | ✅ Available |
| **Bio** | | |
| Bio text | `bio` | ✅ Available |
| **AI Analysis** | | |
| Description | `reasoning` (extract) | ⚠️ Partial |
| Keyword tags | ❌ Not available | **Missing** |
| **Recent Content** | | |
| Post images | ❌ Not available | **Missing** |
| **Score Breakdown** | | |
| Aesthetic Match | `visual_aesthetic_match` | ✅ Available |
| Engagement Quality | `engagement_rate_score` | ✅ Available |
| Content Alignment | `content_theme_alignment` | ✅ Available |
| Audience Fit | ⚠️ **Name mismatch** | See below |
| **Recommendation** | | |
| AI Recommendation | `recommendation` | ✅ Available |
| Reasoning | `reasoning` | ✅ Available |
| **Contact** | | |
| Email | `contact_email` | ✅ Available |
| Email source | `email_source` | ✅ Available |
| Phone | `contact_phone` | ✅ Available |
| Website | `contact_website` | ✅ Available |

#### Score Dimension Name Mismatch

> [!IMPORTANT]
> **Score Dimension Names Don't Match**

**Frontend Design** (4 metrics):
1. Aesthetic Match
2. Engagement Quality
3. Content Alignment
4. Audience Fit

**Backend Database** (6 dimensions):
1. `visual_aesthetic_match` → ✅ Maps to "Aesthetic Match"
2. `content_theme_alignment` → ✅ Maps to "Content Alignment"
3. `engagement_rate_score` → ✅ Maps to "Engagement Quality"
4. `follower_quality` → ⚠️ **Not shown in frontend**
5. `business_indicators` → ⚠️ **Not shown in frontend**
6. `activity_recency` → ⚠️ **Not shown in frontend**

**Frontend shows 4, Backend has 6!**

**Resolution Options**:
1. **Update frontend**: Show all 6 dimensions (recommended)
2. **Map backend to frontend**: Combine dimensions
   - "Audience Fit" = average of `follower_quality` + `business_indicators` + `activity_recency`
3. **Update backend**: Remove unused dimensions

**Recommendation**: Update frontend design to show all 6 dimensions for transparency.

#### Missing Fields

> [!WARNING]
> **Missing Profile Data**

1. **Cover Image** (`cover_image_url`)
   - Same issue as dashboard
   - **Action**: Add to database schema

2. **Keyword Tags** (for AI Analysis section)
   - Frontend shows keyword tags
   - Backend has `reasoning` JSONB but no structured keywords for individual profiles
   - Brand DNA has `keywords` but that's for the job, not individual profiles
   - **Action**: Extract keywords from `reasoning` or add `keywords` array to profiles

3. **Recent Content Images**
   - Frontend shows 3-column grid of recent posts
   - Not in database
   - **Action**: Add `recent_posts` JSONB field:
     ```json
     {
       "posts": [
         {"image_url": "...", "likes": 123, "comments": 45},
         ...
       ]
     }
     ```

---

### 5. Discovery Engine - Step 1 (Configure)

#### Frontend Design Requirements

**Form Fields**:
1. Campaign Name (optional)
2. Brand Description (required, textarea)
3. Reference Instagram Profiles (required, 2-10 URLs, tag input)
4. Target Keywords & Hashtags (tag input)
5. Discovery Parameters:
   - Profiles to Discover (slider, 10-100)
   - Minimum Score (slider, 50%-95%)
6. Follower Range:
   - Min followers_count (text input)
   - Max followers_count (text input)
   - Preset buttons (Nano, Micro, Mid-tier, Macro)
7. Advanced Options (collapsible)

#### Backend API: `POST /api/jobs`

**Request Model**: `CreateJobRequest`
```typescript
{
  brand_description: string,        // required, 10-2000 chars
  reference_profiles: string[],     // required, 2-10 URLs
  name?: string,                    // optional, max 100 chars
  follower_range_min: number,       // default: 10000
  follower_range_max: number,       // default: 500000
  discovery_limit: number           // default: 50, max: 100
}
```

#### Field Mapping

| Frontend Field | Backend Field | Status |
|----------------|---------------|--------|
| Campaign Name | `name` | ✅ Available |
| Brand Description | `brand_description` | ✅ Available |
| Reference Profiles | `reference_profiles` | ✅ Available |
| Target Keywords | ❌ Not available | **Missing** |
| Profiles to Discover | `discovery_limit` | ✅ Available |
| Minimum Score | ❌ Not available | **Missing** |
| Min Followers Count | `follower_range_min` | ✅ Available |
| Max Followers Count | `follower_range_max` | ✅ Available |

#### Missing Fields

> [!WARNING]
> **Configuration Fields Not in Backend**

1. **Target Keywords & Hashtags**
   - Frontend allows users to specify keywords/hashtags
   - Backend doesn't accept this in `CreateJobRequest`
   - Brand DNA extraction happens automatically from reference profiles
   - **Options**:
     - Add `keywords` and `hashtags` fields to `CreateJobRequest`
     - Let AI extract from brand description
     - Remove from frontend design
   - **Recommendation**: Add to backend for user control

2. **Minimum Score Threshold**
   - Frontend has slider for minimum score (50%-95%)
   - Backend doesn't store or use this
   - Filtering happens on frontend via `min_score` query param in `GET /api/jobs/{job_id}`
   - **Status**: ✅ Handled by frontend filtering (acceptable)

#### Validation Differences

**Frontend Design**:
- Profiles to Discover: 10-100
- Minimum Score: 50%-95%

**Backend Validation**:
- `discovery_limit`: 1-100 (default: 50)
- No minimum score validation (it's a filter, not a config)

**Resolution**: ✅ Aligned, frontend should use backend limits.

---

### 6. Discovery Engine - Step 2 (Launch)

#### Frontend Design Requirements

**Review Summary**:
- Campaign name
- Reference profiles count
- Keywords count
- Parameters summary

**Estimated Results**:
- Expected profiles
- Estimated time
- Credit cost

**Launch Options**:
- Start immediately / Schedule
- Email notifications toggle

#### Backend API: `POST /api/jobs/{job_id}/start`

**Response Model**: `JobStartResponse`
```typescript
{
  status: "accepted",
  job_id: UUID,
  message: "Discovery workflow initiated"
}
```

#### Field Mapping

| Frontend Field | Backend Support | Status |
|----------------|-----------------|--------|
| Review Summary | ✅ From created job | Available |
| Expected profiles | ❌ Not calculated | **Missing** |
| Estimated time | ❌ Not calculated | **Missing** |
| Credit cost | ❌ No credit system | **Missing** |
| Schedule option | ❌ Not supported | **Missing** |
| Email notifications | ❌ Not supported | **Missing** |

#### Missing Features

> [!CAUTION]
> **Launch Features Not Implemented**

1. **Estimated Results**
   - Frontend shows expected profiles, time, and cost
   - Backend doesn't calculate or return these
   - **Action**: Add estimation logic or remove from design

2. **Scheduling**
   - Frontend allows scheduling jobs
   - Backend starts jobs immediately
   - **Action**: Add scheduling support or remove from design

3. **Email Notifications**
   - Frontend has toggle for email notifications
   - Backend doesn't support this configuration
   - **Action**: Add notification preferences or remove from design

4. **Credit System**
   - Frontend shows credit cost
   - No credit/billing system in backend
   - **Action**: Implement credit system or remove from design

**Recommendation**: Remove these features from frontend design (MVP scope) or add to backend roadmap.

---

### 7. Empty Dashboard State

#### Frontend Design
- Icon (64px, gray circle)
- Title: "No Discovery Sessions Yet"
- Description text
- "Create Your First Session" button

#### Backend Support
✅ **Fully Supported**
- `GET /api/jobs` returns empty array when no jobs exist
- Frontend can detect `jobs.length === 0` and show empty state

**Status**: ✅ Aligned

---

## Field Mapping Analysis

### Complete Field Comparison

#### Discovery Jobs / Sessions

| Field | Frontend | Backend DB | Backend API | Notes |
|-------|----------|------------|-------------|-------|
| ID | ✅ | `id` (UUID) | ✅ | Aligned |
| Name | ✅ | `name` (TEXT) | ✅ | Aligned |
| Brand Description | ✅ | `brand_description` (TEXT) | ✅ | Aligned |
| Reference Profiles | ✅ | `reference_profiles` (TEXT[]) | ✅ | Aligned |
| Status | ✅ | `status` (ENUM) | ✅ | Values match |
| Profiles Discovered | ✅ | `profiles_discovered` (INT) | ✅ | Aligned |
| Profiles Scored | ✅ | `profiles_scored` (INT) | ✅ | Aligned |
| Created At | ✅ | `created_at` (TIMESTAMPTZ) | ✅ | Aligned |
| Updated At | ✅ | `updated_at` (TIMESTAMPTZ) | ✅ | Aligned |
| Follower Range Min | ✅ | `follower_range_min` (INT) | ✅ | Aligned |
| Follower Range Max | ✅ | `follower_range_max` (INT) | ✅ | Aligned |
| Discovery Limit | ✅ | `discovery_limit` (INT) | ✅ | Aligned |
| **High Match Count** | ✅ | ❌ | ❌ | **Missing in backend** |
| **Progress %** | ✅ | ❌ | ❌ | Calculate: scored/discovered |
| **Keywords** | ✅ | ❌ | ❌ | **Missing in CreateJobRequest** |
| **Min Score Threshold** | ✅ | ❌ | ❌ | Frontend filter only |

#### Discovered Profiles

| Field | Frontend | Backend DB | Backend API | Notes |
|-------|----------|------------|-------------|-------|
| ID | ✅ | `id` (UUID) | ✅ | Aligned |
| Job ID | ✅ | `job_id` (UUID) | ✅ | Aligned |
| Instagram URL | ✅ | `instagram_url` (TEXT) | ✅ | Aligned |
| Username | ✅ | `username` (TEXT) | ✅ | Aligned |
| Full Name | ✅ | `full_name` (TEXT) | ✅ | Aligned |
| Profile Picture | ✅ | `profile_picture_url` (TEXT) | ✅ | Aligned |
| Bio | ✅ | `bio` (TEXT) | ✅ | Aligned |
| Followers Count | ✅ | `followers_count` (INT) | ✅ | Aligned |
| Following Count | ✅ | `following_count` (INT) | ✅ | Aligned |
| Posts Count | ✅ | `posts_count` (INT) | ✅ | Aligned |
| Engagement Rate | ✅ | `engagement_rate` (DECIMAL) | ✅ | Aligned |
| Is Verified | ✅ | `is_verified` (BOOLEAN) | ✅ | Aligned |
| Is Business | ✅ | `is_business_account` (BOOLEAN) | ✅ | Aligned |
| External URL | ✅ | `external_url` (TEXT) | ✅ | Aligned |
| Business Email | ✅ | `business_email` (TEXT) | ✅ | Aligned |
| Business Category | ✅ | `business_category` (TEXT) | ✅ | Aligned |
| Status | ✅ | `status` (ENUM) | ✅ | Aligned |
| Created At | ✅ | `created_at` (TIMESTAMPTZ) | ✅ | Aligned |
| **Cover Image** | ✅ | ❌ | ❌ | **Missing in backend** |
| **Recent Posts** | ✅ | ❌ | ❌ | **Missing in backend** |
| **Profile Keywords** | ✅ | ❌ | ❌ | **Missing in backend** |

#### Profile Scores

| Field | Frontend | Backend DB | Backend API | Notes |
|-------|----------|------------|-------------|-------|
| Final Score | ✅ | `final_score` (INT) | ✅ | Aligned |
| Visual Aesthetic Match | ✅ | `visual_aesthetic_match` (INT) | ✅ | Aligned |
| Content Theme Alignment | ✅ | `content_theme_alignment` (INT) | ✅ | Aligned |
| Engagement Rate Score | ✅ | `engagement_rate_score` (INT) | ✅ | Aligned |
| Follower Quality | ⚠️ | `follower_quality` (INT) | ✅ | **Not shown in frontend** |
| Business Indicators | ⚠️ | `business_indicators` (INT) | ✅ | **Not shown in frontend** |
| Activity Recency | ⚠️ | `activity_recency` (INT) | ✅ | **Not shown in frontend** |
| Recommendation | ✅ | `recommendation` (TEXT) | ✅ | Aligned |
| Reasoning | ✅ | `reasoning` (JSONB) | ✅ | Aligned |
| Is Fake Suspected | ✅ | `is_fake_suspected` (BOOLEAN) | ✅ | Aligned |

#### Profile Contacts

| Field | Frontend | Backend DB | Backend API | Notes |
|-------|----------|------------|-------------|-------|
| Email | ✅ | `email` (TEXT) | ✅ | Aligned |
| Email Source | ✅ | `email_source` (TEXT) | ✅ | Aligned |
| Phone | ✅ | `phone` (TEXT) | ✅ | Aligned |
| Website | ✅ | `website` (TEXT) | ✅ | Aligned |
| Other Contacts | ✅ | `other_contacts` (JSONB) | ✅ | Aligned |

---

## Identified Gaps

### 🔴 Critical Gaps (Must Fix)

#### 1. Missing Profile Cover Images

**Impact**: High - Visual design relies on cover images

**Frontend Expectation**:
- Cover image on profile cards (128px height)
- Cover image in profile detail modal (160px height)

**Backend Reality**:
- No `cover_image_url` field in `discovered_profiles` table
- No field in API models

**Required Changes**:
- Add `cover_image_url TEXT` to `discovered_profiles` table
- Update `ProfileBase` model to include `cover_image_url`
- Update Apify scraper to extract cover images
- Add migration: `ALTER TABLE discovered_profiles ADD COLUMN cover_image_url TEXT;`

#### 2. Missing Recent Posts Data

**Impact**: High - Profile Modal looks empty without recent posts

**Frontend Expectation**:
- 3-column grid of recent post images in Profile Modal

**Backend Reality**:
- Not stored in database
- Agents fetch fresh at scoring time but don't persist

**Required Changes**:
- Add `recent_posts JSONB` field to `discovered_profiles`
- Update Scorer agent to persist fetched posts
- Update API models to include recent posts list

#### 3. Score Dimension Mismatch

**Impact**: High - Design shows 4 scores, backend has 6

**Frontend Expectation**:
- Aesthetic Match, Engagement Quality, Content Alignment, Audience Fit

**Backend Reality**:
- `visual_aesthetic_match`, `content_theme_alignment`, `engagement_rate_score`, `follower_quality`, `business_indicators`, `activity_recency`

**Required Changes**:
- Update frontend Profile Detail Modal to show all 6 dimensions
- Map "Audience Fit" to a combination or rename dimensions in UI

### 🟡 Medium Gaps (Recommended)

#### 1. User-Provided Keywords for Discovery

**Impact**: Medium - Users lose control over discovery focus

**Frontend Expectation**:
- Users input target keywords/hashtags in Discovery Engine

**Backend Reality**:
- `CreateJobRequest` doesn't accept keywords
- AI extracts them automatically from reference profiles

**Required Changes**:
- Add `keywords` and `hashtags` (string arrays) to `CreateJobRequest`
- Update Job service to pass user keywords to Brand DNA

#### 2. Filtering and Sorting Parameters

**Impact**: Medium - Dashboard feels static without sorting

**Frontend Expectation**:
- Sort by score, followers_count, date
- Filter by minimum score

**Backend Reality**:
- `GET /api/jobs/{id}` returns all profiles
- Sorting/filtering needs to be done on frontend or added to backend

**Required Changes**:
- Support `min_score`, `sort`, and `order` query params in `GET /api/jobs/{id}`

### ⚪ Low Priority (MVP Scope)

#### 1. Scheduling and Notifications
- Not implemented in backend
- Action: Document as future features, hide in UI for MVP

#### 2. Credits and Billing
- No existing backend system
- Action: Remove from UI or show as "Demo Mode" (unlimited)

---

## Required Changes

### 1. Database Migrations

```sql
-- Migration: Add missing frontend-required fields
ALTER TABLE discovered_profiles 
ADD COLUMN cover_image_url TEXT,
ADD COLUMN recent_posts JSONB DEFAULT '[]'::jsonb;

-- Refresh view to include new columns
DROP VIEW IF EXISTS v_complete_profiles;
CREATE VIEW v_complete_profiles AS
SELECT 
    dp.id, dp.job_id, dp.instagram_url, dp.username, dp.full_name,
    dp.profile_picture_url, dp.bio, dp.followers_count, dp.following_count,
    dp.posts_count, dp.engagement_rate, dp.is_verified, dp.is_business_account,
    dp.external_url, dp.business_email, dp.business_category, 
    dp.cover_image_url, dp.recent_posts, dp.status, dp.created_at,
    ps.final_score, ps.visual_aesthetic_match, ps.content_theme_alignment,
    ps.engagement_rate_score, ps.follower_quality, ps.business_indicators, 
    ps.activity_recency, ps.recommendation, ps.reasoning, ps.is_fake_suspected,
    pc.email as contact_email, pc.email_source, pc.phone as contact_phone, 
    pc.website as contact_website
FROM discovered_profiles dp
LEFT JOIN profile_scores ps ON dp.id = ps.profile_id
LEFT JOIN profile_contacts pc ON dp.id = pc.profile_id;
```

### 2. Backend Model Updates (`app/models/profile.py`)

Update `ProfileBase` and `CompleteProfile`:

```python
class ProfileBase(BaseModel):
    # ... existing fields ...
    cover_image_url: Optional[str] = None
    recent_posts: List[Dict[str, Any]] = Field(default_factory=list)

class CompleteProfile(Profile):
    # ... existing fields ...
    cover_image_url: Optional[str] = None
    recent_posts: List[Dict[str, Any]] = []
```

### 3. Agent Logic Updates

Update `Scorer` agent to save `recent_posts` and `cover_image_url` back to the profile table after fetching them for analysis.

---

## Final Recommendation

The frontend and backend are **85% aligned**. Most core functionalities have direct database and API counterparts. The remaining 15% consists of visual assets (`cover_image_url`, `recent_posts`) and UI-specific configuration options (`keywords`, `high_match_count`).

**Immediate Action**: Implement the SQL migration and update Pydantic models to unblock frontend development of profile cards and modals.
