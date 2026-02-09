import { cn } from "../../lib/utils"

interface ScoreRingProps {
    score: number
    size?: number
    strokeWidth?: number
    className?: string
    showText?: boolean
}

export function ScoreRing({
    score,
    size = 48,
    strokeWidth = 4,
    className,
    showText = true,
}: ScoreRingProps) {
    const radius = (size - strokeWidth) / 2
    const circumference = radius * 2 * Math.PI
    const offset = circumference - (score / 100) * circumference

    // Color logic based on score
    const getColor = (s: number) => {
        if (s >= 80) return "text-brand-success"
        if (s >= 50) return "text-brand-warning"
        return "text-brand-error"
    }

    return (
        <div
            className={cn("relative inline-flex items-center justify-center animate-scale-in", className)}
            style={{ width: size, height: size }}
        >
            <svg
                width={size}
                height={size}
                className="transform -rotate-90"
            >
                {/* Background circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    className="text-gray-100"
                />
                {/* Progress circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    style={{
                        strokeDashoffset: offset,
                        transition: 'stroke-dashoffset 1s ease-in-out',
                    }}
                    strokeLinecap="round"
                    fill="transparent"
                    className={cn(getColor(score))}
                />
            </svg>
            {showText && (
                <span className="absolute text-[11px] font-bold text-brand-text">
                    {score}
                </span>
            )}
        </div>
    )
}
