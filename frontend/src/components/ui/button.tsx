import { forwardRef } from "react";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "../../lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", ...props }, ref) => {
    const variants: Record<ButtonVariant, string> = {
      primary: "bg-primary text-primary-foreground hover:bg-primary/90",
      secondary: "border border-border bg-white hover:bg-muted",
      ghost: "hover:bg-muted",
      danger: "bg-red-600 text-white hover:bg-red-700"
    };
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex h-9 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium transition disabled:pointer-events-none disabled:opacity-50",
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
