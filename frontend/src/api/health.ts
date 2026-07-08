import { api } from "./client";
import type { AccountHealth } from "../types/health";

export async function listHealth(): Promise<AccountHealth[]> {
  const response = await api.get<AccountHealth[]>("/health");
  return response.data;
}

export async function getAccountHealth(accountId: string): Promise<AccountHealth> {
  const response = await api.get<AccountHealth>(`/accounts/${accountId}/health`);
  return response.data;
}

export async function evaluateAccountHealth(accountId: string): Promise<AccountHealth> {
  const response = await api.post<AccountHealth>(`/accounts/${accountId}/health/evaluate`);
  return response.data;
}

export async function evaluateAllHealth(): Promise<AccountHealth[]> {
  const response = await api.post<AccountHealth[]>("/health/evaluate-all");
  return response.data;
}
