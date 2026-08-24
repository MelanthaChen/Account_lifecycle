import { api } from "./client";
import type { Account, AccountInput } from "../types/account";

export async function listAccounts() {
  const response = await api.get<unknown>("/accounts");
  return assertAccounts(response.data);
}

export async function getAccount(accountId: string) {
  const response = await api.get<unknown>(`/accounts/${accountId}`);
  return assertAccount(response.data);
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

function assertAccounts(value: unknown): Account[] {
  if (!Array.isArray(value)) {
    throw new Error("Account list response was not JSON array data.");
  }
  return value.map(assertAccount);
}

function assertAccount(value: unknown): Account {
  if (!isRecord(value)) {
    throw new Error("Account response was not JSON object data.");
  }
  if (
    typeof value.id !== "string" ||
    typeof value.nickname !== "string" ||
    typeof value.username !== "string" ||
    value.platform !== "reddit" ||
    !["active", "paused", "error", "archived"].includes(String(value.status))
  ) {
    throw new Error("Account response did not match the frontend account contract.");
  }
  return value as unknown as Account;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
