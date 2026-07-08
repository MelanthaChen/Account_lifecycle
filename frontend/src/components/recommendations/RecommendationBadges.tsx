import { cn } from "../../lib/utils";
import type { RecommendationPriority, RecommendationStatus } from "../../types/recommendation";

export function RecommendationPriorityBadge({ priority }: { priority: RecommendationPriority }) {
  const classes: Record<RecommendationPriority, string> = {
    HIGH: "bg-red-50 text-red-700 ring-red-200",
    MEDIUM: "bg-amber-50 text-amber-700 ring-amber-200",
    LOW: "bg-emerald-50 text-emerald-700 ring-emerald-200"
  };
  return <Badge className={classes[priority]}>{priority}</Badge>;
}

export function RecommendationStatusBadge({ status }: { status: RecommendationStatus }) {
  const classes: Record<RecommendationStatus, string> = {
    ACTIVE: "bg-blue-50 text-blue-700 ring-blue-200",
    DISMISSED: "bg-slate-100 text-slate-600 ring-slate-200",
    COMPLETED: "bg-emerald-50 text-emerald-700 ring-emerald-200"
  };
  return <Badge className={classes[status]}>{status}</Badge>;
}

function Badge({ className, children }: { className: string; children: string }) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1", className)}>
      {children}
    </span>
  );
}
