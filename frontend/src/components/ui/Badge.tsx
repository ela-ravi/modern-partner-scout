import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
    "inline-flex items-center rounded-full px-3 py-1 text-[13px] font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
    {
        variants: {
            variant: {
                default:
                    "bg-brand-blue/10 text-brand-blue",
                secondary:
                    "bg-gray-100 text-brand-secondary",
                success:
                    "bg-brand-success/10 text-brand-success",
                warning:
                    "bg-brand-warning/10 text-brand-warning",
                error:
                    "bg-brand-error/10 text-brand-error",
                outline: "text-brand-text border border-gray-200",
            },
            animate: {
                none: "",
                fadeIn: "animate-fade-in",
            }
        },
        defaultVariants: {
            variant: "default",
            animate: "none",
        },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, animate, ...props }: BadgeProps) {
    return (
        <div className={cn(badgeVariants({ variant, animate }), className)} {...props} />
    )
}

export { Badge, badgeVariants }
