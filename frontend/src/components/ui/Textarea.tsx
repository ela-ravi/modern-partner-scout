import * as React from "react"
import { cn } from "../../lib/utils"

export interface TextareaProps
    extends React.TextareaHTMLAttributes<HTMLTextAreaElement> { }

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
    ({ className, ...props }, ref) => {
        return (
            <textarea
                className={cn(
                    "flex min-h-[80px] w-full rounded-[12px] border border-[rgba(0,0,0,0.1)] bg-white px-3 py-2 text-sm ring-offset-background placeholder:text-[#aeaeb2] focus-visible:outline-none focus-visible:border-[#0071e3] focus-visible:ring-4 focus-visible:ring-[#0071e3]/10 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200 resize-none",
                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Textarea.displayName = "Textarea"

export { Textarea }
