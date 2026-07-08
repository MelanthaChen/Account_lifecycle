import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  dismissRecommendation,
  evaluateAccountRecommendations,
  evaluateAllRecommendations,
  listAccountRecommendations,
  listRecommendations
} from "../api/recommendations";

export function useRecommendations() {
  return useQuery({ queryKey: ["recommendations"], queryFn: listRecommendations });
}

export function useAccountRecommendations(accountId: string) {
  return useQuery({
    queryKey: ["recommendations", accountId],
    queryFn: () => listAccountRecommendations(accountId),
    enabled: Boolean(accountId)
  });
}

export function useEvaluateAllRecommendations() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: evaluateAllRecommendations,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["health"] });
    }
  });
}

export function useEvaluateAccountRecommendations(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => evaluateAccountRecommendations(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["recommendations", accountId] });
      queryClient.invalidateQueries({ queryKey: ["health"] });
      queryClient.invalidateQueries({ queryKey: ["health", accountId] });
    }
  });
}

export function useDismissRecommendation(accountId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: dismissRecommendation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      if (accountId) {
        queryClient.invalidateQueries({ queryKey: ["recommendations", accountId] });
      }
    }
  });
}
