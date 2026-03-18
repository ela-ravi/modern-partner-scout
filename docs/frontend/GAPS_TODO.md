# Frontend Implementation Gaps - TODO

> Generated from Design-to-Implementation Gap Analysis (Feb 2026)
> 
> **Current State:** Frontend is a bare placeholder with no actual implementation
> **Target:** 10 design files to implement with full backend integration

---

## Overview

| Category | Status | Notes |
|----------|--------|-------|
| Pages | ❌ None | 0/7 pages implemented |
| Components | ❌ None | 0/~25 components |
| Routing | ❌ None | No React Router setup |
| Auth | ❌ None | No Supabase Auth integration |
| API Services | ❌ None | No API client |
| State Management | ❌ None | No React Query setup |
| Real-time | ❌ None | No Supabase subscriptions |

---

## Pages to Implement (from designs/)

### 1. Authentication Page (`login.html`)
**Route:** `/login`, `/signup`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Email/password sign in | HIGH | Supabase Auth |
| Email/password sign up | HIGH | Supabase Auth |
| Form validation | HIGH | Client-side |
| Error handling | HIGH | Client-side |
| Redirect after auth | HIGH | React Router |

---

### 2. Empty Dashboard (`empty-dashboard.html`)
**Route:** `/` (when no sessions)

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Empty state illustration | MEDIUM | - |
| "Start New Discovery" button | HIGH | → New Session |
| **"Watch Demo" button** | HIGH | `POST /api/demo/start` ✅ |
| Animated elements | LOW | CSS animations |

---

### 3. Session List Page (`session-list.html`)
**Route:** `/sessions`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| List all sessions | HIGH | `GET /api/jobs` |
| Session cards with status badges | HIGH | - |
| Status colors (pending/analyzing/etc) | HIGH | - |
| Stats: profiles discovered, scored, avg score | HIGH | Job data |
| Delete session | MEDIUM | `DELETE /api/jobs/{id}` |
| Filter by status | MEDIUM | `GET /api/jobs?status=` |
| Search sessions | LOW | Client-side |
| Pagination | LOW | `?limit=&offset=` |

---

### 4. New Session - Step 1 (`discovery-engine-step1.html`)
**Route:** `/new-session`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Campaign name input | HIGH | - |
| Brand description textarea | HIGH | - |
| Reference profiles input (2-10 URLs) | HIGH | - |
| **Keywords input (tags)** | HIGH | Job creation ✅ |
| **Hashtags input (tags)** | HIGH | Job creation ✅ |
| Profiles to discover slider (10-100) | HIGH | - |
| **Minimum score threshold slider** | HIGH | Job creation ✅ |
| Follower range inputs (min/max) | HIGH | - |
| "Next: Review" button | HIGH | - |

---

### 5. New Session - Step 2 (`discovery-engine-step2.html`)
**Route:** `/new-session/review`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Review all inputs | HIGH | - |
| Edit individual sections | MEDIUM | - |
| "Launch Discovery" button | HIGH | `POST /api/jobs` + `POST /api/jobs/{id}/start` |
| Estimated time indicator | LOW | - |

---

### 6. Main Dashboard (`main-discovery-dashboard.html`)
**Route:** `/jobs/{id}`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Header with session selector | HIGH | `GET /api/jobs` |
| Tab navigation (New/Processing/Done) | HIGH | - |
| Profile grid with cards | HIGH | `GET /api/jobs/{id}` |
| Profile card: image, name, handle, followers | HIGH | - |
| Profile card: score badge | HIGH | - |
| Profile card: email icon | HIGH | - |
| Profile card: verified badge | MEDIUM | - |
| Sort by score | MEDIUM | `?sort=score` |
| Search profiles | MEDIUM | `?search=` |
| Analytics summary panel | HIGH | `GET /api/jobs/{id}/analytics` |
| Real-time updates | HIGH | Supabase Realtime |
| Skeleton loaders | MEDIUM | - |
| Toast notifications | MEDIUM | - |
| **Cancel job button** | HIGH | `POST /api/jobs/{id}/cancel` ✅ |

---

### 7. Processing Pipeline (`ai-agent-processing-pipeline.html`)
**Route:** `/jobs/{id}/processing` or modal

