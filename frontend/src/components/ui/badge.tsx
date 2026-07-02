import { cn } from "../../lib/utils";
import type { AccountStatus } from "../../types/account";

const statusClasses: Record<AccountStatus, string> = {
  active: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  paused: "bg-amber-50 text-amber-700 ring-amber-200",
  error: "bg-red-50 text-red-700 ring-red-200",
  archived: "bg-slate-100 text-slate-600 ring-slate-200"
};

export function StatusBadge({ status }: { status: AccountStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1",
        statusClasses[status]
      )}
    >
      {status}
    </span>
  );
}
