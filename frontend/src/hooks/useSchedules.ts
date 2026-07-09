import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCampaignSchedule,
  deleteCampaignSchedule,
  getCampaignSchedule,
  listSchedules,
  runCampaignScheduleNow,
  updateCampaignSchedule
} from "../api/schedules";
import type { CampaignScheduleInput } from "../types/schedule";

export function useSchedules() {
  return useQuery({ queryKey: ["schedules"], queryFn: listSchedules });
}

export function useCampaignSchedule(campaignId: string) {
  return useQuery({
    queryKey: ["campaigns", campaignId, "schedule"],
    queryFn: () => getCampaignSchedule(campaignId),
    enabled: Boolean(campaignId),
    retry: false
  });
}

export function useSaveCampaignSchedule(campaignId: string, hasSchedule: boolean) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CampaignScheduleInput) =>
      hasSchedule ? updateCampaignSchedule(campaignId, input) : createCampaignSchedule(campaignId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "schedule"] });
    }
  });
}

export function useDeleteCampaignSchedule(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteCampaignSchedule(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "schedule"] });
    }
  });
}

export function useRunCampaignScheduleNow(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => runCampaignScheduleNow(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schedules"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
      queryClient.invalidateQueries({ queryKey: ["activities"] });
    }
  });
}
