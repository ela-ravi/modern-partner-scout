import { cn } from "../../lib/utils"

interface ProgressBarProps {
    value: number
    max?: number
    className?: string
    color?: "blue" | "success" | "warning" | "error"
    showValue?: boolean
    label?: string
}

export function ProgressBar({
    value,
    max = 100,
    className,
    color = "blue",
    showValue = false,
    label,
}: ProgressBarProps) {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

    const colorClasses = {
        blue: "bg-brand-blue",
        success: "bg-brand-success",
        warning: "bg-brand-warning",
        error: "bg-brand-error",
    }

    return (
        <div className={cn("w-full", className)}>
            {(label || showValue) && (
                <div className="flex justify-between items-center mb-1.5">
                    {label && <span className="text-xs font-medium text-brand-secondary">{label}</span>}
                    {showValue && <span className="text-xs font-bold text-brand-text">{value}%</span>}
                </div>
            )}
            <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                    className={cn(
                        "h-full transition-all duration-1000 ease-out rounded-full",
                        colorClasses[color]
                    )}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}
