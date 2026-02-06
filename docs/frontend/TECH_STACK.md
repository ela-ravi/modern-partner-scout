# Frontend Tech Stack - PartnerScout AI

> **Status**: FINALIZED  
> **Last Updated**: 2026-02-06

---

## Overview

This document captures all frontend technology decisions for PartnerScout AI. The design follows an **Apple-inspired aesthetic** with custom components built on accessible primitives.

---

## Core Stack

| Category | Technology | Version | Status |
|----------|------------|---------|--------|
| Framework | React | 19.x | ✅ Configured |
| Language | TypeScript | 5.9.x | ✅ Configured |
| Build Tool | Vite | 7.x | ✅ Configured |
| Styling | Tailwind CSS | 4.x | ✅ Configured |
| Linting | ESLint | 9.x | ✅ Configured |

---

## Additional Dependencies

### Routing
| Package | Version | Purpose |
|---------|---------|---------|
| `react-router-dom` | ^6.x | Client-side routing |

### State Management
| Package | Version | Purpose |
|---------|---------|---------|
| `@tanstack/react-query` | ^5.x | Server state (caching, refetching, mutations) |
| React Context | built-in | Client state (auth, theme, toast) |

### Forms & Validation
| Package | Version | Purpose |
|---------|---------|---------|
| `react-hook-form` | ^7.x | Form state management |
| `zod` | ^3.x | Schema validation (TypeScript-first) |
| `@hookform/resolvers` | ^3.x | Zod integration with react-hook-form |

### UI Primitives (Radix UI)
| Package | Version | Purpose |
|---------|---------|---------|
| `@radix-ui/react-dialog` | ^1.x | Modal dialogs |
| `@radix-ui/react-dropdown-menu` | ^2.x | Dropdown menus |
| `@radix-ui/react-tooltip` | ^1.x | Tooltips |
| `@radix-ui/react-tabs` | ^1.x | Tab navigation |
| `@radix-ui/react-select` | ^2.x | Select dropdowns |
| `@radix-ui/react-slider` | ^1.x | Range sliders (discovery config) |
| `@radix-ui/react-slot` | ^1.x | Component composition |

> **Why Radix UI?**  
> Provides unstyled, accessible primitives. We style them with Tailwind to match the Apple-inspired designs exactly. No fighting against opinionated styles.

### Icons
| Package | Version | Purpose |
|---------|---------|---------|
| `@material-symbols/react-400` | ^0.x | Material Symbols icons (matches designs) |

> **Note**: The designs use Material Symbols Outlined. This React wrapper provides tree-shakable, typed icons.

### Authentication & Database
| Package | Version | Purpose |
|---------|---------|---------|
| `@supabase/supabase-js` | ^2.x | Supabase client (auth + realtime) |

### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| `date-fns` | ^3.x | Date formatting and manipulation |
| `clsx` | ^2.x | Conditional class names |
| `tailwind-merge` | ^2.x | Merge Tailwind classes without conflicts |

### Testing (TDD)
| Package | Version | Purpose |
|---------|---------|---------|
| `vitest` | ^2.x | Test runner (Vite-native) |
| `@testing-library/react` | ^16.x | React component testing |
| `@testing-library/jest-dom` | ^6.x | DOM matchers |
| `@testing-library/user-event` | ^14.x | User interaction simulation |
| `jsdom` | ^24.x | DOM environment for tests |
| `msw` | ^2.x | Mock Service Worker for API mocking |
| `vitest-axe` | ^0.x | Accessibility testing in Vitest |

### Accessibility Linting
| Package | Version | Purpose |
|---------|---------|---------|
| `eslint-plugin-jsx-a11y` | ^6.x | JSX accessibility linting rules |

### Code Quality
| Package | Version | Purpose |
|---------|---------|---------|
| `prettier` | ^3.x | Code formatting |
| `prettier-plugin-tailwindcss` | ^0.x | Tailwind class sorting |

---

## Design System

### Apple-Inspired Color Palette

From `designs/main-discovery-dashboard.html`:

```css
/* Background & Surface */
--apple-bg: #fbfbfd;
--apple-card: #ffffff;
--apple-gray: #f5f5f7;
--apple-border: rgba(0, 0, 0, 0.06);

/* Brand Colors */
--apple-blue: #0071e3;
--apple-blue-hover: #0077ed;
--apple-green: #34c759;
--apple-orange: #ff9500;
--apple-red: #ff3b30;
--apple-purple: #af52de;

/* Text Colors */
--apple-text: #1d1d1f;
--apple-text-secondary: #6e6e73;   /* WCAG 2.2 AA compliant (5.2:1 ratio) */
--apple-text-tertiary: #8e8e93;    /* WCAG 2.2 AA compliant (4.5:1 ratio) */
```

### Typography

- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, sans-serif
- **Font Smoothing**: antialiased

### Border Radius

| Element | Radius |
|---------|--------|
| Cards | 18px |
| Buttons | 12px |
| Pill buttons | 980px |
| Inputs | 12px |
| Avatars | 12-16px |

### Shadows

```css
/* Card shadow */
box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04), 0 0 1px rgba(0, 0, 0, 0.1);

/* Card hover shadow */
box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.1);

/* Modal shadow */
box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

### Animations (CSS Only)

| Animation | Timing | Easing |
|-----------|--------|--------|
| fade-in | 0.6s | ease-out |
| slide-up | 0.6s | cubic-bezier(0.16, 1, 0.3, 1) |
| scale-in | 0.4s | cubic-bezier(0.16, 1, 0.3, 1) |

> **Decision**: CSS-only animations (no Framer Motion). All animations are achievable with Tailwind CSS.

---

## Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI Library | Radix UI + Custom | Apple aesthetic requires custom styling; Radix provides accessible primitives |
| Icons | Material Symbols | Matches existing designs exactly |
| State | React Query + Context | Minimal boilerplate, excellent caching |
| Forms | react-hook-form + zod | Type-safe, performant |
| Animation | CSS only | Designs use simple transitions; no need for JS animation library |
| Testing | Vitest + RTL | TDD from start; Vite-native for speed |
| Styling | Tailwind CSS 4 | Already configured; design tokens via CSS variables |

---

## What's NOT Included

| Technology | Reason |
|------------|--------|
| Material UI | Design aesthetic mismatch |
| Chakra UI | Opinionated styling conflicts with Apple design |
| shadcn/ui | Would require heavy customization; using Radix directly |
| Framer Motion | CSS animations sufficient for our needs |
| Redux/Zustand | React Query + Context is sufficient |
| Axios | Native fetch with typed wrapper is simpler |

---

## Next Steps

1. Install all dependencies
2. Configure Tailwind with Apple design tokens
3. Set up Vitest for TDD
4. Create base UI components library
5. Implement pages per `GAPS_TODO.md`

---

## Related Documents

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Frontend architecture patterns
- [GAPS_TODO.md](./GAPS_TODO.md) - Frontend implementation gaps
- [FUNCTIONALITIES.md](./FUNCTIONALITIES.md) - Expected features
- [BACKEND_MAPPING.md](./BACKEND_MAPPING.md) - API mapping
