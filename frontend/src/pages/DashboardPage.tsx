import {
  Activity,
  AlertTriangle,
  CalendarCheck2,
  CheckCircle2,
  HeartPulse,
  ListChecks,
  RadioTower,
  ShieldAlert,
  Sparkles
} from "lucide-react";

import { ControlCenterTimeline } from "../components/dashboard/ControlCenterTimeline";
import { DashboardMetricCard } from "../components/dashboard/DashboardMetricCard";
import { HealthOverviewTable } from "../components/dashboard/HealthOverviewTable";
import { QuickActionsPanel } from "../components/dashboard/QuickActionsPanel";
import { RecentCampaignsTable } from "../components/dashboard/RecentCampaignsTable";
import { RecommendedActionsPanel } from "../components/dashboard/RecommendedActionsPanel";
import { UpcomingRunsPanel } from "../components/dashboard/UpcomingRunsPanel";
import { useActivities } from "../hooks/useActivities";
import { useAccounts } from "../hooks/useAccounts";
import { useWorkerHeartbeat } from "../hooks/useAutomationJobs";
import { useBehaviorTemplates } from "../hooks/useBehaviorTemplates";
import { useCampaigns, useRunCampaign } from "../hooks/useCampaigns";
import { useEvaluateAllHealth, useHealth } from "../hooks/useHealth";
import { useEvaluateAllRecommendations, useRecommendations } from "../hooks/useRecommendations";
import { useSchedules } from "../hooks/useSchedules";
import { useToast } from "../store/useToast";
import type { Campaign } from "../types/campaign";

export function DashboardPage() {
  const accounts = useAccounts();
  const activities = useActivities({ limit: 50 });
  const campaigns = useCampaigns();
  const health = useHealth();
  const recommendations = useRecommendations();
  const schedules = useSchedules();
  const heartbeat = useWorkerHeartbeat();
  const templates = useBehaviorTemplates();
  const runCampaign = useRunCampaign();
  const evaluateHealth = useEvaluateAllHealth();
  const evaluateRecommendations = useEvaluateAllRecommendations();
  const { notify } = useToast();

  const accountList = accounts.data ?? [];
  const activityList = activities.data ?? [];
  const campaignList = campaigns.data ?? [];
  const healthList = health.data ?? [];
  const recommendationList = recommendations.data ?? [];
  const scheduleList = schedules.data ?? [];
  const workerStats = heartbeat.data;
  const templateList = templates.data ?? [];

  const healthyAccounts = healthList.filter((record) => record.health_status === "HEALTHY").length;
  const warningAccounts = healthList.filter((record) => record.health_status === "WARNING").length;
  const criticalAccounts = healthList.filter((record) => record.health_status === "CRITICAL").length;
  const campaignsToday = campaignList.filter((campaign) => isToday(campaign.created_at)).length;
  const workflowRunsToday = campaignList.filter(
    (campaign) => isToday(campaign.updated_at) && ["Running", "Completed", "Failed"].includes(campaign.status)
  ).length;
  const activitiesToday = activityList.filter((activity) => isToday(activity.created_at)).length;
  const activeRecommendations = recommendationList.filter((recommendation) => recommendation.status === "ACTIVE").length;
  const averageHealthScore = healthList.length
    ? Math.round(healthList.reduce((total, record) => total + record.health_score, 0) / healthList.length)
    : 0;

  function handleRunCampaign(campaign: Campaign) {
    runCampaign.mutate(campaign.id, {
      onSuccess: (response) =>
        notify(response.success ? "Campaign completed." : "Campaign finished with failures.", response.success ? "success" : "error"),
      onError: () => notify("Unable to run campaign.", "error")
    });
  }

  return (
    <div className="space-y-6">
      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="rounded-md border border-border bg-white p-5 shadow-sm">
          <h1 className="text-2xl font-semibold">Account Lifecycle Control Center</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Review account health, recommended next steps, campaign readiness, and recent operations from one place.
          </p>
        </div>
        <QuickActionsPanel
          evaluatingHealth={evaluateHealth.isPending}
          evaluatingRecommendations={evaluateRecommendations.isPending}
          onEvaluateHealth={() =>
            evaluateHealth.mutate(undefined, {
              onSuccess: () => notify("Health evaluated for all accounts.", "success"),
              onError: () => notify("Unable to evaluate health.", "error")
            })
          }
          onEvaluateRecommendations={() =>
            evaluateRecommendations.mutate(undefined, {
              onSuccess: () => notify("Recommendations evaluated for all accounts.", "success"),
              onError: () => notify("Unable to evaluate recommendations.", "error")
            })
          }
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <DashboardMetricCard
          icon={CheckCircle2}
          title="Healthy Accounts"
          value={`${healthyAccounts}`}
          description="Accounts currently evaluated as healthy."
          tone="green"
        />
        <DashboardMetricCard
          icon={AlertTriangle}
          title="Warning Accounts"
          value={`${warningAccounts}`}
          description="Accounts that need attention soon."
          tone="yellow"
        />
        <DashboardMetricCard
          icon={ShieldAlert}
          title="Critical Accounts"
          value={`${criticalAccounts}`}
          description="Accounts that should be reviewed first."
          tone="red"
        />
        <DashboardMetricCard
          icon={CalendarCheck2}
          title="Campaigns Today"
          value={`${campaignsToday}`}
          description="Campaigns created today."
          tone="blue"
        />
        <DashboardMetricCard
          icon={ListChecks}
          title="Workflow Runs Today"
          value={`${workflowRunsToday}`}
          description="Campaign workflows updated as running or finished today."
          tone="blue"
        />
        <DashboardMetricCard
          icon={Activity}
          title="Activities Today"
          value={`${activitiesToday}`}
          description="Logged account operations today."
        />
        <DashboardMetricCard
          icon={Sparkles}
          title="Recommendation Count"
          value={`${activeRecommendations}`}
          description="Active recommendations waiting for review."
          tone={activeRecommendations ? "yellow" : "green"}
        />
        <DashboardMetricCard
          icon={HeartPulse}
          title="Average Health Score"
          value={`${averageHealthScore}`}
          description={healthList.length ? "Average score across evaluated accounts." : "No evaluated accounts yet."}
          tone={averageHealthScore >= 80 ? "green" : averageHealthScore >= 50 ? "yellow" : "red"}
        />
        <DashboardMetricCard
          icon={RadioTower}
          title="Active Workers"
          value={`${workerStats?.active_workers ?? 0}`}
          description="Local automation agents currently running jobs."
          tone={workerStats?.active_workers ? "green" : "yellow"}
        />
        <DashboardMetricCard
          icon={ListChecks}
          title="Queued Jobs"
          value={`${workerStats?.queued_jobs ?? 0}`}
          description="Automation jobs waiting for an agent."
          tone={workerStats?.queued_jobs ? "yellow" : "green"}
        />
        <DashboardMetricCard
          icon={Activity}
          title="Running Jobs"
          value={`${workerStats?.running_jobs ?? 0}`}
          description="Automation jobs currently owned by workers."
          tone={workerStats?.running_jobs ? "blue" : "green"}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.8fr)]">
        <HealthOverviewTable
          accounts={accountList}
          health={healthList}
          isError={accounts.isError || health.isError}
          isLoading={accounts.isLoading || health.isLoading}
        />
        <RecommendedActionsPanel
          accounts={accountList}
          recommendations={recommendationList}
          templates={templateList}
          isError={accounts.isError || recommendations.isError || templates.isError}
          isLoading={accounts.isLoading || recommendations.isLoading || templates.isLoading}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.8fr)]">
        <RecentCampaignsTable
          accounts={accountList}
          campaigns={campaignList}
          isError={accounts.isError || campaigns.isError}
          isLoading={accounts.isLoading || campaigns.isLoading}
          isRunning={runCampaign.isPending}
          onRun={handleRunCampaign}
        />
        <ControlCenterTimeline
          accounts={accountList}
          activities={activityList}
          isError={accounts.isError || activities.isError}
          isLoading={accounts.isLoading || activities.isLoading}
        />
      </div>

      <UpcomingRunsPanel
        campaigns={campaignList}
        schedules={scheduleList}
        isError={campaigns.isError || schedules.isError}
        isLoading={campaigns.isLoading || schedules.isLoading}
      />

      <WorkersPanel
        workers={workerStats?.workers ?? []}
        queuedJobs={workerStats?.queued_jobs ?? 0}
        runningJobs={workerStats?.running_jobs ?? 0}
        isLoading={heartbeat.isLoading}
        isError={heartbeat.isError}
      />
    </div>
  );
}

