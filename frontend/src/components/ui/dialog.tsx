import type { ReactNode } from "react";
import { X } from "lucide-react";

import { cn } from "../../lib/utils";

interface DialogProps {
  children: ReactNode;
  description?: string;
  onOpenChange: (open: boolean) => void;
  open: boolean;
  title: string;
}

export function Dialog({ children, description, onOpenChange, open, title }: DialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center px-4 py-6">
      <button
        type="button"
        className="absolute inset-0 bg-foreground/35"
        onClick={() => onOpenChange(false)}
        aria-label="Close dialog"
      />
      <section
        className={cn(
          "relative max-h-[calc(100vh-3rem)] w-full max-w-2xl overflow-y-auto rounded-md border border-border bg-white p-5 shadow-xl"
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 id="dialog-title" className="text-lg font-semibold">
              {title}
            </h2>
            {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
          </div>
          <button
            type="button"
            className="rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            onClick={() => onOpenChange(false)}
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>
        {children}
      </section>
    </div>
  );
}
