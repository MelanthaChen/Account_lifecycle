import { RefreshCw, X } from "lucide-react";

import { Button } from "../components/ui/button";
import {
  RecommendationPriorityBadge,
  RecommendationStatusBadge
} from "../components/recommendations/RecommendationBadges";
import { useAccounts } from "../hooks/useAccounts";
import {
  useDismissRecommendation,
  useEvaluateAllRecommendations,
  useRecommendations
} from "../hooks/useRecommendations";
import { useToast } from "../store/useToast";
import type { Account } from "../types/account";
import type { AccountRecommendation } from "../types/recommendation";

export function RecommendationsPage() {
  const accounts = useAccounts();
  const recommendations = useRecommendations();
  const evaluateAll = useEvaluateAllRecommendations();
  const dismiss = useDismissRecommendation();
  const { notify } = useToast();
  const accountMap = new Map((accounts.data ?? []).map((account) => [account.id, account]));

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Recommendations</h1>
          <p className="mt-1 text-sm text-muted-foreground">Rule-based next-best actions for managed accounts.</p>
        </div>
        <Button
          type="button"
          disabled={evaluateAll.isPending}
          onClick={() =>
            evaluateAll.mutate(undefined, {
              onSuccess: () => notify("Recommendations evaluated for all accounts.", "success"),
              onError: () => notify("Unable to evaluate recommendations.", "error")
            })
          }
        >
          <RefreshCw size={16} className={evaluateAll.isPending ? "animate-spin" : ""} />
          {evaluateAll.isPending ? "Evaluating..." : "Evaluate All"}
        </Button>
      </div>

      {recommendations.isLoading || accounts.isLoading ? (
        <StatePanel title="Loading recommendations..." />
      ) : recommendations.isError || accounts.isError ? (
        <StatePanel title="Unable to load recommendations." tone="error" />
      ) : (recommendations.data ?? []).length === 0 ? (
        <StatePanel title="No recommendations yet. Run Evaluate All." />
      ) : (
        <div className="space-y-3">
          {(recommendations.data ?? []).map((recommendation) => (
            <RecommendationCard
              key={recommendation.id}
              account={accountMap.get(recommendation.account_id)}
              recommendation={recommendation}
              dismissing={dismiss.isPending}
              onDismiss={() =>
                dismiss.mutate(recommendation.id, {
                  onSuccess: () => notify("Recommendation dismissed.", "success"),
                  onError: () => notify("Unable to dismiss recommendation.", "error")
                })
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}

function RecommendationCard({
  account,
  dismissing,
  onDismiss,
  recommendation
}: {
  account?: Account;
  dismissing: boolean;
  onDismiss: () => void;
  recommendation: AccountRecommendation;
}) {
  const isActive = recommendation.status === "ACTIVE";
  return (
    <article className="rounded-md border border-border bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold">{recommendation.title}</h2>
            <RecommendationPriorityBadge priority={recommendation.priority} />
            <RecommendationStatusBadge status={recommendation.status} />
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{recommendation.description}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
            <span>{account?.nickname ?? recommendation.account_id}</span>
            <span>{recommendation.recommendation_type}</span>
            {recommendation.recommended_template_id ? <span>Template linked</span> : null}
          </div>
        </div>
        {isActive ? (
          <Button type="button" variant="secondary" disabled={dismissing} onClick={onDismiss}>
            <X size={16} />
            Dismiss
          </Button>
        ) : null}
      </div>
    </article>
  );
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-12 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-12 text-center text-sm text-muted-foreground"
      }
    >
      {title}
    </div>
  );
}
