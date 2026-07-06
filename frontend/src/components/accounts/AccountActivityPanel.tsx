import { ActivityTimeline } from "../activity/ActivityTimeline";
import { useActivities } from "../../hooks/useActivities";
import type { Account } from "../../types/account";

export function AccountActivityPanel({ account }: { account: Account }) {
  const activities = useActivities({ accountId: account.id, limit: 20 });

  if (activities.isLoading) {
    return <StatePanel title="Loading recent activities..." />;
  }

  if (activities.isError) {
    return <StatePanel title="Unable to load activities." tone="error" />;
  }

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-base font-semibold">Recent Activities</h2>
        <p className="mt-1 text-sm text-muted-foreground">Last 20 actions recorded for this account.</p>
      </div>
      <ActivityTimeline activities={activities.data ?? []} compact />
    </section>
  );
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
