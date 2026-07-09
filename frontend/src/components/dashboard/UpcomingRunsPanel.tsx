import { Link } from "react-router-dom";

import { DashboardEmptyState, DashboardSection } from "./DashboardSection";
import type { Campaign } from "../../types/campaign";
import type { CampaignSchedule } from "../../types/schedule";

interface UpcomingRunsPanelProps {
  campaigns: Campaign[];
  isError: boolean;
  isLoading: boolean;
  schedules: CampaignSchedule[];
}

export function UpcomingRunsPanel({
  campaigns,
  isError,
  isLoading,
  schedules
}: UpcomingRunsPanelProps) {
  const upcoming = schedules
    .filter((schedule) => schedule.enabled)
    .sort((left, right) => dateValue(left.next_run_at) - dateValue(right.next_run_at))
    .slice(0, 6);

  return (
    <DashboardSection title="Upcoming Runs" description="Enabled campaign schedules registered with the scheduler.">
      {isLoading ? (
        <DashboardEmptyState>Loading upcoming runs...</DashboardEmptyState>
      ) : isError ? (
        <DashboardEmptyState>Unable to load schedules.</DashboardEmptyState>
      ) : upcoming.length === 0 ? (
        <DashboardEmptyState>No scheduled runs yet.</DashboardEmptyState>
      ) : (
        <div className="divide-y divide-border">
          {upcoming.map((schedule) => {
            const campaign = campaigns.find((item) => item.id === schedule.campaign_id);
            return (
              <div key={schedule.id} className="grid gap-2 px-4 py-3 text-sm sm:grid-cols-[minmax(0,1fr)_160px_120px] sm:items-center">
                <div>
                  <Link to={`/campaigns/${schedule.campaign_id}`} className="font-medium hover:text-primary">
                    {campaign?.name ?? "Unknown Campaign"}
                  </Link>
                  <div className="mt-1 text-xs text-muted-foreground">
                    {schedule.schedule_type}
                    {schedule.cron_expression ? ` · ${schedule.cron_expression}` : ""}
                  </div>
                </div>
                <div className="text-muted-foreground">
                  {schedule.next_run_at ? formatDate(schedule.next_run_at) : "Pending"}
                </div>
                <div className="text-muted-foreground">{schedule.last_status ?? "Not run"}</div>
              </div>
            );
          })}
        </div>
      )}
    </DashboardSection>
  );
}

function dateValue(value: string | null) {
  return value ? new Date(value).getTime() : Number.MAX_SAFE_INTEGER;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
