import type { ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { cn } from '@/lib/utils'
import CloseIcon from '@mui/icons-material/Close'

export interface ModalProps {
  /** Whether the modal is open */
  open: boolean
  /** Callback when open state changes */
  onOpenChange: (open: boolean) => void
  /** Modal content */
  children: ReactNode
  /** Modal title for accessibility */
  title?: string
  /** Modal description for accessibility */
  description?: string
  /** Size variant */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
}

const sizeStyles = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
  full: 'max-w-[95vw]',
}

export function Modal({
  open,
  onOpenChange,
  children,
  title,
  description,
  size = 'md',
}: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay
          className={cn(
            'fixed inset-0 z-50',
            'bg-black/40 backdrop-blur-sm',
            'data-[state=open]:animate-fade-in',
            'data-[state=closed]:animate-fade-out'
          )}
        />
        <Dialog.Content
          className={cn(
            'fixed left-1/2 top-1/2 z-50 -translate-x-1/2 -translate-y-1/2',
            'w-full p-6 rounded-2xl',
            'bg-apple-card shadow-modal',
            'max-h-[90vh] overflow-y-auto',
            'data-[state=open]:animate-scale-in',
            'focus:outline-none',
            sizeStyles[size]
          )}
          aria-describedby={description ? 'modal-description' : undefined}
        >
          {/* Header with title and close button */}
          <div className="flex items-center justify-between mb-4">
            {title && (
              <Dialog.Title className="text-lg font-semibold text-apple-text">
                {title}
              </Dialog.Title>
            )}
            <Dialog.Close
              className={cn(
                'p-2 rounded-full',
                'text-apple-text-secondary hover:text-apple-text',
                'hover:bg-apple-gray transition-colors',
                'focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2',
                'min-w-[24px] min-h-[24px]', // WCAG 2.5.8
                !title && 'ml-auto'
              )}
              aria-label="Close"
            >
              <CloseIcon className="w-5 h-5" />
            </Dialog.Close>
          </div>

          {description && (
            <Dialog.Description
              id="modal-description"
              className="text-sm text-apple-text-secondary mb-4"
            >
              {description}
            </Dialog.Description>
          )}

          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

// Additional exports for compound component pattern
export const ModalTrigger = Dialog.Trigger
export const ModalClose = Dialog.Close
