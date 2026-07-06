import {
  CheckCircle2,
  CircleDot,
  Clock3,
  ExternalLink,
  Loader2,
  XCircle
} from "lucide-react";

import { cn } from "../../lib/utils";
import type { Activity, ActivityStatus } from "../../types/activity";

interface ActivityTimelineProps {
  activities: Activity[];
  compact?: boolean;
  emptyText?: string;
}

const statusClasses: Record<ActivityStatus, string> = {
  SUCCESS: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  FAILED: "bg-red-50 text-red-700 ring-red-200",
  RUNNING: "bg-blue-50 text-blue-700 ring-blue-200",
  PENDING: "bg-slate-100 text-slate-600 ring-slate-200",
  CANCELLED: "bg-amber-50 text-amber-700 ring-amber-200"
};

const statusIcons: Record<ActivityStatus, typeof CheckCircle2> = {
  SUCCESS: CheckCircle2,
  FAILED: XCircle,
  RUNNING: Loader2,
  PENDING: Clock3,
  CANCELLED: CircleDot
};

export function ActivityTimeline({
  activities,
  compact = false,
  emptyText = "No activities yet."
}: ActivityTimelineProps) {
  if (activities.length === 0) {
    return (
      <div className="rounded-md border border-border bg-white px-4 py-10 text-center text-sm text-muted-foreground">
        {emptyText}
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-md border border-border bg-white">
      <div className={compact ? "divide-y divide-border" : "overflow-x-auto"}>
        {compact ? (
          activities.map((activity) => <ActivityCard key={activity.id} activity={activity} />)
        ) : (
          <table className="w-full min-w-[880px] text-left text-sm">
            <thead className="border-b border-border bg-muted/60 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Platform</th>
                <th className="px-4 py-3">Target URL</th>
                <th className="px-4 py-3">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {activities.map((activity) => (
                <tr key={activity.id}>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(activity.created_at)}</td>
                  <td className="px-4 py-3 font-medium">{formatActivityType(activity.activity_type)}</td>
                  <td className="px-4 py-3">
                    <ActivityStatusBadge status={activity.status} />
                  </td>
                  <td className="px-4 py-3 capitalize text-muted-foreground">{activity.platform}</td>
                  <td className="max-w-xs truncate px-4 py-3 text-muted-foreground">
                    {activity.target_url ? (
                      <span className="inline-flex items-center gap-1">
                        <ExternalLink size={13} />
                        {activity.target_url}
                      </span>
                    ) : (
                      "None"
                    )}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDuration(activity.duration_ms)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function ActivityCard({ activity }: { activity: Activity }) {
  const Icon = statusIcons[activity.status];
  return (
    <div className="flex gap-3 p-4">
      <div className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-md bg-muted">
        <Icon size={16} className={activity.status === "RUNNING" ? "animate-spin" : ""} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <div className="text-sm font-medium">{activity.title ?? formatActivityType(activity.activity_type)}</div>
          <ActivityStatusBadge status={activity.status} />
        </div>
        <div className="mt-1 text-xs text-muted-foreground">
          {formatDate(activity.created_at)} · {formatDuration(activity.duration_ms)}
        </div>
        {activity.target_url ? (
          <div className="mt-1 truncate text-xs text-muted-foreground">{activity.target_url}</div>
        ) : null}
      </div>
    </div>
  );
}

export function ActivityStatusBadge({ status }: { status: ActivityStatus }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1",
        statusClasses[status]
      )}
    >
      {status}
    </span>
  );
}

function formatActivityType(value: string) {
  return value.replaceAll("_", " ");
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function formatDuration(value: number | null) {
  if (value === null) {
    return "Pending";
  }
  if (value < 1000) {
    return `${value} ms`;
  }
  return `${(value / 1000).toFixed(1)} s`;
}
