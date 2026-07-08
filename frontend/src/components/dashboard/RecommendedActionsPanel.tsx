import { ArrowRight, ClipboardPlus } from "lucide-react";
import { Link } from "react-router-dom";

import { RecommendationPriorityBadge } from "../recommendations/RecommendationBadges";
import { Button } from "../ui/button";
import { DashboardEmptyState, DashboardSection } from "./DashboardSection";
import type { Account } from "../../types/account";
import type { BehaviorTemplate } from "../../types/behaviorTemplate";
import type { AccountRecommendation } from "../../types/recommendation";

interface RecommendedActionsPanelProps {
  accounts: Account[];
  isError: boolean;
  isLoading: boolean;
  recommendations: AccountRecommendation[];
  templates: BehaviorTemplate[];
}

export function RecommendedActionsPanel({
  accounts,
  isError,
  isLoading,
  recommendations,
  templates
}: RecommendedActionsPanelProps) {
  const accountMap = new Map(accounts.map((account) => [account.id, account]));
  const templateMap = new Map(templates.map((template) => [template.id, template]));
  const activeRecommendations = recommendations
    .filter((recommendation) => recommendation.status === "ACTIVE")
    .slice(0, 6);

  return (
    <DashboardSection title="Recommended Actions" description="Rule-based next steps from account health signals.">
      {isLoading ? (
        <DashboardEmptyState>Loading recommendations...</DashboardEmptyState>
      ) : isError ? (
        <DashboardEmptyState>Unable to load recommendations.</DashboardEmptyState>
      ) : activeRecommendations.length === 0 ? (
        <DashboardEmptyState>No recommendations.</DashboardEmptyState>
      ) : (
        <div className="grid gap-3 p-4 lg:grid-cols-2">
          {activeRecommendations.map((recommendation) => {
            const account = accountMap.get(recommendation.account_id);
            const template = recommendation.recommended_template_id
              ? templateMap.get(recommendation.recommended_template_id)
              : undefined;
            return (
              <article key={recommendation.id} className="rounded-md border border-border bg-background p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <RecommendationPriorityBadge priority={recommendation.priority} />
                  <span className="text-xs font-medium uppercase text-muted-foreground">
                    {account?.nickname ?? "Unknown account"}
                  </span>
                </div>
                <h3 className="mt-3 text-sm font-semibold">{recommendation.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{recommendation.description}</p>
                <dl className="mt-3 grid gap-2 text-xs text-muted-foreground">
                  <div>
                    <dt className="font-medium text-foreground">Reason</dt>
                    <dd>{formatReason(recommendation.reason.rule)}</dd>
                  </div>
                  <div>
                    <dt className="font-medium text-foreground">Suggested Behavior Template</dt>
                    <dd>{template?.name ?? "No template required"}</dd>
                  </div>
                </dl>
                <div className="mt-4 flex flex-wrap gap-2">
                  <Link
                    to={`/accounts/${recommendation.account_id}`}
                    className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium transition hover:bg-muted"
                  >
                    Open Account
                    <ArrowRight size={15} />
                  </Link>
                  <Link to="/campaigns">
                    <Button type="button" variant="secondary">
                      <ClipboardPlus size={15} />
                      Create Campaign
                    </Button>
                  </Link>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </DashboardSection>
  );
}

function formatReason(value: unknown) {
  if (typeof value !== "string") {
    return "Rule-based recommendation";
  }
  return value.replaceAll("_", " ");
}
