import { RefreshCw, ServerCog, ShieldCheck, Wifi } from "lucide-react";

import { Button } from "../components/ui/button";
import { api } from "../api/client";
import { useAutomationAgentHeartbeat } from "../hooks/useAutomationJobs";
import { useToast } from "../store/useToast";

export function SettingsPage() {
  const heartbeat = useAutomationAgentHeartbeat();
  const { notify } = useToast();
  const apiBaseUrl = api.defaults.baseURL ?? "/api/v1";
  const agent = heartbeat.data?.workers[0] ?? null;

  async function checkApi() {
    try {
      await api.get("/accounts");
      notify("Backend API is reachable.", "success");
    } catch {
      notify("Backend API check failed.", "error");
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Settings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Runtime configuration and connectivity status for this deployment.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={() => heartbeat.refetch()}>
            <RefreshCw size={16} className={heartbeat.isFetching ? "animate-spin" : ""} />
            Refresh Agent
          </Button>
          <Button type="button" onClick={checkApi}>
            <Wifi size={16} />
            Check API
          </Button>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-md border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <ServerCog size={17} className="text-muted-foreground" />
            <h2 className="text-base font-semibold">Backend Connection</h2>
          </div>
          <div className="mt-4 space-y-3 text-sm">
            <SettingRow label="API Base URL" value={apiBaseUrl} />
            <SettingRow label="Frontend Mode" value={import.meta.env.MODE} />
            <SettingRow label="Build" value={import.meta.env.PROD ? "Production" : "Development"} />
          </div>
        </section>

        <section className="rounded-md border border-border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <ShieldCheck size={17} className="text-muted-foreground" />
            <h2 className="text-base font-semibold">Automation Agent</h2>
          </div>
          {heartbeat.isLoading ? (
            <div className="mt-4 text-sm text-muted-foreground">Loading agent status...</div>
          ) : heartbeat.isError ? (
            <div className="mt-4 text-sm text-red-700">Unable to load agent status.</div>
          ) : agent ? (
            <div className="mt-4 space-y-3 text-sm">
              <SettingRow label="Runtime" value="Automation Agent" />
              <SettingRow label="Status" value={agent.online_status} />
              <SettingRow label="Current Job" value={agent.running_job ?? "Idle"} />
              <SettingRow label="Last Heartbeat" value={new Date(agent.last_seen).toLocaleString()} />
              <SettingRow label="Host" value={agent.hostname ?? "Unknown"} />
            </div>
          ) : (
            <div className="mt-4 text-sm text-muted-foreground">No heartbeat has been received.</div>
          )}
        </section>
      </div>
    </div>
  );
}

function SettingRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-md bg-muted px-3 py-2 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className="break-all font-medium">{value}</span>
    </div>
  );
}
