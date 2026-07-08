import { api } from "./client";
import type { AccountRecommendation } from "../types/recommendation";

export async function listRecommendations(): Promise<AccountRecommendation[]> {
  const response = await api.get<AccountRecommendation[]>("/recommendations");
  return response.data;
}

export async function listAccountRecommendations(accountId: string): Promise<AccountRecommendation[]> {
  const response = await api.get<AccountRecommendation[]>(`/accounts/${accountId}/recommendations`);
  return response.data;
}

export async function evaluateAllRecommendations(): Promise<AccountRecommendation[]> {
  const response = await api.post<AccountRecommendation[]>("/recommendations/evaluate-all");
  return response.data;
}

export async function evaluateAccountRecommendations(accountId: string): Promise<AccountRecommendation[]> {
  const response = await api.post<AccountRecommendation[]>(`/accounts/${accountId}/recommendations/evaluate`);
  return response.data;
}

export async function dismissRecommendation(recommendationId: string): Promise<AccountRecommendation> {
  const response = await api.post<AccountRecommendation>(`/recommendations/${recommendationId}/dismiss`);
  return response.data;
}
