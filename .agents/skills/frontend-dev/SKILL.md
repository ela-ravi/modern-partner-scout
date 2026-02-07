# Frontend Development Agent

## Purpose
Implement EPIC-5: Frontend Application Development using React + TypeScript.

## Before Starting
Read these files in order:
1. `PROJECT_CONTEXT.md` - Project overview
2. `docs/Frontend_Functionalities.md` - All 79 UI functionalities
3. `docs/Frontend_Design_Validation_Report.md` - Design coverage
4. `docs/Supabase_Database_Guide.md` - Section 10 (TypeScript types)
5. `docs/PartnerScout_AI_Agile_Development_Plan.md` - EPIC-5 section
6. `designs/` folder - All HTML mockups

## Current Status
- Frontend project initialized (React + Vite + TypeScript + Tailwind)
- Backend APIs working on port 8001
- Supabase configured in frontend `.env`
- HTML design mockups ready in `designs/` folder

## Design Files Reference
| File | Purpose |
|------|---------|
| `login.html` | Auth pages (Sign In/Sign Up) |
| `session-list.html` | Session history list |
| `discovery-engine-step1.html` | New session form |
| `discovery-engine-step2.html` | Session review before launch |
| `ai-agent-processing-pipeline.html` | Live processing view |
| `main-discovery-dashboard.html` | Main dashboard with tabs |
| `profile-detail-model-view.html` | Profile detail modal |
| `ai-email-composer.html` | Email composer |
| `empty-dashboard.html` | Empty state for new users |
| `ui-components.html` | Component library reference |

## Tech Stack
- React 18 + TypeScript
- Tailwind CSS (Apple-inspired theme)
- Supabase Client (auth + realtime)
- React Router v6

## Key Components to Build

### Pages
- `LoginPage.tsx` - Auth (sign in/sign up)
- `DashboardPage.tsx` - Main dashboard with tabs
- `SessionListPage.tsx` - All sessions
- `NewSessionPage.tsx` - Create new discovery
- `ProcessingPage.tsx` - Live pipeline view

### Components
- `ProfileCard.tsx` - Profile display card
- `ProfileDetailModal.tsx` - Full profile view
- `ScoreBreakdown.tsx` - 6-dimension score chart
- `SessionCard.tsx` - Session list item
- `EmailComposer.tsx` - AI email generator
- `StatusBadge.tsx` - Status indicators
- `LoadingSkeleton.tsx` - Loading states

### Hooks
- `useAuth.ts` - Supabase auth
- `useJobs.ts` - Jobs CRUD
- `useProfiles.ts` - Profiles data
- `useRealtime.ts` - Supabase subscriptions

## API Integration
```typescript
const API_BASE = 'http://localhost:8001/api';

// Jobs
GET    /api/jobs              // List jobs
POST   /api/jobs              // Create job
GET    /api/jobs/{id}         // Get job details
DELETE /api/jobs/{id}         // Delete job
POST   /api/jobs/{id}/start   // Start discovery
GET    /api/jobs/{id}/analytics // Get stats

// Email
POST   /api/email/generate    // Generate email draft
```

## Styling Guidelines
- Primary: `#0071e3` (Apple Blue)
- Background: `#fbfbfd`
- Text: `#1d1d1f`
- Success: `#34c759`
- Warning: `#ff9500`
- Error: `#ff3b30`
- Border radius: 12-20px
- Generous whitespace

## Validation
After implementing each component:
1. Compare with design in `designs/` folder
2. Test with real API data
3. Check responsive behavior
4. Verify Supabase realtime updates