# PartnerScout AI - Frontend Design Plan

> **Version**: 1.0  
> **Last Updated**: February 7, 2026  
> **Design Philosophy**: Apple-inspired minimalism with premium aesthetics

---

## Table of Contents

1. [Design System](#design-system)
2. [Page Specifications](#page-specifications)
3. [Component Library](#component-library)
4. [Interaction Patterns](#interaction-patterns)
5. [Implementation Guidelines](#implementation-guidelines)

---

## Design System

### Color Palette

#### Primary Colors
```css
--apple-bg: #fbfbfd          /* Main background */
--apple-card: #ffffff        /* Card backgrounds */
--apple-gray: #f5f5f7        /* Secondary backgrounds */
--apple-border: rgba(0, 0, 0, 0.06)  /* Subtle borders */
```

#### Brand Colors
```css
--apple-blue: #0071e3        /* Primary actions, links */
--apple-blue-hover: #0077ed  /* Hover state for blue */
--apple-green: #34c759       /* Success, positive states */
--apple-orange: #ff9500      /* Warnings, highlights */
--apple-red: #ff3b30         /* Errors, destructive actions */
--apple-purple: #af52de      /* Accents, special indicators */
```

#### Text Colors
```css
--apple-text: #1d1d1f               /* Primary text */
--apple-text-secondary: #86868b    /* Secondary text */
--apple-text-tertiary: #aeaeb2     /* Tertiary text, placeholders */
```

### Typography

**Font Family**: Inter (with fallback to system fonts)
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

**Font Smoothing**:
```css
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale;
```

#### Type Scale

| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| Display | 4xl (36px) | 600 | 1.1 | Page titles |
| H1 | 3xl (30px) | 600 | 1.2 | Section headers |
| H2 | 2xl (24px) | 600 | 1.3 | Subsection headers |
| H3 | xl (20px) | 600 | 1.4 | Card titles |
| Body | base (16px) | 400 | 1.5 | Body text |
| Small | sm (14px) | 400/500 | 1.4 | Labels, metadata |
| Tiny | xs (12px) | 500/600 | 1.3 | Badges, captions |

### Spacing System

**Base Unit**: 4px

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Small gaps |
| md | 12px | Default gaps |
| lg | 16px | Section spacing |
| xl | 24px | Large spacing |
| 2xl | 32px | Extra large spacing |
| 3xl | 48px | Page sections |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| sm | 8px | Small elements |
| md | 12px | Inputs, buttons |
| lg | 16px | Cards |
| xl | 20px | Modals, large cards |
| 2xl | 24px | Hero sections |
| full | 980px | Pills, rounded buttons |

### Shadows

```css
/* Card Shadow */
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1);

/* Card Hover Shadow */
box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1);

/* Modal Shadow */
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Dropdown Shadow */
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.1);
```

### Animations

#### Keyframes

```css
/* Fade In */
@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Slide Down */
@keyframes slideDown {
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
}

/* Scale In */
@keyframes scaleIn {
  0% { opacity: 0; transform: scale(0.96); }
  100% { opacity: 1; transform: scale(1); }
}

/* Toast In */
@keyframes toastIn {
  0% { opacity: 0; transform: translateX(100%); }
  100% { opacity: 1; transform: translateX(0); }
}

/* Shimmer (Skeleton Loader) */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Spin (Loading) */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

#### Animation Durations

- **Fast**: 0.2s - Micro-interactions (hover, focus)
- **Normal**: 0.3s - Standard transitions
- **Slow**: 0.4-0.6s - Page transitions, modals

#### Easing Functions

- **Standard**: `ease` - Default transitions
- **Smooth**: `cubic-bezier(0.16, 1, 0.3, 1)` - Smooth, natural motion
- **Ease Out**: `ease-out` - Deceleration

---

## Page Specifications

### 1. Login Page

**Route**: `/login`  
**Layout**: Centered authentication card

#### Structure
- **Background**: `apple-gray` (#f5f5f7)
- **Container**: Max-width 448px, centered
- **Card**: White background, rounded-2xl (20px), shadow

#### Elements

1. **Logo Section**
   - Logo icon: 48px × 48px, rounded-2xl, gradient (blue)
   - Brand name: "PartnerScout", font-semibold, text-2xl
   - Welcome message: "Welcome back", text-3xl, font-semibold
   - Subtitle: Secondary text color

2. **Tab Switcher**
   - Background: `apple-gray`
   - Active tab: White background with shadow
   - Tabs: "Sign In" / "Sign Up"

3. **Form Fields**
   - Email input with label
   - Password input with show/hide toggle
   - "Forgot password?" link (blue)
   - "Keep me signed in" checkbox

4. **Submit Button**
   - Full width, `apple-button` style
   - Text: "Sign In"

5. **Social Login**
   - Divider with "or continue with" text
   - Google and GitHub buttons (2-column grid)

6. **Footer**
   - Terms and Privacy Policy links

#### States
- **Error**: Red border on inputs, error message with icon
- **Loading**: Disabled button with spinner

---

### 2. Session List Page

**Route**: `/sessions`  
**Layout**: Full-width with header and content area

#### Header
- Sticky header with backdrop blur
- Logo and navigation (Dashboard, Sessions, Analytics)
- Search, notifications, user menu

#### Content Structure

1. **Page Header**
   - Title: "Discovery Sessions", text-4xl
   - Subtitle: "View and manage all your discovery campaigns"
   - "New Session" button (primary)

2. **Stats Summary** (4-column grid)
   - Total Sessions
   - Active
   - Completed
   - Total Profiles

3. **Filter Tabs**
   - All, Active, Completed, Failed
   - Show count badges

4. **Session Cards** (Vertical stack)
   Each card contains:
   - Icon (48px, colored background)
   - Session name and status badge
   - Metadata (created date, last updated)
   - Stats (profiles discovered, scored, high matches)
   - Action buttons (View Details, More options)
   - Progress bar (for active sessions)

#### Session Status Badges

| Status | Background | Text Color |
|--------|-----------|-----------|
| Pending | `#f5f5f7` | `#86868b` |
| Analyzing | `rgba(175, 82, 222, 0.1)` | `#af52de` |
| Discovering | `rgba(0, 113, 227, 0.1)` | `#0071e3` |
| Scoring | `rgba(255, 149, 0, 0.1)` | `#ff9500` |
| Completed | `rgba(52, 199, 89, 0.1)` | `#34c759` |
| Failed | `rgba(255, 59, 48, 0.1)` | `#ff3b30` |

---

### 3. Main Discovery Dashboard

**Route**: `/dashboard/:jobId`  
**Layout**: Full-width with header and grid layout

#### Header
- Same as Session List Page
- Session selector dropdown (shows active session)

#### Content Structure

1. **Page Header**
   - Title: "Discovery Dashboard", text-4xl
   - Subtitle: Profile count and high matches
   - Filters and "New Discovery" buttons

2. **Stats Grid** (4-column)
   - Total Discovered (with +12 today indicator)
   - High Match (percentage of total)
   - Emails Found (extraction rate)
   - Avg Score (trend indicator)

3. **Tab Navigation**
   - All, New, Processing, Done (with counts)
   - Sort dropdown (Score, Date, Engagement)

4. **Partner Grid** (3-column responsive)
   Each profile card:
   - Cover image (128px height, gradient overlay)
   - Badge (NEW, EMAIL, TOP MATCH)
   - Profile image (56px, rounded-xl, overlapping cover)
   - Name and username
   - Bio (2-line clamp)
   - Stats: Followers, Engagement
   - Match score (circular progress ring)
   - Actions: View Profile, Email, Bookmark

#### Profile Card Variants

- **New Profile**: Green "NEW" badge
- **Email Found**: Blue "EMAIL" badge
- **Top Match**: Orange "★ TOP" badge, orange score color

---

### 4. Profile Detail Modal

**Route**: Modal overlay (not a route)  
**Trigger**: Click "View Profile" on any profile card

#### Structure

- **Backdrop**: `rgba(0, 0, 0, 0.4)` with blur(8px)
- **Modal**: Max-width 896px, max-height 90vh, rounded-2xl

#### Sections

1. **Header with Cover** (160px height)
   - Cover image with overlay
   - Close button (top-right)
   - Badge (top-left)
   - Profile image (80px, overlapping)
   - Name, username, "View on Instagram" button

2. **Left Column** (2/3 width)
   - **Bio Section**: Gray background card
   - **Stats Grid**: 4 columns (Followers, Following, Engagement, Posts)
   - **AI Analysis**: Description + keyword tags
   - **Recent Content**: 3-column image grid

3. **Right Column** (1/3 width)
   - **Match Score**: Large circular indicator (112px)
   - **Score Breakdown**: 4 metrics with progress bars
     - Aesthetic Match
     - Engagement Quality
     - Content Alignment
     - Audience Fit
   - **AI Recommendation**: Green-tinted card
   - **Contact Info**: Email with source badge
   - **Actions**: Compose Email (primary), Save, Skip

#### Score Breakdown Colors

- Progress bars: Blue gradient (`#0071e3` to `#00a2ff`)
- Background: `#f5f5f7`

---

### 5. Discovery Engine - Step 1 (Configure)

**Route**: `/discovery/new` or `/discovery/:id/edit`  
**Layout**: Centered form, max-width 768px

#### Header
- Logo and close button
- **Stepper**: 2 steps (Configure, Launch)
  - Active step: Blue circle with number
  - Upcoming: Gray circle

#### Form Sections

1. **Campaign Name**
   - Text input, full width

2. **Brand Description** (Optional)
   - Textarea, 3 rows
   - Helper text

3. **Reference Instagram Profiles** (Required: 2-10)
   - Tag input with removable chips
   - Blue background tags with close icon

4. **Target Keywords & Hashtags**
   - Tag input similar to profiles

5. **Discovery Parameters** (2-column grid)
   - **Profiles to Discover**: Slider (10-100)
   - **Minimum Score**: Slider (50%-95%)

6. **Follower Range**
   - Min/Max text inputs
   - Preset buttons: Nano, Micro, Mid-tier, Macro

7. **Advanced Options**
   - Collapsible section (expandable)

#### Footer Actions
- Cancel (secondary)
- Continue (primary with arrow)

---

### 6. Discovery Engine - Step 2 (Launch)

**Route**: `/discovery/new/launch`  
**Layout**: Same as Step 1

#### Content

1. **Review Summary**
   - Campaign name
   - Reference profiles count
   - Keywords count
   - Parameters summary

2. **Estimated Results**
   - Expected profiles
   - Estimated time
   - Credit cost

3. **Launch Options**
   - Start immediately / Schedule
   - Email notifications toggle

#### Footer Actions
- Back (secondary)
- Launch Discovery (primary)

---

### 7. Empty Dashboard State

**Route**: `/dashboard` (when no sessions exist)  
**Layout**: Centered empty state

#### Structure

- Icon: 64px, gray circle background
- Title: "No Discovery Sessions Yet"
- Description: Helpful text
- "Create Your First Session" button (primary)
- Optional: Quick start guide or video

---

## Component Library

### Buttons

#### Primary Button (`.apple-button`)
```css
background: #0071e3;
color: white;
border-radius: 980px;
font-weight: 500;
padding: 12px 24px;
transition: all 0.2s ease;

&:hover {
  background: #0077ed;
}
```

#### Secondary Button (`.apple-button-secondary`)
```css
background: rgba(0, 113, 227, 0.1);
color: #0071e3;
border-radius: 980px;
font-weight: 500;
padding: 12px 24px;
transition: all 0.2s ease;

&:hover {
  background: rgba(0, 113, 227, 0.15);
}
```

#### Tertiary Button
```css
background: #f5f5f7;
color: #1d1d1f;
border-radius: 980px;
font-weight: 500;
padding: 12px 24px;

&:hover {
  background: #ebebeb;
}
```

#### Icon Button
```css
padding: 8px;
border-radius: 50%;
background: transparent;

&:hover {
  background: #f5f5f7;
}
```

### Inputs

#### Text Input (`.apple-input`)
```css
background: #ffffff;
border: 1px solid rgba(0, 0, 0, 0.1);
border-radius: 12px;
padding: 14px 16px;
color: #1d1d1f;
transition: all 0.2s ease;

&:focus {
  border-color: #0071e3;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
  outline: none;
}

&::placeholder {
  color: #aeaeb2;
}

&.error {
  border-color: #ff3b30;
  box-shadow: 0 0 0 3px rgba(255, 59, 48, 0.1);
}

&.success {
  border-color: #34c759;
  box-shadow: 0 0 0 3px rgba(52, 199, 89, 0.1);
}
```

### Cards

#### Standard Card (`.apple-card`)
```css
background: #ffffff;
border-radius: 18px;
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1);
transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);

&:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1);
}
```

#### Session Card
```css
background: #ffffff;
border-radius: 16px;
border: 1px solid rgba(0, 0, 0, 0.04);
padding: 24px;
transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);

&:hover {
  border-color: rgba(0, 113, 227, 0.2);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}
```

#### Section Card (`.section-card`)
```css
background: #f5f5f7;
border-radius: 14px;
padding: 20px;
```

### Badges

#### Status Badge
```css
font-size: 11px;
font-weight: 600;
letter-spacing: 0.02em;
padding: 4px 10px;
border-radius: 980px;
```

#### Tag/Chip
```css
display: inline-flex;
align-items: center;
gap: 6px;
padding: 6px 12px;
background: rgba(0, 113, 227, 0.08);
border-radius: 980px;
font-size: 14px;
font-weight: 500;
color: #0071e3;
```

### Modals

#### Modal Backdrop
```css
background: rgba(0, 0, 0, 0.4);
backdrop-filter: blur(8px);
position: fixed;
inset: 0;
z-index: 50;
```

#### Modal Content
```css
background: #ffffff;
border-radius: 20px;
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
max-width: 896px;
max-height: 90vh;
overflow: hidden;
```

### Dropdowns

#### User Dropdown
```css
background: #ffffff;
border-radius: 14px;
box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.1);
min-width: 220px;
padding: 8px 0;
```

#### Dropdown Item
```css
display: flex;
align-items: center;
gap: 12px;
padding: 10px 16px;
color: #1d1d1f;
font-size: 14px;
transition: background 0.15s ease;

&:hover {
  background: #f5f5f7;
}

&.danger {
  color: #ff3b30;
}
```

### Toast Notifications

#### Toast Container
```css
position: fixed;
top: 24px;
right: 24px;
z-index: 100;
display: flex;
flex-direction: column;
gap: 12px;
```

#### Toast
```css
background: #ffffff;
border-radius: 14px;
box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.1);
padding: 14px 18px;
display: flex;
align-items: flex-start;
gap: 12px;
min-width: 320px;
max-width: 420px;
animation: toastIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
```

#### Toast Variants
- **Success**: `border-left: 4px solid #34c759`
- **Error**: `border-left: 4px solid #ff3b30`
- **Warning**: `border-left: 4px solid #ff9500`
- **Info**: `border-left: 4px solid #0071e3`

### Loading States

#### Spinner
```css
width: 24px;
height: 24px;
border: 3px solid #f5f5f7;
border-top-color: #0071e3;
border-radius: 50%;
animation: spin 1s linear infinite;
```

#### Skeleton Loader
```css
background: linear-gradient(90deg, #f5f5f7 25%, #ebebeb 50%, #f5f5f7 75%);
background-size: 200% 100%;
animation: shimmer 1.5s infinite;
border-radius: 8px;
```

### Progress Indicators

#### Circular Score Ring
```css
background: conic-gradient(
  from 0deg,
  #0071e3 0%,
  #0071e3 var(--score),
  #f5f5f7 var(--score),
  #f5f5f7 100%
);
border-radius: 50%;
padding: 3px;
```

#### Linear Progress Bar
```css
.score-bar {
  background: #f5f5f7;
  border-radius: 4px;
  height: 6px;
}

.score-bar-fill {
  background: linear-gradient(90deg, #0071e3, #00a2ff);
  border-radius: 4px;
  height: 100%;
  transition: width 0.3s ease;
}
```

---

## Interaction Patterns

### Hover Effects

1. **Cards**: Lift with shadow increase
   ```css
   transform: translateY(-4px);
   box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
   ```

2. **Buttons**: Slight color shift
   ```css
   background: #0077ed; /* from #0071e3 */
   ```

3. **Links**: Underline on hover
   ```css
   text-decoration: underline;
   ```

4. **Icons**: Background color change
   ```css
   background: #f5f5f7;
   ```

### Focus States

All interactive elements should have visible focus states:
```css
&:focus-visible {
  outline: 2px solid #0071e3;
  outline-offset: 2px;
}
```

### Loading States

1. **Button Loading**: Show spinner, disable interaction
2. **Page Loading**: Full-page spinner with message
3. **Skeleton Loading**: Show placeholder content structure

### Error Handling

1. **Form Validation**: Red border + error message with icon
2. **API Errors**: Toast notification (error variant)
3. **Service Unavailable**: Full-page error state with retry button

### Success Feedback

1. **Form Submission**: Toast notification (success variant)
2. **Actions**: Visual confirmation (checkmark, color change)

### Micro-interactions

1. **Staggered Animations**: Delay animations by 50-100ms for list items
2. **Smooth Transitions**: Use cubic-bezier easing for natural motion
3. **Hover Scaling**: Subtle scale (1.05) on images within cards

---

## Implementation Guidelines

### Technology Stack

#### Framework
- **React** with TypeScript
- **React Router** for navigation
- **TanStack Query** (React Query) for data fetching

#### Styling
- **TailwindCSS** with custom configuration
- Custom CSS for complex animations
- CSS-in-JS for dynamic styles (optional)

#### Icons
- **Material Symbols Outlined** from Google Fonts
- Variable font settings for fill states

### File Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   ├── Dropdown.tsx
│   │   ├── Spinner.tsx
│   │   └── Skeleton.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── PageContainer.tsx
│   └── features/
│       ├── auth/
│       │   └── LoginForm.tsx
│       ├── sessions/
│       │   ├── SessionCard.tsx
│       │   └── SessionList.tsx
│       ├── dashboard/
│       │   ├── ProfileCard.tsx
│       │   ├── ProfileGrid.tsx
│       │   └── StatsGrid.tsx
│       └── discovery/
│           ├── ConfigureForm.tsx
│           └── LaunchForm.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── SessionListPage.tsx
│   ├── DashboardPage.tsx
│   └── DiscoveryPage.tsx
├── styles/
│   ├── globals.css
│   ├── animations.css
│   └── tailwind.config.js
└── utils/
    ├── cn.ts (classname utility)
    └── animations.ts
```

### TailwindCSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'apple-bg': '#fbfbfd',
        'apple-card': '#ffffff',
        'apple-gray': '#f5f5f7',
        'apple-border': 'rgba(0, 0, 0, 0.06)',
        'apple-blue': '#0071e3',
        'apple-blue-hover': '#0077ed',
        'apple-green': '#34c759',
        'apple-orange': '#ff9500',
        'apple-red': '#ff3b30',
        'apple-purple': '#af52de',
        'apple-text': '#1d1d1f',
        'apple-text-secondary': '#86868b',
        'apple-text-tertiary': '#aeaeb2',
      },
      fontFamily: {
        'sf': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif']
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-down': 'slideDown 0.3s ease-out forwards',
        'scale-in': 'scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'toast-in': 'toastIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'shimmer': 'shimmer 1.5s infinite',
        'spin': 'spin 1s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        toastIn: {
          '0%': { opacity: '0', transform: 'translateX(100%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### Accessibility Guidelines

1. **Keyboard Navigation**
   - All interactive elements must be keyboard accessible
   - Logical tab order
   - Visible focus indicators

2. **Screen Readers**
   - Semantic HTML elements
   - ARIA labels where needed
   - Alt text for images

3. **Color Contrast**
   - Minimum 4.5:1 for normal text
   - Minimum 3:1 for large text
   - Don't rely solely on color for information

4. **Motion**
   - Respect `prefers-reduced-motion`
   - Provide alternatives to animations

### Performance Optimization

1. **Code Splitting**
   - Lazy load routes
   - Dynamic imports for heavy components

2. **Image Optimization**
   - Use WebP format
   - Lazy load images
   - Responsive images with srcset

3. **Bundle Size**
   - Tree-shake unused code
   - Minimize dependencies
   - Use production builds

4. **Caching**
   - Cache API responses
   - Service worker for offline support

### Responsive Design

#### Breakpoints
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

#### Mobile-First Approach
- Design for mobile first
- Progressive enhancement for larger screens
- Touch-friendly targets (minimum 44px)

### Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest 2 versions)
- **Mobile**: iOS Safari 14+, Chrome Android
- **Fallbacks**: Graceful degradation for older browsers

---

## Design Principles

### 1. Minimalism
- Remove unnecessary elements
- Focus on essential information
- White space is your friend

### 2. Consistency
- Reuse components
- Maintain visual hierarchy
- Follow established patterns

### 3. Clarity
- Clear labels and instructions
- Obvious call-to-actions
- Helpful error messages

### 4. Delight
- Smooth animations
- Thoughtful micro-interactions
- Premium feel

### 5. Performance
- Fast load times
- Responsive interactions
- Optimized assets

---

## Additional Resources

### Design Tools
- **Figma**: For design mockups and prototypes
- **Tailwind UI**: Component inspiration
- **Apple Human Interface Guidelines**: Design reference

### Development Tools
- **React DevTools**: Component debugging
- **Lighthouse**: Performance auditing
- **axe DevTools**: Accessibility testing

### Testing
- **Jest**: Unit testing
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **Storybook**: Component documentation

---

## Changelog

### Version 1.0 (February 7, 2026)
- Initial design plan based on reference designs
- Complete design system specification
- Page layouts and component library
- Implementation guidelines

---

**End of Document**
