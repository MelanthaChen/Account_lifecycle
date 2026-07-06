import type { Platform } from "./account";

export type ActivityStatus = "PENDING" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED";

export type ActivityType =
  | "LOGIN"
  | "OPEN_BROWSER"
  | "OPEN_HOME"
  | "BROWSE"
  | "UPVOTE"
  | "DOWNVOTE"
  | "COMMENT"
  | "POST"
  | "JOIN_SUBREDDIT"
  | "LEAVE_SUBREDDIT"
  | "SYNC_PROFILE"
  | "VALIDATE_SESSION"
  | "REFRESH_SESSION"
  | "DELETE_SESSION";

export interface Activity {
  id: string;
  account_id: string;
  platform: Platform;
  activity_type: ActivityType;
  status: ActivityStatus;
  target_url: string | null;
  title: string | null;
  metadata: Record<string, unknown> | null;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  created_at: string;
  updated_at: string;
}

export interface ActivityFilters {
  accountId?: string;
  limit?: number;
  offset?: number;
  activity_type?: ActivityType;
  status?: ActivityStatus;
}
