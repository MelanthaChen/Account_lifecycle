import { Clock3, HeartPulse, ShieldCheck, TrendingUp } from "lucide-react";

import { ActivityTimeline } from "../components/activity/ActivityTimeline";
import { GrowthChart } from "../components/dashboard/GrowthChart";
import { PlatformChart } from "../components/dashboard/PlatformChart";
import { StatusChart } from "../components/dashboard/StatusChart";
import { SummaryCard } from "../components/dashboard/SummaryCard";
import { useActivities } from "../hooks/useActivities";
import { useAccounts } from "../hooks/useAccounts";

export function DashboardPage() {
  const accounts = useAccounts();
  const activities = useActivities({ limit: 10 });
  const accountList = accounts.data ?? [];
  const healthyAccounts = accountList.filter((account) => account.status === "active").length;
  const totalKarma = accountList.reduce(
    (total, account) => total + (account.karma_post ?? 0) + (account.karma_comment ?? 0),
    0
  );
  const lastSyncDates = accountList
    .map((account) => account.last_sync)
    .filter((value): value is string => Boolean(value))
    .map((value) => new Date(value).getTime());
  const lastSync = lastSyncDates.length
    ? new Date(Math.max(...lastSyncDates)).toLocaleString()
    : "Never";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">Account Intelligence Platform</h1>
        <p className="max-w-3xl text-sm text-muted-foreground">
          Monitor managed social accounts, track operational health, and prepare a clean foundation for
          future provider intelligence.
        </p>
      </div>

      {accounts.isError ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Unable to load account metrics from the API.
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={ShieldCheck} label="Total Accounts" value={`${accountList.length}`} />
        <SummaryCard icon={HeartPulse} label="Healthy Accounts" value={`${healthyAccounts}`} />
        <SummaryCard icon={Clock3} label="Last Sync" value={lastSync} />
        <SummaryCard icon={TrendingUp} label="Total Karma" value={totalKarma.toLocaleString()} />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <PlatformChart accounts={accountList} />
        <StatusChart accounts={accountList} />
        <GrowthChart />
      </div>

      <section className="space-y-3">
        <div>
          <h2 className="text-base font-semibold">Recent Activities</h2>
          <p className="mt-1 text-sm text-muted-foreground">Latest account operations across the platform.</p>
        </div>
        {activities.isLoading ? (
          <div className="rounded-md border border-border bg-white px-4 py-10 text-center text-sm text-muted-foreground">
            Loading activities...
          </div>
        ) : activities.isError ? (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-10 text-center text-sm text-red-700">
            Unable to load recent activities.
          </div>
        ) : (
          <ActivityTimeline activities={activities.data ?? []} compact />
        )}
      </section>
    </div>
  );
}
