import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createCampaign, deleteCampaign, listCampaigns, runCampaign } from "../api/campaigns";

export function useCampaigns() {
  return useQuery({ queryKey: ["campaigns"], queryFn: listCampaigns });
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
