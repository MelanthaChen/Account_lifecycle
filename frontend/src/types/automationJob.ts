export type AutomationJobStatus = "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED";

export interface AutomationJob {
  id: string;
  job_type: string;
  campaign_id: string | null;
  account_id: string;
  workflow_id: string | null;
  status: AutomationJobStatus;
  queued_at: string;
  started_at: string | null;
  completed_at: string | null;
  worker_id: string | null;
  result_json: Record<string, unknown> | null;
  error: string | null;
}

export interface AutomationAgentHeartbeat {
  active_workers: number;
  workers: AutomationAgentStatus[];
  queued_jobs: number;
  running_jobs: number;
  completed_jobs: number;
}

export interface AutomationAgentStatus {
  worker_id: string;
  hostname: string | null;
  last_seen: string;
  status: "Online" | "Offline" | "Idle" | "Running" | string;
  online_status: "Online" | "Offline" | string;
  running_job: string | null;
}
