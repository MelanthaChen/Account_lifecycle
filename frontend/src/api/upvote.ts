import { api } from "./client";

export interface UpvoteRequest {
  account_id: string;
  target_url: string;
}

export interface UpvoteResponse {
  status: "received";
  target_url: string;
  account_id: string;
}

export async function createUpvoteRequest(input: UpvoteRequest): Promise<UpvoteResponse> {
  const response = await api.post<UpvoteResponse>("/upvote", input);
  return response.data;
}
