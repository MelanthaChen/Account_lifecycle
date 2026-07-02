import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createAccount,
  deleteAccount,
  getAccount,
  getAccountAnalytics,
  listAccounts,
  listSyncJobs,
  syncAccount,
  updateAccount
} from "../api/accounts";
import type { AccountInput } from "../types/account";

export function useAccounts(search?: string) {
  return useQuery({ queryKey: ["accounts", search], queryFn: () => listAccounts(search) });
}

export function useAccount(accountId: string) {
  return useQuery({ queryKey: ["account", accountId], queryFn: () => getAccount(accountId) });
}

export function useAccountAnalytics(accountId: string) {
  return useQuery({
    queryKey: ["account", accountId, "analytics"],
    queryFn: () => getAccountAnalytics(accountId)
  });
}

export function useSyncJobs(accountId: string) {
  return useQuery({ queryKey: ["account", accountId, "sync-jobs"], queryFn: () => listSyncJobs(accountId) });
}

export function useCreateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["accounts"] })
  });
}

export function useUpdateAccount(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: Partial<AccountInput>) => updateAccount(accountId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId] });
    }
  });
}

export function useDeleteAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["accounts"] })
  });
}

export function useSyncAccount(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => syncAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["account", accountId] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId, "sync-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId, "analytics"] });
    }
  });
}

export function useSyncAnyAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: syncAccount,
    onSuccess: (_, accountId) => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId, "sync-jobs"] });
      queryClient.invalidateQueries({ queryKey: ["account", accountId, "analytics"] });
    }
  });
}
