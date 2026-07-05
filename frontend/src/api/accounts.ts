import { api } from "./client";
import type { Account, AccountInput } from "../types/account";

export async function listAccounts() {
  const response = await api.get<Account[]>("/accounts");
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

export async function syncAccountProfile(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/sync-profile`);
  return response.data;
}

export async function createAccountSession(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/session/create`);
  return response.data;
}

export async function finishAccountSession(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/session/finish`);
  return response.data;
}

export async function validateAccountSession(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/session/validate`);
  return response.data;
}

export async function refreshAccountSession(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/session/refresh`);
  return response.data;
}

export async function deleteAccountSession(accountId: string) {
  const response = await api.delete<Account>(`/accounts/${accountId}/session`);
  return response.data;
}

export async function openAccountBrowser(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/browser/open`);
  return response.data;
}

export async function openAccountHome(accountId: string) {
  const response = await api.post<Account>(`/accounts/${accountId}/browser/open-home`);
  return response.data;
}
