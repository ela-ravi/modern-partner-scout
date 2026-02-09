# PartnerScout AI - Frontend Agile Implementation Plan

> **EPIC 5**: Frontend Application Development  
> **Approach**: Incremental, Component-Driven Development with Phase-by-Phase Playwright Validation  
> **Design Reference**: [Frontend Design Plan](frontend_design_plan.md)  
> **Functional Reference**: [Frontend Functionalities](../Frontend_Functionalities.md)  
> **Status**: Ready for Implementation  

---

## Agile Hierarchy Legend

| Level | Format | Description |
|-------|--------|-------------|
| **Epic** | EPIC-5 | Frontend Application Development |
| **Feature** | FEAT-5.X | Distinct functionality area (e.g., Auth, Dashboard) |
| **Story** | STORY-5.X.Y | User-facing deliverable |
| **Task** | TASK-5.X.Y.Z | Technical implementation work |
| **Subtask** | SUB-5.X.Y.Z.N | Granular work items (CSS, Logic, Integration) |
| **Testing** | TEST-5.X.Y.P | Playwright test specification for validation |

---

## FEAT-5.1: Foundation, Design System & Testing Setup

**Description**: Establish the visual foundation, build reusable UI components based on the Apple-inspired minimalism theme, and initialize the automated testing suite.

### STORY-5.1.1: Core Design System Setup
**As a** developer, **I want** a centralized design system and testing framework **so that** the UI is consistent, fast to build, and automatically validated.

#### TASK-5.1.1.1: Global Styles & CSS Variables
- **SUB-5.1.1.1.1**: Define Color Palette (Primary, Brand, Text, Success/Warning/Error) in `index.css`.
- **SUB-5.1.1.1.2**: Implement Typography system (Inter font, type scale).
- **SUB-5.1.1.1.3**: Set up Spacing system (4px base unit).
- **SUB-5.1.1.1.4**: Define Border Radius and Shadow tokens.
- **SUB-5.1.1.1.5**: Implement core animations (fadeIn, slideUp, shimmer, spin).

#### TASK-5.1.1.2: Atomic Component Library
- **SUB-5.1.1.2.1**: **Buttons**: Implement Primary, Secondary, Tertiary, and Icon variants.
- **SUB-5.1.1.2.2**: **Inputs**: Implement standard text input with focus, error, and success states.
- **SUB-5.1.1.2.3**: **Badges**: Create Status Badges (Processing, Done) and Authenticity Badges (Genuine, Suspicious, Fake).
- **SUB-5.1.1.2.4**: **Progress Indicators**: Create Linear Progress Bar and Circular Score Ring.
- **SUB-5.1.1.2.5**: **Skeleton Loaders**: Implement card and text placeholders.

#### TASK-5.1.1.3: Testing Framework Initialization
- **SUB-5.1.1.3.1**: Initialize Playwright in the `frontend/` directory.
- **SUB-5.1.1.3.2**: Configure Playwright for multiple browsers (Chromium, WebKit, Firefox).
- **SUB-5.1.1.3.3**: Set up test environment variables and global tear-up/down logic.
- **SUB-5.1.1.3.4**: Implement `test-utils` for common Playwright actions (login, navigation).

#### TEST-5.1.1.P: Design System Validation
- Verify all CSS variables are correctly injected into the DOM.
- Verify basic Button and Input components render with correct Apple-inspired styles.
- Verify Storybook-style view (if used) or a Test Page renders all atomic components correctly.

---

## FEAT-5.2: User Authentication & Onboarding

**Description**: Implement secure login and signup flows using Supabase Auth, validated by automated E2E tests.

### STORY-5.2.1: Authentication Pages
**As a** new or returning user, **I want** to securely access my account **so that** I can manage my discovery sessions.

#### TASK-5.2.1.1: Login/Signup Page Implementation
- **SUB-5.2.1.1.1**: Build centered auth card layout on `apple-gray` background.
- **SUB-5.2.1.1.2**: Implement "Sign In" and "Sign Up" tabs within the card.
- **SUB-5.2.1.1.3**: Integrate email/password forms with validation feedback.
- **SUB-5.2.1.1.4**: Implement Social Login buttons (Google, GitHub) using Supabase Auth.
- **SUB-5.2.1.1.5**: Implement logic for persistent sessions and redirection after login.

