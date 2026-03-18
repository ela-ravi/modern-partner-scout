/**
 * ErrorBoundary Component
 * Catches JavaScript errors in child component tree
 */

import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from '@/components/ui/Button'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import RefreshIcon from '@mui/icons-material/Refresh'
import HomeIcon from '@mui/icons-material/Home'

export interface ErrorBoundaryProps {
  /** Child components */
  children: ReactNode
  /** Custom fallback UI */
  fallback?: ReactNode
  /** Called when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.props.onError?.(error, errorInfo)
  }

  handleReload = (): void => {
    window.location.reload()
  }

  handleGoHome = (): void => {
    window.location.href = '/'
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div
          className="min-h-[400px] flex items-center justify-center p-8"
          role="alert"
          aria-live="assertive"
        >
          <div className="max-w-md text-center">
            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-apple-red/10 flex items-center justify-center">
              <ErrorOutlineIcon className="text-apple-red w-8 h-8" />
            </div>

            <h2 className="text-2xl font-semibold text-apple-text mb-2">
              Something went wrong
            </h2>

            <p className="text-apple-text-secondary mb-6">
              We encountered an unexpected error. Please try refreshing the page or go back to the home page.
            </p>

            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 text-left bg-gray-100 rounded-lg p-4">
                <summary className="cursor-pointer text-sm font-medium text-apple-text-secondary">
                  Error Details
                </summary>
                <pre className="mt-2 text-xs text-apple-red overflow-auto whitespace-pre-wrap">
                  {this.state.error.message}
                </pre>
              </details>
            )}

            <div className="flex justify-center gap-3">
              <Button
                variant="secondary"
                onClick={this.handleGoHome}
                leftIcon={<HomeIcon />}
              >
                Go Home
              </Button>
              <Button
                variant="primary"
                onClick={this.handleReload}
                leftIcon={<RefreshIcon />}
              >
                Refresh Page
              </Button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
