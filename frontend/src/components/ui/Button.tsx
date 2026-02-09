import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const buttonVariants = cva(
    "inline-flex items-center justify-center whitespace-nowrap rounded-full text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue/20 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
    {
        variants: {
            variant: {
                default:
                    "bg-brand-blue text-white hover:bg-[#0077ed] shadow-sm",
                destructive:
                    "bg-brand-error text-white hover:bg-[#ff4b41] shadow-sm",
                outline:
                    "border border-gray-200 bg-transparent hover:bg-gray-50",
                secondary:
                    "bg-gray-100 text-brand-text hover:bg-gray-200",
                ghost: "hover:bg-gray-100 text-brand-text",
                link: "text-brand-blue underline-offset-4 hover:underline",
            },
            size: {
                default: "h-11 px-6 py-2.5",
                sm: "h-9 px-4 text-xs",
                lg: "h-12 px-10 text-base",
                icon: "h-10 w-10",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        // Basic implementation without Radix Slot for now to avoid extra installs if not needed
        // But keeping API compatible.
        const Comp = asChild ? Slot : "button"
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants }
