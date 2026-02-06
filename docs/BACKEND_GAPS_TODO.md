# Backend Implementation Gaps - TODO

> Generated from Design-API Gap Analysis (Feb 2026)
> These items are needed to fully support all functionalities in the 10 design files.

---

## HIGH Priority (Core functionality gaps)

- [x] **1. Job Control Endpoints (Cancel/Stop)** ✅ COMPLETED
  - `POST /api/jobs/{job_id}/cancel`
  - Stop a running discovery workflow mid-execution
  - Update job status to `cancelled`
  - ✅ Implemented: Feb 2026

- [ ] **2. Bookmark Profile**
  - `POST /api/profiles/{profile_id}/bookmark` - Save/bookmark a profile
  - `DELETE /api/profiles/{profile_id}/bookmark` - Remove bookmark
  - `GET /api/jobs/{job_id}/bookmarks` - Get bookmarked profiles for a job
  - Requires: Add `bookmarked` boolean column to `discovered_profiles` table

- [ ] **3. Skip Profile**
  - `PATCH /api/profiles/{profile_id}` with `{ "skipped": true }`
  - Or dedicated `POST /api/profiles/{profile_id}/skip`
  - Requires: Add `skipped` boolean column to `discovered_profiles` table

- [ ] **4. Profile Search**
  - Add `?search=` query parameter to `GET /api/jobs/{job_id}`
  - Filter profiles by username or full_name (case-insensitive)

- [ ] **4b. Profile Sorting** *(NEW)*
  - Add `?sort=score&order=desc` query parameters to `GET /api/jobs/{job_id}`
  - Support sorting by: `score`, `followers_count`, `engagement_rate`, `created_at`
  - Order: `asc` or `desc` (default: `desc` for score)
  - Frontend design shows "Sort by: Score (High to Low)" dropdown

---

## MEDIUM Priority (Enhanced UX)

- [x] **5. Job Creation Enhancements (Keywords, Hashtags, Min Score)** ✅ COMPLETED
  - Add `keywords` and `hashtags` array fields to `POST /api/jobs`
  - Add `min_score_threshold` field to filter profiles
  - Store user-provided keywords alongside AI-extracted ones
  - Requires: Add columns to `discovery_jobs` table
  - ✅ Implemented: Feb 2026 - Migration: `004_job_creation_enhancements.sql`

- [ ] **6. Real-time Activity Logs**
  - `GET /api/jobs/{job_id}/logs` - Fetch recent activity logs
  - WebSocket/SSE endpoint for streaming updates (stretch)
  - Requires: New `activity_logs` table

- [ ] **7. Email Templates CRUD**
  - `POST /api/email/templates` - Create template
  - `GET /api/email/templates` - List user's templates
  - `GET /api/email/templates/{id}` - Get single template
  - `PATCH /api/email/templates/{id}` - Update template
  - `DELETE /api/email/templates/{id}` - Delete template
  - Requires: New `email_templates` table

---

## LOW Priority (Nice-to-have)

- [x] **8. Demo/Seed Data Mode** ✅ COMPLETED
  - `POST /api/demo/start` - Create demo job with pre-seeded profiles
  - Supports "Watch Demo" button in empty dashboard
  - Uses seed data, no actual API calls
  - ✅ Implemented: Feb 2026 - Creates 10 pre-scored profiles

- [ ] **9. Save Email Drafts**
  - `POST /api/email/drafts` - Save draft
  - `GET /api/email/drafts` - List drafts
  - `GET /api/email/drafts/{id}` - Get draft
  - `PATCH /api/email/drafts/{id}` - Update draft
  - `DELETE /api/email/drafts/{id}` - Delete draft
  - Requires: New `email_drafts` table

- [ ] **10. Email Scheduling**
  - Implement actual scheduling logic for `schedule_for` field
  - Background job to send scheduled emails
  - Requires: Job queue (Celery, APScheduler, etc.)

- [ ] **11. Email Quality Score**
  - Add `quality_score` (0-100) to `POST /api/email/generate` response
  - Evaluate personalization, length, tone match

- [ ] **12. AI Personalization Insights**
  - Add `insights` array to `POST /api/email/generate` response
  - Suggestions like "Mention their viral post", "Reference location"

- [ ] **13. Global Analytics**
  - `GET /api/analytics` - User-level analytics across all jobs
  - Total profiles discovered, average scores, email success rate

- [ ] **14. User Preferences**
  - `GET /api/user/preferences` - Get user settings
  - `PATCH /api/user/preferences` - Update settings
  - Default tones, notification preferences, etc.

---

## Database Schema Changes Required

| Table | Change | For Item |
|-------|--------|----------|
| `discovered_profiles` | Add `bookmarked` (boolean, default false) | #2 |
| `discovered_profiles` | Add `skipped` (boolean, default false) | #3 |
| `discovery_jobs` | Add `keywords` (text[]), `hashtags` (text[]) | #7 |
| `discovery_jobs` | Add `min_score_threshold` (int, default 50) | #7 |
| `email_templates` | New table (id, user_id, name, type, subject_template, body_template, created_at, updated_at) | #5 |
| `email_drafts` | New table (id, user_id, profile_id, job_id, subject, body, tone, created_at, updated_at) | #9 |
| `activity_logs` | New table (id, job_id, event_type, message, metadata, created_at) | #6 |

---

## Implementation Order Recommendation

1. **Phase 1 - Core:** Items 1, 2 (Cancel Job, Bookmark)
2. **Phase 2 - UX Polish:** Items 3, 4, 5, 7 (Skip, Search, Templates, Keywords)
3. **Phase 3 - Real-time:** Item 6 (Activity Logs)
4. **Phase 4 - Nice-to-have:** Items 8-14

---

*Last updated: February 2026*
