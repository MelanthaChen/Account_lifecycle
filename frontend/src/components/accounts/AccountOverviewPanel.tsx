import { Lightbulb, RefreshCw, X } from "lucide-react";

import { Button } from "../ui/button";
import { HealthStatusBadge, RiskBadge } from "../health/HealthBadges";
import {
  RecommendationPriorityBadge,
  RecommendationStatusBadge
} from "../recommendations/RecommendationBadges";
import { StatusBadge } from "../ui/badge";
import { useSyncAccountProfile } from "../../hooks/useAccounts";
import { useAccountHealth, useEvaluateAccountHealth } from "../../hooks/useHealth";
import {
  useAccountRecommendations,
  useDismissRecommendation,
  useEvaluateAccountRecommendations
} from "../../hooks/useRecommendations";
import { useToast } from "../../store/useToast";
import type { Account } from "../../types/account";

export function AccountOverviewPanel({ account }: { account: Account }) {
  const syncProfile = useSyncAccountProfile(account.id);
  const health = useAccountHealth(account.id);
  const evaluateHealth = useEvaluateAccountHealth(account.id);
  const recommendations = useAccountRecommendations(account.id);
  const evaluateRecommendations = useEvaluateAccountRecommendations(account.id);
  const dismissRecommendation = useDismissRecommendation(account.id);
  const { notify } = useToast();
  const activeRecommendations = (recommendations.data ?? []).filter(
    (recommendation) => recommendation.status === "ACTIVE"
  );

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 rounded-md border border-border bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          {account.avatar_url ? (
            <img
              src={account.avatar_url}
              alt=""
              className="h-14 w-14 flex-none rounded-full border border-border object-cover"
            />
          ) : (
            <div className="flex h-14 w-14 flex-none items-center justify-center rounded-full border border-border bg-muted text-sm font-semibold text-muted-foreground">
              {account.nickname.slice(0, 2).toUpperCase()}
            </div>
          )}
          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold">{account.display_name ?? account.nickname}</h2>
            <p className="mt-0.5 text-sm text-muted-foreground">
              u/{account.reddit_username ?? account.username}
            </p>
          </div>
        </div>
        <Button
          type="button"
          disabled={syncProfile.isPending}
          onClick={() =>
            syncProfile.mutate(undefined, {
              onSuccess: () => notify("Profile synced.", "success"),
              onError: () => notify("Unable to sync profile.", "error")
            })
          }
        >
          <RefreshCw size={16} className={syncProfile.isPending ? "animate-spin" : ""} />
          {syncProfile.isPending ? "Syncing..." : "Sync Profile"}
        </Button>
      </div>

      <div className="rounded-md border border-border bg-white p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-medium uppercase text-muted-foreground">Health</div>
            {health.data ? (
              <div className="mt-2 flex flex-wrap items-center gap-3">
                <div className="text-3xl font-semibold">{health.data.health_score}</div>
                <HealthStatusBadge status={health.data.health_status} />
                <RiskBadge risk={health.data.risk_level} />
              </div>
            ) : (
              <div className="mt-2 text-sm text-muted-foreground">
                {health.isLoading ? "Loading health..." : "Not evaluated"}
              </div>
            )}
          </div>
          <Button
            type="button"
            variant="secondary"
            disabled={evaluateHealth.isPending}
            onClick={() =>
              evaluateHealth.mutate(undefined, {
                onSuccess: () => notify("Health evaluated.", "success"),
                onError: () => notify("Unable to evaluate health.", "error")
              })
            }
          >
            <RefreshCw size={16} className={evaluateHealth.isPending ? "animate-spin" : ""} />
            {evaluateHealth.isPending ? "Evaluating..." : "Evaluate Health"}
          </Button>
        </div>
        {health.data ? (
          <div className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
            <HealthSignal label="Session" value={health.data.signals.session_valid ? "Valid" : "Invalid"} />
            <HealthSignal label="Profile" value={health.data.signals.profile_synced ? "Synced" : "Not synced"} />
            <HealthSignal label="Risk" value={health.data.risk_level} />
          </div>
        ) : null}
      </div>

      <div className="rounded-md border border-border bg-white p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-medium uppercase text-muted-foreground">Recommendations</div>
            <div className="mt-2 text-sm text-muted-foreground">
              {recommendations.isLoading
                ? "Loading recommendations..."
                : activeRecommendations.length
                  ? `${activeRecommendations.length} active recommendation${activeRecommendations.length === 1 ? "" : "s"}`
                  : "No active recommendations"}
            </div>
          </div>
          <Button
            type="button"
            variant="secondary"
            disabled={evaluateRecommendations.isPending}
            onClick={() =>
              evaluateRecommendations.mutate(undefined, {
                onSuccess: () => notify("Recommendations evaluated.", "success"),
                onError: () => notify("Unable to evaluate recommendations.", "error")
              })
            }
          >
            <RefreshCw size={16} className={evaluateRecommendations.isPending ? "animate-spin" : ""} />
            {evaluateRecommendations.isPending ? "Evaluating..." : "Evaluate Recommendations"}
          </Button>
        </div>
        {activeRecommendations.length ? (
          <div className="mt-4 space-y-2">
            {activeRecommendations.slice(0, 3).map((recommendation) => (
              <div key={recommendation.id} className="rounded-md bg-muted px-3 py-3">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <Lightbulb size={15} className="text-muted-foreground" />
                      <span className="font-medium">{recommendation.title}</span>
                      <RecommendationPriorityBadge priority={recommendation.priority} />
                      <RecommendationStatusBadge status={recommendation.status} />
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{recommendation.description}</p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    disabled={dismissRecommendation.isPending}
                    onClick={() =>
                      dismissRecommendation.mutate(recommendation.id, {
                        onSuccess: () => notify("Recommendation dismissed.", "success"),
                        onError: () => notify("Unable to dismiss recommendation.", "error")
                      })
                    }
                  >
                    <X size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <DetailItem label="Nickname" value={account.nickname} />
        <DetailItem label="Platform" value={account.platform} className="capitalize" />
        <DetailItem label="Username" value={account.reddit_username ?? account.username} />
        <DetailItem label="Display Name" value={account.display_name ?? "Not synced"} />
        <DetailItem label="Post Karma" value={formatNumber(account.karma_post)} />
        <DetailItem label="Comment Karma" value={formatNumber(account.karma_comment)} />
        <DetailItem label="Cake Day" value={account.cake_day ?? "Not synced"} />
        <DetailItem label="Last Profile Sync" value={formatDate(account.last_profile_sync)} />
        <div className="rounded-md border border-border bg-white p-4">
          <div className="text-xs font-medium uppercase text-muted-foreground">Status</div>
          <div className="mt-2">
            <StatusBadge status={account.status} />
          </div>
        </div>
        <DetailItem label="Created" value={new Date(account.created_at).toLocaleString()} />
        <div className="rounded-md border border-border bg-white p-4 lg:col-span-2">
          <div className="text-xs font-medium uppercase text-muted-foreground">Notes</div>
          <div className="mt-2 text-sm text-foreground">{account.notes || "No notes."}</div>
        </div>
      </div>
    </section>
  );
}

function HealthSignal({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-muted px-3 py-2">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 font-medium">{value}</div>
    </div>
  );
}

function DetailItem({
  className,
  label,
  value
}: {
  className?: string;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className={["mt-2 text-sm font-medium text-foreground", className].filter(Boolean).join(" ")}>
        {value}
      </div>
    </div>
  );
}

function formatNumber(value: number | null) {
  return value === null ? "Not synced" : value.toLocaleString();
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Never";
}