#### TEST-5.2.1.P: Auth Flow Validation (Playwright)
- **TEST-5.2.1.P.1**: Verify unauthorized users are redirected to `/login` when accessing `/sessions`.
- **TEST-5.2.1.P.2**: Verify successful login redirects to `/sessions`.
- **TEST-5.2.1.P.3**: Verify form validation errors appear for invalid email/password formats.

---

## FEAT-5.3: Discovery Session Management (Dashboard & List)

**Description**: Management of multiple discovery sessions with real-time status tracking.

### STORY-5.3.1: Session Management Hub
**As a** user, **I want** to see all my discovery sessions **so that** I can track progress and access results.

#### TASK-5.3.1.1: Session List UI & Logic
- **SUB-5.3.1.1.1**: Build the `/sessions` page with 4-column Global Stats Summary.
- **SUB-5.3.1.1.2**: Implement `SessionCard` with status badges, progress bars, and metadata.
- **SUB-5.3.1.1.3**: Implement Delete and Retry handlers using repository pattern.
- **SUB-5.3.1.1.4**: Implement Status Badge logic (Pending, Analyzing, Discovering, Scoring, Completed, Failed).

#### TASK-5.3.1.2: Empty Dashboard State
- **SUB-5.3.1.2.1**: Build `EmptyState` component for new users without sessions.
- **SUB-5.3.1.2.2**: Add "Create Your First Session" CTA with helpful onboarding text.

#### TEST-5.3.1.P: Session Hub Validation (Playwright)
- **TEST-5.3.1.P.1**: Verify empty state appears for users with zero sessions.
- **TEST-5.3.1.P.2**: Verify session list displays correct metadata for existing sessions.
- **TEST-5.3.1.P.3**: Verify "Delete" action removes the session and updates the UI.

---

## FEAT-5.4: Discovery Dashboard & Partner View

**Description**: Main workspace for viewing discovered influencers and boutique partners with real-time updates.

### STORY-5.4.1: Live Partner Feed
**As a** user, **I want** to see discovered profiles appearing in real-time **so that** I can evaluate them immediately.

#### TASK-5.4.1.1: Dashboard Layout & Analytics
- **SUB-5.4.1.1.1**: Build `/dashboard/:jobId` page with dynamic 4-column Stats Grid (+12 today indicators).
- **SUB-5.4.1.1.2**: Implement Tab Navigation (All, New, Processing, Done).
- **SUB-5.4.1.1.3**: Add Sort logic (Final Score, Followers Count, Engagement).

#### TASK-5.4.1.2: Profile Grid & Realtime Synergy
- **SUB-5.4.1.2.1**: Build high-fidelity `ProfileCard` (Cover image, Round avatars, Score Ring).
- **SUB-5.4.1.2.2**: Implement Authenticity Verdict logic (Genuine, Suspicious, Fake) based on `follower_quality`.
- **SUB-5.4.1.2.3**: Set up Supabase Realtime subscription to handle card status transitions.
- **SUB-5.4.1.2.4**: Implement card "NEW" and "EMAIL" status markers.

#### TEST-5.4.1.P: Dashboard & Realtime Validation (Playwright)
- **TEST-5.4.1.P.1**: Verify profile filtering by score and status tabs.
- **TEST-5.4.1.P.2**: Mock a Realtime event (status: processing -> done) and verify card update without refresh.
- **TEST-5.4.1.P.3**: Verify Authenticity badge correctly corresponds to the score range.

---

## FEAT-5.5: Profile Detail View & AI Insights

**Description**: Detailed drill-down into a specific profile's data and AI-generated scores.

### STORY-5.5.1: Deep Analysis View
**As a** user, **I want** a detailed breakdown of why a profile was scored a certain way **so that** I can trust the AI's recommendation.

#### TASK-5.5.1.1: Detailed Modal Implementation
- **SUB-5.5.1.1.1**: Build `ProfileDetailModal` with Apple-inspired grid (Bio/Stats/Posts vs Score/Rec/Contact).
- **SUB-5.5.1.1.2**: Render Stats Grid (Followers Count, Following Count, Engagement, Posts).
- **SUB-5.5.1.1.3**: Implement `RecentPostsGrid` using the `recent_posts` JSON data.
- **SUB-5.5.1.1.4**: Implement Keyword Tag extraction logic from `reasoning`.

