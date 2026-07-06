import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createTestActivity, listActivities } from "../api/activities";
import type { ActivityFilters } from "../types/activity";

export function useActivities(filters: ActivityFilters = {}) {
  return useQuery({
    queryKey: ["activities", filters],
    queryFn: () => listActivities(filters)
  });
}

export function useCreateTestActivity(accountId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => createTestActivity(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["activities"] });
    }
  });
}
