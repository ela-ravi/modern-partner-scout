# Frontend Architecture - PartnerScout AI

> **Version**: 1.0  
> **Last Updated**: 2026-02-06  
> **Status**: APPROVED

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Project Structure](#project-structure)
4. [Packlets Architecture](#packlets-architecture)
5. [Component Library](#component-library)
6. [State Management](#state-management)
7. [Data Flow](#data-flow)
8. [API Layer](#api-layer)
9. [Design Token System](#design-token-system)
10. [Builder Pattern](#builder-pattern)
11. [Routing](#routing)
12. [Testing Strategy](#testing-strategy)
13. [Error Handling](#error-handling)
14. [Performance Considerations](#performance-considerations)
15. [Future Considerations](#future-considerations)

---

## Overview

PartnerScout AI frontend is a React 19 application built with TypeScript, following a **domain-driven modular architecture** inspired by enterprise-scale patterns while remaining pragmatic for our scope.

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module Organization | Packlets pattern | Domain isolation, lazy loading |
| Component Structure | Atomic Design | Clear abstraction levels |
| State Management | React Query + Context | Minimal boilerplate, excellent caching |
| Styling | Tailwind CSS + Tokens | Design system consistency |
| Data Transformation | Builder pattern | Separation of API from UI |
| API Communication | Typed fetch wrapper | Type safety, centralized errors |

---

## Architecture Principles

### 1. Domain-Driven Organization
Code is organized by business domain (auth, jobs, profiles, email), not by technical type (components, hooks, utils).

### 2. Single Responsibility
Each module, component, and function has one clear purpose.

### 3. Dependency Direction
Dependencies flow inward: Pages → Features → Components → UI primitives.

### 4. Type Safety
TypeScript strict mode. No `any` types. API responses typed end-to-end.

### 5. Testability First
Pure functions for data transformation. Dependency injection for services. TDD approach.

### 6. Lazy Loading
Route-based code splitting. Heavy components loaded on demand.

---

## Project Structure

```
frontend/src/
│
├── packlets/                    # Domain-driven modules
│   ├── auth/                    # Authentication domain
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useSession.ts
│   │   ├── utils/
│   │   │   └── token.ts
│   │   └── index.ts             # Barrel exports
│   │
│   ├── jobs/                    # Discovery jobs domain
│   │   ├── builders/
│   │   │   ├── build-job-card.ts
│   │   │   └── build-job-stats.ts
│   │   ├── hooks/
│   │   │   ├── useJobs.ts
│   │   │   ├── useJob.ts
│   │   │   └── useCreateJob.ts
│   │   ├── utils/
│   │   │   └── job-status.ts
│   │   └── index.ts
│   │
│   ├── profiles/                # Discovered profiles domain
│   │   ├── builders/
│   │   │   ├── build-profile-card.ts
│   │   │   ├── build-profile-detail.ts
│   │   │   └── build-score-breakdown.ts
│   │   ├── hooks/
│   │   │   ├── useProfiles.ts
│   │   │   ├── useProfile.ts
│   │   │   └── useProfileActions.ts
│   │   ├── utils/
│   │   │   ├── format-followers.ts
│   │   │   └── score-utils.ts
│   │   └── index.ts
│   │
│   ├── email/                   # Email composer domain
│   │   ├── builders/
│   │   │   └── build-email-template.ts
│   │   ├── hooks/
│   │   │   ├── useGenerateEmail.ts
│   │   │   └── useSendEmail.ts
│   │   └── index.ts
│   │
│   ├── pipeline/                # Discovery pipeline domain
│   │   ├── hooks/
│   │   │   └── usePipelineStatus.ts
│   │   ├── utils/
│   │   │   └── stage-utils.ts
│   │   └── index.ts
│   │
│   └── common/                  # Shared utilities
│       ├── hooks/
│       │   ├── useDebounce.ts
│       │   ├── useLocalStorage.ts
│       │   └── useMediaQuery.ts
│       ├── utils/
│       │   ├── cn.ts            # Class name merger
│       │   ├── format-date.ts
│       │   └── format-number.ts
│       └── index.ts
│
├── components/                  # UI Component Library
│   ├── ui/                      # Base components (atoms)
│   │   ├── Button/
│   │   ├── Card/
│   │   ├── Badge/
│   │   ├── Input/
│   │   ├── Modal/
│   │   ├── Dropdown/
│   │   ├── Toast/
│   │   ├── Skeleton/
│   │   ├── ScoreRing/
│   │   └── index.ts
│   │
│   ├── composite/               # Composite components (molecules)
│   │   ├── Header/
│   │   ├── ProfileCard/
│   │   ├── JobCard/
│   │   ├── StatsGrid/
│   │   ├── FilterBar/
│   │   ├── TabGroup/
│   │   ├── SearchInput/
│   │   └── index.ts
│   │
│   ├── features/                # Feature components (organisms)
│   │   ├── ProfileGrid/
│   │   ├── ProfileDetail/
│   │   ├── EmailComposer/
│   │   ├── DiscoveryPipeline/
│   │   ├── DiscoveryConfig/
│   │   ├── SessionList/
│   │   └── index.ts
│   │
│   └── layouts/                 # Page layouts
│       ├── DashboardLayout/
│       ├── AuthLayout/
│       ├── FullscreenLayout/
│       └── index.ts
│
├── pages/                       # Route pages
│   ├── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── DiscoveryConfigPage.tsx
│   ├── SessionsPage.tsx
│   ├── SessionDetailPage.tsx
│   └── NotFoundPage.tsx
│
├── lib/                         # Core libraries
│   ├── api/
│   │   ├── client.ts            # Base API client
│   │   ├── errors.ts            # API error types
│   │   └── index.ts
│   ├── tokens/
│   │   ├── colors.ts
│   │   ├── borders.ts
│   │   ├── motion.ts
│   │   └── index.ts
│   ├── supabase/
│   │   └── client.ts
│   ├── query/
│   │   └── client.ts            # React Query config
│   └── utils/
│       └── cn.ts
│
├── services/                    # API service functions
│   ├── auth.ts
│   ├── jobs.ts
│   ├── profiles.ts
│   ├── email.ts
│   └── demo.ts
│
├── types/                       # TypeScript definitions
│   ├── api/
│   │   ├── job.ts
│   │   ├── profile.ts
│   │   ├── email.ts
│   │   └── index.ts
│   ├── ui/
│   │   └── index.ts
│   └── index.ts
│
├── test/                        # Test utilities
│   ├── setup.ts
│   ├── utils.tsx                # Render helpers
│   ├── mocks/
│   │   ├── handlers.ts          # MSW handlers
│   │   └── data/                # Mock data
│   └── factories/               # Test data factories
│
├── styles/
│   └── tailwind.css             # Global styles + tokens
│
├── App.tsx                      # Root component
├── main.tsx                     # Entry point
└── routes.tsx                   # Route definitions
```

---

## Packlets Architecture

### What is a Packlet?

A **packlet** is a self-contained domain module that owns:
- Its hooks (data fetching, mutations)
- Its builders (data transformation)
- Its utilities (domain-specific helpers)
- Its barrel exports (public API)

### Packlet Structure

```
packlets/{domain}/
├── builders/          # API → UI data transformation
│   └── build-*.ts
├── hooks/             # React hooks for this domain
│   └── use*.ts
├── utils/             # Domain-specific utilities
│   └── *.ts
├── context/           # Optional: domain context
│   └── *Context.tsx
└── index.ts           # Barrel exports (public API)
```

### Packlet Rules

1. **Single Export Point**: All public APIs exported via `index.ts`
2. **No Cross-Packlet Imports**: Use `common` for shared code
3. **Hooks Own Data Fetching**: Services called only from hooks
4. **Builders Are Pure**: No side effects, easy to test

### Example: Jobs Packlet

```typescript
// packlets/jobs/index.ts
export { useJobs, useJob, useCreateJob, useCancelJob } from './hooks';
export { buildJobCard, buildJobStats, buildJobProgress } from './builders';
export { getJobStatusColor, isJobActive } from './utils';
```

```typescript
// Usage in a component
import { useJobs, buildJobCard } from '@/packlets/jobs';

function JobList() {
  const { data: jobs, isLoading } = useJobs();
  
  if (isLoading) return <Skeleton />;
  
  return (
    <div>
      {jobs.map(job => (
        <JobCard key={job.id} {...buildJobCard(job)} />
      ))}
    </div>
  );
}
```

---

## Component Library

### Hierarchy (Atomic Design)

```
┌─────────────────────────────────────────────────────────┐
│  PAGES (routes)                                         │
│  └── Compose features and layouts                       │
├─────────────────────────────────────────────────────────┤
│  LAYOUTS (templates)                                    │
│  └── Page structure, navigation, common elements        │
├─────────────────────────────────────────────────────────┤
│  FEATURES (organisms)                                   │
│  └── Complex, domain-specific components                │
│      ProfileGrid, EmailComposer, DiscoveryPipeline      │
├─────────────────────────────────────────────────────────┤
│  COMPOSITE (molecules)                                  │
│  └── Combinations of UI primitives                      │
│      ProfileCard, StatsGrid, FilterBar                  │
├─────────────────────────────────────────────────────────┤
│  UI (atoms)                                             │
│  └── Base primitives, no business logic                 │
│      Button, Card, Badge, Input, Modal                  │
└─────────────────────────────────────────────────────────┘
```

### Component File Structure

```
components/ui/Button/
├── Button.tsx           # Component implementation
├── Button.test.tsx      # Tests
├── Button.types.ts      # TypeScript interfaces (if complex)
└── index.ts             # Barrel export
```

### Component Guidelines

| Level | Business Logic | Data Fetching | Examples |
|-------|----------------|---------------|----------|
| UI | None | None | Button, Card, Badge |
| Composite | Minimal | None | ProfileCard, StatsGrid |
| Features | Yes | Via hooks | ProfileGrid, EmailComposer |
| Pages | Orchestration | Via hooks | DashboardPage |

---

## State Management

### Decision Flow

```
┌─────────────────────────────────────────┐
│         Where should state live?         │
└─────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │ Data from server?   │
        └─────────────────────┘
           │              │
          Yes            No
           │              │
           ▼              ▼
    ┌───────────┐  ┌─────────────────┐
    │  React    │  │ Shared across   │
    │  Query    │  │ components?     │
    └───────────┘  └─────────────────┘
                       │         │
                      Yes       No
                       │         │
                       ▼         ▼
                 ┌─────────┐ ┌──────────┐
                 │ Context │ │ useState │
                 └─────────┘ └──────────┘
```

### State Categories

| Category | Solution | Examples |
|----------|----------|----------|
| Server State | React Query | Jobs, Profiles, User data |
| Auth State | Context + Supabase | User session, tokens |
| UI State (local) | useState | Modal open, input value |
| UI State (shared) | Context | Toast notifications, theme |
| URL State | React Router | Filters, pagination, active tab |

### React Query Patterns

```typescript
// Queries: GET data
const { data, isLoading, error } = useQuery({
  queryKey: ['jobs'],
  queryFn: () => jobsService.list(),
});

// Mutations: POST/PUT/DELETE
const { mutate, isPending } = useMutation({
  mutationFn: jobsService.create,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['jobs'] });
    toast.success('Job created');
  },
});

// Optimistic Updates (see hooks/profiles/useToggleBookmark.ts)
// Actual implementation uses PATCH /api/profiles/{id}/bookmark
const { mutate } = useMutation({
  mutationFn: ({ jobId, profileId }) => profilesService.toggleBookmark(jobId, profileId),
  onMutate: async ({ profileId }) => {
    await queryClient.cancelQueries({ queryKey: profilesKeys.lists() });
    const previousQueries = queryClient.getQueriesData({ queryKey: profilesKeys.lists() });
    queryClient.setQueriesData({ queryKey: profilesKeys.lists() }, (old) => ({
      ...old,
      profiles: old.profiles.map(p =>
        p.id === profileId ? { ...p, is_bookmarked: !p.is_bookmarked } : p
      ),
    }));
    return { previousQueries };
  },
  onError: (_err, _vars, context) => {
    // Rollback all queries on error
    for (const [key, data] of context.previousQueries) {
      queryClient.setQueryData(key, data);
    }
  },
  onSettled: (_, __, { jobId }) => {
    queryClient.invalidateQueries({ queryKey: profilesKeys.lists() });
    queryClient.invalidateQueries({ queryKey: profilesKeys.analytics(jobId) });
  },
});
```

### Context Structure

```typescript
// contexts/AuthContext.tsx
interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

// contexts/ToastContext.tsx
interface ToastContextValue {
  toasts: Toast[];
  success: (message: string) => void;
  error: (message: string) => void;
  dismiss: (id: string) => void;
}
```

---

## Data Flow

### Complete Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                           USER ACTION                               │
│                        (click, submit, etc.)                        │
└────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                            COMPONENT                                │
│                         (ProfileGrid)                               │
│                                                                     │
│  const { data, isLoading } = useProfiles(jobId);                   │
│  const profiles = data?.map(buildProfileCard);                     │
└────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────────┐
│         PACKLET HOOK        │   │          BUILDER                 │
│        (useProfiles)        │   │     (buildProfileCard)           │
│                             │   │                                  │
│  return useQuery({          │   │  function buildProfileCard(      │
│    queryKey: ['profiles'],  │   │    profile: ApiProfile           │
│    queryFn: () =>           │   │  ): ProfileCardProps {           │
│      profilesService.list() │   │    return {                      │
│  });                        │   │      name: profile.full_name,    │
│                             │   │      score: profile.score,       │
└─────────────────────────────┘   │      ...                         │
              │                   │    };                            │
              ▼                   │  }                               │
┌─────────────────────────────┐   └─────────────────────────────────┘
│          SERVICE            │
│    (profilesService)        │
│                             │
│  list: (jobId) =>           │
│    api.get(`/profiles`)     │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│         API CLIENT          │
│         (lib/api)           │
│                             │
│  - Add auth headers         │
│  - Handle errors            │
│  - Transform response       │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│       FASTAPI BACKEND       │
│     (api.partnerscout.ai)   │
└─────────────────────────────┘
```

### Mutation Flow

```
USER ACTION (Create Job)
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│   Component     │────▶│  useMutation     │
│   (Form)        │     │  (useCreateJob)  │
└─────────────────┘     └──────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌───────────┐    ┌───────────┐    ┌───────────┐
       │ onMutate  │    │ mutationFn│    │ onSuccess │
       │ (optimist)│    │ (API call)│    │ (refresh) │
       └───────────┘    └───────────┘    └───────────┘
                               │
                               ▼
                        ┌───────────┐
                        │  Service  │
                        │  (jobs)   │
                        └───────────┘
                               │
                               ▼
                        ┌───────────┐
                        │  Backend  │
                        └───────────┘
```

---

## API Layer

### API Client Architecture

```typescript
// lib/api/client.ts
import { ApiError } from './errors';

interface RequestConfig extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  constructor(
    private baseUrl: string,
    private getToken: () => Promise<string | null>
  ) {}

  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const { params, ...init } = config;
    
    // Build URL with query params
    const url = new URL(`${this.baseUrl}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    
    // Get auth token
    const token = await this.getToken();
    
    // Make request
    const response = await fetch(url.toString(), {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...init.headers,
      },
    });
    
    // Handle errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(response.status, error.error?.message || 'Request failed');
    }
    
    // Return typed response
    return response.json();
  }

  get<T>(endpoint: string, params?: Record<string, string>) {
    return this.request<T>(endpoint, { method: 'GET', params });
  }

  post<T>(endpoint: string, data?: unknown) {
    return this.request<T>(endpoint, { 
      method: 'POST', 
      body: data ? JSON.stringify(data) : undefined 
    });
  }

  put<T>(endpoint: string, data: unknown) {
    return this.request<T>(endpoint, { 
      method: 'PUT', 
      body: JSON.stringify(data) 
    });
  }

  delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

export const api = new ApiClient(
  import.meta.env.VITE_API_URL,
  async () => {
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  }
);
```

### Service Layer

```typescript
// services/jobs.ts
import { api } from '@/lib/api';
import type { Job, JobSummary, CreateJobRequest, JobCancelResponse } from '@/types/api';

export const jobsService = {
  list: () => 
    api.get<JobSummary[]>('/api/jobs'),

  get: (id: string) => 
    api.get<Job>(`/api/jobs/${id}`),

  create: (data: CreateJobRequest) => 
    api.post<Job>('/api/jobs', data),

  cancel: (id: string) => 
    api.post<JobCancelResponse>(`/api/jobs/${id}/cancel`),
};

// services/profiles.ts
import { api } from '@/lib/api';
import type { Profile, ProfilesResponse, ProfileUpdateRequest } from '@/types/api';

export const profilesService = {
  list: (jobId: string, params?: { status?: string; limit?: number; offset?: number }) =>
    api.get<ProfilesResponse>(`/api/jobs/${jobId}/profiles`, params),

  get: (jobId: string, profileId: string) =>
    api.get<Profile>(`/api/jobs/${jobId}/profiles/${profileId}`),

  updateStatus: (jobId: string, profileId: string, data: ProfileUpdateRequest) =>
    api.put<Profile>(`/api/jobs/${jobId}/profiles/${profileId}`, data),

  toggleBookmark: (_jobId: string, profileId: string) =>
    api.patch<{ id: string; is_bookmarked: boolean }>(`/api/profiles/${profileId}/bookmark`, {}),
};
```

---

## Design Token System

### Token Categories

```typescript
// lib/tokens/colors.ts
export const ColorToken = {
  // Background & Surface
  appleBg: '#fbfbfd',
  appleCard: '#ffffff',
  appleGray: '#f5f5f7',
  appleBorder: 'rgba(0, 0, 0, 0.06)',
  
  // Brand Colors
  appleBlue: '#0071e3',
  appleBlueHover: '#0077ed',
  appleGreen: '#34c759',
  appleOrange: '#ff9500',
  appleRed: '#ff3b30',
  applePurple: '#af52de',
  
  // Text Colors
  appleText: '#1d1d1f',
  appleTextSecondary: '#86868b',
  appleTextTertiary: '#aeaeb2',
} as const;

// lib/tokens/borders.ts
export const BorderToken = {
  radiusCard: '18px',
  radiusButton: '12px',
  radiusPill: '980px',
  radiusInput: '12px',
  radiusAvatar: '16px',
} as const;

// lib/tokens/shadows.ts
export const ShadowToken = {
  card: '0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1)',
  cardHover: '0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1)',
  modal: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
} as const;

// lib/tokens/motion.ts
export const MotionToken = {
  fadeIn: 'fadeIn 0.6s ease-out forwards',
  slideUp: 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
  scaleIn: 'scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
  easeOut: 'cubic-bezier(0.16, 1, 0.3, 1)',
} as const;
```

### Tailwind Integration

```css
/* styles/tailwind.css */
@import "tailwindcss";

@theme {
  /* Colors */
  --color-apple-bg: #fbfbfd;
  --color-apple-card: #ffffff;
  --color-apple-gray: #f5f5f7;
  --color-apple-border: rgba(0, 0, 0, 0.06);
  --color-apple-blue: #0071e3;
  --color-apple-blue-hover: #0077ed;
  --color-apple-green: #34c759;
  --color-apple-orange: #ff9500;
  --color-apple-red: #ff3b30;
  --color-apple-purple: #af52de;
  --color-apple-text: #1d1d1f;
  --color-apple-text-secondary: #86868b;
  --color-apple-text-tertiary: #aeaeb2;

  /* Border Radius */
  --radius-card: 18px;
  --radius-button: 12px;
  --radius-pill: 980px;

  /* Shadows */
  --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1);
  --shadow-card-hover: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1);
  --shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  /* Typography */
  --font-family-sf: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;

  /* Animations */
  --animate-fade-in: fadeIn 0.6s ease-out forwards;
  --animate-slide-up: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  --animate-scale-in: scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}
```

---

## Builder Pattern

### Purpose

Builders transform API response shapes into component prop shapes. This separation provides:
- **Testability**: Pure functions, easy to unit test
- **Reusability**: Same builder across different components
- **Maintainability**: API changes only affect builders, not components

### Builder Structure

```typescript
// packlets/profiles/builders/build-profile-card.ts
import type { ApiProfile } from '@/types/api';
import type { ProfileCardProps } from '@/components/composite/ProfileCard';
import { formatFollowers, formatEngagement } from '../utils';
import { buildBadges } from './build-badges';

export function buildProfileCard(profile: ApiProfile): ProfileCardProps {
  return {
    id: profile.id,
    name: profile.full_name || profile.username,
    username: profile.username,
    avatarUrl: profile.profile_pic_url,
    coverUrl: profile.cover_url,
    bio: profile.biography,
    followers: formatFollowers(profile.follower_count),
    engagement: formatEngagement(profile.engagement_rate),
    score: profile.score?.overall_score ?? 0,
    status: profile.status,
    hasEmail: Boolean(profile.email),
    badges: buildBadges(profile),
  };
}

// packlets/profiles/builders/build-profile-detail.ts
export function buildProfileDetail(profile: ApiProfile): ProfileDetailProps {
  return {
    ...buildProfileCard(profile),
    bio: profile.biography,
    posts: profile.post_count,
    following: profile.following_count,
    email: profile.email,
    emailSource: profile.email_source,
    aiAnalysis: profile.score?.reasoning,
    scoreBreakdown: buildScoreBreakdown(profile.score),
    recentPosts: profile.recent_posts?.slice(0, 3) ?? [],
  };
}

// packlets/profiles/builders/build-score-breakdown.ts
export function buildScoreBreakdown(score: ApiScore | null): ScoreBreakdownItem[] {
  if (!score) return [];
  
  return [
    { label: 'Aesthetic Match', value: score.aesthetic_score, max: 100 },
    { label: 'Engagement Quality', value: score.engagement_score, max: 100 },
    { label: 'Content Alignment', value: score.content_score, max: 100 },
    { label: 'Audience Fit', value: score.audience_score, max: 100 },
  ];
}
```

### Usage in Components

```typescript
// components/features/ProfileGrid/ProfileGrid.tsx
import { useProfiles, buildProfileCard } from '@/packlets/profiles';
import { ProfileCard } from '@/components/composite/ProfileCard';

export function ProfileGrid({ jobId }: { jobId: string }) {
  const { data: profiles, isLoading } = useProfiles(jobId);

  if (isLoading) {
    return <ProfileGridSkeleton />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {profiles?.map((profile) => (
        <ProfileCard
          key={profile.id}
          {...buildProfileCard(profile)}
          onView={() => openProfileModal(profile.id)}
          onEmail={() => openEmailComposer(profile.id)}
        />
      ))}
    </div>
  );
}
```

---

## Routing

### Route Structure

```typescript
// routes.tsx
import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { AuthLayout } from '@/components/layouts/AuthLayout';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { LoadingPage } from '@/components/LoadingPage';

// Lazy load pages
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const DiscoveryConfigPage = lazy(() => import('@/pages/DiscoveryConfigPage'));
const SessionsPage = lazy(() => import('@/pages/SessionsPage'));
const SessionDetailPage = lazy(() => import('@/pages/SessionDetailPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/login',
    element: (
      <AuthLayout>
        <Suspense fallback={<LoadingPage />}>
          <LoginPage />
        </Suspense>
      </AuthLayout>
    ),
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: '/dashboard',
            element: (
              <Suspense fallback={<LoadingPage />}>
                <DashboardPage />
              </Suspense>
            ),
          },
          {
            path: '/discovery/new',
            element: (
              <Suspense fallback={<LoadingPage />}>
                <DiscoveryConfigPage />
              </Suspense>
            ),
          },
          {
            path: '/sessions',
            element: (
              <Suspense fallback={<LoadingPage />}>
                <SessionsPage />
              </Suspense>
            ),
          },
          {
            path: '/jobs/:jobId',
            element: (
              <Suspense fallback={<LoadingPage />}>
                <DashboardPage />
              </Suspense>
            ),
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
```

### Route Map

| Path | Page | Auth Required |
|------|------|---------------|
| `/` | Redirect to `/dashboard` | Yes |
| `/login` | Login Page | No |
| `/dashboard` | Discovery Dashboard | Yes |
| `/discovery/new` | Discovery Configuration | Yes |
| `/sessions` | Sessions List | Yes |
| `/jobs/:id` | Job Dashboard | Yes |
| `*` | 404 Not Found | No |

---

## Testing Strategy

### Test Types

| Type | Tool | Purpose | Location |
|------|------|---------|----------|
| Unit | Vitest | Builders, utils, hooks | `*.test.ts` |
| Component | RTL | UI components | `*.test.tsx` |
| Integration | RTL + MSW | Features with API | `*.integration.test.tsx` |
| E2E | Playwright | Critical flows | `e2e/*.spec.ts` |

### Test Structure

```typescript
// packlets/profiles/builders/build-profile-card.test.ts
import { describe, it, expect } from 'vitest';
import { buildProfileCard } from './build-profile-card';
import { createMockProfile } from '@/test/factories/profile';

describe('buildProfileCard', () => {
  it('transforms API profile to card props', () => {
    const apiProfile = createMockProfile({
      full_name: 'John Doe',
      username: 'johndoe',
      follower_count: 150000,
    });

    const result = buildProfileCard(apiProfile);

    expect(result).toEqual({
      id: apiProfile.id,
      name: 'John Doe',
      username: 'johndoe',
      followers: '150K',
      // ...
    });
  });

  it('falls back to username when full_name is empty', () => {
    const apiProfile = createMockProfile({ full_name: '', username: 'johndoe' });
    
    const result = buildProfileCard(apiProfile);
    
    expect(result.name).toBe('johndoe');
  });
});
```

### Component Tests

```typescript
// components/composite/ProfileCard/ProfileCard.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfileCard } from './ProfileCard';

describe('ProfileCard', () => {
  const defaultProps = {
    id: '1',
    name: 'Test User',
    username: 'testuser',
    avatarUrl: 'https://example.com/avatar.jpg',
    followers: '100K',
    engagement: '5.2%',
    score: 85,
    onView: vi.fn(),
    onEmail: vi.fn(),
  };

  it('renders profile information', () => {
    render(<ProfileCard {...defaultProps} />);

    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('@testuser')).toBeInTheDocument();
    expect(screen.getByText('100K')).toBeInTheDocument();
    expect(screen.getByText('85')).toBeInTheDocument();
  });

  it('calls onView when View Profile is clicked', async () => {
    const user = userEvent.setup();
    render(<ProfileCard {...defaultProps} />);

    await user.click(screen.getByRole('button', { name: /view profile/i }));

    expect(defaultProps.onView).toHaveBeenCalled();
  });
});
```

### MSW Handlers

```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/jobs', () => {
    return HttpResponse.json([
      { id: '1', name: 'Test Job', status: 'completed' },
    ]);
  }),

  http.get('/api/jobs/:jobId/profiles', ({ params }) => {
    return HttpResponse.json({
      profiles: [
        { id: '1', username: 'testuser', score: { overall_score: 85 } },
      ],
      total: 1,
    });
  }),

  http.post('/api/jobs/:jobId/cancel', ({ params }) => {
    return HttpResponse.json({
      job_id: params.jobId,
      status: 'cancelled',
      message: 'Job cancelled successfully',
    });
  }),
];
```

---

## Error Handling

### Error Boundary

```typescript
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Future: send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

### API Error Handling

```typescript
// lib/api/errors.ts
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }

  get isUnauthorized() {
    return this.status === 401;
  }

  get isNotFound() {
    return this.status === 404;
  }

  get isServerError() {
    return this.status >= 500;
  }
}

// Usage in React Query
const { error } = useQuery({
  queryKey: ['profiles'],
  queryFn: profilesService.list,
});

if (error instanceof ApiError) {
  if (error.isUnauthorized) {
    // Redirect to login
  }
  if (error.isNotFound) {
    // Show not found state
  }
}
```

---

## Performance Considerations

### Code Splitting

```typescript
// Lazy load pages
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));

// Lazy load heavy components
const EmailComposer = lazy(() => import('@/components/features/EmailComposer'));
```

### React Query Optimizations

```typescript
// Query client configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30,   // 30 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

### Memoization Guidelines

```typescript
// Memoize expensive computations
const sortedProfiles = useMemo(
  () => profiles?.sort((a, b) => b.score - a.score),
  [profiles]
);

// Memoize callbacks passed to children
const handleView = useCallback((id: string) => {
  setSelectedProfile(id);
  openModal();
}, [openModal]);
```

### Image Optimization

- Use appropriate image sizes from API
- Lazy load images below the fold
- Use placeholder/skeleton while loading

---

## Future Considerations

### Feature Flags (When Needed)

```typescript
// lib/features.ts
export const FeatureFlags = {
  DEMO_MODE: true,
  EMAIL_COMPOSER: true,
  BULK_ACTIONS: false,
  EXPORT_CSV: false,
} as const;

export function isEnabled(flag: keyof typeof FeatureFlags): boolean {
  return FeatureFlags[flag];
}
```

### Analytics (Post-MVP)

```typescript
// lib/analytics/manager.ts
interface AnalyticsEvent {
  name: string;
  properties?: Record<string, unknown>;
}

class AnalyticsManager {
  private consumers: AnalyticsConsumer[] = [];
  
  register(consumer: AnalyticsConsumer) {
    this.consumers.push(consumer);
  }
  
  track(event: AnalyticsEvent) {
    this.consumers.forEach(c => c.track(event));
  }
}
```

### Internationalization (If Needed)

```typescript
// Future: react-i18next setup
const { t } = useTranslation();
<h1>{t('dashboard.title')}</h1>
```

---

## Related Documents

- [TECH_STACK.md](./TECH_STACK.md) - Technology decisions
- [GAPS_TODO.md](./GAPS_TODO.md) - Implementation gaps
- [BACKEND_MAPPING.md](./BACKEND_MAPPING.md) - API mapping
