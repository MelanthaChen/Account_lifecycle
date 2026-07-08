import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { evaluateAccountHealth, evaluateAllHealth, getAccountHealth, listHealth } from "../api/health";

export function useHealth() {
  return useQuery({ queryKey: ["health"], queryFn: listHealth });
}

export function useAccountHealth(accountId: string) {
  return useQuery({
    queryKey: ["health", accountId],
    queryFn: () => getAccountHealth(accountId),
    enabled: Boolean(accountId)
  });
}

export function useEvaluateAccountHealth(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => evaluateAccountHealth(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["health"] });
      queryClient.invalidateQueries({ queryKey: ["health", accountId] });
    }
  });
}

export function useEvaluateAllHealth() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: evaluateAllHealth,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["health"] })
  });
}
