import { api } from "./client";
import type { AutomationJob, AutomationJobStatus, WorkerHeartbeat } from "../types/automationJob";

export async function listAutomationJobs(params: {
  limit?: number;
  status?: AutomationJobStatus;
} = {}): Promise<AutomationJob[]> {
  const response = await api.get<AutomationJob[]>("/jobs", { params });
  return response.data;
}

export async function getAutomationJob(jobId: string): Promise<AutomationJob> {
  const response = await api.get<AutomationJob>(`/jobs/${jobId}`);
  return response.data;
}

export async function getWorkerHeartbeat(): Promise<WorkerHeartbeat> {
  const response = await api.get<WorkerHeartbeat>("/workers/heartbeat");
  return response.data;
}
