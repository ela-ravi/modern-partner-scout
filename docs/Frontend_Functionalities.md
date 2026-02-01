# PartnerScout AI - Frontend Functionalities Reference

> A comprehensive list of all frontend functionalities extracted from project documentation. Use this as a checklist when designing and building the frontend.

---

## Table of Contents

1. [Authentication & User Management](#1-authentication--user-management)
2. [Discovery Session Management](#2-discovery-session-management)
3. [Brand Analysis](#3-brand-analysis)
4. [Profile Discovery](#4-profile-discovery)
5. [Profile Scoring](#5-profile-scoring)
6. [Contact Extraction](#6-contact-extraction)
7. [Dashboard Views](#7-dashboard-views)
8. [Profile Detail View](#8-profile-detail-view)
9. [Email Composer](#9-email-composer-mock)
10. [Real-time Updates](#10-real-time-updates)
11. [Error Handling](#11-error-handling)
12. [Analytics Summary](#12-analytics-summary)
13. [UI States](#13-ui-states)

---

## 1. Authentication & User Management

| # | Functionality |
|---|---------------|
| 1 | User sign up with email/password via Supabase Auth |
| 2 | User login with existing credentials |
| 3 | User logout and session termination |
| 4 | JWT token validation for all API requests |
| 5 | Multi-user support with data isolation per user |

---

## 2. Discovery Session Management

| # | Functionality |
|---|---------------|
| 6 | Create new discovery session with brand description and reference profiles |
| 7 | List all past discovery sessions for current user |
| 8 | View single session details with all profiles and scores |
| 9 | Start/resume a discovery session workflow |
| 10 | Delete a session and all related data |
| 11 | Session status tracking (pending → analyzing → discovering → scoring → completed/failed) |
| 12 | Switch between multiple sessions without losing data |
| 13 | View session progress (profiles discovered / profiles scored) |
| 14 | Retry failed sessions via `POST /api/jobs/{id}/retry` |

---

## 3. Brand Analysis

| # | Functionality |
|---|---------------|
| 15 | Input brand description text |
| 16 | Add 2-10 reference Instagram profile URLs |
| 17 | Extract brand DNA (hashtags, keywords, embedding vector) from references |
| 18 | Display extracted hashtags and keywords |
| 19 | Store brand identity for matching |

---

## 4. Profile Discovery

| # | Functionality |
|---|---------------|
| 20 | Discover similar Instagram profiles based on brand DNA |
| 21 | Search by hashtags and keywords |
| 22 | Filter profiles by follower count range (10K-500K) |
| 23 | Deduplicate discovered profiles by username |
| 24 | Set discovery limit (default: 50 profiles) |
| 25 | Display discovered profiles with username, full_name, profile_picture, bio, followers, following, posts_count, engagement_rate, and URL |
| 25a | Display external_url (website link from bio) |
| 25b | Display business_email (for business accounts) |
| 25c | Display business_category (business type) |
| 25d | Display following_ratio (following/followers for fake detection) |

---

## 5. Profile Scoring

| # | Functionality |
|---|---------------|
| 26 | Score profiles against brand DNA (0-100 scale) |
| 27 | Calculate visual aesthetic match sub-score (0-100, 25% weight) |
| 28 | Calculate content theme alignment sub-score (0-100, 20% weight) |
| 29 | Calculate engagement rate sub-score (0-100, 15% weight) |
| 30 | Calculate follower quality sub-score (0-100, 15% weight) - fake detection |
| 31 | Calculate business indicators sub-score (0-100, 15% weight) |
| 32 | Calculate activity recency sub-score (0-100, 10% weight) |
| 33 | Display overall weighted score |
| 34 | Show AI-generated reasoning/summary for each score |
| 35 | Show AI-generated partnership recommendation |
| 36 | Display authenticity verdict (genuine/suspicious/fake) based on follower_quality |
| 37 | Filter profiles by minimum score threshold (default: ≥50) via `?min_score=50` |

---

## 6. Contact Extraction

| # | Functionality |
|---|---------------|
| 38 | Extract email from profile bio |
| 39 | Extract email from business_email field (Apify) |
| 40 | Extract email from linked website |
| 41 | Display extracted email with source indicator (bio/business_email/website) |
| 42 | Show email availability icon on profile cards |

---

## 7. Dashboard Views

| # | Functionality |
|---|---------------|
| 43 | **NEW tab** - Display freshly discovered profiles (not yet scored) |
| 44 | **PROCESSING tab** - Display profiles currently being scored |
| 45 | **DONE tab** - Display final ranked profiles with scores |
| 46 | Profile cards with profile_picture_url, username, full_name, follower count |
| 47 | Score badge/indicator on profile cards |
| 48 | Authenticity indicator on profile cards (Genuine/Suspicious/Fake) |
| 49 | Email availability indicator on profile cards |
| 50 | Sort profiles by score (highest first) via `?sort=score&order=desc` |
| 51 | Real-time updates as profiles are discovered and scored |
| 52 | Progress bar/indicator showing discovery status |
| 53 | Session selector dropdown to switch sessions |

---

## 8. Profile Detail View

| # | Functionality |
|---|---------------|
| 54 | Full profile information display (username, full_name, bio, profile_picture_url) |
| 55 | Score breakdown visualization (all 6 dimensions with weights) |
| 56 | Visual aesthetic match (25%) bar/chart |
| 57 | Content theme alignment (20%) bar/chart |
| 58 | Engagement rate score (15%) bar/chart |
| 59 | Follower quality (15%) bar/chart with authenticity verdict |
| 60 | Business indicators (15%) bar/chart |
| 61 | Activity recency (10%) bar/chart |
| 62 | AI reasoning/summary display |
| 63 | Partnership recommendation display |
| 64 | Contact information display |
| 65 | Link to Instagram profile |
| 65a | Display follower/following counts, posts_count, and following_ratio |
| 65b | Display engagement rate |
| 65c | Display verification and business account badges |
| 65d | Display external_url (website) and business_category |
| 65e | Display authenticity badge (Genuine/Suspicious/Fake based on follower_quality)

---

## 9. Email Composer (Mock)

| # | Functionality |
|---|---------------|
| 56 | AI-generated email draft based on profile and brand |
| 57 | Preview outreach email before sending |
| 58 | Send email button (mock/demo only) |

---

## 10. Real-time Updates

| # | Functionality |
|---|---------------|
| 59 | Live profile card appearance as discovered |
| 60 | Live score badge updates when scoring completes |
| 61 | Live email icon appearance when contact extracted |
| 62 | Live status transitions (NEW → PROCESSING → DONE) |
| 63 | Live progress counter updates |
| 64 | WebSocket/polling for dashboard updates (every 2s) |

---

## 11. Error Handling

| # | Functionality |
|---|---------------|
| 65 | Display error messages for failed operations |
| 66 | Show job failure status with error details |
| 67 | Graceful fallback when services unavailable |
| 68 | Invalid input validation feedback |
| 69 | Daily job limit exceeded notification |

---

## 12. Analytics Summary

> **API:** `GET /api/jobs/{id}/analytics` returns pre-calculated analytics

| # | Functionality |
|---|---------------|
| 70 | Total profiles discovered count (`profiles_discovered`) |
| 71 | Total profiles scored count (`profiles_scored`) |
| 72 | Average score across all profiles (`average_score`) |
| 73 | Count of profiles with email (`profiles_with_email`) |
| 74 | Count of high-scoring profiles by tier (`score_distribution.excellent/good/moderate/poor`) |

---

## 13. UI States

| # | Functionality |
|---|---------------|
| 75 | Empty state for new users (no sessions) |
| 76 | Loading states during API calls |
| 77 | Skeleton loaders for profile cards |
| 78 | Success/confirmation toasts |
| 79 | Error toast notifications |

---

## Page/Component Mapping

| Page/Component | Functionalities |
|----------------|-----------------|
| **Login/Signup Page** | 1, 2 |
| **Session List Page** | 7, 10, 12, 14, 49, 75 |
| **New Session Form** | 6, 15, 16 |
| **Main Dashboard** | 39-49, 59-64, 70-74, 76-79 |
| **Profile Card Component** | 25, 42-44, 55a-55c |
| **Profile Detail Modal** | 50-55, 55a-55c |
| **Email Composer Modal** | 56-58 (uses `POST /api/email/generate` and `POST /api/email/send`) |
| **Progress Indicator** | 11, 13, 47, 63 |
| **Error Display** | 65-69, 79 |
| **Brand DNA Display** | 17, 18 |
| **Analytics Panel** | 70-74 (uses `GET /api/jobs/{id}/analytics`) |

---

## API Endpoints Reference

| Functionality | API Endpoint |
|---------------|--------------|
| Create session | `POST /api/jobs` |
| List sessions | `GET /api/jobs` |
| Get session details | `GET /api/jobs/{id}` |
| Get session analytics | `GET /api/jobs/{id}/analytics` |
| Start discovery | `POST /api/jobs/{id}/start` |
| Retry failed session | `POST /api/jobs/{id}/retry` |
| Update session name | `PATCH /api/jobs/{id}` |
| Delete session | `DELETE /api/jobs/{id}` |
| Generate outreach email | `POST /api/email/generate` |
| Send email (mock) | `POST /api/email/send` |
| Real-time updates | Supabase Realtime WebSocket |

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `docs/Partner_Scout_AI_PRD.md` | Product requirements and user stories |
| `docs/Backend_Implementation_Guide.md` | API contracts and data models |
| `docs/Supabase_Database_Guide.md` | Database schema and TypeScript types |
| `designs/*.html` | UI mockups and design references |

---

*Last updated: February 2026*

