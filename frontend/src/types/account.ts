export type AccountStatus = "active" | "paused" | "error" | "archived";
export type Platform = "reddit";

export interface Account {
  id: string;
  nickname: string;
  reddit_username: string;
  status: AccountStatus;
  platform: Platform;
  created_at: string;
  updated_at: string;
  last_sync: string | null;
  notes: string | null;
  is_active: boolean;
}

export interface AccountInput {
  nickname: string;
  reddit_username: string;
  status: AccountStatus;
  notes?: string | null;
  is_active: boolean;
}

export interface AccountAnalytics {
  account_id: string;
  total_posts: number;
  total_comments: number;
  total_score: number;
  top_subreddits: Array<{ name: string; activity_count: number }>;
  activity_by_day: Array<{ day: string; activity: number }>;
}

export interface SyncJob {
  id: string;
  account_id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  started_at: string | null;
  finished_at: string | null;
  error: string | null;
  created_at: string;
}
