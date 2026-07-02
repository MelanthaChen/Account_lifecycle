import { AlertTriangle } from "lucide-react";

import { Button } from "./button";

interface AlertDialogProps {
  confirmLabel?: string;
  description: string;
  isPending?: boolean;
  onConfirm: () => void;
  onOpenChange: (open: boolean) => void;
  open: boolean;
  title: string;
}

export function AlertDialog({
  confirmLabel = "Delete",
  description,
  isPending,
  onConfirm,
  onOpenChange,
  open,
  title
}: AlertDialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center px-4 py-6">
      <button
        type="button"
        className="absolute inset-0 bg-foreground/35"
        onClick={() => onOpenChange(false)}
        aria-label="Cancel"
      />
      <section
        className="relative w-full max-w-md rounded-md border border-border bg-white p-5 shadow-xl"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="alert-title"
      >
        <div className="flex gap-3">
          <div className="flex h-9 w-9 flex-none items-center justify-center rounded-md bg-red-50 text-red-700">
            <AlertTriangle size={18} />
          </div>
          <div>
            <h2 id="alert-title" className="font-semibold">
              {title}
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          </div>
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="button" variant="danger" disabled={isPending} onClick={onConfirm}>
            {isPending ? "Deleting..." : confirmLabel}
          </Button>
        </div>
      </section>
    </div>
  );
}
