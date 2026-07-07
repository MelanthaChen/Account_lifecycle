import { api } from "./client";

export interface UpvoteRequest {
  account_ids: string[];
  target_url: string;
}

export interface UpvoteResult {
  account: string;
  opened: boolean;
}

export interface UpvoteResponse {
  success: boolean;
  results: UpvoteResult[];
}

export async function createUpvoteRequest(input: UpvoteRequest): Promise<UpvoteResponse> {
  const response = await api.post<UpvoteResponse>("/upvote", input);
  return response.data;
}
