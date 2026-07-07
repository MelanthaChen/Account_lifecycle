import { api } from "./client";
import type { Campaign, CampaignInput, CampaignRunResponse } from "../types/campaign";

export async function listCampaigns(): Promise<Campaign[]> {
  const response = await api.get<Campaign[]>("/campaigns");
  return response.data;
}

export async function createCampaign(input: CampaignInput): Promise<Campaign> {
  const response = await api.post<Campaign>("/campaigns", input);
  return response.data;
}

export async function deleteCampaign(campaignId: string): Promise<void> {
  await api.delete(`/campaigns/${campaignId}`);
}

export async function runCampaign(campaignId: string): Promise<CampaignRunResponse> {
  const response = await api.post<CampaignRunResponse>(`/campaigns/${campaignId}/run`);
  return response.data;
}
