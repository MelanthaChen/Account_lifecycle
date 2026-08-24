import { useQuery } from "@tanstack/react-query";

import { getAutomationAgentHeartbeat, getAutomationJob, listAutomationJobs } from "../api/automationJobs";
import type { AutomationJobStatus } from "../types/automationJob";

export function useAutomationJobs(params: { limit?: number; status?: AutomationJobStatus } = {}) {
  return useQuery({
    queryKey: ["automation-jobs", params],
    queryFn: () => listAutomationJobs(params),
    refetchInterval: 5_000
  });
}

export function useAutomationJob(jobId: string | null) {
  return useQuery({
    queryKey: ["automation-jobs", jobId],
    queryFn: () => getAutomationJob(jobId ?? ""),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "QUEUED" || status === "RUNNING" ? 2_000 : false;
    }
  });
}

export function useAutomationAgentHeartbeat() {
  return useQuery({
    queryKey: ["automation-agent", "heartbeat"],
    queryFn: getAutomationAgentHeartbeat,
    refetchInterval: 5_000
  });
}
