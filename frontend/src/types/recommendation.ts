export type RecommendationStatus = "ACTIVE" | "DISMISSED" | "COMPLETED";
export type RecommendationPriority = "HIGH" | "MEDIUM" | "LOW";
export type RecommendationType =
  | "RUN_WARM_UP"
  | "RUN_QUICK_UPVOTE"
  | "RUN_CASUAL_READER"
  | "RUN_DEEP_READER"
  | "SYNC_PROFILE"
  | "REFRESH_SESSION"
  | "NO_ACTION";

export interface AccountRecommendation {
  id: string;
  account_id: string;
  recommendation_type: RecommendationType;
  priority: RecommendationPriority;
  title: string;
  description: string;
  recommended_template_id: string | null;
  status: RecommendationStatus;
  reason: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
