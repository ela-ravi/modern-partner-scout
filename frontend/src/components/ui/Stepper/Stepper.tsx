import { cn } from '@/lib/utils'
import CheckIcon from '@mui/icons-material/Check'

export type StepStatus = 'complete' | 'active' | 'upcoming'

export interface Step {
  label: string
  status: StepStatus
}

export interface StepperProps {
  /** Array of steps to display */
  steps: Step[]
  /** Hide step labels on mobile */
  hideLabelsOnMobile?: boolean
  /** Additional class names */
  className?: string
}

export function Stepper({ steps, hideLabelsOnMobile = false, className }: StepperProps) {
  return (
    <div className={cn('flex items-center justify-center gap-0', className)}>
      {steps.map((step, index) => (
        <div key={step.label} className="flex items-center">
          {/* Step */}
          <div
            className="flex items-center gap-3"
            data-status={step.status}
            aria-current={step.status === 'active' ? 'step' : undefined}
          >
            {/* Step Indicator */}
            <div
              className={cn(
                'w-9 h-9 rounded-full flex items-center justify-center font-semibold text-sm',
                'transition-all duration-300',
                step.status === 'complete' && 'bg-apple-green text-white shadow-lg',
                step.status === 'active' && 'bg-apple-blue text-white shadow-lg',
                step.status === 'upcoming' && 'bg-apple-gray text-apple-text-tertiary'
              )}
            >
              {step.status === 'complete' ? (
                <CheckIcon
                  className="w-5 h-5"
                  aria-label={`${step.label} complete`}
                />
              ) : (
                <span>{index + 1}</span>
              )}
            </div>

            {/* Step Label */}
            <span
              className={cn(
                'font-medium',
                step.status === 'complete' && 'text-apple-green',
                step.status === 'active' && 'text-apple-text',
                step.status === 'upcoming' && 'text-apple-text-tertiary',
                hideLabelsOnMobile && 'hidden sm:block'
              )}
            >
              {step.label}
            </span>
          </div>

          {/* Connector */}
          {index < steps.length - 1 && (
            <div
              data-connector
              className={cn(
                'flex-1 h-px mx-6 max-w-[80px]',
                'transition-all duration-300',
                step.status === 'complete' ? 'bg-apple-green' : 'bg-gradient-to-r from-apple-blue to-apple-gray'
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}
