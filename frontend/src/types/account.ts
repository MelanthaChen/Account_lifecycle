export type AccountStatus = "active" | "paused" | "error" | "archived";
export type Platform = "reddit";

export interface Account {
  id: string;
  nickname: string;
  username: string;
  status: AccountStatus;
  platform: Platform;
  created_at: string;
  updated_at: string;
  last_sync: string | null;
  notes: string | null;
  is_active: boolean;
  session_path: string | null;
  session_status: string | null;
  last_login: string | null;
  last_validation: string | null;
  browser_profile: string | null;
  provider: string | null;
  browser_profile_path: string | null;
  storage_directory: string | null;
  launch_visible_browser: boolean;
}

export interface AccountInput {
  nickname: string;
  platform: Platform;
  username: string;
  status: AccountStatus;
  notes?: string | null;
  is_active: boolean;
  provider?: string | null;
  launch_visible_browser: boolean;
}