| Feature | Priority | Backend API |
|---------|----------|-------------|
| 4-stage pipeline visualization | HIGH | - |
| Stage 1: Brand Analyzer | HIGH | Status updates |
| Stage 2: Discovery Engine | HIGH | Status updates |
| Stage 3: Scoring Agent | HIGH | Status updates |
| Stage 4: Email Extractor | HIGH | Status updates |
| Progress indicators | HIGH | - |
| Live activity log | MEDIUM | - |
| **Stop/Cancel button** | HIGH | `POST /api/jobs/{id}/cancel` ✅ |
| Error state UI | MEDIUM | - |
| Daily limit warning | LOW | - |

---

### 8. Profile Detail Modal (`profile-detail-model-view.html`)
**Route:** Modal overlay

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Modal with backdrop | HIGH | - |
| Cover image + profile photo | HIGH | - |
| Username, full name, bio | HIGH | - |
| Stats: followers, following, posts, engagement | HIGH | - |
| Match score (circular progress) | HIGH | - |
| Score breakdown (6 dimensions) | HIGH | - |
| AI analysis text | HIGH | - |
| Recommendation badge | HIGH | - |
| Contact info section | HIGH | - |
| "Compose Email" button | HIGH | → Email Composer |
| "View on Instagram" link | HIGH | External link |
| Bookmark/Save button | ~~MEDIUM~~ ✅ DONE | `PATCH /api/profiles/{id}/bookmark` |
| Skip button | MEDIUM | Future: `POST /api/profiles/{id}/skip` |

---

### 9. Email Composer (`ai-email-composer.html`)
**Route:** Modal or `/compose/{profile_id}`

| Feature | Priority | Backend API |
|---------|----------|-------------|
| Subject line input | HIGH | - |
| Email body editor | HIGH | - |
| "Generate with AI" button | HIGH | `POST /api/email/generate` |
| Tone selector (formal/casual/friendly) | HIGH | - |
| Personalization chips | MEDIUM | - |
| Preview mode | MEDIUM | - |
| "Send Email" button | HIGH | `POST /api/email/send` |
| Schedule for later | LOW | Future |
| Save as draft | LOW | Future |

---

## Shared Components to Build

### Layout Components
| Component | Priority | Notes |
|-----------|----------|-------|
| `AppLayout` | HIGH | Header, nav, main content area |
| `Header` | HIGH | Logo, nav, session selector, user menu |
| `Sidebar` (optional) | LOW | If needed for navigation |

### UI Components
| Component | Priority | Notes |
|-----------|----------|-------|
| `Button` | HIGH | Primary, secondary, ghost variants |
| `Input` | HIGH | Text, email, password variants |
| `Textarea` | HIGH | For brand description |
| `Slider` | HIGH | For discovery limit, min score |
| `TagInput` | HIGH | For keywords, hashtags |
| `Badge` | HIGH | Status badges with colors |
| `Card` | HIGH | Session card, profile card |
| `Modal` | HIGH | For profile detail, email composer |
| `Toast` | MEDIUM | Success/error notifications |
| `Skeleton` | MEDIUM | Loading states |
| `Tabs` | HIGH | New/Processing/Done |
| `ProgressRing` | HIGH | Circular score display |
| `ProgressBar` | HIGH | Dimension score bars |
| `Avatar` | HIGH | User and profile avatars |
| `Dropdown` | MEDIUM | Session selector, user menu |

### Feature Components
| Component | Priority | Notes |
|-----------|----------|-------|
| `ProfileCard` | HIGH | Grid item with score, email icon |
| `ProfileDetailModal` | HIGH | Full profile view |
| `SessionCard` | HIGH | Session list item |
| `ScoreBreakdown` | HIGH | 6 dimension bars |
| `PipelineProgress` | HIGH | 4-stage visualization |
| `ActivityLog` | MEDIUM | Live updates list |
| `AnalyticsSummary` | HIGH | Stats panel |
| `EmptyState` | HIGH | For empty dashboard |

---

## Services/Hooks to Build

### API Services (`src/services/`)
| Service | Methods | Backend |
|---------|---------|---------|
| `api.ts` | Base axios/fetch client | - |
| `jobsApi.ts` | CRUD, start, cancel, analytics | `/api/jobs/*` |
| `profilesApi.ts` | Get profiles, toggle bookmark | `/api/jobs/{id}`, `/api/profiles/{id}/bookmark` |
| `emailApi.ts` | generate, send | `/api/email/*` |
| `demoApi.ts` | start demo | `/api/demo/start` |