#### TASK-5.5.1.2: AI Scoring & Recommendation
- **SUB-5.5.1.2.1**: Implement 6-Dimension Score Breakdown (Linear Progress Bars).
- **SUB-5.5.1.2.2**: Render AI Recommendation section (Verdict + Summary + Recommendation).
- **SUB-5.5.1.2.3**: Build Contact section with Email source indicators and "Compose" button.

#### TEST-5.5.1.P: Profile Insight Validation (Playwright)
- **TEST-5.5.1.P.1**: Verify modal opens on card click and displays the correct partner's data.
- **TEST-5.5.1.P.2**: Verify all 6 score dimensions are visible with correct numerical values.
- **TEST-5.5.1.P.3**: Verify recent posts grid displays images (or placeholders if URL invalid).

---

## FEAT-5.6: Discovery Engine Flow (Multi-step)

**Description**: The "Launch" workflow for creating and configuring new discovery sessions.

### STORY-5.6.1: Workflow Initiation
**As a** user, **I want** a guided process to set my discovery parameters **so that** I find the right partners.

#### TASK-5.6.1.1: Multi-Step Configuration UI
- **SUB-5.6.1.1.1**: Build Step 1 Form (Brand Description, Reference Profile tag input).
- **SUB-5.6.1.1.2**: Implement Step 1 Advanced Filters (Follower Range Presets, Max Limit, Min Score).
- **SUB-5.6.1.1.3**: Build Step 2 Review Summary with configuration validation.
- **SUB-5.6.1.1.4**: Implement "Launch" logic: Call `/api/jobs` then `/api/jobs/{id}/start`.

#### TEST-5.6.1.P: Engine Workflow Validation (Playwright)
- **TEST-5.6.1.P.1**: Verify "Next" is disabled until required description and 2+ URLs are provided.
- **TEST-5.6.1.P.2**: Verify Step 2 correctly reflects the settings entered in Step 1.
- **TEST-5.6.1.P.3**: Verify successful launch redirects to the session dashboard.

---

## FEAT-5.7: AI Email Composer & Outreach

**Description**: drafting and sending (mock) outreach emails based on profile data.

### STORY-5.7.1: Personalized Outreach flow
**As a** user, **I want** an AI-drafted email personalized to each profile **so that** I can reach out faster.

#### TASK-5.7.1.1: Email Composer Implementation
- **SUB-5.7.1.1.1**: Build `EmailComposer` modal with tone selection (Friendly, Professional, Direct).
- **SUB-5.7.1.1.2**: Implement "Regenerate" handler and editable email fields.
- **SUB-5.7.1.1.3**: Implement "Send Email" mock action with success toast.

#### TEST-5.7.1.P: Email Flow Validation (Playwright)
- **TEST-5.7.1.P.1**: Verify changing tone updates the email content (mocked API).
- **TEST-5.7.1.P.2**: Verify success toast appears after "sending".

---

## FEAT-5.8: Error Handling & System Feedback

**Description**: Implementation of robust error states and notifications.

### STORY-5.8.1: Graceful System Failures
**As a** user, **I want** clear feedback when errors occur **so that** I know how to resolve them.

#### TASK-5.8.1.1: Notification & Modal States
- **SUB-5.8.1.1.1**: Build `DailyLimitModal` for quota exceeded errors.
- **SUB-5.8.1.1.2**: Build `ServiceUnavailableModal` for maintenance/API down states.
- **SUB-5.8.1.1.3**: Implement Global Toast Notification system.

#### TEST-5.8.1.P: Error State Validation (Playwright)
- **TEST-5.8.1.P.1**: Force a 429 Error (via mock) and verify `DailyLimitModal` appears.
- **TEST-5.8.1.P.2**: Force a 500 Error and verify Error Toast appears.

---

## FEAT-5.9: Implementation Polish & Performance

**Description**: Finalizing the "Apple-level" feel and optimizing performance.

### STORY-5.9.1: UX Polish
- **SUB-5.9.1.1.1**: Implement staggered animations for grid items.
- **SUB-5.9.1.1.2**: Conduct Responsive Audit (Mobile/Tablet/Desktop).
- **SUB-5.9.1.1.3**: Add subtle hover micro-interactions to all navigational icons.
- **SUB-5.9.1.1.4**: Perform complete cross-browser testing.

#### TEST-5.9.1.P: Final Quality Audit (Playwright)
- **TEST-5.9.1.P.1**: Visual Regression Tests to ensure no style regressions.
- **TEST-5.9.1.P.2**: Accessibility (Axe) audit via Playwright-axe.
