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
}

export interface AccountInput {
  nickname: string;
  platform: Platform;
  username: string;
  status: AccountStatus;
  notes?: string | null;
  is_active: boolean;
}