function WorkersPanel({
  workers,
  queuedJobs,
  runningJobs,
  isLoading,
  isError
}: {
  workers: Array<{
    worker_id: string;
    hostname: string | null;
    last_seen: string;
    status: string;
    online_status: string;
    running_job: string | null;
  }>;
  queuedJobs: number;
  runningJobs: number;
  isLoading: boolean;
  isError: boolean;
}) {
  return (
    <section className="rounded-md border border-border bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-2 border-b border-border pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Automation Workers</h2>
          <p className="mt-1 text-sm text-muted-foreground">Local agents connected to this backend.</p>
        </div>
        <div className="text-sm text-muted-foreground">
          Queued {queuedJobs} · Running {runningJobs}
        </div>
      </div>
      {isLoading ? (
        <div className="py-6 text-sm text-muted-foreground">Loading workers...</div>
      ) : isError ? (
        <div className="py-6 text-sm text-red-700">Unable to load workers.</div>
      ) : workers.length === 0 ? (
        <div className="py-6 text-sm text-muted-foreground">No workers have checked in yet.</div>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-2 pr-4">Worker Name</th>
                <th className="py-2 pr-4">Online Status</th>
                <th className="py-2 pr-4">Current Job</th>
                <th className="py-2 pr-4">Last Heartbeat</th>
                <th className="py-2 pr-4">Host</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {workers.map((worker) => (
                <tr key={worker.worker_id}>
                  <td className="py-2 pr-4 font-medium">{worker.worker_id}</td>
                  <td className="py-2 pr-4">
                    <span className={worker.online_status === "Online" ? "text-emerald-700" : "text-red-700"}>
                      {worker.status}
                    </span>
                  </td>
                  <td className="py-2 pr-4">{worker.running_job ?? "Idle"}</td>
                  <td className="py-2 pr-4">{new Date(worker.last_seen).toLocaleString()}</td>
                  <td className="py-2 pr-4">{worker.hostname ?? "Unknown"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function isToday(value: string) {
  const date = new Date(value);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear()
    && date.getMonth() === now.getMonth()
    && date.getDate() === now.getDate()
  );
}
