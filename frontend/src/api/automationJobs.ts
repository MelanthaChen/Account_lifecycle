import { api } from "./client";
import type { AutomationAgentHeartbeat, AutomationJob, AutomationJobStatus } from "../types/automationJob";

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

export async function getAutomationAgentHeartbeat(): Promise<AutomationAgentHeartbeat> {
  const response = await api.get<AutomationAgentHeartbeat>("/agent/heartbeat");
  return response.data;
}
