export type HealthStatus = "HEALTHY" | "WARNING" | "CRITICAL";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export interface HealthSignals {
  session_valid?: boolean;
  profile_synced?: boolean;
  email_verified?: boolean;
  reddit_username?: boolean;
  account_age_days?: number | null;
  post_karma?: number | null;
  comment_karma?: number | null;
  last_activity_hours?: number | null;
  workflow_success_rate?: number | null;
}

export interface AccountHealth {
  id: string;
  account_id: string;
  health_score: number;
  health_status: HealthStatus;
  risk_level: RiskLevel;
  signals: HealthSignals;
  last_evaluated_at: string;
  created_at: string;
  updated_at: string;
}
