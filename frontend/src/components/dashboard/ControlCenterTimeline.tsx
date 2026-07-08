import {
  CheckCircle2,
  CircleDot,
  Clock3,
  Loader2,
  XCircle
} from "lucide-react";

import { DashboardEmptyState, DashboardSection } from "./DashboardSection";
import type { Account } from "../../types/account";
import type { Activity, ActivityStatus } from "../../types/activity";

interface ControlCenterTimelineProps {
  accounts: Account[];
  activities: Activity[];
  isError: boolean;
  isLoading: boolean;
}

const statusIcons: Record<ActivityStatus, typeof CheckCircle2> = {
  SUCCESS: CheckCircle2,
  FAILED: XCircle,
  RUNNING: Loader2,
  PENDING: Clock3,
  CANCELLED: CircleDot
};

export function ControlCenterTimeline({
  accounts,
  activities,
  isError,
  isLoading
}: ControlCenterTimelineProps) {
  const accountMap = new Map(accounts.map((account) => [account.id, account]));
  const recentActivities = [...activities]
    .sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime())
    .slice(0, 10);

  return (
    <DashboardSection title="Activity Timeline" description="Newest events across accounts and workflows.">
      {isLoading ? (
        <DashboardEmptyState>Loading activity...</DashboardEmptyState>
      ) : isError ? (
        <DashboardEmptyState>Unable to load recent activity.</DashboardEmptyState>
      ) : recentActivities.length === 0 ? (
        <DashboardEmptyState>No recent activity.</DashboardEmptyState>
      ) : (
        <div className="p-4">
          <div className="relative space-y-4 before:absolute before:left-[4.25rem] before:top-2 before:h-[calc(100%-1rem)] before:w-px before:bg-border">
            {recentActivities.map((activity) => {
              const Icon = statusIcons[activity.status];
              const account = accountMap.get(activity.account_id);
              return (
                <div key={activity.id} className="relative grid grid-cols-[58px_32px_minmax(0,1fr)] gap-3">
                  <div className="pt-1 text-right text-xs text-muted-foreground">{formatTime(activity.created_at)}</div>
                  <div className="z-10 flex h-8 w-8 items-center justify-center rounded-full border border-border bg-white">
                    <Icon size={15} className={activity.status === "RUNNING" ? "animate-spin" : ""} />
                  </div>
                  <div className="min-w-0 rounded-md bg-background px-3 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-medium">{activity.title ?? formatType(activity.activity_type)}</span>
                      <span className="text-xs text-muted-foreground">{activity.status}</span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {account?.nickname ?? "Account"} · {formatType(activity.activity_type)}
                      {activity.duration_ms !== null ? ` · ${formatDuration(activity.duration_ms)}` : ""}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </DashboardSection>
  );
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatType(value: string) {
  return value.replaceAll("_", " ");
}

function formatDuration(value: number) {
  if (value < 1000) {
    return `${value} ms`;
  }
  return `${(value / 1000).toFixed(1)} s`;
}
