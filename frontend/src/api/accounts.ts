import { api } from "./client";
import type { Account, AccountAnalytics, AccountInput, SyncJob } from "../types/account";

export async function listAccounts(search?: string) {
  const response = await api.get<Account[]>("/accounts", { params: { search: search || undefined } });
  return response.data;
}

export async function getAccount(accountId: string) {
  const response = await api.get<Account>(`/accounts/${accountId}`);
  return response.data;
}

export async function createAccount(input: AccountInput) {
  const response = await api.post<Account>("/accounts", input);
  return response.data;
}

export async function updateAccount(accountId: string, input: Partial<AccountInput>) {
  const response = await api.patch<Account>(`/accounts/${accountId}`, input);
  return response.data;
}

export async function deleteAccount(accountId: string) {
  await api.delete(`/accounts/${accountId}`);
}

export async function syncAccount(accountId: string) {
  const response = await api.post<SyncJob>(`/accounts/${accountId}/sync`);
  return response.data;
}

export async function listSyncJobs(accountId: string) {
  const response = await api.get<SyncJob[]>(`/accounts/${accountId}/sync/jobs`);
  return response.data;
}

export async function getAccountAnalytics(accountId: string) {
  const response = await api.get<AccountAnalytics>(`/accounts/${accountId}/analytics`);
  return response.data;
}
