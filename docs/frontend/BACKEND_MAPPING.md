# Frontend-to-Backend API Mapping

> Complete verification of all frontend design requirements against backend API availability.
> 
> ✅ = Available | ❌ = Missing (see ../BACKEND_GAPS_TODO.md) | ⚠️ = Partial

---

## 1. Authentication (`login.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Sign in with email/password | Supabase Auth | ✅ |
| Sign up with email/password | Supabase Auth | ✅ |
| Password reset | Supabase Auth | ✅ |
| Session management | JWT + Supabase | ✅ |

---

## 2. Empty Dashboard (`empty-dashboard.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Start New Discovery button | → New Session Page | ✅ (Frontend route) |
| Watch Demo button | `POST /api/demo/start` | ✅ |

---

## 3. Session List (`session-list.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| List all sessions | `GET /api/jobs` | ✅ |
| Session status badge | Job `status` field | ✅ |
| Profiles discovered count | Job `profiles_discovered` field | ✅ |
| Profiles scored count | Job `profiles_scored` field | ✅ |
| Delete session | `DELETE /api/jobs/{id}` | ✅ |
| Filter by status | `GET /api/jobs?status=completed` | ✅ |
| Click to open session | `GET /api/jobs/{id}` | ✅ |

---

## 4. New Session - Step 1 (`discovery-engine-step1.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Campaign name input | `POST /api/jobs` → `name` | ✅ |
| Brand description textarea | `POST /api/jobs` → `brand_description` | ✅ |
| Reference profiles (2-10) | `POST /api/jobs` → `reference_profiles` | ✅ |
| Keywords input | `POST /api/jobs` → `keywords` | ✅ |
| Hashtags input | `POST /api/jobs` → `hashtags` | ✅ |
| Profiles to discover slider | `POST /api/jobs` → `discovery_limit` | ✅ |
| Minimum score threshold | `POST /api/jobs` → `min_score_threshold` | ✅ |
| Follower range (min/max) | `POST /api/jobs` → `follower_range_min/max` | ✅ |

---

## 5. New Session - Step 2 (`discovery-engine-step2.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Review all inputs | Frontend state | ✅ (No API needed) |
| Launch Discovery button | `POST /api/jobs` + `POST /api/jobs/{id}/start` | ✅ |

---

## 6. Main Dashboard (`main-discovery-dashboard.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Header session selector | `GET /api/jobs` | ✅ |
| Tab: New profiles | `GET /api/jobs/{id}?profile_status=new` | ✅ |
| Tab: Processing profiles | `GET /api/jobs/{id}?profile_status=processing` | ✅ |
| Tab: Done profiles | `GET /api/jobs/{id}?profile_status=done` | ✅ |
| Profile grid display | `GET /api/jobs/{id}` → `profiles` | ✅ |
| Filter by min score | `GET /api/jobs/{id}?min_score=70` | ✅ |
| Pagination | `GET /api/jobs/{id}?profile_limit=50&profile_offset=0` | ✅ |
| Sort by score | `GET /api/jobs/{id}?sort=score&order=desc` | ❌ #4b |
| Search by username | `GET /api/jobs/{id}?search=keyword` | ❌ #4 |
| Analytics panel | `GET /api/jobs/{id}/analytics` | ✅ |
| Real-time updates | Supabase Realtime subscriptions | ✅ |
| Start New Discovery button | → New Session Page | ✅ (Frontend route) |

---

## 7. Processing Pipeline (`ai-agent-processing-pipeline.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Pipeline stage visualization | Job `status` field | ✅ |
| Progress indicators | Job `profiles_discovered`, `profiles_scored` | ✅ |
| Cancel/Stop button | `POST /api/jobs/{id}/cancel` | ✅ |
| Error state display | Job `error_message` field | ✅ |
| Activity log (live) | Real-time + logs | ❌ #6 |

---

## 8. Profile Detail Modal (`profile-detail-model-view.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Profile info (name, bio, etc.) | Profile data in job response | ✅ |
| Followers/Following/Posts | Profile data | ✅ |
| Engagement rate | Profile `engagement_rate` | ✅ |
| Match score (circular) | Profile `final_score` | ✅ |
| Score breakdown (6 dims) | Profile score dimensions | ✅ |
| AI Analysis text | Profile `reasoning` | ✅ |
| Recommendation badge | Profile `recommendation` | ✅ |
| Contact info (email) | Profile `contact_email` | ✅ |
| View on Instagram link | External URL | ✅ (No API needed) |
| Compose Email button | → Email Composer | ✅ (Frontend route) |
| Save/Bookmark button | `POST /api/profiles/{id}/bookmark` | ❌ #2 |
| Skip button | `PATCH /api/profiles/{id}` skipped | ❌ #3 |

---

## 9. Email Composer (`ai-email-composer.html`)

| UI Feature | Backend API | Status |
|------------|-------------|--------|
| Subject line input | Client-side | ✅ |
| Email body editor | Client-side | ✅ |
| Generate with AI button | `POST /api/email/generate` | ✅ |
| Tone selector dropdown | `GET /api/email/tones` | ✅ |
| Personalization chips | AI suggestions in response | ✅ |
| Preview toggle | Client-side | ✅ |
| Send Email button | `POST /api/email/send` | ✅ |
| Load template dropdown | `GET /api/email/templates` | ❌ #7 |
| Save as Draft button | `POST /api/email/drafts` | ❌ #9 |
| Schedule for later | Email scheduling | ❌ #10 |

---

## Summary

### ✅ Available APIs (All Core Features Ready)

| Count | Category |
|-------|----------|
| 20+ | Fully implemented endpoints |
| 100% | Core job CRUD operations |
| 100% | Agent endpoints (analyze, discover, score) |
| 100% | Email generation and sending |
| 100% | Demo mode |
| 100% | Job control (start, cancel, retry) |

### ❌ Missing APIs (Already in BACKEND_GAPS_TODO.md)

| # | Feature | Priority |
|---|---------|----------|
| 2 | Bookmark Profile | HIGH |
| 3 | Skip Profile | HIGH |
| 4 | Profile Search | HIGH |
| **4b** | **Profile Sorting** *(NEW)* | **HIGH** |
| 6 | Activity Logs | MEDIUM |
| 7 | Email Templates CRUD | MEDIUM |
| 9 | Save Email Drafts | LOW |
| 10 | Email Scheduling | LOW |

### New Gap Found

**#4b Profile Sorting** - The main dashboard design shows a "Sort by: Score (High to Low)" dropdown, but `GET /api/jobs/{id}` doesn't support `?sort=` parameter.

---

## Conclusion

**All core frontend features have backend API support.**

The only missing features are already documented in `../BACKEND_GAPS_TODO.md` with the addition of:
- **#4b Profile Sorting** - Add `?sort=score&order=desc` to profile listing

No other gaps found between frontend designs and backend APIs.

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Frontend architecture patterns
- [TECH_STACK.md](./TECH_STACK.md) - Technology decisions
- [GAPS_TODO.md](./GAPS_TODO.md) - Frontend implementation gaps
- [../BACKEND_GAPS_TODO.md](../BACKEND_GAPS_TODO.md) - Backend implementation gaps

---

*Last updated: February 2026*
