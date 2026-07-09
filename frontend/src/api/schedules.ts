import { api } from "./client";
import type { CampaignRunResponse } from "../types/campaign";
import type { CampaignSchedule, CampaignScheduleInput } from "../types/schedule";

export async function listSchedules(): Promise<CampaignSchedule[]> {
  const response = await api.get<CampaignSchedule[]>("/schedules");
  return response.data;
}

export async function getCampaignSchedule(campaignId: string): Promise<CampaignSchedule> {
  const response = await api.get<CampaignSchedule>(`/campaigns/${campaignId}/schedule`);
  return response.data;
}

export async function createCampaignSchedule(
  campaignId: string,
  input: CampaignScheduleInput
): Promise<CampaignSchedule> {
  const response = await api.post<CampaignSchedule>(`/campaigns/${campaignId}/schedule`, input);
  return response.data;
}

export async function updateCampaignSchedule(
  campaignId: string,
  input: CampaignScheduleInput
): Promise<CampaignSchedule> {
  const response = await api.put<CampaignSchedule>(`/campaigns/${campaignId}/schedule`, input);
  return response.data;
}

export async function deleteCampaignSchedule(campaignId: string): Promise<void> {
  await api.delete(`/campaigns/${campaignId}/schedule`);
}

export async function runCampaignScheduleNow(campaignId: string): Promise<CampaignRunResponse> {
  const response = await api.post<CampaignRunResponse>(`/campaigns/${campaignId}/schedule/run-now`);
  return response.data;
}
