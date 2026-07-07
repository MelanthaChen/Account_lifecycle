import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCampaign,
  deleteCampaign,
  getCampaign,
  getCampaignWorkflow,
  listCampaigns,
  replaceCampaignWorkflow,
  runCampaign,
  runCampaignWorkflow
} from "../api/campaigns";
import type { WorkflowInput } from "../types/campaign";

export function useCampaigns() {
  return useQuery({ queryKey: ["campaigns"], queryFn: listCampaigns });
}

export function useCampaign(campaignId: string) {
  return useQuery({
    queryKey: ["campaigns", campaignId],
    queryFn: () => getCampaign(campaignId),
    enabled: Boolean(campaignId)
  });
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCampaign,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
}

export function useDeleteCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteCampaign,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
}

export function useRunCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: runCampaign,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["campaigns"] })
  });
}

export function useCampaignWorkflow(campaignId: string) {
  return useQuery({
    queryKey: ["campaigns", campaignId, "workflow"],
    queryFn: () => getCampaignWorkflow(campaignId),
    enabled: Boolean(campaignId)
  });
}

export function useReplaceCampaignWorkflow(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: WorkflowInput) => replaceCampaignWorkflow(campaignId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "workflow"] });
    }
  });
}

export function useRunCampaignWorkflow(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => runCampaignWorkflow(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "workflow"] });
    }
  });
}
