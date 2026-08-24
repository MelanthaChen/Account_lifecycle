import { Activity, BarChart3, Clock3, ListChecks } from "lucide-react";

import { useActivities } from "../../hooks/useActivities";
import { useAutomationJobs } from "../../hooks/useAutomationJobs";
import type { Account } from "../../types/account";
import type { AutomationJobStatus } from "../../types/automationJob";

export function AccountAnalyticsPanel({ account }: { account: Account }) {
  const activities = useActivities({ accountId: account.id, limit: 200 });
  const jobs = useAutomationJobs({ limit: 200 });
  const accountJobs = (jobs.data ?? []).filter((job) => job.account_id === account.id);
  const completedJobs = accountJobs.filter((job) => job.status === "SUCCESS").length;
  const failedJobs = accountJobs.filter((job) => job.status === "FAILED").length;
  const runningJobs = accountJobs.filter((job) => job.status === "RUNNING" || job.status === "QUEUED").length;
  const successRate = completedJobs + failedJobs > 0
    ? Math.round((completedJobs / (completedJobs + failedJobs)) * 100)
    : null;

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-base font-semibold">Account Analytics</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Metrics calculated from stored activity records and automation jobs.
        </p>
      </div>

      {activities.isLoading || jobs.isLoading ? (
        <StatePanel title="Loading account analytics..." />
      ) : activities.isError || jobs.isError ? (
        <StatePanel title="Unable to load account analytics." tone="error" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Metric icon={Activity} label="Activities" value={`${activities.data?.length ?? 0}`} />
            <Metric icon={ListChecks} label="Completed Jobs" value={`${completedJobs}`} />
            <Metric icon={Clock3} label="Queued or Running" value={`${runningJobs}`} />
            <Metric icon={BarChart3} label="Success Rate" value={successRate === null ? "No runs" : `${successRate}%`} />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Breakdown title="Activity Types" rows={countBy(activities.data ?? [], "activity_type")} />
            <Breakdown title="Job Status" rows={countJobStatuses(accountJobs)} />
          </div>
        </>
      )}
    </section>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Activity; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <div className="flex items-center gap-2 text-xs font-medium uppercase text-muted-foreground">
        <Icon size={15} />
        {label}
      </div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function Breakdown({ rows, title }: { rows: Array<{ label: string; value: number }>; title: string }) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <h3 className="text-sm font-semibold">{title}</h3>
      {rows.length === 0 ? (
        <div className="mt-3 text-sm text-muted-foreground">No records available.</div>
      ) : (
        <div className="mt-3 space-y-2">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between rounded-md bg-muted px-3 py-2 text-sm">
              <span>{row.label}</span>
              <span className="font-medium">{row.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function countBy<T, K extends keyof T>(items: T[], key: K) {
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const label = String(item[key] ?? "Unknown");
    counts.set(label, (counts.get(label) ?? 0) + 1);
  });
  return [...counts.entries()].map(([label, value]) => ({ label, value }));
}

function countJobStatuses(items: Array<{ status: AutomationJobStatus }>) {
  return countBy(items, "status");
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-10 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-10 text-center text-sm text-muted-foreground"
      }
    >
      {title}
    </div>
  );
}
