/* eslint-disable react-refresh/only-export-components */
import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { AuthLayout } from '@/components/layouts/AuthLayout'
import { MarketingLayout } from '@/components/layouts/MarketingLayout'
import { ProtectedRoute } from '@/components/ProtectedRoute'

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const SessionsPage = lazy(() => import('@/pages/SessionsPage'))
const DiscoveryConfigPage = lazy(() => import('@/pages/DiscoveryConfigPage'))
const ProcessingPage = lazy(() => import('@/pages/ProcessingPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

// Marketing pages
const LandingPage = lazy(() => import('@/pages/marketing/LandingPage'))
const ContactPage = lazy(() => import('@/pages/marketing/ContactPage'))
const PrivacyPage = lazy(() => import('@/pages/marketing/PrivacyPage'))
const TermsPage = lazy(() => import('@/pages/marketing/TermsPage'))
const DocsPage = lazy(() => import('@/pages/marketing/DocsPage'))
const AboutPage = lazy(() => import('@/pages/marketing/AboutPage'))
const BlogPage = lazy(() => import('@/pages/marketing/BlogPage'))
const CareersPage = lazy(() => import('@/pages/marketing/CareersPage'))
const ChangelogPage = lazy(() => import('@/pages/marketing/ChangelogPage'))
const CookiesPage = lazy(() => import('@/pages/marketing/CookiesPage'))

// DEV ONLY: Mockup pages for UI design reference — remove before production deploy
const MockGallery = lazy(() => import('@/mockups/MockGallery'))
const MockLoginPage = lazy(() => import('@/mockups/MockLoginPage'))
const MockSessionsPage = lazy(() => import('@/mockups/MockSessionsPage'))
const MockDiscoveryConfigPage = lazy(() => import('@/mockups/MockDiscoveryConfigPage'))
const MockProcessingPage = lazy(() => import('@/mockups/MockProcessingPage'))
const MockDashboardPage = lazy(() => import('@/mockups/MockDashboardPage'))
const MockErrorPage = lazy(() => import('@/mockups/MockErrorPage'))
const MockNotFoundPage = lazy(() => import('@/mockups/MockNotFoundPage'))

// Loading fallback
function PageLoader() {
  return (
    <div className="min-h-[400px] flex items-center justify-center">
      <div className="w-8 h-8 border-4 border-apple-blue border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

// Wrap lazy components with Suspense
function withSuspense(
  Component: React.LazyExoticComponent<React.ComponentType<unknown>>
): ReactNode {
  return (
    <Suspense fallback={<PageLoader />}>
      <Component />
    </Suspense>
  )
}

export const router = createBrowserRouter([
  // Marketing pages (public, with MarketingLayout)
  // Uses path: '/' so React Router unambiguously owns the root and sub-paths
  {
    path: '/',
    element: <MarketingLayout />,
    children: [
      {
        index: true,
        element: withSuspense(LandingPage),
      },
      {
        path: 'contact',
        element: withSuspense(ContactPage),
      },
      {
        path: 'privacy',
        element: withSuspense(PrivacyPage),
      },
      {
        path: 'terms',
        element: withSuspense(TermsPage),
      },
      {
        path: 'docs',
        element: withSuspense(DocsPage),
      },
      {
        path: 'about',
        element: withSuspense(AboutPage),
      },
      {
        path: 'blog',
        element: withSuspense(BlogPage),
      },
      {
        path: 'careers',
        element: withSuspense(CareersPage),
      },
      {
        path: 'changelog',
        element: withSuspense(ChangelogPage),
      },
      {
        path: 'cookies',
        element: withSuspense(CookiesPage),
      },
    ],
  },

  // Auth routes (public)
  {
    path: '/login',
    element: <AuthLayout>{withSuspense(LoginPage)}</AuthLayout>,
  },

  // Protected routes
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: 'dashboard',
            element: <Navigate to="/sessions" replace />,
          },
          {
            path: 'sessions',
            element: withSuspense(SessionsPage),
          },
          {
            path: 'new-session',
            element: withSuspense(DiscoveryConfigPage),
          },
          {
            path: 'jobs/:jobId',
            element: withSuspense(DashboardPage),
          },
          {
            path: 'jobs/:jobId/processing',
            element: withSuspense(ProcessingPage),
          },
        ],
      },
    ],
  },

  // DEV ONLY: UI Design Mockups (public, no auth required)
  {
    path: '/mockups',
    children: [
      { index: true, element: withSuspense(MockGallery) },
      { path: 'login', element: withSuspense(MockLoginPage) },
      { path: 'sessions', element: withSuspense(MockSessionsPage) },
      { path: 'discovery-config', element: withSuspense(MockDiscoveryConfigPage) },
      { path: 'processing', element: withSuspense(MockProcessingPage) },
      { path: 'dashboard', element: withSuspense(MockDashboardPage) },
      { path: 'error', element: withSuspense(MockErrorPage) },
      { path: 'not-found', element: withSuspense(MockNotFoundPage) },
    ],
  },

  // 404 catch-all
  {
    path: '*',
    element: withSuspense(NotFoundPage),
  },
])
