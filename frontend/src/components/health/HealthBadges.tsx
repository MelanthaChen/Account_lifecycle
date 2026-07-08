import { cn } from "../../lib/utils";
import type { HealthStatus, RiskLevel } from "../../types/health";

export function HealthStatusBadge({ status }: { status: HealthStatus }) {
  const classes: Record<HealthStatus, string> = {
    HEALTHY: "bg-emerald-50 text-emerald-700",
    WARNING: "bg-amber-50 text-amber-700",
    CRITICAL: "bg-red-50 text-red-700"
  };
  return <span className={cn("rounded px-2 py-1 text-xs font-medium", classes[status])}>{status}</span>;
}

export function RiskBadge({ risk }: { risk: RiskLevel }) {
  const classes: Record<RiskLevel, string> = {
    LOW: "bg-emerald-50 text-emerald-700",
    MEDIUM: "bg-amber-50 text-amber-700",
    HIGH: "bg-red-50 text-red-700"
  };
  return <span className={cn("rounded px-2 py-1 text-xs font-medium", classes[risk])}>{risk}</span>;
}
