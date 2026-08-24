import { useQuery } from "@tanstack/react-query";

import { getWorkerHeartbeat, listAutomationJobs } from "../api/automationJobs";
import type { AutomationJobStatus } from "../types/automationJob";

export function useAutomationJobs(params: { limit?: number; status?: AutomationJobStatus } = {}) {
  return useQuery({
    queryKey: ["automation-jobs", params],
    queryFn: () => listAutomationJobs(params),
    refetchInterval: 5_000
  });
}

export function useWorkerHeartbeat() {
  return useQuery({
    queryKey: ["workers", "heartbeat"],
    queryFn: getWorkerHeartbeat,
    refetchInterval: 5_000
  });
}
