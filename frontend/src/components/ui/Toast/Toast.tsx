/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import WarningIcon from '@mui/icons-material/Warning'
import InfoIcon from '@mui/icons-material/Info'
import CloseIcon from '@mui/icons-material/Close'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastContextValue {
  toasts: Toast[]
  success: (message: string, duration?: number) => void
  error: (message: string, duration?: number) => void
  warning: (message: string, duration?: number) => void
  info: (message: string, duration?: number) => void
  dismiss: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

const DEFAULT_DURATION = 5000

const toastConfig: Record<ToastType, { icon: ReactNode; className: string }> = {
  success: {
    icon: <CheckCircleIcon className="w-5 h-5" />,
    className: 'bg-apple-green text-white',
  },
  error: {
    icon: <ErrorIcon className="w-5 h-5" />,
    className: 'bg-apple-red text-white',
  },
  warning: {
    icon: <WarningIcon className="w-5 h-5" />,
    className: 'bg-apple-orange text-white',
  },
  info: {
    icon: <InfoIcon className="w-5 h-5" />,
    className: 'bg-apple-blue text-white',
  },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((type: ToastType, message: string, duration = DEFAULT_DURATION) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast: Toast = { id, type, message, duration }

    setToasts((prev) => [...prev, newToast])

    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, duration)
    }
  }, [])

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const value: ToastContextValue = {
    toasts,
    success: (message, duration) => addToast('success', message, duration),
    error: (message, duration) => addToast('error', message, duration),
    warning: (message, duration) => addToast('warning', message, duration),
    info: (message, duration) => addToast('info', message, duration),
    dismiss,
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

interface ToastContainerProps {
  toasts: Toast[]
  onDismiss: (id: string) => void
}

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <div
      className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

interface ToastItemProps {
  toast: Toast
  onDismiss: (id: string) => void
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const config = toastConfig[toast.type]

  return (
    <div
      className={cn(
        'flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg',
        'animate-slide-down',
        config.className
      )}
      role={toast.type === 'error' ? 'alert' : 'status'}
    >
      <span aria-hidden="true">{config.icon}</span>
      <p className="flex-1 text-sm font-medium">{toast.message}</p>
      <button
        onClick={() => onDismiss(toast.id)}
        className={cn(
          'p-1 rounded-full hover:bg-white/20 transition-colors',
          'min-w-[24px] min-h-[24px]' // WCAG 2.5.8
        )}
        aria-label="Dismiss notification"
      >
        <CloseIcon className="w-4 h-4" />
      </button>
    </div>
  )
}
