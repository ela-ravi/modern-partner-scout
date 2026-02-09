/* eslint-disable react-refresh/only-export-components */
import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { AuthLayout } from '@/components/layouts/AuthLayout'
import { ProtectedRoute } from '@/components/ProtectedRoute'

// Lazy load pages for code splitting
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const SessionsPage = lazy(() => import('@/pages/SessionsPage'))
const DiscoveryConfigPage = lazy(() => import('@/pages/DiscoveryConfigPage'))
const ProcessingPage = lazy(() => import('@/pages/ProcessingPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

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
  // Redirect root to sessions
  {
    path: '/',
    element: <Navigate to="/sessions" replace />,
  },

  // Redirect old dashboard URL to sessions
  {
    path: '/dashboard',
    element: <Navigate to="/sessions" replace />,
  },

  // Auth routes (public)
  {
    path: '/login',
    element: <AuthLayout>{withSuspense(LoginPage)}</AuthLayout>,
  },

  // Protected routes
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: '/sessions',
            element: withSuspense(SessionsPage),
          },
          {
            path: '/new-session',
            element: withSuspense(DiscoveryConfigPage),
          },
          {
            path: '/jobs/:jobId',
            element: withSuspense(DashboardPage),
          },
          {
            path: '/jobs/:jobId/processing',
            element: withSuspense(ProcessingPage),
          },
        ],
      },
    ],
  },

  // 404 catch-all
  {
    path: '*',
    element: withSuspense(NotFoundPage),
  },
])
