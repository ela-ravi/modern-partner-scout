# PartnerScout AI - Manual API Testing Guide

This guide provides step-by-step instructions for manually testing PartnerScout API endpoints using Swagger UI and curl.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Authentication Setup](#2-authentication-setup)
3. [Jobs API Testing](#3-jobs-api-testing)
4. [Agent API Testing](#4-agent-api-testing)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Prerequisites

### 1.1 Start the Backend Server

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The server will be available at `http://localhost:8000`.

### 1.2 Access Swagger UI

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 1.3 Verify Test User Exists

A test user must exist in Supabase's `auth.users` table. To check or create one:

```bash
cd backend
source venv/bin/activate
python -c "
from app.db.supabase import get_supabase_admin_client

db = get_supabase_admin_client()
result = db.from_('users').select('id, email').execute()
print('Existing users:', result.data)
"
```

If no users exist, the system will create one automatically when you first authenticate, or you can create one via Supabase Dashboard.

**Current Test User ID**: `5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9`

### 1.4 Environment Configuration

Ensure your `backend/.env` file has these configured:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
N8N_SERVICE_KEY=test-service-key-12345
```

---

## 2. Authentication Setup

PartnerScout uses two authentication methods:

| Auth Type | Header | Used For |
|-----------|--------|----------|
| **BearerAuth** | `Authorization: Bearer <JWT>` | User-facing endpoints (`/api/jobs`, etc.) |
| **ServiceKeyAuth** | `X-Service-Key: <key>` | Agent endpoints (`/api/agent/*`) called by N8N/orchestrator |

### 2.1 Generate a Test JWT Token

Run this command to generate a fresh token (valid for 1 hour):

```bash
cd backend
source venv/bin/activate
python -c "from app.guards.auth import create_test_token; print(create_test_token('5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9'))"
```

**Sample Output:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1YmY0NWYxYy0yYzBlLTRmY2QtYWI2NC05ZGJiYzQ0MDJjYTkiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImlhdCI6MTc3MDI4NTEzMSwiZXhwIjoxNzcwMjg4NzMxLCJhdWQiOiJhdXRoZW50aWNhdGVkIn0.E3R_trJXhteOvfqXBrNoSepwweDjl56xPL0OTcLk6zs
```

### 2.2 Authorize in Swagger UI

1. Open http://localhost:8000/docs
2. Click the **"Authorize"** button (🔒 icon, top right)
3. In the popup:
   - **BearerAuth**: Paste your JWT token (without "Bearer" prefix)
   - **ServiceKeyAuth**: Enter `test-service-key-12345` (for agent endpoints)
4. Click **"Authorize"** then **"Close"**

> **Note**: The token expires after 1 hour. Regenerate if you get `401 UNAUTHORIZED` errors.

### 2.3 Using curl with Authentication

**For User Endpoints (BearerAuth):**
```bash
TOKEN="your-jwt-token-here"
curl -X GET http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**For Agent Endpoints (ServiceKeyAuth):**
```bash
curl -X POST http://localhost:8000/api/agent/analyze-brand \
  -H "X-Service-Key: test-service-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "..."}'
```

---

## 3. Jobs API Testing

All Jobs API endpoints require **BearerAuth** (JWT token).

### 3.1 Create a New Job

**Endpoint:** `POST /api/jobs`

**Swagger Steps:**
1. Navigate to `POST /api/jobs` section
2. Click "Try it out"
3. Enter the request body:

```json
{
  "brand_description": "Sustainable fashion brand focused on minimalist aesthetics, ethical production, and timeless wardrobe essentials.",
  "reference_profiles": [
    "https://instagram.com/everlane",
    "https://instagram.com/reformation"
  ],
  "name": "Sustainable Fashion Discovery",
  "follower_range_min": 5000,
  "follower_range_max": 500000,
  "discovery_limit": 50,
  "keywords": ["sustainable", "ethical", "minimalist"],
  "hashtags": ["sustainablefashion", "ethicalfashion"],
  "min_score_threshold": 60
}
```

4. Click "Execute"

**Expected Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9",
  "name": "Sustainable Fashion Discovery",
  "brand_description": "Sustainable fashion brand...",
  "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/reformation"],
  "status": "pending",
  "created_at": "2026-02-05T10:30:00Z",
  "updated_at": "2026-02-05T10:30:00Z"
}
```

**curl Command:**
```bash
TOKEN="your-jwt-token"
curl -X POST http://localhost:8000/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_description": "Sustainable fashion brand focused on minimalist aesthetics",
    "reference_profiles": ["https://instagram.com/everlane", "https://instagram.com/reformation"],
    "name": "Test Job",
    "follower_range_min": 5000,
    "follower_range_max": 500000,
    "discovery_limit": 50
  }'
```

**Validation Rules:**
- `brand_description`: Required, 10-5000 characters
- `reference_profiles`: Required, 2-10 valid Instagram URLs
- `name`: Optional, max 100 characters
- `follower_range_min`: Optional, default 5000
- `follower_range_max`: Optional, default 500000
- `discovery_limit`: Optional, default 50, max 100
- `keywords`: Optional, array of strings (auto-normalized to lowercase)
- `hashtags`: Optional, array of strings (auto-prefixed with #)
- `min_score_threshold`: Optional, 0-100 (default 50)

---

### 3.2 List All Jobs

**Endpoint:** `GET /api/jobs`

**Swagger Steps:**
1. Navigate to `GET /api/jobs` section
2. Click "Try it out"
3. Optionally set query parameters:
   - `status`: Filter by status (pending, analyzing, discovering, scoring, completed, failed)
   - `limit`: Number of results (default 50)
   - `offset`: Pagination offset (default 0)
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "jobs": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Sustainable Fashion Discovery",
      "status": "pending",
      "created_at": "2026-02-05T10:30:00Z",
      "profile_count": 0
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/jobs?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3.3 Get Job Details

**Endpoint:** `GET /api/jobs/{job_id}`

**Swagger Steps:**
1. Navigate to `GET /api/jobs/{job_id}` section
2. Click "Try it out"
3. Enter the `job_id` from a previously created job
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9",
  "name": "Sustainable Fashion Discovery",
  "brand_description": "...",
  "status": "pending",
  "profiles": [],
  "brand_dna": null,
  "created_at": "2026-02-05T10:30:00Z"
}
```

**curl Command:**
```bash
JOB_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
curl -X GET "http://localhost:8000/api/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3.4 Start Discovery Workflow

**Endpoint:** `POST /api/jobs/{job_id}/start`

> **Note**: This endpoint triggers the N8N webhook. If N8N is not running, you'll get an `N8N_ERROR`.

**Swagger Steps:**
1. Navigate to `POST /api/jobs/{job_id}/start` section
2. Click "Try it out"
3. Enter the `job_id`
4. Click "Execute"

**Expected Response (202 Accepted):**
```json
{
  "message": "Discovery workflow started",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "analyzing"
}
```

**Expected Error (N8N not running):**
```json
{
  "error": {
    "code": "N8N_ERROR",
    "message": "Failed to trigger discovery workflow: [Errno 61] Connection refused"
  }
}
```

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/jobs/$JOB_ID/start" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3.5 Update Job

**Endpoint:** `PATCH /api/jobs/{job_id}`

**Swagger Steps:**
1. Navigate to `PATCH /api/jobs/{job_id}` section
2. Click "Try it out"
3. Enter the `job_id`
4. Enter the fields to update:

```json
{
  "name": "Updated Job Name",
  "discovery_limit": 75
}
```

5. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Updated Job Name",
  "discovery_limit": 75,
  "status": "pending"
}
```

**curl Command:**
```bash
curl -X PATCH "http://localhost:8000/api/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Job Name"}'
```

---

### 3.6 Delete Job

**Endpoint:** `DELETE /api/jobs/{job_id}`

**Swagger Steps:**
1. Navigate to `DELETE /api/jobs/{job_id}` section
2. Click "Try it out"
3. Enter the `job_id`
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "message": "Job deleted successfully",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**curl Command:**
```bash
curl -X DELETE "http://localhost:8000/api/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3.7 Get Job Quota

**Endpoint:** `GET /api/jobs/quota`

Check remaining daily job creation quota.

**Expected Response (200 OK):**
```json
{
  "daily_limit": 10,
  "used_today": 2,
  "remaining": 8
}
```

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/jobs/quota" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3.8 Cancel Job

**Endpoint:** `POST /api/jobs/{job_id}/cancel`

Cancel a running discovery job mid-execution.

**Swagger Steps:**
1. Navigate to `POST /api/jobs/{job_id}/cancel` section
2. Click "Try it out"
3. Enter the `job_id` of a pending/running job
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "status": "cancelled",
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "cancelled_at": "2026-02-06T10:00:00Z",
  "message": "Discovery job cancelled successfully"
}
```

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/jobs/$JOB_ID/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

**Cancellable States:** `pending`, `analyzing`, `discovering`, `scoring`

**Non-Cancellable States:** `completed`, `cancelled`, `failed`

---

### 3.9 Demo Mode (No Auth Required)

**Endpoint:** `POST /api/demo/start`

Create a demo job with 10 pre-seeded, pre-scored profiles. Works without authentication.

**Swagger Steps:**
1. Navigate to `POST /api/demo/start` section
2. Click "Try it out"
3. Click "Execute" (no auth needed)

**Expected Response (201 Created):**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "message": "Demo job created with 10 sample profiles",
  "profiles_count": 10,
  "redirect_url": "/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "is_demo": true
}
```

**curl Command:**
```bash
curl -X POST "http://localhost:8000/api/demo/start"
```

> **Note**: Demo jobs are immediately in `completed` status with 10 sample sustainable lifestyle profiles, each with scores and recommendations.

---

### 3.10 Toggle Profile Bookmark

**Endpoint:** `PATCH /api/profiles/{profile_id}/bookmark`

Toggle the bookmark status of a discovered profile. Each call flips the `is_bookmarked` boolean.

**Swagger Steps:**
1. Navigate to `PATCH /api/profiles/{profile_id}/bookmark` section
2. Click "Try it out"
3. Enter a valid `profile_id` from a discovered profile
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "is_bookmarked": true
}
```

**curl Command:**
```bash
PROFILE_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
curl -X PATCH "http://localhost:8000/api/profiles/$PROFILE_ID/bookmark" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Notes:**
- First call sets `is_bookmarked: true`, second call sets `is_bookmarked: false`
- Use `GET /api/jobs/{job_id}?is_bookmarked=true` to filter only bookmarked profiles

---

### 3.11 Get Job Analytics

**Endpoint:** `GET /api/jobs/{job_id}/analytics`

Get aggregated analytics for a job including profile counts, average scores, and score distribution.

**Expected Response (200 OK):**
```json
{
  "total_profiles": 19,
  "done_profiles": 9,
  "avg_score": 54,
  "max_score": 82,
  "profiles_with_email": 3,
  "new_profiles": 10,
  "score_distribution": {
    "excellent": 1,
    "good": 3,
    "moderate": 4,
    "poor": 1
  }
}
```

**curl Command:**
```bash
curl -X GET "http://localhost:8000/api/jobs/$JOB_ID/analytics" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 4. Agent API Testing

Agent endpoints are called by the workflow orchestrator (N8N or Python script) and require **ServiceKeyAuth**.

### 4.1 Authentication for Agent Endpoints

Use the `X-Service-Key` header with the value from your `.env` file:

```bash
curl -X POST http://localhost:8000/api/agent/analyze-brand \
  -H "X-Service-Key: test-service-key-12345" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "..."}'
```

In Swagger UI, authorize using **ServiceKeyAuth** (not BearerAuth).

### 4.2 Agent Endpoints Overview

| Endpoint | Purpose |
|----------|---------|
| `POST /api/agent/analyze-brand` | Extract brand DNA from reference profiles |
| `POST /api/agent/discover` | Find candidate Instagram profiles |
| `POST /api/agent/score` | Score and rank candidate profiles |
| `GET /api/agent/status` | Check agent service health |

> **Full agent documentation**: See [Agents_Documentation.md](./Agents_Documentation.md)

---

## 5. Troubleshooting

### 5.1 401 UNAUTHORIZED - "Authorization header required"

**Cause**: Missing or invalid JWT token.

**Solutions:**
1. Ensure you've authorized in Swagger UI (click "Authorize" button)
2. Regenerate token if expired:
   ```bash
   python -c "from app.guards.auth import create_test_token; print(create_test_token('5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9'))"
   ```
3. In Swagger, paste token WITHOUT "Bearer" prefix

### 5.2 401 UNAUTHORIZED - "Invalid service key"

**Cause**: Wrong `X-Service-Key` for agent endpoints.

**Solutions:**
1. Check `N8N_SERVICE_KEY` in your `.env` file
2. Restart the server after changing `.env`
3. Use the same key in your request header

### 5.3 422 VALIDATION_ERROR - Foreign Key Constraint

**Cause**: The user ID in your token doesn't exist in the database.

**Solutions:**
1. Check existing users:
   ```bash
   python -c "
   from app.db.supabase import get_supabase_admin_client
   db = get_supabase_admin_client()
   print(db.from_('users').select('id').execute().data)
   "
   ```
2. Create token with an existing user ID
3. Or create a new user via Supabase Dashboard

### 5.4 422 VALIDATION_ERROR - Reference Profiles

**Error**: "At least 2 valid reference profiles are required"

**Solution**: Provide 2-10 valid Instagram URLs in `reference_profiles` array.

### 5.5 N8N_ERROR - Connection Refused

**Cause**: N8N is not running when calling `/api/jobs/{job_id}/start`.

**Solutions:**
1. Start N8N if you want workflow orchestration
2. Or use the Python fallback orchestrator (see [Orchestration.md](./Orchestration.md))
3. For testing without N8N, job creation and listing still work

### 5.6 JOB_NOT_FOUND

**Cause**: Job doesn't exist or belongs to another user.

**Solutions:**
1. Verify job ID is correct
2. Ensure you're using a token for the user who created the job
3. List jobs first to get valid job IDs: `GET /api/jobs`

---

## Quick Reference

### Generate New Token
```bash
cd backend && source venv/bin/activate
python -c "from app.guards.auth import create_test_token; print(create_test_token('5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9'))"
```

### Test User ID
```
5bf45f1c-2c0e-4fcd-ab64-9dbbc4402ca9
```

### Service Key
```
test-service-key-12345
```

### API Base URL
```
http://localhost:8000
```

### Swagger UI
```
http://localhost:8000/docs
```

---

## LLM Provider Configuration

Set in `backend/.env`:

```bash
# Choose one LLM provider
LLM_PROVIDER=huggingface  # Options: openai, gemini, ollama, openrouter, huggingface

# Choose one embedding provider  
EMBEDDING_PROVIDER=huggingface  # Options: openai, gemini, huggingface
```

### Provider API Keys

| Provider | Env Variable | Get Key At |
|----------|-------------|------------|
| OpenAI | `OPENAI_API_KEY` | platform.openai.com |
| Gemini | `GEMINI_API_KEY` | ai.google.dev |
| OpenRouter | `OPENROUTER_API_KEY` | openrouter.ai/keys |
| HuggingFace | `HUGGINGFACE_API_KEY` | huggingface.co/settings/tokens |

### Recommended: HuggingFace (Free)

```bash
LLM_PROVIDER=huggingface
HUGGINGFACE_API_KEY=hf_xxx
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
EMBEDDING_PROVIDER=huggingface
```

