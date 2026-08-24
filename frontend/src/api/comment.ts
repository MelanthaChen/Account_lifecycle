import { api } from "./client";

export type CommentSource = "MANUAL_TEXT" | "AI_GENERATE" | "BEHAVIOR_TEMPLATE";

export interface CommentRequest {
  type: "COMMENT";
  payload: {
    url: string;
    text: string;
  };
  account_ids: string[];
}

export interface CommentJob {
  id: string;
  account_id: string;
  account: string;
  status: "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED";
}

export interface CommentResponse {
  success: boolean;
  type: "COMMENT";
  payload: {
    url: string;
    text: string;
  };
  jobs: CommentJob[];
}

export async function createCommentRequest(input: CommentRequest): Promise<CommentResponse> {
  const response = await api.post<CommentResponse>("/comment", input);
  return response.data;
}
