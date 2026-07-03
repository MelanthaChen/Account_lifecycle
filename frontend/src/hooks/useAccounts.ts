import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createAccount,
  deleteAccount,
  deleteAccountSession,
  getAccount,
  listAccounts,
  loginAccount,
  logoutAccountSession,
  openAccountBrowser,
  openAccountHome,
  refreshAccountSession,
  updateAccount,
  validateAccountSession
} from "../api/accounts";
import type { AccountInput, AccountLoginInput } from "../types/account";

export function useAccounts() {
  return useQuery({ queryKey: ["accounts"], queryFn: listAccounts });
}

export function useAccount(accountId: string) {
  return useQuery({
    queryKey: ["accounts", accountId],
    queryFn: () => getAccount(accountId),
    enabled: Boolean(accountId)
  });
}

export function useCreateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createAccount,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["accounts"] })
  });
}

export function useUpdateAccount() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ accountId, input }: { accountId: string; input: Partial<AccountInput> }) =>
      updateAccount(accountId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["accounts"] });
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

function invalidateAccount(queryClient: ReturnType<typeof useQueryClient>, accountId: string) {
  queryClient.invalidateQueries({ queryKey: ["accounts"] });
  queryClient.invalidateQueries({ queryKey: ["accounts", accountId] });
}

export function useLoginAccount(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: AccountLoginInput) => loginAccount(accountId, input),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useValidateAccountSession(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => validateAccountSession(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useRefreshAccountSession(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => refreshAccountSession(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useDeleteAccountSession(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteAccountSession(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useLogoutAccountSession(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => logoutAccountSession(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useOpenAccountBrowser(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => openAccountBrowser(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}

export function useOpenAccountHome(accountId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => openAccountHome(accountId),
    onSuccess: () => invalidateAccount(queryClient, accountId)
  });
}
