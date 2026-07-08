import type { LucideIcon } from "lucide-react";

interface DashboardMetricCardProps {
  description: string;
  icon: LucideIcon;
  title: string;
  tone?: "default" | "green" | "yellow" | "red" | "blue";
  value: string;
}

const toneClasses = {
  default: "bg-muted text-muted-foreground",
  green: "bg-emerald-50 text-emerald-700",
  yellow: "bg-amber-50 text-amber-700",
  red: "bg-red-50 text-red-700",
  blue: "bg-blue-50 text-blue-700"
};

export function DashboardMetricCard({
  description,
  icon: Icon,
  title,
  tone = "default",
  value
}: DashboardMetricCardProps) {
  return (
    <div className="rounded-md border border-border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-medium uppercase text-muted-foreground">{title}</div>
          <div className="mt-3 text-3xl font-semibold tracking-normal">{value}</div>
        </div>
        <div className={`flex h-9 w-9 flex-none items-center justify-center rounded-md ${toneClasses[tone]}`}>
          <Icon size={18} />
        </div>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">{description}</p>
    </div>
  );
}
