export type CampaignStatus = "Draft" | "Ready" | "Running" | "Completed" | "Failed";
export type CampaignActionType = "UPVOTE";

export interface Campaign {
  id: string;
  name: string;
  description: string | null;
  platform: "reddit";
  action_type: CampaignActionType;
  target_url: string;
  status: CampaignStatus;
  account_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface CampaignInput {
  name: string;
  description?: string | null;
  platform: "reddit";
  action_type: CampaignActionType;
  target_url: string;
  account_ids: string[];
}

export interface CampaignRunResult {
  account: string;
  opened: boolean;
  clicked: boolean;
  verified: boolean;
  reason: string | null;
}

export interface CampaignRunResponse {
  campaign: Campaign;
  success: boolean;
  results: CampaignRunResult[];
}
