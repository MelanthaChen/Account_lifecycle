import { api } from "./client";

export interface UpvoteRequest {
  account_ids: string[];
  target_url: string;
}

export interface UpvoteResult {
  id: string;
  account_id: string;
  account: string;
  status: "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED";
}

export interface UpvoteResponse {
  success: boolean;
  target_url: string;
  jobs: UpvoteResult[];
}

export async function createUpvoteRequest(input: UpvoteRequest): Promise<UpvoteResponse> {
  const response = await api.post<UpvoteResponse>("/upvote", input);
  return response.data;
}
