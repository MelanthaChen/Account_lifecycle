import { CheckCircle2, Info, X, XCircle } from "lucide-react";

import { useToast, type ToastTone } from "../../store/useToast";
import { cn } from "../../lib/utils";

const toneClasses: Record<ToastTone, string> = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  error: "border-red-200 bg-red-50 text-red-900",
  info: "border-border bg-white text-foreground"
};

const icons: Record<ToastTone, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: XCircle,
  info: Info
};

export function ToastViewport() {
  const { messages, dismiss } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex w-[min(360px,calc(100vw-2rem))] flex-col gap-2">
      {messages.map((toast) => {
        const Icon = icons[toast.tone];
        return (
          <div
            key={toast.id}
            className={cn(
              "flex items-start gap-3 rounded-md border p-3 text-sm shadow-lg",
              toneClasses[toast.tone]
            )}
          >
            <Icon className="mt-0.5 h-4 w-4 flex-none" />
            <div className="min-w-0 flex-1">{toast.message}</div>
            <button
              type="button"
              className="rounded-sm p-0.5 opacity-70 hover:opacity-100"
              onClick={() => dismiss(toast.id)}
              aria-label="Dismiss notification"
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
