import { Activity, BarChart3, BriefcaseBusiness, HeartPulse, RadioTower } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { useAccounts } from "../hooks/useAccounts";
import { useActivities } from "../hooks/useActivities";
import { useAutomationJobs } from "../hooks/useAutomationJobs";
import { useCampaigns } from "../hooks/useCampaigns";
import { useHealth } from "../hooks/useHealth";

export function AnalyticsPage() {
  const accounts = useAccounts();
  const activities = useActivities({ limit: 200 });
  const jobs = useAutomationJobs({ limit: 200 });
  const campaigns = useCampaigns();
  const health = useHealth();

  const isLoading = accounts.isLoading || activities.isLoading || jobs.isLoading || campaigns.isLoading || health.isLoading;
  const isError = accounts.isError || activities.isError || jobs.isError || campaigns.isError || health.isError;
  const accountCount = accounts.data?.length ?? 0;
  const campaignCount = campaigns.data?.length ?? 0;
  const activityCount = activities.data?.length ?? 0;
  const jobCount = jobs.data?.length ?? 0;
  const averageHealth = (health.data ?? []).length
    ? Math.round((health.data ?? []).reduce((total, record) => total + record.health_score, 0) / (health.data ?? []).length)
    : 0;

  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Operational analytics calculated from accounts, campaigns, automation jobs, health, and activities.
        </p>
      </div>

      {isLoading ? (
        <StatePanel title="Loading analytics..." />
      ) : isError ? (
        <StatePanel title="Unable to load analytics." tone="error" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <Metric icon={RadioTower} label="Accounts" value={accountCount} />
            <Metric icon={BriefcaseBusiness} label="Campaigns" value={campaignCount} />
            <Metric icon={Activity} label="Activities" value={activityCount} />
            <Metric icon={BarChart3} label="Automation Jobs" value={jobCount} />
            <Metric icon={HeartPulse} label="Average Health" value={averageHealth} />
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            <ChartCard title="Automation Jobs by Status" data={countsBy(jobs.data ?? [], "status")} />
            <ChartCard title="Activity by Type" data={countsBy(activities.data ?? [], "activity_type")} />
            <ChartCard title="Campaigns by Status" data={countsBy(campaigns.data ?? [], "status")} />
            <ChartCard title="Health Status" data={countsBy(health.data ?? [], "health_status")} />
          </div>
        </>
      )}
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Activity; label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center gap-2 text-xs font-medium uppercase text-muted-foreground">
        <Icon size={15} />
        {label}
      </div>
      <div className="mt-3 text-2xl font-semibold">{value.toLocaleString()}</div>
    </div>
  );
}

function ChartCard({ data, title }: { data: Array<{ name: string; value: number }>; title: string }) {
  return (
    <section className="rounded-md border border-border bg-white p-5 shadow-sm">
      <h2 className="text-sm font-semibold">{title}</h2>
      {data.length === 0 ? (
        <div className="py-12 text-center text-sm text-muted-foreground">No records available.</div>
      ) : (
        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

function countsBy<T, K extends keyof T>(items: T[], key: K) {
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const name = String(item[key] ?? "Unknown");
    counts.set(name, (counts.get(name) ?? 0) + 1);
  });
  return [...counts.entries()].map(([name, value]) => ({ name, value }));
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-12 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-12 text-center text-sm text-muted-foreground"
      }
    >
      {title}
    </div>
  );
}
