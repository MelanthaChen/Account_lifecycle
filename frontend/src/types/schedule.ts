export type ScheduleType = "ONCE" | "DAILY" | "WEEKLY" | "CUSTOM_CRON";

export interface CampaignSchedule {
  id: string;
  campaign_id: string;
  enabled: boolean;
  schedule_type: ScheduleType;
  cron_expression: string | null;
  timezone: string;
  next_run_at: string | null;
  last_run_at: string | null;
  last_status: string | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignScheduleInput {
  enabled: boolean;
  schedule_type: ScheduleType;
  cron_expression?: string | null;
  timezone: string;
  next_run_at?: string | null;
}
