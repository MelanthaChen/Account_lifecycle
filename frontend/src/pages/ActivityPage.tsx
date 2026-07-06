import { Plus, RefreshCw } from "lucide-react";

import { ActivityTimeline } from "../components/activity/ActivityTimeline";
import { Button } from "../components/ui/button";
import { useActivities, useCreateTestActivity } from "../hooks/useActivities";
import { useToast } from "../store/useToast";

export function ActivityPage() {
  const activities = useActivities({ limit: 50 });
  const createTestActivity = useCreateTestActivity();
  const { notify } = useToast();

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Activity</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Audit trail for account operations and browser actions.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={() => activities.refetch()}>
            <RefreshCw size={16} className={activities.isFetching ? "animate-spin" : ""} />
            Refresh
          </Button>
          <Button
            type="button"
            disabled={createTestActivity.isPending}
            onClick={() =>
              createTestActivity.mutate(undefined, {
                onSuccess: () => notify("Test activity generated.", "success"),
                onError: () => notify("Unable to generate test activity.", "error")
              })
            }
          >
            <Plus size={16} />
            {createTestActivity.isPending ? "Generating..." : "Generate Test Activity"}
          </Button>
        </div>
      </div>

      {activities.isLoading ? (
        <StatePanel title="Loading activities..." />
      ) : activities.isError ? (
        <StatePanel title="Unable to load activities." tone="error" />
      ) : (
        <ActivityTimeline activities={activities.data ?? []} />
      )}
    </div>
  );
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