### Custom Hooks (`src/hooks/`)
| Hook | Purpose |
|------|---------|
| `useAuth` | Supabase auth state |
| `useJobs` | React Query for jobs list |
| `useJob` | React Query for single job |
| `useProfiles` | React Query for job profiles |
| `useToggleBookmark` | Optimistic bookmark toggle with rollback |
| `useRealtime` | Supabase realtime subscriptions |
| `useToast` | Toast notifications |

### Context (`src/context/`)
| Context | Purpose |
|---------|---------|
| `AuthContext` | User session |
| `ToastContext` | Toast state |

---

## Routing Structure

```
/                           → Empty Dashboard or redirect to /sessions
/login                      → Auth page (sign in)
/signup                     → Auth page (sign up)
/sessions                   → Session list
/new-session                → Step 1: Configure
/new-session/review         → Step 2: Review & Launch
/jobs/:id                   → Main dashboard
/jobs/:id/processing        → Pipeline view (or modal)
```

---

## Backend APIs - Readiness Status

| API | Status | Notes |
|-----|--------|-------|
| `POST /api/jobs` | ✅ Ready | Includes keywords, hashtags, min_score |
| `GET /api/jobs` | ✅ Ready | List all jobs |
| `GET /api/jobs/{id}` | ✅ Ready | Get job with profiles |
| `DELETE /api/jobs/{id}` | ✅ Ready | Delete job |
| `POST /api/jobs/{id}/start` | ✅ Ready | Start workflow |
| `POST /api/jobs/{id}/cancel` | ✅ Ready | Cancel job ✅ NEW |
| `PATCH /api/jobs/{id}/status` | ✅ Ready | Update status |
| `GET /api/jobs/{id}/analytics` | ✅ Ready | Get stats |
| `POST /api/demo/start` | ✅ Ready | Demo mode ✅ NEW |
| `PATCH /api/profiles/{id}/bookmark` | ✅ Ready | Toggle bookmark ✅ NEW |
| `POST /api/email/generate` | ✅ Ready | AI email |
| `POST /api/email/send` | ✅ Ready | Send email |
| `POST /api/agent/*` | ✅ Ready | Agent endpoints |
| Supabase Realtime | ✅ Ready | Real-time updates |

---

## Implementation Priority

### Phase 1: Core Foundation
1. Project setup (React Router, React Query, Supabase client)
2. Auth flow (login, signup, protected routes)
3. Layout components (Header, AppLayout)
4. Session list page
5. Empty dashboard with demo button

### Phase 2: Session Creation
1. New session form (Step 1)
2. Review & launch (Step 2)
3. Job creation API integration

### Phase 3: Main Dashboard
1. Profile grid
2. Profile cards
3. Tab navigation
4. Real-time updates
5. Analytics summary

### Phase 4: Profile Detail
1. Profile modal
2. Score breakdown
3. AI analysis display
4. Email composer integration

### Phase 5: Pipeline & Polish
1. Processing pipeline view
2. Cancel job functionality
3. Toast notifications
4. Skeleton loaders
5. Error handling

---

## Design System Notes

From the HTML designs, extract:
- **Colors:** Apple-inspired palette (`apple-blue: #0071e3`, `apple-green: #34c759`, etc.)
- **Font:** Inter (already in designs)
- **Border radius:** 12px-20px for cards, 980px for pills
- **Shadows:** Subtle box-shadows
- **Animations:** `fade-in`, `slide-up`, `scale-in`

---

## Existing Assets to Use

| Asset | Location | Notes |
|-------|----------|-------|
| Tailwind config | `frontend/tailwind.config.js` | Extend with design colors |
| Global styles | `frontend/src/styles/globals.css` | Add design system vars |
| Types | `frontend/src/types/` | Add API response types |

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Frontend architecture patterns
- [TECH_STACK.md](./TECH_STACK.md) - Technology decisions
- [BACKEND_MAPPING.md](./BACKEND_MAPPING.md) - API mapping
- [FUNCTIONALITIES.md](./FUNCTIONALITIES.md) - Feature checklist

---

*Last updated: February 2026*
