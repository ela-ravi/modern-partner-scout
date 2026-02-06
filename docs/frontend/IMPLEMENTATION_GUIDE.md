# Frontend Implementation Guide - Agile Methodology

> **Version**: 1.3  
> **Last Updated**: 2026-02-06  
> **Methodology**: Agile (Scrum)  
> **Sprint Duration**: 2 weeks  
> **Accessibility**: WCAG 2.2 Level AA Compliant  
> **E2E Testing**: Playwright (per Feature/Epic)

---

## Table of Contents

1. [Overview](#overview)
2. [Release Plan](#release-plan)
3. [Validation Framework](#validation-framework)
4. [Epic 1: Project Foundation](#epic-1-project-foundation)
5. [Epic 2: Authentication & User Management](#epic-2-authentication--user-management)
6. [Epic 3: Session Management](#epic-3-session-management)
7. [Epic 4: Discovery Configuration](#epic-4-discovery-configuration)
8. [Epic 5: Main Dashboard](#epic-5-main-dashboard)
9. [Epic 6: Profile Detail & Actions](#epic-6-profile-detail--actions)
10. [Epic 7: Email Composer](#epic-7-email-composer)
11. [Epic 8: Processing Pipeline](#epic-8-processing-pipeline)
12. [Epic 9: Polish & Production](#epic-9-polish--production)
13. [Definition of Done](#definition-of-done)
14. [Acceptance Criteria Template](#acceptance-criteria-template)
15. [Accessibility Requirements](#accessibility-requirements)

---

## Overview

### Project Scope

Build a complete React frontend for PartnerScout AI that enables D2C brands to discover, analyze, and contact Instagram influencers for partnerships.

### Key Metrics

| Metric | Target |
|--------|--------|
| Total Epics | 9 |
| Total Features | 29 |
| Total User Stories | 70+ |
| Estimated Sprints | 6-8 |
| Team Size | 1-2 developers |
| WCAG Compliance | Level AA |

### Dependencies

| Dependency | Status |
|------------|--------|
| Backend APIs | ✅ Ready |
| Design Files | ✅ Complete |
| Supabase Project | ✅ Configured |
| Tech Stack | ✅ Decided |
| WCAG Audit | ✅ Complete (see `designs/WCAG_AUDIT_REPORT.md`) |

---

## Release Plan

```
┌────────────────────────────────────────────────────────────────────┐
│                        RELEASE TIMELINE                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Sprint 1-2     Sprint 3      Sprint 4      Sprint 5-6    Sprint 7 │
│  ─────────────────────────────────────────────────────────────────▶│
│                                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌───────┐ │
│  │ Epic 1  │   │ Epic 3  │   │ Epic 5  │   │ Epic 6  │   │ Epic 9│ │
│  │ Epic 2  │   │ Epic 4  │   │         │   │ Epic 7  │   │       │ │
│  │         │   │         │   │         │   │ Epic 8  │   │       │ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └───────┘ │
│                                                                     │
│  Foundation   Session Flow   Dashboard    Interactions   Polish    │
│  + Auth                                                             │
│                                                                     │
│  MVP Alpha ─────────────────▶ MVP Beta ──────────────▶ Release     │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Milestones

| Milestone | Sprint | Deliverable |
|-----------|--------|-------------|
| **Alpha** | Sprint 2 | Auth + Session List + Empty State |
| **Beta** | Sprint 4 | Full Dashboard with Profiles |
| **RC1** | Sprint 6 | All Features Complete |
| **Release** | Sprint 7 | Production Ready |

---

## Validation Framework

> **Principle**: Every piece of work must be validated before moving to the next level.  
> **Approach**: Test-Driven Development (TDD) with manual verification at each checkpoint.

### Validation Levels

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION PYRAMID                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                           ┌─────────┐                                    │
│                           │  Epic   │  ← E2E Tests + Stakeholder Demo   │
│                         ┌─┴─────────┴─┐                                  │
│                         │   Feature   │  ← Integration Tests + QA       │
│                       ┌─┴─────────────┴─┐                                │
│                       │     Story       │  ← Unit Tests + Manual Check  │
│                     ┌─┴─────────────────┴─┐                              │
│                     │       Task          │  ← Code Review + Lint        │
│                   ┌─┴─────────────────────┴─┐                            │
│                   │       Sub-Task          │  ← Build Passes            │
│                   └─────────────────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Validation Checklist by Level

#### Sub-Task Validation ✓
```bash
# After each sub-task:
npm run build        # No TypeScript errors
npm run lint         # No ESLint warnings
git diff             # Review changes
```

#### Task Validation ✓
```bash
# After each task:
npm run test         # Related tests pass
npm run test:a11y    # Accessibility tests pass (if applicable)
# Manual: Visual inspection in browser
```

#### Story Validation ✓
```bash
# After each story:
npm run test         # All story tests pass
npm run test:coverage # Coverage meets threshold
# Manual: Test all acceptance criteria
# Manual: Keyboard navigation test
# Manual: Screen reader spot check
```

#### Feature Validation ✓
```bash
# After each feature:
npm run test         # All feature tests pass
npm run build        # Production build succeeds
# Manual: Feature demo to stakeholder
# Manual: Cross-browser testing (Chrome, Firefox, Safari)
# Manual: Responsive testing (mobile, tablet, desktop)
```

#### Epic Validation ✓
```bash
# After each epic:
npm run test         # Full test suite passes
npm run build        # Production build succeeds
npm run test:e2e     # E2E tests pass (if applicable)
# Manual: Full accessibility audit (axe DevTools)
# Manual: Performance audit (Lighthouse)
# Manual: Stakeholder sign-off
```

### Validation Commands Reference

| Command | Purpose | When to Run |
|---------|---------|-------------|
| `npm run dev` | Start dev server | During development |
| `npm run build` | Production build | After each task |
| `npm run lint` | ESLint check | After each sub-task |
| `npm run test` | Run unit tests | After each task |
| `npm run test:watch` | Tests in watch mode | During TDD |
| `npm run test:coverage` | Coverage report | After each story |
| `npm run test:a11y` | Accessibility tests | After each story |
| `npm run test:e2e` | Playwright E2E tests | After each feature |

### Playwright E2E Testing Strategy

> **Skill Reference**: `.cursor/skills/playwright-skill/SKILL.md`

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        E2E TESTING PYRAMID                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                         ┌─────────────┐                                  │
│                         │   E2E       │  ← Playwright (~25-30 tests)    │
│                         │  (10-15%)   │    Per Feature + Epic           │
│                       ┌─┴─────────────┴─┐                                │
│                       │  Integration    │  ← MSW + RTL (per Feature)     │
│                       │    (20-25%)     │                                │
│                     ┌─┴─────────────────┴─┐                              │
│                     │     Unit Tests      │  ← Vitest (per Story/Task)   │
│                     │      (60-70%)       │                              │
│                     └─────────────────────┘                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**When to Write Playwright Tests:**

| Level | Write E2E? | Reason |
|-------|------------|--------|
| Sub-task | ❌ No | Too granular |
| Task | ❌ No | Unit tests better |
| Story | ⚠️ Critical only | Key user journeys |
| **Feature** | ✅ Yes | After feature complete |
| **Epic** | ✅ Yes | Full user flow |

**Playwright Workflow:**
1. Detect dev server: `node -e "require('./lib/helpers').detectDevServers()..."`
2. Write test to `/tmp/playwright-test-*.js`
3. Execute: `cd $SKILL_DIR && node run.js /tmp/playwright-test-*.js`
4. Browser opens visible (headless: false by default)

**E2E Test Count Target:**

| Epic | Tests |
|------|-------|
| Epic 1 (Foundation) | 0 |
| Epic 2 (Auth) | 3-4 |
| Epic 3 (Sessions) | 4-5 |
| Epic 4 (Discovery Config) | 3-4 |
| Epic 5 (Dashboard) | 5-6 |
| Epic 6 (Profile Detail) | 3-4 |
| Epic 7 (Email) | 2-3 |
| Epic 8 (Pipeline) | 2-3 |
| Epic 9 (Polish) | 0 (refine) |
| **Total** | **~25-30** |

### TDD Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                      TDD CYCLE (Per Task)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    1. RED          2. GREEN         3. REFACTOR                 │
│    ┌────────┐      ┌────────┐       ┌────────┐                  │
│    │ Write  │ ───▶ │ Write  │ ───▶  │ Clean  │                  │
│    │ Failing│      │ Minimal│       │  Up    │                  │
│    │  Test  │      │  Code  │       │  Code  │                  │
│    └────────┘      └────────┘       └────────┘                  │
│         │               │                │                       │
│         ▼               ▼                ▼                       │
│    npm run test    npm run test    npm run test                 │
│    (FAIL ❌)       (PASS ✅)       (PASS ✅)                    │
│                                                                  │
│    4. VALIDATE                                                   │
│    ┌────────────────────────────────────────┐                   │
│    │ • npm run build (no errors)            │                   │
│    │ • npm run lint (no warnings)           │                   │
│    │ • Manual browser check                 │                   │
│    │ • Commit with descriptive message      │                   │
│    └────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Epic 1: Project Foundation

> **Goal**: Set up the project infrastructure, tooling, and base components
> **Priority**: P0 (Critical)
> **Sprint**: 1

### 🎯 Epic 1 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ All Features Complete | All 5 features delivered | Dev |
| ✅ Dev Environment Works | `npm run dev` starts successfully | Dev |
| ✅ Tests Pass | `npm run test` passes 100% | Dev |
| ✅ Build Succeeds | `npm run build` completes | Dev |
| ✅ No Lint Errors | `npm run lint` clean | Dev |
| ✅ Components Render | All base components visible in browser | Dev |
| ✅ Routing Works | Navigation between placeholder pages | Dev |
| ✅ Design Tokens Applied | Colors, fonts match design files | Dev |
| ✅ A11y Foundation | Focus styles, skip link working | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 1.1: Project Setup

#### Story 1.1.1: Initialize Development Environment
**As a** developer  
**I want** a fully configured React project  
**So that** I can start building features immediately

**Tasks:**
- [ ] **T1.1.1.1**: Install npm dependencies
  - [ ] react-router-dom
  - [ ] @tanstack/react-query
  - [ ] react-hook-form + zod + @hookform/resolvers
  - [ ] @supabase/supabase-js
  - [ ] date-fns, clsx, tailwind-merge
- [ ] **T1.1.1.2**: Install Radix UI primitives
  - [ ] @radix-ui/react-dialog
  - [ ] @radix-ui/react-dropdown-menu
  - [ ] @radix-ui/react-tooltip
  - [ ] @radix-ui/react-tabs
  - [ ] @radix-ui/react-select
  - [ ] @radix-ui/react-slider
  - [ ] @radix-ui/react-slot
- [ ] **T1.1.1.3**: Install testing dependencies
  - [ ] vitest, jsdom
  - [ ] @testing-library/react, jest-dom, user-event
  - [ ] msw (Mock Service Worker)
  - [ ] vitest-axe (for a11y testing)
- [ ] **T1.1.1.7**: Configure Playwright E2E testing
  - [ ] Verify `.cursor/skills/playwright-skill` is set up
  - [ ] Run `cd .cursor/skills/playwright-skill && npm run setup`
  - [ ] Add `test:e2e` script to package.json
  - [ ] Create `e2e/` directory for test organization
- [ ] **T1.1.1.4**: Install @material-symbols/react-400 for icons
- [ ] **T1.1.1.5**: Configure path aliases in tsconfig.json (`@/`)
- [ ] **T1.1.1.6**: ♿ Install eslint-plugin-jsx-a11y for accessibility linting

**Acceptance Criteria:**
- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts development server
- [ ] `npm run test` runs test suite
- [ ] TypeScript strict mode enabled

**🧪 Validation Steps:**
```bash
# Sub-task validation (after each package install):
npm run build  # Verify no dependency conflicts

# Task validation:
npm run dev    # Server starts on http://localhost:5173
npm run test   # Test runner executes (may have 0 tests initially)
npm run lint   # No errors

# Story validation:
# Manual: Open http://localhost:5173 in browser
# Manual: Verify React renders "Hello World" or placeholder
# Manual: Check browser console for errors (should be none)
```

---

#### Story 1.1.2: Configure Design System
**As a** developer  
**I want** Apple design tokens configured in Tailwind  
**So that** components match the design files

**Tasks:**
- [ ] **T1.1.2.1**: Create `src/styles/tailwind.css` with CSS variables
  - [ ] Color tokens (apple-bg, apple-blue, apple-green, etc.)
  - [ ] Border radius tokens (card, button, pill)
  - [ ] Shadow tokens (card, card-hover, modal)
  - [ ] Animation keyframes (fadeIn, slideUp, scaleIn)
- [ ] **T1.1.2.2**: Create `src/lib/tokens/` directory
  - [ ] colors.ts
  - [ ] borders.ts
  - [ ] shadows.ts
  - [ ] motion.ts
  - [ ] index.ts (barrel export)
- [ ] **T1.1.2.3**: Add Inter font via Google Fonts or local
- [ ] **T1.1.2.4**: Configure Prettier with tailwind plugin
- [ ] **T1.1.2.5**: ♿ Fix WCAG color contrast issues
  - [ ] `apple-text-secondary`: #86868b → #6e6e73 (5.2:1 ratio)
  - [ ] `apple-text-tertiary`: #aeaeb2 → #8e8e93 (4.5:1 ratio)
  - [ ] Input borders: rgba(0,0,0,0.1) → rgba(0,0,0,0.25) (3:1 ratio)

**Acceptance Criteria:**
- [ ] All design colors available as Tailwind classes
- [ ] Custom animations work in components
- [ ] Inter font loads correctly
- [ ] ♿ All text colors meet 4.5:1 contrast ratio
- [ ] ♿ All UI elements meet 3:1 contrast ratio

**🧪 Validation Steps:**
```bash
# Task validation (after each token file):
npm run build  # TypeScript compiles tokens

# Story validation:
npm run dev
# Manual: Create test component with design tokens:
#   <div className="bg-apple-bg text-apple-text">
#     <span className="text-apple-text-secondary">Secondary</span>
#     <button className="bg-apple-blue text-white animate-fade-in">Test</button>
#   </div>
# Manual: Verify colors match designs/main-discovery-dashboard.html
# Manual: Verify Inter font renders (check DevTools > Elements > Computed)
# Manual: Run contrast checker on text colors (WebAIM Contrast Checker)
```

---

#### Story 1.1.3: Set Up Testing Infrastructure
**As a** developer  
**I want** a TDD-ready testing environment  
**So that** I can write tests before implementation

**Tasks:**
- [ ] **T1.1.3.1**: Create `vitest.config.ts`
- [ ] **T1.1.3.2**: Create `src/test/setup.ts` with jest-dom
- [ ] **T1.1.3.3**: Create `src/test/utils.tsx` with render helpers
- [ ] **T1.1.3.4**: Create `src/test/mocks/handlers.ts` for MSW
- [ ] **T1.1.3.5**: Create `src/test/mocks/server.ts` for MSW server
- [ ] **T1.1.3.6**: Write first passing test to verify setup

**Acceptance Criteria:**
- [ ] `npm run test` runs successfully
- [ ] Tests can render React components
- [ ] MSW intercepts API calls in tests

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test   # First test file runs

# Story validation:
npm run test   # All setup tests pass
npm run test:coverage  # Coverage report generates

# Manual: Verify test output shows:
#   ✓ renders React components
#   ✓ MSW intercepts requests
```

**📋 Feature 1.1 Validation:**
```bash
# After completing all Feature 1.1 stories:
npm run dev      # Dev server starts
npm run build    # Production build succeeds
npm run test     # All tests pass
npm run lint     # No lint errors
# Manual: Verify all acceptance criteria met
```

---

### Feature 1.2: Core Libraries

#### Story 1.2.1: Create API Client
**As a** developer  
**I want** a typed API client  
**So that** all API calls are consistent and type-safe

**Tasks:**
- [ ] **T1.2.1.1**: Create `src/lib/api/client.ts`
  - [ ] Base URL from env
  - [ ] Auth token injection
  - [ ] GET, POST, PUT, DELETE methods
  - [ ] Error handling
- [ ] **T1.2.1.2**: Create `src/lib/api/errors.ts`
  - [ ] ApiError class
  - [ ] Error type guards (isUnauthorized, isNotFound, etc.)
- [ ] **T1.2.1.3**: Write unit tests for API client

**Acceptance Criteria:**
- [ ] API client handles auth headers
- [ ] Errors are properly typed
- [ ] Tests pass for all HTTP methods

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- src/lib/api  # API client tests pass

# Story validation:
npm run test:coverage -- src/lib/api  # 90%+ coverage
# Manual: Test with MSW mock:
#   - GET request returns data
#   - POST sends body correctly
#   - 401 throws UnauthorizedError
#   - 404 throws NotFoundError
```

---

#### Story 1.2.2: Configure React Query
**As a** developer  
**I want** React Query configured with defaults  
**So that** server state is managed consistently

**Tasks:**
- [ ] **T1.2.2.1**: Create `src/lib/query/client.ts`
  - [ ] Default staleTime (5 minutes)
  - [ ] Default gcTime (30 minutes)
  - [ ] Retry configuration
- [ ] **T1.2.2.2**: Create QueryClientProvider wrapper
- [ ] **T1.2.2.3**: Add to App.tsx providers

**Acceptance Criteria:**
- [ ] QueryClientProvider wraps app
- [ ] Default options applied to all queries

**🧪 Validation Steps:**
```bash
# Task validation:
npm run build  # No errors with QueryClient

# Story validation:
npm run dev
# Manual: Check React DevTools for QueryClientProvider
# Manual: Verify no "missing QueryClient" errors in console
```

---

#### Story 1.2.3: Configure Supabase Client
**As a** developer  
**I want** Supabase client configured  
**So that** I can use auth and realtime features

**Tasks:**
- [ ] **T1.2.3.1**: Create `src/lib/supabase/client.ts`
- [ ] **T1.2.3.2**: Create environment variables
  - [ ] VITE_SUPABASE_URL
  - [ ] VITE_SUPABASE_ANON_KEY
  - [ ] VITE_API_URL
- [ ] **T1.2.3.3**: Create `.env.example` file

**Acceptance Criteria:**
- [ ] Supabase client initializes without errors
- [ ] Environment variables documented

**🧪 Validation Steps:**
```bash
# Task validation:
npm run build  # No missing env errors

# Story validation:
npm run dev
# Manual: Check browser console - no Supabase init errors
# Manual: Verify .env.example has all required vars documented
```

**📋 Feature 1.2 Validation:**
```bash
# After completing all Feature 1.2 stories:
npm run test -- src/lib  # All library tests pass
npm run build           # Production build succeeds
# Manual: API client, QueryClient, Supabase all functional
```

---

### Feature 1.3: Base UI Components

#### Story 1.3.1: Create Button Component
**As a** developer  
**I want** a reusable Button component  
**So that** all buttons match the design system

**Tasks:**
- [ ] **T1.3.1.1**: Create `src/components/ui/Button/Button.tsx`
  - [ ] Variants: primary, secondary, ghost, danger
  - [ ] Sizes: sm, md, lg (minimum 24×24px touch target)
  - [ ] Loading state with spinner
  - [ ] Disabled state with `aria-disabled`
  - [ ] Icon support (left/right)
- [ ] **T1.3.1.2**: Create `Button.test.tsx`
- [ ] **T1.3.1.3**: Create barrel export `index.ts`
- [ ] **T1.3.1.4**: ♿ Add accessibility features
  - [ ] `:focus-visible` ring style (3px apple-blue, 2px offset)
  - [ ] Icon-only buttons require `aria-label` prop
  - [ ] Loading state announces "Loading" to screen readers

**Acceptance Criteria:**
- [ ] All variants render correctly
- [ ] Loading spinner shows when loading=true
- [ ] Matches Apple button design (pill shape, colors)
- [ ] ♿ Focus ring visible on keyboard navigation
- [ ] ♿ Minimum 24×24px touch target (WCAG 2.5.8)

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Button.test.tsx  # Component tests pass

# Story validation:
npm run test -- Button  # All Button tests pass
npm run dev
# Manual: Visual inspection of all variants (primary, secondary, ghost, danger)
# Manual: Test loading state - spinner visible
# Manual: Tab to button - focus ring visible (3px blue outline)
# Manual: Measure button size - min 24×24px
# A11y: Run axe DevTools on button showcase
```

---

#### Story 1.3.2: Create Input Component
**As a** developer  
**I want** a reusable Input component  
**So that** all form inputs are consistent

**Tasks:**
- [ ] **T1.3.2.1**: Create `src/components/ui/Input/Input.tsx`
  - [ ] Types: text, email, password, number
  - [ ] Label support (required, linked with `htmlFor`)
  - [ ] Error state with message
  - [ ] Helper text
  - [ ] Left/right icons
- [ ] **T1.3.2.2**: Create `Input.test.tsx`
- [ ] **T1.3.2.3**: Integrate with react-hook-form
- [ ] **T1.3.2.4**: ♿ Add accessibility features
  - [ ] `aria-invalid="true"` when error present
  - [ ] `aria-describedby` linking to error/helper text
  - [ ] `autocomplete` attribute support (email, password, etc.)
  - [ ] Border contrast 3:1 ratio (rgba(0,0,0,0.25))
  - [ ] `:focus-visible` ring style

**Acceptance Criteria:**
- [ ] Error styling matches designs
- [ ] Works with react-hook-form register
- [ ] ♿ Label linked to input with `for`/`id`
- [ ] ♿ Error messages announced by screen readers
- [ ] ♿ Supports browser autofill (WCAG 1.3.5)

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Input.test.tsx  # Tests pass

# Story validation:
npm run dev
# Manual: Type in input - value updates
# Manual: Trigger error state - red border, error message visible
# Manual: Tab to input - focus ring visible
# A11y: VoiceOver - label announced on focus
# A11y: VoiceOver - error message announced when invalid
# Manual: Chrome autofill works on email input
```

---

#### Story 1.3.3: Create Card Component
**As a** developer  
**I want** a reusable Card component  
**So that** card layouts are consistent

**Tasks:**
- [ ] **T1.3.3.1**: Create `src/components/ui/Card/Card.tsx`
  - [ ] Default card styles (18px radius, shadow)
  - [ ] Hover effect (lift + shadow)
  - [ ] Card.Header, Card.Body, Card.Footer sub-components
- [ ] **T1.3.3.2**: Create `Card.test.tsx`

**Acceptance Criteria:**
- [ ] Cards have Apple-style shadow
- [ ] Hover animation works
- [ ] Sub-components compose correctly

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Card.test.tsx

# Story validation:
npm run dev
# Manual: Card visible with shadow
# Manual: Hover - card lifts with enhanced shadow
# Manual: Card.Header, Card.Body, Card.Footer compose correctly
```

---

#### Story 1.3.4: Create Badge Component
**As a** developer  
**I want** a reusable Badge component  
**So that** status indicators are consistent

**Tasks:**
- [ ] **T1.3.4.1**: Create `src/components/ui/Badge/Badge.tsx`
  - [ ] Variants: new, processing, done, failed, cancelled
  - [ ] Colors matching status
  - [ ] Pill and dot styles
- [ ] **T1.3.4.2**: Create `Badge.test.tsx`
- [ ] **T1.3.4.3**: ♿ Add accessible status indication
  - [ ] Include icon AND text (not color alone) per WCAG 1.4.1
  - [ ] Add status icons: ✓ done, ⏳ processing, ✕ failed, ⊘ cancelled
  - [ ] `aria-label` for screen reader context

**Acceptance Criteria:**
- [ ] Each status has correct color
- [ ] Matches design file badges
- [ ] ♿ Status conveyed by icon + text, not just color (WCAG 1.4.1)
- [ ] ♿ Screen readers announce status correctly

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Badge.test.tsx

# Story validation:
npm run dev
# Manual: All variants visible (new, processing, done, failed, cancelled)
# Manual: Each badge has icon + text (not color alone)
# A11y: VoiceOver - status announced correctly
# A11y: High contrast mode - badges distinguishable
```

---

#### Story 1.3.5: Create Modal Component
**As a** developer  
**I want** a reusable Modal component  
**So that** dialogs are accessible and consistent

**Tasks:**
- [ ] **T1.3.5.1**: Create `src/components/ui/Modal/Modal.tsx`
  - [ ] Use @radix-ui/react-dialog (provides ARIA by default)
  - [ ] Backdrop blur effect
  - [ ] Close button with `aria-label="Close"`
  - [ ] Modal.Header, Modal.Body, Modal.Footer
  - [ ] Size variants (sm, md, lg, xl)
- [ ] **T1.3.5.2**: Create `Modal.test.tsx`
- [ ] **T1.3.5.3**: ♿ Implement keyboard accessibility (WCAG 2.1.1, 2.1.2)
  - [ ] Escape key closes modal
  - [ ] Focus trapped inside modal (Tab cycles within)
  - [ ] Focus returns to trigger element on close
  - [ ] First focusable element receives focus on open
- [ ] **T1.3.5.4**: ♿ Add ARIA attributes (WCAG 4.1.2)
  - [ ] `role="dialog"` (Radix provides this)
  - [ ] `aria-modal="true"`
  - [ ] `aria-labelledby` pointing to title
  - [ ] `aria-describedby` for description (optional)

**Acceptance Criteria:**
- [ ] Modal has backdrop blur
- [ ] Escape key closes modal
- [ ] ♿ Focus trapped inside modal (cannot Tab outside)
- [ ] ♿ Focus returns to trigger on close
- [ ] ♿ Screen reader announces modal title and role

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Modal.test.tsx

# Story validation:
npm run dev
# Manual: Open modal - backdrop blur visible
# Manual: Press Escape - modal closes
# A11y: Tab through modal - focus stays inside (trap works)
# A11y: Close modal - focus returns to trigger button
# A11y: VoiceOver - announces "dialog" and modal title
# A11y: Try to Tab outside modal - should not escape
```

---

#### Story 1.3.6: Create Toast Component
**As a** developer  
**I want** a toast notification system  
**So that** users get feedback on actions

**Tasks:**
- [ ] **T1.3.6.1**: Create `src/components/ui/Toast/Toast.tsx`
  - [ ] Variants: success, error, warning, info
  - [ ] Auto-dismiss with timer
  - [ ] Manual dismiss button (min 24×24px)
  - [ ] Stacking multiple toasts
- [ ] **T1.3.6.2**: Create `src/contexts/ToastContext.tsx`
  - [ ] toast.success(), toast.error() methods
- [ ] **T1.3.6.3**: Create `Toast.test.tsx`
- [ ] **T1.3.6.4**: ♿ Add ARIA live region (WCAG 4.1.3)
  - [ ] Toast container: `aria-live="polite"` `aria-atomic="true"`
  - [ ] Error toasts: `role="alert"` for immediate announcement
  - [ ] Dismiss button: `aria-label="Dismiss notification"`

**Acceptance Criteria:**
- [ ] Toasts appear in top-right corner
- [ ] Auto-dismiss after 5 seconds
- [ ] Multiple toasts stack correctly
- [ ] ♿ Screen readers announce toast content (WCAG 4.1.3)
- [ ] ♿ Error toasts announced immediately

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Toast.test.tsx

# Story validation:
npm run dev
# Manual: Trigger toast - appears in top-right
# Manual: Wait 5 seconds - toast auto-dismisses
# Manual: Trigger multiple toasts - they stack vertically
# Manual: Click dismiss button - toast removes
# A11y: VoiceOver - toast content announced on appear
# A11y: Error toast - announced immediately (role="alert")
```

---

#### Story 1.3.7: Create Skeleton Component
**As a** developer  
**I want** skeleton loading components  
**So that** loading states are visually appealing

**Tasks:**
- [ ] **T1.3.7.1**: Create `src/components/ui/Skeleton/Skeleton.tsx`
  - [ ] Shimmer animation
  - [ ] Variants: text, circle, rect
  - [ ] Custom width/height
- [ ] **T1.3.7.2**: Create `Skeleton.test.tsx`

**Acceptance Criteria:**
- [ ] Shimmer animation runs smoothly
- [ ] Can create profile card skeletons

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- Skeleton.test.tsx

# Story validation:
npm run dev
# Manual: Skeleton visible with shimmer animation
# Manual: Animation is smooth (60fps)
# Manual: Create profile card skeleton layout
```

---

#### Story 1.3.8: Create Textarea Component
**As a** developer  
**I want** a reusable Textarea component  
**So that** multi-line inputs are consistent (brand description, email body)

**Tasks:**
- [ ] **T1.3.8.1**: Create `src/components/ui/Textarea/Textarea.tsx`
  - [ ] Label support (required, linked with `htmlFor`)
  - [ ] Error state with message
  - [ ] Character count (optional)
  - [ ] Auto-resize (optional)
- [ ] **T1.3.8.2**: Create `Textarea.test.tsx`
- [ ] **T1.3.8.3**: Integrate with react-hook-form
- [ ] **T1.3.8.4**: ♿ Add accessibility features
  - [ ] `aria-invalid="true"` when error present
  - [ ] `aria-describedby` linking to error/helper text

**Acceptance Criteria:**
- [ ] Multi-line text entry works
- [ ] Error styling matches Input component
- [ ] Works with react-hook-form register

**🧪 Validation Steps:**
```bash
npm run test -- Textarea.test.tsx
npm run dev
# Manual: Type multi-line text → works correctly
# Manual: Trigger error state → red border visible
```

---

#### Story 1.3.9: Create Avatar Component
**As a** developer  
**I want** a reusable Avatar component  
**So that** profile images are consistent

**Tasks:**
- [ ] **T1.3.9.1**: Create `src/components/ui/Avatar/Avatar.tsx`
  - [ ] Image with fallback (initials)
  - [ ] Sizes: sm, md, lg, xl
  - [ ] Border/ring style
  - [ ] Loading skeleton
- [ ] **T1.3.9.2**: Create `Avatar.test.tsx`
- [ ] **T1.3.9.3**: ♿ Add accessible alt text
  - [ ] `alt="Profile photo of {name}"` (not generic)
  - [ ] Fallback initials: `aria-label="{name}"`

**Acceptance Criteria:**
- [ ] Shows image when available
- [ ] Shows initials fallback when image fails
- [ ] Matches profile card design
- [ ] ♿ Meaningful alt text

**🧪 Validation Steps:**
```bash
npm run test -- Avatar.test.tsx
npm run dev
# Manual: Avatar shows image
# Manual: Break image URL → initials appear
# A11y: VoiceOver reads "Profile photo of [name]"
```

**📋 Feature 1.3 Validation:**
```bash
# After completing all Feature 1.3 stories:
npm run test -- src/components/ui  # All UI component tests pass
npm run build                      # Production build succeeds
# Manual: All 9 components render correctly
# A11y: Run axe DevTools on component showcase page
# A11y: Keyboard navigation works for all interactive components
```

---

### Feature 1.4: Routing Setup

#### Story 1.4.1: Configure React Router
**As a** developer  
**I want** routing configured  
**So that** navigation works between pages

**Tasks:**
- [ ] **T1.4.1.1**: Create `src/routes.tsx` with route definitions
- [ ] **T1.4.1.2**: Create lazy-loaded page imports
- [ ] **T1.4.1.3**: Create placeholder pages
  - [ ] LoginPage
  - [ ] DashboardPage
  - [ ] SessionsPage
  - [ ] DiscoveryConfigPage
  - [ ] NotFoundPage
- [ ] **T1.4.1.4**: Add router to App.tsx

**Acceptance Criteria:**
- [ ] All routes are defined
- [ ] 404 page shows for unknown routes
- [ ] Pages lazy load correctly

**🧪 Validation Steps:**
```bash
# Task validation:
npm run build  # Lazy imports resolve

# Story validation:
npm run dev
# Manual: Navigate to /login - LoginPage renders
# Manual: Navigate to /dashboard - DashboardPage renders
# Manual: Navigate to /unknown-route - 404 page shows
# Manual: Check Network tab - pages lazy load (separate chunks)
```

**📋 Feature 1.4 Validation:**
```bash
# After completing Feature 1.4:
npm run build  # Build succeeds with code splitting
# Manual: All routes accessible via URL
# Manual: Browser back/forward works
```

---

### Feature 1.5: Accessibility Foundation

> ♿ **WCAG Compliance**: This feature addresses critical accessibility requirements that apply globally.

#### Story 1.5.1: Configure Focus Styles
**As a** keyboard user  
**I want** visible focus indicators  
**So that** I can navigate the interface (WCAG 2.4.7)

**Tasks:**
- [ ] **T1.5.1.1**: Create global `:focus-visible` styles in `tailwind.css`
  ```css
  :focus-visible {
    outline: 3px solid var(--apple-blue);
    outline-offset: 2px;
  }
  ```
- [ ] **T1.5.1.2**: Create focus ring utility classes
  - [ ] `focus-ring` - default ring style
  - [ ] `focus-ring-inset` - inset for inputs
- [ ] **T1.5.1.3**: Ensure 3:1 contrast for focus indicator on all backgrounds
- [ ] **T1.5.1.4**: Test keyboard navigation through all interactive elements
- [ ] **T1.5.1.5**: Add scroll-margin-top for sticky header (WCAG 2.4.11)
  ```css
  :focus { scroll-margin-top: 80px; }
  ```

**Acceptance Criteria:**
- [ ] All interactive elements show focus ring on Tab
- [ ] Focus indicator visible on all backgrounds
- [ ] Focused elements not obscured by sticky header

**🧪 Validation Steps:**
```bash
# Task validation:
npm run build  # CSS compiles

# Story validation:
npm run dev
# A11y: Tab through page - all buttons/links show focus ring
# A11y: Focus ring visible on white background
# A11y: Focus ring visible on dark/colored backgrounds
# A11y: Tab to element near top - not hidden behind sticky header
```

---

#### Story 1.5.2: Create Skip Link Component
**As a** screen reader user  
**I want** to skip repetitive navigation  
**So that** I can access main content quickly (WCAG 2.4.1)

**Tasks:**
- [ ] **T1.5.2.1**: Create `src/components/ui/SkipLink/SkipLink.tsx`
- [ ] **T1.5.2.2**: Position visually hidden until focused
  ```css
  .skip-link {
    @apply sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 
           focus:bg-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg focus:z-[100];
  }
  ```
- [ ] **T1.5.2.3**: Link to `#main-content` anchor
- [ ] **T1.5.2.4**: Add SkipLink to all layout components
- [ ] **T1.5.2.5**: Add `id="main-content"` to main content areas

**Acceptance Criteria:**
- [ ] Skip link visible when Tab pressed at page load
- [ ] Clicking skip link moves focus to main content
- [ ] Works in all layouts (Dashboard, Auth, etc.)

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- SkipLink.test.tsx

# Story validation:
npm run dev
# A11y: Load page, press Tab - skip link appears
# A11y: Click skip link - focus moves to #main-content
# A11y: Tab again - focus continues from main content
# A11y: VoiceOver - announces "Skip to main content" link
```

---

#### Story 1.5.3: Create Screen Reader Utilities
**As a** developer  
**I want** utility components for screen readers  
**So that** I can provide context to assistive technology

**Tasks:**
- [ ] **T1.5.3.1**: Create `src/components/ui/VisuallyHidden/VisuallyHidden.tsx`
  - [ ] Hides content visually but keeps it accessible
- [ ] **T1.5.3.2**: Create `src/lib/a11y/announcer.ts`
  - [ ] Live region announcer for dynamic updates
  - [ ] announce(message, priority: 'polite' | 'assertive')
- [ ] **T1.5.3.3**: Add announcer to ToastContext for screen reader support

**Acceptance Criteria:**
- [ ] VisuallyHidden content readable by screen readers
- [ ] Announcer works for dynamic content updates

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- VisuallyHidden.test.tsx

# Story validation:
npm run dev
# Manual: VisuallyHidden text not visible on screen
# A11y: VoiceOver - VisuallyHidden text is announced
# Manual: Trigger announcer - dynamic update occurs
# A11y: VoiceOver - dynamic announcement heard
```

---

#### Story 1.5.4: Configure ESLint Accessibility Rules
**As a** developer  
**I want** linting rules for accessibility  
**So that** issues are caught during development

**Tasks:**
- [ ] **T1.5.4.1**: Install `eslint-plugin-jsx-a11y`
- [ ] **T1.5.4.2**: Configure recommended rules in eslint.config.js
- [ ] **T1.5.4.3**: Add custom rules for project patterns
  - [ ] Require alt text on images
  - [ ] Require aria-label on icon buttons
  - [ ] Warn on missing form labels

**Acceptance Criteria:**
- [ ] ESLint reports accessibility violations
- [ ] CI fails on critical a11y issues

**🧪 Validation Steps:**
```bash
# Task validation:
npm run lint  # a11y rules active

# Story validation:
# Test: Create component with missing alt text
#   <img src="test.jpg" />
# Run: npm run lint
# Expected: ESLint error for missing alt

# Test: Create icon button without aria-label
#   <button><Icon /></button>
# Run: npm run lint
# Expected: ESLint warning for missing accessible name
```

**📋 Feature 1.5 Validation:**
```bash
# After completing all Feature 1.5 stories:
npm run lint   # No a11y lint errors
npm run test   # A11y component tests pass
# A11y: Full keyboard navigation test
# A11y: Skip link works on all layouts
# A11y: Focus styles visible throughout app
```

---

## Epic 2: Authentication & User Management

> **Goal**: Implement secure user authentication with Supabase
> **Priority**: P0 (Critical)
> **Sprint**: 1-2

### 🎯 Epic 2 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ All Features Complete | 3 features delivered | Dev |
| ✅ Login Works | User can sign in with email/password | Dev |
| ✅ Sign Up Works | New user can create account | Dev |
| ✅ Protected Routes | Unauthenticated users redirected | Dev |
| ✅ Sign Out Works | User can log out | Dev |
| ✅ Session Persists | Refresh page keeps user logged in | Dev |
| ✅ Error Handling | Invalid credentials show error | Dev |
| ✅ A11y Compliant | Forms accessible, autocomplete works | Dev |
| ✅ Security Review | No tokens in URL or localStorage exposed | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 2.1: Auth Context

#### Story 2.1.1: Create Auth Context
**As a** developer  
**I want** an auth context  
**So that** user state is available throughout the app

**Tasks:**
- [ ] **T2.1.1.1**: Create `src/packlets/auth/context/AuthContext.tsx`
  - [ ] User state
  - [ ] Loading state
  - [ ] isAuthenticated computed
  - [ ] signIn, signUp, signOut methods
- [ ] **T2.1.1.2**: Create `useAuth` hook
- [ ] **T2.1.1.3**: Add AuthProvider to App.tsx
- [ ] **T2.1.1.4**: Write tests for auth context

**Acceptance Criteria:**
- [ ] User state updates on auth changes
- [ ] Loading state shows during auth operations
- [ ] Sign out clears user state

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- AuthContext.test.tsx

# Story validation:
npm run dev
# Manual: Login - user state updates in React DevTools
# Manual: Refresh page - user stays logged in (session persists)
# Manual: Sign out - user state clears
```

---

#### Story 2.1.2: Create Protected Route Component
**As a** user  
**I want** to be redirected to login if not authenticated  
**So that** protected content is secure

**Tasks:**
- [ ] **T2.1.2.1**: Create `src/components/ProtectedRoute.tsx`
- [ ] **T2.1.2.2**: Redirect to /login if not authenticated
- [ ] **T2.1.2.3**: Show loading state while checking auth
- [ ] **T2.1.2.4**: Wrap protected routes in routes.tsx

**Acceptance Criteria:**
- [ ] Unauthenticated users redirected to /login
- [ ] Auth check shows loading spinner
- [ ] Authenticated users see protected content

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- ProtectedRoute.test.tsx

# Story validation:
npm run dev
# Manual: Visit /dashboard while logged out - redirected to /login
# Manual: Login - redirected back to /dashboard
# Manual: Loading spinner visible during auth check
```

**📋 Feature 2.1 Validation:**
```bash
# After completing Feature 2.1:
npm run test -- src/packlets/auth  # All auth tests pass
# Manual: Full auth flow works (login, protected routes, logout)
```

---

### Feature 2.2: Login Page

#### Story 2.2.1: Build Login Form
**As a** user  
**I want** to sign in with email and password  
**So that** I can access my discovery sessions

**Tasks:**
- [ ] **T2.2.1.1**: Create `src/pages/LoginPage.tsx`
- [ ] **T2.2.1.2**: Create login form with react-hook-form
  - [ ] Email input
  - [ ] Password input
  - [ ] Submit button
  - [ ] Loading state
- [ ] **T2.2.1.3**: Add zod validation schema
- [ ] **T2.2.1.4**: Connect to Supabase signInWithPassword
- [ ] **T2.2.1.5**: Handle errors (invalid credentials)
- [ ] **T2.2.1.6**: Redirect to /dashboard on success
- [ ] **T2.2.1.7**: Style to match login.html design
- [ ] **T2.2.1.8**: ♿ Add accessibility features
  - [ ] `autocomplete="email"` on email input (WCAG 1.3.5)
  - [ ] `autocomplete="current-password"` on password input
  - [ ] Error messages with `aria-describedby` and `role="alert"`
  - [ ] Actionable error suggestions (e.g., "Forgot password?" link)

**Acceptance Criteria:**
- [ ] Form validates email format
- [ ] Error shown for invalid credentials
- [ ] Successful login redirects to dashboard
- [ ] Matches Apple-style design
- [ ] ♿ Supports password manager autofill (WCAG 3.3.8)
- [ ] ♿ Errors announced to screen readers

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- LoginPage.test.tsx

# Story validation:
npm run dev
# Manual: Submit empty form - validation errors shown
# Manual: Enter invalid email - "Invalid email" error
# Manual: Enter wrong password - "Invalid credentials" error
# Manual: Login with valid credentials - redirected to /dashboard
# A11y: Password manager autofills email/password
# A11y: Tab through form - all fields accessible
# A11y: VoiceOver - errors announced
```

---

#### Story 2.2.2: Build Sign Up Form
**As a** new user  
**I want** to create an account  
**So that** I can start discovering partners

**Tasks:**
- [ ] **T2.2.2.1**: Add sign up tab/toggle to LoginPage
- [ ] **T2.2.2.2**: Create sign up form
  - [ ] Email input
  - [ ] Password input
  - [ ] Confirm password input
- [ ] **T2.2.2.3**: Add password strength validation
- [ ] **T2.2.2.4**: Connect to Supabase signUp
- [ ] **T2.2.2.5**: Handle email confirmation flow
- [ ] **T2.2.2.6**: Show success message after sign up

**Acceptance Criteria:**
- [ ] Passwords must match
- [ ] Password minimum length enforced
- [ ] User sees confirmation message

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- SignUpForm.test.tsx

# Story validation:
npm run dev
# Manual: Passwords don't match - error shown
# Manual: Password too short - error shown
# Manual: Valid sign up - confirmation message displayed
# Manual: Check email for confirmation link (if enabled)
```

**📋 Feature 2.2 Validation:**
```bash
# After completing Feature 2.2:
npm run test -- src/pages/LoginPage  # All login tests pass
# Manual: Full login and sign up flow works
# A11y: Form accessibility complete
```

**🎭 Playwright E2E:** `e2e/auth.spec.js`
```
Tests to write after feature complete:
1. "User can login with valid credentials" → redirects to /dashboard
2. "Login shows error for invalid credentials"
3. "User can sign up with new account"
4. "Logged in user can access protected routes"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
- Auto-detect dev server first
- Use visible browser (headless: false)
- Save screenshots to /tmp/
```

---

### Feature 2.3: User Menu

#### Story 2.3.1: Build User Dropdown Menu
**As a** user  
**I want** a user menu in the header  
**So that** I can sign out and access settings

**Tasks:**
- [ ] **T2.3.1.1**: Create `src/components/composite/UserMenu/UserMenu.tsx`
- [ ] **T2.3.1.2**: Use @radix-ui/react-dropdown-menu (provides ARIA by default)
- [ ] **T2.3.1.3**: Show user avatar (initial letter)
- [ ] **T2.3.1.4**: Menu items: Profile, Settings, Sign Out
- [ ] **T2.3.1.5**: Connect Sign Out to auth context
- [ ] **T2.3.1.6**: ♿ Add accessibility features (WCAG 2.1.1, 4.1.2)
  - [ ] Radix provides `aria-haspopup`, `aria-expanded` by default
  - [ ] Keyboard: Enter/Space opens, Escape closes
  - [ ] Arrow keys navigate menu items
  - [ ] Add `aria-label` to trigger: "User menu for {name}"

**Acceptance Criteria:**
- [ ] Dropdown opens on click
- [ ] Sign out logs user out
- [ ] Matches design header user menu
- [ ] ♿ Keyboard accessible (Enter, Arrows, Escape)
- [ ] ♿ Screen reader announces menu state

**🧪 Validation Steps:**
```bash
# Task validation:
npm run test -- UserMenu.test.tsx

# Story validation:
npm run dev
# Manual: Click avatar - dropdown opens
# Manual: Click "Sign Out" - user logged out
# A11y: Tab to avatar, press Enter - menu opens
# A11y: Arrow keys - navigate menu items
# A11y: Escape - menu closes
# A11y: VoiceOver - announces "menu expanded/collapsed"
```

**📋 Feature 2.3 Validation:**
```bash
# After completing Feature 2.3:
npm run test -- UserMenu  # Tests pass
# Manual: User menu works in header
```

---

## Epic 3: Session Management

> **Goal**: Enable users to view, create, and manage discovery sessions
> **Priority**: P0 (Critical)
> **Sprint**: 2-3

### 🎯 Epic 3 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Sessions List | User sees all their sessions | Dev |
| ✅ Create Session | User can start new discovery | Dev |
| ✅ Delete Session | User can delete sessions | Dev |
| ✅ Empty State | First-time users see welcome + demo CTA | Dev |
| ✅ Demo Mode | "Watch Demo" creates sample session | Dev |
| ✅ Session Card | Status, counts, dates display correctly | Dev |
| ✅ Navigation | Click session → dashboard | Dev |
| ✅ Layout | Header, footer, responsive | Dev |
| ✅ A11y Compliant | Keyboard nav, screen reader | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 3.1: Sessions API Integration

#### Story 3.1.1: Create Jobs Service
**As a** developer  
**I want** a jobs API service  
**So that** I can fetch and manage discovery sessions

**Tasks:**
- [ ] **T3.1.1.1**: Create `src/services/jobs.ts`
  - [ ] list(): GET /api/jobs
  - [ ] get(id): GET /api/jobs/{id}
  - [ ] create(data): POST /api/jobs
  - [ ] delete(id): DELETE /api/jobs/{id}
  - [ ] start(id): POST /api/jobs/{id}/start
  - [ ] cancel(id): POST /api/jobs/{id}/cancel
  - [ ] retry(id): POST /api/jobs/{id}/retry
- [ ] **T3.1.1.2**: Create `src/services/demo.ts`
  - [ ] startDemo(): POST /api/demo/start
- [ ] **T3.1.1.3**: Create TypeScript types in `src/types/api/job.ts`
- [ ] **T3.1.1.4**: Write tests with MSW mocks

**Acceptance Criteria:**
- [ ] All endpoints return typed responses
- [ ] Tests cover success and error cases

**🧪 Validation Steps:**
```bash
npm run test -- src/services/jobs  # All service tests pass
# Verify MSW mocks all endpoints correctly
```

---

#### Story 3.1.2: Create Jobs Packlet Hooks
**As a** developer  
**I want** React Query hooks for jobs  
**So that** components can easily fetch job data

**Tasks:**
- [ ] **T3.1.2.1**: Create `src/packlets/jobs/hooks/useJobs.ts`
- [ ] **T3.1.2.2**: Create `src/packlets/jobs/hooks/useJob.ts`
- [ ] **T3.1.2.3**: Create `src/packlets/jobs/hooks/useCreateJob.ts`
- [ ] **T3.1.2.4**: Create `src/packlets/jobs/hooks/useCancelJob.ts`
- [ ] **T3.1.2.5**: Create `src/packlets/jobs/hooks/useDeleteJob.ts`
- [ ] **T3.1.2.6**: Create barrel export in `src/packlets/jobs/index.ts`

**Acceptance Criteria:**
- [ ] Hooks use React Query
- [ ] Mutations invalidate queries on success
- [ ] Error states handled

**🧪 Validation Steps:**
```bash
npm run test -- src/packlets/jobs/hooks  # All hook tests pass
# Manual: Verify React Query DevTools shows correct cache state
```

**📋 Feature 3.1 Validation:**
```bash
npm run test -- src/services/jobs src/packlets/jobs  # All pass
# Manual: API integration works with real backend
```

---

### Feature 3.2: Empty Dashboard

#### Story 3.2.1: Build Empty State
**As a** new user  
**I want** to see a welcome screen when I have no sessions  
**So that** I know how to get started

**Tasks:**
- [ ] **T3.2.1.1**: Create `src/components/features/EmptyState/EmptyState.tsx`
- [ ] **T3.2.1.2**: Add illustration/icon
- [ ] **T3.2.1.3**: Add "Start New Discovery" CTA button
- [ ] **T3.2.1.4**: Add "Watch Demo" button
- [ ] **T3.2.1.5**: Style to match empty-dashboard.html
- [ ] **T3.2.1.6**: Connect demo button to POST /api/demo/start

**Acceptance Criteria:**
- [ ] Shows when user has no sessions
- [ ] "New Discovery" navigates to /new-session
- [ ] "Watch Demo" creates demo job and redirects

**🧪 Validation Steps:**
```bash
npm run test -- EmptyState  # Tests pass
npm run dev
# Manual: New user sees empty state with illustration
# Manual: Click "New Discovery" → navigates to /new-session
# Manual: Click "Watch Demo" → creates demo job, redirects to dashboard
```

**📋 Feature 3.2 Validation:**
```bash
# After completing Feature 3.2:
# Manual: Empty state displays for users with 0 sessions
# Manual: Demo button creates job via POST /api/demo/start
```

---

### Feature 3.3: Sessions List Page

#### Story 3.3.1: Build Session Card Component
**As a** user  
**I want** to see my sessions as cards  
**So that** I can quickly understand their status

**Tasks:**
- [ ] **T3.3.1.1**: Create `src/components/composite/SessionCard/SessionCard.tsx`
  - [ ] Session name
  - [ ] Status badge
  - [ ] Created date
  - [ ] Profiles discovered count
  - [ ] Profiles scored count
  - [ ] Delete button
- [ ] **T3.3.1.2**: Create job builders
  - [ ] `src/packlets/jobs/builders/build-session-card.ts`
- [ ] **T3.3.1.3**: Create `SessionCard.test.tsx`

**Acceptance Criteria:**
- [ ] Status badge shows correct color
- [ ] Delete button triggers confirmation
- [ ] Matches session-list.html card design

**🧪 Validation Steps:**
```bash
npm run test -- SessionCard  # Tests pass
# Manual: Card displays all fields (name, status, date, counts)
# Manual: Delete button shows confirmation modal
```

---

#### Story 3.3.2: Build Sessions List Page
**As a** user  
**I want** to see all my discovery sessions  
**So that** I can manage and review them

**Tasks:**
- [ ] **T3.3.2.1**: Create `src/pages/SessionsPage.tsx`
- [ ] **T3.3.2.2**: Fetch sessions with useJobs hook
- [ ] **T3.3.2.3**: Render SessionCard grid
- [ ] **T3.3.2.4**: Add loading skeletons
- [ ] **T3.3.2.5**: Add "New Discovery" button in header
- [ ] **T3.3.2.6**: Show EmptyState if no sessions
- [ ] **T3.3.2.7**: Add delete confirmation modal

**Acceptance Criteria:**
- [ ] Sessions load and display correctly
- [ ] Clicking session navigates to dashboard
- [ ] Delete removes session from list
- [ ] Loading state shows skeletons

**🧪 Validation Steps:**
```bash
npm run test -- SessionsPage  # Tests pass
npm run dev
# Manual: Sessions grid loads with user's sessions
# Manual: Click session card → navigates to /jobs/{id}
# Manual: Delete session → confirmation → removed from list
# Manual: Loading state shows skeleton cards
```

**📋 Feature 3.3 Validation:**
```bash
# After completing Feature 3.3:
# Manual: Full sessions list functionality works
# A11y: Keyboard navigation through session cards
```

**🎭 Playwright E2E:** `e2e/sessions.spec.js`
```
Tests to write after feature complete:
1. "User sees empty state when no sessions exist"
2. "User can create new discovery session"
3. "Sessions list displays all user sessions"
4. "User can delete a session with confirmation"
5. "Click session navigates to dashboard"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
```

---

### Feature 3.4: Layout Components

#### Story 3.4.1: Build Header Component
**As a** user  
**I want** a consistent header  
**So that** I can navigate the app

**Tasks:**
- [ ] **T3.4.1.1**: Create `src/components/composite/Header/Header.tsx`
  - [ ] Logo with link to home
  - [ ] Navigation links (Dashboard, Sessions)
  - [ ] Session selector (optional)
  - [ ] User menu
- [ ] **T3.4.1.2**: Style to match design header
- [ ] **T3.4.1.3**: Make sticky with backdrop blur
- [ ] **T3.4.1.4**: ♿ Add landmark and skip link (WCAG 1.3.1, 2.4.1)
  - [ ] Wrap navigation in `<nav aria-label="Main navigation">`
  - [ ] Include SkipLink component as first focusable element
  - [ ] Logo: Add `aria-label="PartnerScout home"` or use `<title>` in SVG

**Acceptance Criteria:**
- [ ] Header sticks to top
- [ ] Navigation links work
- [ ] Backdrop blur on scroll
- [ ] ♿ Skip link visible on Tab at page load
- [ ] ♿ Navigation wrapped in `<nav>` landmark

**🧪 Validation Steps:**
```bash
npm run test -- Header  # Tests pass
npm run dev
# Manual: Header sticks on scroll with backdrop blur
# Manual: Nav links work (Dashboard, Sessions)
# A11y: Tab → skip link visible → Tab → nav links
# A11y: VoiceOver announces "Main navigation"
```

---

#### Story 3.4.2: Build Dashboard Layout
**As a** developer  
**I want** a reusable layout component  
**So that** pages have consistent structure

**Tasks:**
- [ ] **T3.4.2.1**: Create `src/components/layouts/DashboardLayout/DashboardLayout.tsx`
- [ ] **T3.4.2.2**: Include Header
- [ ] **T3.4.2.3**: Include main content area
- [ ] **T3.4.2.4**: Include Footer
- [ ] **T3.4.2.5**: Add to router outlet

**Acceptance Criteria:**
- [ ] Layout wraps all dashboard pages
- [ ] Max width constraint applied
- [ ] Responsive padding

**🧪 Validation Steps:**
```bash
npm run test -- DashboardLayout  # Tests pass
# Manual: Layout renders header, main, footer
# Manual: Max width applies on wide screens
# Manual: Responsive padding on mobile/tablet/desktop
```

**📋 Feature 3.4 Validation:**
```bash
# After completing Feature 3.4:
# Manual: All pages use consistent layout
# Manual: Responsive design works across breakpoints
```

---

## Epic 4: Discovery Configuration

> **Goal**: Enable users to configure and launch new discovery sessions
> **Priority**: P0 (Critical)
> **Sprint**: 3

### 🎯 Epic 4 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Form Renders | All config fields display | Dev |
| ✅ Validation Works | Required fields, min/max enforced | Dev |
| ✅ Tag Input | Keywords/hashtags as chips | Dev |
| ✅ Sliders Work | Discovery limit, score threshold | Dev |
| ✅ Review Step | All values displayed before launch | Dev |
| ✅ Launch Creates Job | POST /api/jobs succeeds | Dev |
| ✅ Redirects | After launch → pipeline page | Dev |
| ✅ A11y Compliant | Forms accessible | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 4.1: Configuration Form Components

#### Story 4.1.1: Create Tag Input Component
**As a** user  
**I want** to enter keywords and hashtags as tags  
**So that** I can easily manage my search terms

**Tasks:**
- [ ] **T4.1.1.1**: Create `src/components/ui/TagInput/TagInput.tsx`
  - [ ] Add tags on Enter/comma
  - [ ] Remove tags with X button (min 24×24px)
  - [ ] Max tags limit
  - [ ] Validation (e.g., hashtags start with #)
- [ ] **T4.1.1.2**: Integrate with react-hook-form
- [ ] **T4.1.1.3**: Write tests
- [ ] **T4.1.1.4**: ♿ Add accessibility features
  - [ ] `aria-describedby` for input instructions
  - [ ] Remove button: `aria-label="Remove {tag}"`
  - [ ] Announce tag additions/removals via live region
  - [ ] Keyboard: Backspace removes last tag when input empty

**Acceptance Criteria:**
- [ ] Tags appear as chips
- [ ] Tags removable
- [ ] Works with form validation
- [ ] ♿ Screen reader announces tag changes
- [ ] ♿ Remove buttons have accessible names

**🧪 Validation Steps:**
```bash
npm run test -- TagInput  # Tests pass
# Manual: Type tag + Enter → chip appears
# Manual: Click X on chip → tag removed
# A11y: VoiceOver announces "tag added/removed"
```

---

#### Story 4.1.2: Create Slider Component
**As a** user  
**I want** slider inputs for ranges  
**So that** I can easily set discovery limits

**Tasks:**
- [ ] **T4.1.2.1**: Create `src/components/ui/Slider/Slider.tsx`
  - [ ] Use @radix-ui/react-slider for ARIA support
  - [ ] Min/max values
  - [ ] Step size
  - [ ] Current value display
  - [ ] Range variant (min-max)
- [ ] **T4.1.2.2**: Style to match design
- [ ] **T4.1.2.3**: Integrate with react-hook-form
- [ ] **T4.1.2.4**: ♿ Add accessibility features (WCAG 4.1.2)
  - [ ] `role="slider"` (Radix provides)
  - [ ] `aria-valuemin`, `aria-valuemax`, `aria-valuenow`
  - [ ] `aria-label` or `aria-labelledby` for context
  - [ ] Keyboard: Arrow keys adjust value

**Acceptance Criteria:**
- [ ] Slider tracks thumb position
- [ ] Value updates on drag
- [ ] Matches Apple slider aesthetic
- [ ] ♿ Keyboard adjustable with arrow keys
- [ ] ♿ Screen reader announces current value

**🧪 Validation Steps:**
```bash
npm run test -- Slider  # Tests pass
# Manual: Drag slider → value updates
# A11y: Tab to slider, use arrow keys → value changes
# A11y: VoiceOver announces "slider, 50 of 100"
```

---

#### Story 4.1.3: Create Stepper Component
**As a** user  
**I want** to see my progress through the configuration steps  
**So that** I know where I am in the process

**Tasks:**
- [ ] **T4.1.3.1**: Write tests first (TDD)
  - [ ] Test renders correct number of steps
  - [ ] Test active step is highlighted
  - [ ] Test completed step shows checkmark
  - [ ] Test responsive behavior
- [ ] **T4.1.3.2**: Create `src/components/ui/Stepper/Stepper.tsx`
  - [ ] Steps array with label and status (active/complete/upcoming)
  - [ ] Circular step indicators with numbers
  - [ ] Checkmark icon for completed steps
  - [ ] Connector lines between steps
- [ ] **T4.1.3.3**: Add responsive design (hide labels on mobile)
- [ ] **T4.1.3.4**: Style to match discovery-engine-step1.html stepper
- [ ] **T4.1.3.5**: ♿ Add accessibility features
  - [ ] `aria-current="step"` on active step
  - [ ] Descriptive text for screen readers
- [ ] **T4.1.3.6**: Create `Stepper.test.tsx`

**Acceptance Criteria:**
- [ ] Stepper shows 2 steps (Configure, Launch)
- [ ] Active step highlighted with blue
- [ ] Completed step shows green checkmark
- [ ] Responsive on mobile
- [ ] All tests pass

**🧪 Validation Steps:**
```bash
npm run test -- Stepper  # Tests pass
# Manual: Step 1 active on config page
# Manual: Step 1 complete, Step 2 active on review page
# A11y: Screen reader announces current step
```

---

#### Story 4.1.4: Create Follower Range Presets
**As a** user  
**I want** quick preset buttons for follower ranges  
**So that** I can quickly select common influencer tiers

**Tasks:**
- [ ] **T4.1.4.1**: Write tests first (TDD)
  - [ ] Test 4 preset buttons render
  - [ ] Test clicking preset updates form values
  - [ ] Test active state styling
  - [ ] Test custom values clear active preset
- [ ] **T4.1.4.2**: Create `src/components/composite/FollowerPresets/FollowerPresets.tsx`
  - [ ] Nano (1K-10K)
  - [ ] Micro (10K-100K)
  - [ ] Mid-tier (100K-500K)
  - [ ] Macro (500K+)
- [ ] **T4.1.4.3**: Clicking preset fills min/max follower inputs
- [ ] **T4.1.4.4**: Active state styling for selected preset
- [ ] **T4.1.4.5**: Style to match discovery-engine-step1.html preset buttons
- [ ] **T4.1.4.6**: Create `FollowerPresets.test.tsx`

**Acceptance Criteria:**
- [ ] 4 preset buttons display below follower inputs
- [ ] Clicking preset updates min/max values
- [ ] Active preset visually highlighted
- [ ] Custom values clear active preset state
- [ ] All tests pass

**🧪 Validation Steps:**
```bash
npm run test -- FollowerPresets  # Tests pass
npm run test -- DiscoveryConfigPage  # Integration tests pass
# Manual: Click "Micro" → min=10000, max=100000
# Manual: Active button shows blue highlight
```

**📋 Feature 4.1 Validation:**
```bash
npm run test -- TagInput Slider Stepper  # Tests pass
# Manual: All form components work correctly
```

---

### Feature 4.2: Discovery Configuration Page

#### Story 4.2.1: Build Step 1 Form
**As a** user  
**I want** to configure my discovery session  
**So that** I can find relevant partners

**Tasks:**
- [ ] **T4.2.1.1**: Create `src/pages/DiscoveryConfigPage.tsx`
- [ ] **T4.2.1.2**: Create form with react-hook-form
  - [ ] Campaign name input
  - [ ] Brand description textarea
  - [ ] Reference profiles input (URL list)
  - [ ] Keywords tag input
  - [ ] Hashtags tag input
  - [ ] Discovery limit slider (10-100)
  - [ ] Min score threshold slider (0-100)
  - [ ] Follower range inputs (min/max)
- [ ] **T4.2.1.3**: Add zod validation schema
- [ ] **T4.2.1.4**: Style to match discovery-engine-step1.html
- [ ] **T4.2.1.5**: Add "Next: Review" button

**Acceptance Criteria:**
- [ ] All inputs validate correctly
- [ ] 2-10 reference profiles required
- [ ] Form state persists during navigation

**🧪 Validation Steps:**
```bash
npm run test -- DiscoveryConfigPage  # Tests pass
npm run dev
# Manual: Fill all fields → "Next: Review" button enabled
# Manual: Missing required field → validation error
# Manual: Navigate away and back → form state persists
```

---

#### Story 4.2.2: Build Step 2 Review Page
**As a** user  
**I want** to review my configuration before launching  
**So that** I can verify everything is correct

**Tasks:**
- [ ] **T4.2.2.1**: Create review section in page
- [ ] **T4.2.2.2**: Display all configured values
- [ ] **T4.2.2.3**: Add edit buttons per section
- [ ] **T4.2.2.4**: Add "Launch Discovery" button
- [ ] **T4.2.2.5**: Connect to create job mutation
- [ ] **T4.2.2.6**: On success, navigate to /jobs/{id}
- [ ] **T4.2.2.7**: Add Stepper component (Step 1 complete, Step 2 active)
- [ ] **T4.2.2.8**: Add estimated time display (~3-5 minutes)
- [ ] **T4.2.2.9**: Add info note about real-time updates
  - [ ] Blue info box with icon
  - [ ] Text: "Profiles will appear on your dashboard as they're discovered"

**Acceptance Criteria:**
- [ ] All values displayed correctly
- [ ] Can go back to edit
- [ ] Launch creates job and redirects
- [ ] Stepper shows progress (Step 1 ✓, Step 2 active)
- [ ] Estimated time displayed
- [ ] Info note visible before launch button

**🧪 Validation Steps:**
```bash
npm run test -- ReviewPage  # Tests pass
npm run dev
# Manual: All configured values shown on review page
# Manual: Stepper shows Step 1 complete with checkmark
# Manual: Estimated time "~3-5 minutes" displayed
# Manual: Info note about real-time updates visible
# Manual: Click "Edit" → returns to config form
# Manual: Click "Launch Discovery" → job created, redirects to /jobs/{id}
```

**📋 Feature 4.2 Validation:**
```bash
# After completing Feature 4.2:
# Manual: Full discovery configuration flow works
# Manual: Job created in backend with correct data
```

**🎭 Playwright E2E:** `e2e/discovery-config.spec.js`
```
Tests to write after feature complete:
1. "User can fill all configuration fields"
2. "Form validation prevents invalid submission"
3. "Review step shows all configured values"
4. "Launch creates job and redirects to pipeline"
5. "Stepper shows correct step (1 on config, 2 on review)"
6. "Follower presets fill min/max values correctly"
7. "Review page shows estimated time and info note"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
- Test tag input (add/remove tags)
- Test slider inputs (drag or keyboard)
- Test multi-step navigation
- Test stepper visual states (active, complete)
- Test preset button interactions
- Test info note visibility on review page
```

---

## Epic 5: Main Dashboard

> **Goal**: Build the primary profile discovery dashboard
> **Priority**: P0 (Critical)
> **Sprint**: 4

### 🎯 Epic 5 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Profiles Load | Discovered profiles display | Dev |
| ✅ Profile Cards | Avatar, name, score, actions visible | Dev |
| ✅ Score Ring | Visual percentage display | Dev |
| ✅ Tab Filtering | All, New, Processing, Done filters work | Dev |
| ✅ Sorting | Sort by score, date, etc. | Dev |
| ✅ Stats Grid | Analytics summary accurate | Dev |
| ✅ Pagination | Load More works | Dev |
| ✅ Real-time Updates | New profiles appear without refresh | Dev |
| ✅ A11y Compliant | Cards, tabs, keyboard nav | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

**🎭 Epic 5 E2E Test:** `e2e/epic5-dashboard-journey.spec.js`
```
Full user journey test (run after Epic complete):
1. Login → Navigate to session → View dashboard
2. Filter by tabs → Sort profiles → Click profile
3. View detail modal → Close modal
4. Test responsive (desktop → tablet → mobile)

This validates the entire dashboard epic end-to-end.
```

---

### Feature 5.1: Profiles API Integration

#### Story 5.1.1: Create Profiles Service & Hooks
**As a** developer  
**I want** profiles API integration  
**So that** I can display discovered profiles

**Tasks:**
- [ ] **T5.1.1.1**: Create `src/services/profiles.ts`
- [ ] **T5.1.1.2**: Create TypeScript types in `src/types/api/profile.ts`
- [ ] **T5.1.1.3**: Create `src/packlets/profiles/hooks/useProfiles.ts`
- [ ] **T5.1.1.4**: Create `src/packlets/profiles/hooks/useProfile.ts`
- [ ] **T5.1.1.5**: Create profile builders
  - [ ] `build-profile-card.ts`
  - [ ] `build-profile-detail.ts`
  - [ ] `build-score-breakdown.ts`

**Acceptance Criteria:**
- [ ] Profiles fetch correctly
- [ ] Builders transform API data to UI props
- [ ] Types match backend response

**🧪 Validation Steps:**
```bash
npm run test -- src/services/profiles src/packlets/profiles  # Tests pass
# Manual: Profiles load from API
# Manual: Builder transforms data correctly
```

**📋 Feature 5.1 Validation:**
```bash
# After completing Feature 5.1:
# Manual: Profiles API integration works end-to-end
```

---

### Feature 5.2: Profile Card Component

#### Story 5.2.1: Build Profile Card
**As a** user  
**I want** to see profile cards in a grid  
**So that** I can quickly scan discovered partners

**Tasks:**
- [ ] **T5.2.1.1**: Create `src/components/composite/ProfileCard/ProfileCard.tsx`
  - [ ] Cover image with gradient
  - [ ] Profile avatar
  - [ ] Name and username
  - [ ] Follower count
  - [ ] Engagement rate
  - [ ] Score ring with value
  - [ ] Status badge (NEW, EMAIL, TOP)
  - [ ] Action buttons (View, Email, Bookmark)
- [ ] **T5.2.1.2**: Create `ProfileCard.test.tsx`
- [ ] **T5.2.1.3**: Add hover animations
- [ ] **T5.2.1.4**: ♿ Add accessibility features (WCAG 1.1.1, 2.5.3)
  - [ ] Avatar: `alt="Profile photo of {name}"` (not generic "Avatar")
  - [ ] Cover: `alt=""` (decorative) or describe if meaningful
  - [ ] Card as `<article>` with `aria-labelledby` pointing to name
  - [ ] Icon buttons: `aria-label="Email {name}"`, `aria-label="Bookmark {name}"`
  - [ ] View button: `aria-label="View profile for {name}"`

**Acceptance Criteria:**
- [ ] Score ring shows percentage visually
- [ ] Hover lifts card with shadow
- [ ] Matches main-discovery-dashboard.html card
- [ ] ♿ Descriptive alt text on images (WCAG 1.1.1)
- [ ] ♿ All icon buttons have accessible names (WCAG 2.5.3)

**🧪 Validation Steps:**
```bash
npm run test -- ProfileCard  # Tests pass
npm run dev
# Manual: Card displays all fields (avatar, name, score, followers)
# Manual: Hover → card lifts with enhanced shadow
# A11y: VoiceOver reads "Profile photo of [name]"
# A11y: Icon buttons have "Email [name]", "Bookmark [name]" labels
```

---

#### Story 5.2.2: Build Score Ring Component
**As a** user  
**I want** to see scores as circular progress  
**So that** I can quickly assess match quality

**Tasks:**
- [ ] **T5.2.2.1**: Create `src/components/ui/ScoreRing/ScoreRing.tsx`
  - [ ] Conic gradient based on score
  - [ ] Score number in center
  - [ ] Color variants by score range
- [ ] **T5.2.2.2**: Write tests
- [ ] **T5.2.2.3**: ♿ Add ARIA progressbar (WCAG 4.1.2)
  - [ ] `role="progressbar"`
  - [ ] `aria-valuenow={score}`
  - [ ] `aria-valuemin="0"` `aria-valuemax="100"`
  - [ ] `aria-label="Match score"` or `aria-labelledby`

**Acceptance Criteria:**
- [ ] Ring fills based on score percentage
- [ ] High scores use different color
- [ ] Smooth rendering
- [ ] ♿ Screen reader announces score value (e.g., "Match score: 85 of 100")

**🧪 Validation Steps:**
```bash
npm run test -- ScoreRing  # Tests pass
# Manual: Ring displays with correct fill percentage
# Manual: 80+ scores use green, 50-79 use blue, <50 use gray
# A11y: VoiceOver reads "Match score: 85 of 100"
```

**📋 Feature 5.2 Validation:**
```bash
# After completing Feature 5.2:
# Manual: Profile cards render correctly with all data
# A11y: All card elements accessible
```

---

### Feature 5.3: Dashboard Page

#### Story 5.3.1: Build Dashboard Page Structure
**As a** user  
**I want** to see my discovery dashboard  
**So that** I can review and manage discovered profiles

**Tasks:**
- [ ] **T5.3.1.1**: Create `src/pages/DashboardPage.tsx`
- [ ] **T5.3.1.2**: Add page header with title and stats
- [ ] **T5.3.1.3**: Add tab navigation (All, New, Processing, Done)
  - [ ] Use @radix-ui/react-tabs for ARIA support
- [ ] **T5.3.1.4**: Add sort dropdown
  - [ ] Use @radix-ui/react-select for ARIA support
- [ ] **T5.3.1.5**: Add profile grid
- [ ] **T5.3.1.6**: ♿ Implement accessible tabs pattern (WCAG 4.1.2)
  - [ ] `role="tablist"` on container (Radix provides)
  - [ ] `role="tab"` on tab buttons
  - [ ] `role="tabpanel"` on content panels
  - [ ] `aria-selected` on active tab
  - [ ] Arrow key navigation between tabs
  - [ ] Home/End key navigation to first/last tab

**Acceptance Criteria:**
- [ ] Page loads with job data
- [ ] Tabs filter profiles by status
- [ ] Sort changes profile order
- [ ] ♿ Tabs navigable with arrow keys
- [ ] ♿ Screen reader announces active tab

**🧪 Validation Steps:**
```bash
npm run test -- DashboardPage  # Tests pass
npm run dev
# Manual: Page loads with job title and profiles
# Manual: Click "New" tab → shows only new profiles
# Manual: Change sort → profiles reorder
# A11y: Arrow keys navigate between tabs
# A11y: VoiceOver announces "New tab, selected"
```

---

#### Story 5.3.2: Build Analytics Summary Panel
**As a** user  
**I want** to see analytics stats  
**So that** I understand my discovery results

**Tasks:**
- [ ] **T5.3.2.1**: Create `src/components/composite/StatsGrid/StatsGrid.tsx`
  - [ ] Total Discovered
  - [ ] High Match count
  - [ ] Emails Found
  - [ ] Average Score
- [ ] **T5.3.2.2**: Fetch from GET /api/jobs/{id}/analytics
- [ ] **T5.3.2.3**: Add icons and trend indicators

**Acceptance Criteria:**
- [ ] Stats update with real data
- [ ] Matches design stat cards

**🧪 Validation Steps:**
```bash
npm run test -- StatsGrid  # Tests pass
# Manual: Stats display (Total, High Match, Emails, Avg Score)
# Manual: Values match job analytics data
```

---

#### Story 5.3.3: Build Profile Grid
**As a** user  
**I want** profiles displayed in a responsive grid  
**So that** I can browse them efficiently

**Tasks:**
- [ ] **T5.3.3.1**: Create `src/components/features/ProfileGrid/ProfileGrid.tsx`
- [ ] **T5.3.3.2**: Render ProfileCard for each profile
- [ ] **T5.3.3.3**: Add skeleton loading state
- [ ] **T5.3.3.4**: Add empty state if no profiles
- [ ] **T5.3.3.5**: Add "Load More" button for pagination

**Acceptance Criteria:**
- [ ] Grid is responsive (1/2/3 columns)
- [ ] Skeletons show while loading
- [ ] Pagination works

**🧪 Validation Steps:**
```bash
npm run test -- ProfileGrid  # Tests pass
npm run dev
# Manual: Grid is 1 column on mobile, 2 on tablet, 3 on desktop
# Manual: Loading → skeleton cards visible
# Manual: Click "Load More" → more profiles appear
```

**📋 Feature 5.3 Validation:**
```bash
# After completing Feature 5.3:
# Manual: Full dashboard page works with real data
# Manual: Responsive design on all breakpoints
```

**🎭 Playwright E2E:** `e2e/dashboard.spec.js`
```
Tests to write after feature complete:
1. "Dashboard loads with job data and profiles"
2. "Tab filtering shows correct profiles"
3. "Sort dropdown changes profile order"
4. "Click profile card opens detail modal"
5. "Pagination loads more profiles"
6. "Responsive: test desktop, tablet, mobile viewports"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
- Use viewport testing for responsive
- Take screenshots at each breakpoint
```

---

### Feature 5.4: Real-time Updates

#### Story 5.4.1: Implement Real-time Profile Updates
**As a** user  
**I want** to see profiles appear as they're discovered  
**So that** I get real-time feedback

**Tasks:**
- [ ] **T5.4.1.1**: Create `src/packlets/common/hooks/useRealtime.ts`
- [ ] **T5.4.1.2**: Subscribe to discovered_profiles changes
- [ ] **T5.4.1.3**: Subscribe to profile_scores changes
- [ ] **T5.4.1.4**: Update React Query cache on changes
- [ ] **T5.4.1.5**: Add slide-in animation for new profiles

**Acceptance Criteria:**
- [ ] New profiles appear without refresh
- [ ] Scores update when scoring completes
- [ ] Animations are smooth

**🧪 Validation Steps:**
```bash
npm run test -- useRealtime  # Tests pass
npm run dev
# Manual: Start discovery job → profiles appear in real-time
# Manual: Scores update automatically when scoring completes
# Manual: New profile slides in with animation
```

**📋 Feature 5.4 Validation:**
```bash
# After completing Feature 5.4:
# Manual: Real-time updates work with Supabase
# Manual: No page refresh needed to see new data
```

---

## Epic 6: Profile Detail & Actions

> **Goal**: Enable detailed profile viewing and user actions
> **Priority**: P1 (High)
> **Sprint**: 5

### 🎯 Epic 6 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Modal Opens | Click profile → modal opens | Dev |
| ✅ All Data Displayed | Bio, stats, score, email | Dev |
| ✅ Score Breakdown | 4-6 dimensions with bars | Dev |
| ✅ Copy Email | Copy button works | Dev |
| ✅ Bookmark Works | Toggle bookmark state | Dev |
| ✅ Modal A11y | Focus trap, keyboard nav | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 6.1: Profile Detail Modal

#### Story 6.1.1: Build Profile Detail Modal
**As a** user  
**I want** to see full profile details  
**So that** I can make informed partnership decisions

**Tasks:**
- [ ] **T6.1.1.1**: Create `src/components/features/ProfileDetail/ProfileDetail.tsx`
- [ ] **T6.1.1.2**: Build header section (cover, avatar, name)
- [ ] **T6.1.1.3**: Build info section (bio, stats)
- [ ] **T6.1.1.4**: Build score section (ring, breakdown bars)
- [ ] **T6.1.1.5**: Build AI analysis section
- [ ] **T6.1.1.6**: Build contact section (email with copy)
- [ ] **T6.1.1.7**: Build action buttons (Email, Save, Skip)
- [ ] **T6.1.1.8**: Style to match profile-detail-model-view.html

**Acceptance Criteria:**
- [ ] All profile data displayed
- [ ] Score breakdown shows 4-6 dimensions
- [ ] Copy email button works
- [ ] Modal scrolls if content overflows

**🧪 Validation Steps:**
```bash
npm run test -- ProfileDetail  # Tests pass
npm run dev
# Manual: Click profile card → modal opens
# Manual: All sections visible (header, bio, stats, scores, contact)
# Manual: Click copy email → email copied to clipboard
# Manual: Long content → modal scrolls
# A11y: Focus trapped in modal
# A11y: Escape closes modal
```

---

#### Story 6.1.2: Build Score Breakdown Component
**As a** user  
**I want** to see how the AI scored the profile  
**So that** I understand the match reasoning

**Tasks:**
- [ ] **T6.1.2.1**: Create `src/components/composite/ScoreBreakdown/ScoreBreakdown.tsx`
  - [ ] Progress bars for each dimension
  - [ ] Labels and percentages
  - [ ] Color coding by value
- [ ] **T6.1.2.2**: Write tests
- [ ] **T6.1.2.3**: ♿ Add ARIA to progress bars (WCAG 4.1.2)
  - [ ] Each bar: `role="progressbar"`
  - [ ] `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
  - [ ] `aria-label="{Dimension} score: {value} percent"`

**Acceptance Criteria:**
- [ ] Bars fill based on score
- [ ] Labels match AI dimensions
- [ ] ♿ Screen reader announces each dimension score

**🧪 Validation Steps:**
```bash
npm run test -- ScoreBreakdown  # Tests pass
# Manual: Each dimension shows progress bar
# A11y: VoiceOver reads "Engagement score: 85 percent"
```

**📋 Feature 6.1 Validation:**
```bash
# After completing Feature 6.1:
# Manual: Profile detail modal fully functional
# A11y: Complete modal accessibility
```

**🎭 Playwright E2E:** `e2e/profile-detail.spec.js`
```
Tests to write after feature complete:
1. "Profile modal opens with all data displayed"
2. "Score breakdown shows dimension bars"
3. "Copy email button copies to clipboard"
4. "Modal closes with Escape key"
5. "Focus trap works inside modal"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
```

---

### Feature 6.2: Profile Actions

#### Story 6.2.1: Implement Bookmark Action
**As a** user  
**I want** to bookmark interesting profiles  
**So that** I can find them later

**Tasks:**
- [ ] **T6.2.1.1**: Add bookmark button to ProfileCard
- [ ] **T6.2.1.2**: Add bookmark button to ProfileDetail
- [ ] **T6.2.1.3**: Create bookmark mutation (when API ready)
- [ ] **T6.2.1.4**: Toggle bookmark icon state
- [ ] **T6.2.1.5**: Show toast on bookmark

**Acceptance Criteria:**
- [ ] Icon toggles between outlined/filled
- [ ] Toast confirms action
- [ ] (Future: persists to backend)

**🧪 Validation Steps:**
```bash
npm run test -- Bookmark  # Tests pass
# Manual: Click bookmark → icon fills, toast shows
# Manual: Click again → icon outlines, toast shows
```

---

#### Story 6.2.2: Implement Skip Action
**As a** user  
**I want** to skip irrelevant profiles  
**So that** they don't clutter my results

**Tasks:**
- [ ] **T6.2.2.1**: Add skip button to ProfileDetail modal
- [ ] **T6.2.2.2**: Create skip mutation (when API ready: PATCH /api/profiles/{id})
- [ ] **T6.2.2.3**: Remove profile from current view on skip
- [ ] **T6.2.2.4**: Show toast confirmation
- [ ] **T6.2.2.5**: ♿ Confirm action is reversible (undo toast or filter to show skipped)

**Acceptance Criteria:**
- [ ] Skip removes profile from grid
- [ ] Toast confirms skip with optional undo
- [ ] (Future: persists to backend)

**🧪 Validation Steps:**
```bash
npm run test -- SkipProfile  # Tests pass
# Manual: Click skip → profile removed from grid
# Manual: Toast shows with undo option
```

**📋 Feature 6.2 Validation:**
```bash
# After completing Feature 6.2:
# Manual: All profile actions work (bookmark, skip)
```

---

## Epic 7: Email Composer

> **Goal**: Enable AI-powered email composition and sending
> **Priority**: P1 (High)
> **Sprint**: 5-6

### 🎯 Epic 7 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Modal Opens | Email button opens composer | Dev |
| ✅ AI Generates | "Generate" creates personalized email | Dev |
| ✅ Edit Works | User can modify email | Dev |
| ✅ Tone Selection | Tone dropdown changes generation | Dev |
| ✅ Send Works | Email sent successfully | Dev |
| ✅ Loading States | Spinners during generation/send | Dev |
| ✅ A11y Compliant | Form accessible | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 7.1: Email Service Integration

#### Story 7.1.1: Create Email Service
**As a** developer  
**I want** email API integration  
**So that** users can generate and send emails

**Tasks:**
- [ ] **T7.1.1.1**: Create `src/services/email.ts`
  - [ ] generate(data): POST /api/email/generate
  - [ ] send(data): POST /api/email/send
  - [ ] getTones(): GET /api/email/tones
- [ ] **T7.1.1.2**: Create TypeScript types
- [ ] **T7.1.1.3**: Create hooks in `src/packlets/email/`

**Acceptance Criteria:**
- [ ] Generate returns email content
- [ ] Send returns success response

**🧪 Validation Steps:**
```bash
npm run test -- src/services/email src/packlets/email  # Tests pass
# Manual: API calls work with backend
```

**📋 Feature 7.1 Validation:**
```bash
# After completing Feature 7.1:
# Manual: Email API integration complete
```

---

### Feature 7.2: Email Composer Modal

#### Story 7.2.1: Build Email Composer
**As a** user  
**I want** to compose AI-generated emails  
**So that** I can reach out to partners professionally

**Tasks:**
- [ ] **T7.2.1.1**: Create `src/components/features/EmailComposer/EmailComposer.tsx`
- [ ] **T7.2.1.2**: Add recipient info header
- [ ] **T7.2.1.3**: Add subject input
- [ ] **T7.2.1.4**: Add email body textarea
- [ ] **T7.2.1.5**: Add tone selector dropdown
- [ ] **T7.2.1.6**: Add "Generate with AI" button
- [ ] **T7.2.1.7**: Add "Send Email" button
- [ ] **T7.2.1.8**: Style to match ai-email-composer.html

**Acceptance Criteria:**
- [ ] AI generates personalized email
- [ ] User can edit before sending
- [ ] Send button triggers email send
- [ ] Loading states for generation

**🧪 Validation Steps:**
```bash
npm run test -- EmailComposer  # Tests pass
npm run dev
# Manual: Click email button on profile → composer opens
# Manual: Click "Generate with AI" → email generated
# Manual: Edit subject/body → changes persist
# Manual: Change tone → regenerate with new tone
# Manual: Click "Send" → email sent, success toast
# A11y: Form fields accessible
# A11y: Loading states announced
```

**📋 Feature 7.2 Validation:**
```bash
# After completing Feature 7.2:
# Manual: Full email flow works end-to-end
# A11y: Modal accessibility complete
```

**🎭 Playwright E2E:** `e2e/email-composer.spec.js`
```
Tests to write after feature complete:
1. "Email composer opens from profile"
2. "AI generates personalized email content"
3. "User can edit subject and body"
4. "Tone selector changes email style"
5. "Send email shows success confirmation"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
- Wait for AI generation (may take a few seconds)
- Verify toast notification appears
```

---

## Epic 8: Processing Pipeline

> **Goal**: Show real-time AI processing status
> **Priority**: P1 (High)
> **Sprint**: 6

### 🎯 Epic 8 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Pipeline Displays | 4 stages visible | Dev |
| ✅ Progress Updates | Current stage highlighted | Dev |
| ✅ Checkmarks | Completed stages show ✓ | Dev |
| ✅ Activity Log | Real-time log entries | Dev |
| ✅ Cancel Works | Job can be cancelled | Dev |
| ✅ Error States | Failures displayed clearly | Dev |
| ✅ A11y Compliant | Progress announced | Dev |
| ✅ Stakeholder Demo | Demo to product owner | PO |

---

### Feature 8.1: Pipeline Visualization

#### Story 8.1.1: Build Pipeline Progress Component
**As a** user  
**I want** to see the AI processing pipeline  
**So that** I know what's happening with my discovery

**Tasks:**
- [ ] **T8.1.1.1**: Create `src/components/features/PipelineProgress/PipelineProgress.tsx`
- [ ] **T8.1.1.2**: Show 4 stages (Analyzer, Discovery, Scoring, Email)
- [ ] **T8.1.1.3**: Highlight current stage
- [ ] **T8.1.1.4**: Show completion checkmarks (icon + text, not color alone)
- [ ] **T8.1.1.5**: Add progress bar per stage
- [ ] **T8.1.1.6**: Style to match ai-agent-processing-pipeline.html
- [ ] **T8.1.1.7**: ♿ Add ARIA progress (WCAG 4.1.2, 1.4.1)
  - [ ] Overall progress: `role="progressbar"` with `aria-valuenow`
  - [ ] Stage status: Conveyed by text + icon, not just color
  - [ ] Stage labels linked to status

**Acceptance Criteria:**
- [ ] Current stage highlighted
- [ ] Completed stages show checkmark with text
- [ ] Animation between stages
- [ ] ♿ Screen reader announces current progress

**🧪 Validation Steps:**
```bash
npm run test -- PipelineProgress  # Tests pass
npm run dev
# Manual: 4 stages display (Analyzer, Discovery, Scoring, Email)
# Manual: Current stage highlighted with spinner
# Manual: Completed stages show ✓ icon + "Complete" text
# A11y: VoiceOver reads "Progress: 50 percent"
```

---

#### Story 8.1.2: Build Activity Log
**As a** user  
**I want** to see real-time activity  
**So that** I know the system is working

**Tasks:**
- [ ] **T8.1.2.1**: Create `src/components/composite/ActivityLog/ActivityLog.tsx`
- [ ] **T8.1.2.2**: Show timestamped log entries
- [ ] **T8.1.2.3**: Auto-scroll to latest
- [ ] **T8.1.2.4**: Color code by type (info, success, error)
  - [ ] Include icon with color for WCAG 1.4.1
- [ ] **T8.1.2.5**: ♿ Add ARIA live region (WCAG 4.1.3)
  - [ ] Container: `aria-live="polite"` `aria-relevant="additions"`
  - [ ] New entries announced to screen readers
  - [ ] `aria-label="Activity log"`

**Acceptance Criteria:**
- [ ] Logs appear in real-time
- [ ] Auto-scrolls to new entries
- [ ] Different colors for log types (with icons)
- [ ] ♿ Screen reader announces new log entries

**🧪 Validation Steps:**
```bash
npm run test -- ActivityLog  # Tests pass
npm run dev
# Manual: Log entries appear as pipeline runs
# Manual: Container auto-scrolls to latest
# Manual: Info=blue, Success=green, Error=red (with icons)
# A11y: VoiceOver announces new log entries
```

**📋 Feature 8.1 Validation:**
```bash
# After completing Feature 8.1:
# Manual: Pipeline visualization complete
# A11y: Progress and logs accessible
```

**🎭 Playwright E2E:** `e2e/pipeline.spec.js`
```
Tests to write after feature complete:
1. "Pipeline shows 4 stages with current highlighted"
2. "Completed stages show checkmark"
3. "Activity log updates in real-time"
4. "Cancel button stops job processing"
5. "Error state displays when job fails"

Use: .cursor/skills/playwright-skill/SKILL.md patterns
- Use page.waitForSelector for dynamic updates
- May need slowMo for visibility
```

---

### Feature 8.2: Pipeline Controls

#### Story 8.2.1: Implement Cancel Job
**As a** user  
**I want** to cancel a running job  
**So that** I can stop the process if needed

**Tasks:**
- [ ] **T8.2.1.1**: Add "Cancel" button to pipeline view
- [ ] **T8.2.1.2**: Connect to POST /api/jobs/{id}/cancel
- [ ] **T8.2.1.3**: Show confirmation modal
- [ ] **T8.2.1.4**: Update UI on cancellation
- [ ] **T8.2.1.5**: Show toast notification

**Acceptance Criteria:**
- [ ] Cancel stops job processing
- [ ] UI updates to cancelled state
- [ ] User gets confirmation

**🧪 Validation Steps:**
```bash
npm run test -- CancelJob  # Tests pass
npm run dev
# Manual: Click "Cancel" → confirmation modal
# Manual: Confirm → job cancelled, status updates
# Manual: Toast shows "Job cancelled"
```

**📋 Feature 8.2 Validation:**
```bash
# After completing Feature 8.2:
# Manual: Cancel functionality works
```

---

## Epic 9: Polish & Production

> **Goal**: Finalize for production deployment
> **Priority**: P2 (Medium)
> **Sprint**: 7

### 🎯 Epic 9 Validation Checklist

| Checkpoint | Validation | Owner |
|------------|------------|-------|
| ✅ Error Handling | All errors gracefully handled | Dev |
| ✅ 404/500 Pages | Error pages display | Dev |
| ✅ Bundle Optimized | < 200KB initial JS | Dev |
| ✅ Lazy Loading | Routes code-split | Dev |
| ✅ No Layout Shift | CLS < 0.1 | Dev |
| ✅ A11y Audit Pass | Zero WCAG violations | Dev |
| ✅ Lighthouse Score | Performance > 90 | Dev |
| ✅ Cross-Browser | Chrome, Firefox, Safari | QA |
| ✅ Security Review | No XSS, CSRF issues | Dev |
| ✅ Production Deploy | App live on production | DevOps |
| ✅ Stakeholder Sign-off | Final approval | PO |

---

### Feature 9.1: Error Handling

#### Story 9.1.1: Implement Global Error Handling
**Tasks:**
- [ ] Create ErrorBoundary component
- [ ] Add error pages (404, 500)
- [ ] Handle API errors gracefully
- [ ] Show user-friendly error messages

**🧪 Validation Steps:**
```bash
npm run test -- ErrorBoundary  # Tests pass
# Manual: Trigger React error → ErrorBoundary catches, shows fallback
# Manual: Navigate to /nonexistent → 404 page
# Manual: Simulate API error → user-friendly message shown
```

**📋 Feature 9.1 Validation:**
```bash
# After completing Feature 9.1:
# Manual: All error scenarios handled gracefully
# Manual: No unhandled exceptions in production
```

---

### Feature 9.2: Performance Optimization

#### Story 9.2.1: Optimize Bundle Size
**Tasks:**
- [ ] Analyze bundle with rollup-plugin-visualizer
- [ ] Ensure proper tree-shaking
- [ ] Lazy load heavy components

**🧪 Validation Steps:**
```bash
npm run build
# Open dist/stats.html → analyze bundle
# Verify no duplicate dependencies
# Verify initial JS < 200KB
```

---

#### Story 9.2.2: Add Loading States
**Tasks:**
- [ ] Add Suspense boundaries
- [ ] Add page-level loading states
- [ ] Ensure no layout shift

**🧪 Validation Steps:**
```bash
npm run build && npm run preview
# Throttle network to Slow 3G
# Navigate between pages → loading states visible
# Measure CLS with Lighthouse → should be < 0.1
```

**📋 Feature 9.2 Validation:**
```bash
# After completing Feature 9.2:
npm run build
# Verify bundle sizes acceptable
# Run Lighthouse performance audit → score > 90
```

---

### Feature 9.3: Accessibility Audit & Remediation

> ♿ **Note**: Core accessibility is built into components throughout Sprints 1-6.  
> This feature covers final validation and edge cases.

#### Story 9.3.1: Automated Accessibility Testing
**As a** developer  
**I want** automated a11y testing in CI  
**So that** regressions are caught early

**Tasks:**
- [ ] **T9.3.1.1**: Add axe-core to Vitest
  - [ ] Install `vitest-axe`
  - [ ] Create a11y test helper
- [ ] **T9.3.1.2**: Add a11y tests to key components
  - [ ] Modal, Toast, Button, Input
  - [ ] ProfileCard, ProfileDetail
  - [ ] Pipeline progress
- [ ] **T9.3.1.3**: Configure CI to fail on a11y violations

**Acceptance Criteria:**
- [ ] All component tests include a11y checks
- [ ] CI reports a11y issues

**🧪 Validation Steps:**
```bash
npm run test  # All tests pass including a11y
# Verify CI pipeline includes a11y checks
# Intentionally add a11y violation → CI fails
```

---

#### Story 9.3.2: Manual Accessibility Audit
**As a** QA tester  
**I want** to verify WCAG compliance  
**So that** the app is accessible to all users

**Tasks:**
- [ ] **T9.3.2.1**: Run axe DevTools on each page
- [ ] **T9.3.2.2**: Run WAVE browser extension
- [ ] **T9.3.2.3**: Keyboard-only navigation test
  - [ ] All interactive elements reachable
  - [ ] Focus order logical
  - [ ] No keyboard traps
- [ ] **T9.3.2.4**: Screen reader testing
  - [ ] VoiceOver (macOS)
  - [ ] NVDA (Windows) if available
- [ ] **T9.3.2.5**: High contrast mode testing
- [ ] **T9.3.2.6**: 200% zoom testing
- [ ] **T9.3.2.7**: Document and fix any issues

**Acceptance Criteria:**
- [ ] Zero Level A violations
- [ ] Zero Level AA violations
- [ ] Audit report documented

**🧪 Validation Steps:**
```bash
# For each page:
# 1. Run axe DevTools → zero violations
# 2. Run WAVE extension → zero errors
# 3. Keyboard-only navigation test → all elements reachable
# 4. VoiceOver test → all content announced
# 5. 200% zoom test → no horizontal scroll
# Document results in WCAG_AUDIT_REPORT.md
```

---

#### Story 9.3.3: Reduced Motion Support
**As a** user with vestibular disorders  
**I want** reduced animations  
**So that** the interface doesn't cause discomfort

**Tasks:**
- [ ] **T9.3.3.1**: Add `prefers-reduced-motion` media query
- [ ] **T9.3.3.2**: Disable animations when preference set
- [ ] **T9.3.3.3**: Use `motion-safe:` Tailwind prefix

**Acceptance Criteria:**
- [ ] Animations disabled when system preference set
- [ ] Core functionality unaffected

**🧪 Validation Steps:**
```bash
# macOS: System Preferences → Accessibility → Display → Reduce motion
# Open app → animations should be disabled
# Verify all functionality still works without animations
```

**📋 Feature 9.3 Validation:**
```bash
# After completing Feature 9.3:
# Full WCAG 2.2 Level AA compliance verified
# Audit report complete
```

---

### Feature 9.4: Production Build

#### Story 9.4.1: Prepare for Deployment
**Tasks:**
- [ ] Configure production environment variables
- [ ] Build and test production bundle
- [ ] Configure error tracking (optional)
- [ ] Set up analytics (optional)

**🧪 Validation Steps:**
```bash
# Create production .env with real values
npm run build
npm run preview
# Manual: Test all flows with production backend
# Manual: Verify no console errors/warnings
# Run Lighthouse: Performance > 90, A11y > 90, Best Practices > 90
# Deploy to production URL
# Smoke test all critical paths
```

**📋 Feature 9.4 Validation:**
```bash
# After completing Feature 9.4:
# Production build deployed and working
# All critical paths verified
# Stakeholder sign-off obtained
```

---

## Definition of Done

### Story Level
- [ ] Code reviewed and approved
- [ ] Unit tests written and passing
- [ ] Integration tests passing (if applicable)
- [ ] Component matches design file
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] ♿ **Accessibility requirements met:**
  - [ ] Keyboard navigable (Tab, Enter, Space, Escape as appropriate)
  - [ ] Focus visible with 3px ring on keyboard navigation
  - [ ] Screen reader announces component purpose
  - [ ] Color contrast meets 4.5:1 (text) / 3:1 (UI elements)
  - [ ] Information not conveyed by color alone
  - [ ] All images have appropriate alt text
  - [ ] All icon buttons have aria-label

### Feature Level
- [ ] All stories complete
- [ ] Feature demo to stakeholder
- [ ] Documentation updated
- [ ] ♿ axe-core audit passes with no violations
- [ ] 🎭 **Playwright E2E tests written and passing**
  - [ ] Tests saved to `e2e/{feature-name}.spec.js`
  - [ ] Uses `.cursor/skills/playwright-skill` patterns
  - [ ] Runs with visible browser (headless: false)
  - [ ] Screenshots saved to /tmp for debugging

### Epic Level
- [ ] All features complete
- [ ] 🎭 **Epic journey E2E test passing**
  - [ ] Full user flow from start to finish
  - [ ] Responsive viewport testing included
- [ ] Performance benchmarks met
- [ ] ♿ WCAG 2.2 Level AA compliant
- [ ] Ready for production

---

## Acceptance Criteria Template

```markdown
**Given** [context/precondition]
**When** [action/trigger]
**Then** [expected outcome]
**And** [additional outcome]
```

### Example

```markdown
**Given** a user is on the login page
**When** they enter valid credentials and click Sign In
**Then** they are redirected to the dashboard
**And** a success toast is shown
```

---

## Story Point Reference

| Points | Effort | Example |
|--------|--------|---------|
| 1 | 1-2 hours | Simple component, single file |
| 2 | 2-4 hours | Component with tests |
| 3 | 4-8 hours | Feature with API integration |
| 5 | 1-2 days | Complex feature, multiple components |
| 8 | 2-3 days | Epic-level feature |
| 13 | 1 week | Major feature with unknowns |

---

## Sprint Capacity Planning

| Sprint | Velocity (Story Points) | Focus |
|--------|------------------------|-------|
| Sprint 1 | 30-40 | Epic 1 (Foundation) |
| Sprint 2 | 30-40 | Epic 1 + Epic 2 (Auth) |
| Sprint 3 | 30-40 | Epic 3 + Epic 4 (Sessions) |
| Sprint 4 | 30-40 | Epic 5 (Dashboard) |
| Sprint 5 | 30-40 | Epic 6 + Epic 7 (Detail + Email) |
| Sprint 6 | 30-40 | Epic 8 (Pipeline) |
| Sprint 7 | 20-30 | Epic 9 (Polish) |

---

## Accessibility Requirements

> ♿ This section summarizes WCAG 2.2 Level AA requirements integrated throughout the guide.

### Critical (Level A) - Must Fix

| Requirement | WCAG | Where Addressed |
|-------------|------|-----------------|
| Alt text on images | 1.1.1 | Story 5.2.1 (ProfileCard) |
| Skip link | 2.4.1 | Story 1.5.2 |
| Keyboard accessibility | 2.1.1 | All interactive components |
| Focus trap in modals | 2.1.2 | Story 1.3.5 (Modal) |
| Color not sole indicator | 1.4.1 | Story 1.3.4 (Badge), 8.1.1 (Pipeline) |
| Focus visible | 2.4.7 | Story 1.5.1 |
| ARIA live regions | 4.1.3 | Story 1.3.6 (Toast), 8.1.2 (ActivityLog) |
| Icon button labels | 2.5.3 | Story 1.3.1, 5.2.1 |
| Progress bar ARIA | 4.1.2 | Story 5.2.2, 6.1.2, 8.1.1 |
| Menu/Tab ARIA | 4.1.2 | Story 2.3.1, 5.3.1 |

### Major (Level AA) - Should Fix

| Requirement | WCAG | Where Addressed |
|-------------|------|-----------------|
| Color contrast 4.5:1 | 1.4.3 | Story 1.1.2 |
| Non-text contrast 3:1 | 1.4.11 | Story 1.1.2, 1.3.2 |
| Autocomplete attributes | 1.3.5 | Story 2.2.1 |
| Focus not obscured | 2.4.11 | Story 1.5.1 |
| Target size 24×24px | 2.5.8 | Story 1.3.1, 1.3.6 |
| Error identification | 3.3.1 | Story 1.3.2, 2.2.1 |
| Reduced motion | 2.3.3 | Story 9.3.3 |

### Testing Tools

| Tool | Purpose |
|------|---------|
| axe DevTools | Automated page audit |
| WAVE | Browser extension audit |
| vitest-axe | CI integration |
| VoiceOver | Screen reader (macOS) |
| NVDA | Screen reader (Windows) |

### Reference

- [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WCAG Audit Report](../../designs/WCAG_AUDIT_REPORT.md)

---

## Playwright E2E Test Organization

```
e2e/
├── auth.spec.js              # Epic 2: Login, signup, logout
├── sessions.spec.js          # Epic 3: Session CRUD
├── discovery-config.spec.js  # Epic 4: Configuration flow
├── dashboard.spec.js         # Epic 5: Dashboard features
├── profile-detail.spec.js    # Epic 6: Profile modal
├── email-composer.spec.js    # Epic 7: Email flow
├── pipeline.spec.js          # Epic 8: Processing pipeline
├── smoke.spec.js             # Quick smoke tests for CI
└── journeys/
    ├── full-discovery.spec.js    # Complete discovery journey
    └── responsive.spec.js        # Viewport testing
```

### Playwright Skill Reference

All E2E tests should follow patterns in `.cursor/skills/playwright-skill/SKILL.md`:

1. **Auto-detect dev servers** before running tests
2. **Write tests to /tmp** for auto-cleanup
3. **Use visible browser** (headless: false) by default
4. **Parameterize URLs** at top of each script
5. **Use helpers** for common actions (safeClick, safeType)
6. **Take screenshots** for debugging failures

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture
- [TECH_STACK.md](./TECH_STACK.md) - Technology decisions
- [GAPS_TODO.md](./GAPS_TODO.md) - Implementation gaps
- [../../.cursor/skills/playwright-skill/SKILL.md](../../.cursor/skills/playwright-skill/SKILL.md) - Playwright automation skill
- [../../designs/](../../designs/) - Design HTML files
- [../../designs/WCAG_AUDIT_REPORT.md](../../designs/WCAG_AUDIT_REPORT.md) - Accessibility audit

---

*Last updated: February 2026*  
*Version: 1.3 - Validated against frontend docs, added missing components/services*
