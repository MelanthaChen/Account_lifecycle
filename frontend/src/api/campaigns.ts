import { api } from "./client";
import type { Campaign, CampaignInput, CampaignRunResponse, Workflow, WorkflowInput } from "../types/campaign";

export async function listCampaigns(): Promise<Campaign[]> {
  const response = await api.get<Campaign[]>("/campaigns");
  return response.data;
}

export async function getCampaign(campaignId: string): Promise<Campaign> {
  const response = await api.get<Campaign>(`/campaigns/${campaignId}`);
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

export async function getCampaignWorkflow(campaignId: string): Promise<Workflow> {
  const response = await api.get<Workflow>(`/campaigns/${campaignId}/workflow`);
  return response.data;
}

export async function replaceCampaignWorkflow(campaignId: string, input: WorkflowInput): Promise<Workflow> {
  const response = await api.put<Workflow>(`/campaigns/${campaignId}/workflow`, input);
  return response.data;
}

export async function runCampaignWorkflow(campaignId: string): Promise<CampaignRunResponse> {
  const response = await api.post<CampaignRunResponse>(`/campaigns/${campaignId}/workflow/run`);
  return response.data;
}
