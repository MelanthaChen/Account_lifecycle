export type CampaignStatus = "Draft" | "Ready" | "Running" | "Completed" | "Failed";
export type CampaignActionType = "UPVOTE";
export type WorkflowActionType = "OPEN_URL" | "WAIT" | "SCROLL" | "OPEN_POST" | "BACK" | "UPVOTE";

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
  id?: string;
  workflow_step_id?: string;
  action_type: WorkflowActionType;
  success: boolean;
  reason: string | null;
  detail: string | null;
}

export interface WorkflowAccountResult {
  account: string;
  steps: CampaignRunResult[];
}

export interface CampaignRunResponse {
  campaign_id: string;
  success: boolean;
  results: WorkflowAccountResult[];
}

export interface WorkflowStep {
  id: string;
  campaign_id: string;
  step_order: number;
  action_type: WorkflowActionType;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  campaign_id: string;
  steps: WorkflowStep[];
}

export interface WorkflowInputStep {
  action_type: WorkflowActionType;
  config: Record<string, unknown>;
}

export interface WorkflowInput {
  steps: WorkflowInputStep[];
}
