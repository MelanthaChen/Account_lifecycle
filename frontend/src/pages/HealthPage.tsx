import { Fragment, useMemo, useState } from "react";
import { ChevronDown, ChevronRight, RefreshCw } from "lucide-react";

import { Button } from "../components/ui/button";
import { HealthStatusBadge, RiskBadge } from "../components/health/HealthBadges";
import { useAccounts } from "../hooks/useAccounts";
import { useEvaluateAllHealth, useHealth } from "../hooks/useHealth";
import { useToast } from "../store/useToast";
import type { Account } from "../types/account";
import type { AccountHealth, HealthSignals } from "../types/health";

export function HealthPage() {
  const accounts = useAccounts();
  const health = useHealth();
  const evaluateAll = useEvaluateAllHealth();
  const { notify } = useToast();
  const [expandedAccountId, setExpandedAccountId] = useState<string | null>(null);

  const rows = useMemo(() => {
    const accountMap = new Map((accounts.data ?? []).map((account) => [account.id, account]));
    return (health.data ?? []).map((record) => ({
      health: record,
      account: accountMap.get(record.account_id)
    }));
  }, [accounts.data, health.data]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Health</h1>
          <p className="mt-1 text-sm text-muted-foreground">Rule-based account health assessments.</p>
        </div>
        <Button
          type="button"
          disabled={evaluateAll.isPending}
          onClick={() =>
            evaluateAll.mutate(undefined, {
              onSuccess: () => notify("Health evaluated for all accounts.", "success"),
              onError: () => notify("Unable to evaluate health.", "error")
            })
          }
        >
          <RefreshCw size={16} className={evaluateAll.isPending ? "animate-spin" : ""} />
          {evaluateAll.isPending ? "Evaluating..." : "Evaluate All"}
        </Button>
      </div>

      {health.isLoading || accounts.isLoading ? (
        <StatePanel title="Loading health..." />
      ) : health.isError || accounts.isError ? (
        <StatePanel title="Unable to load health." tone="error" />
      ) : rows.length === 0 ? (
        <StatePanel title="No health evaluations yet. Run Evaluate All." />
      ) : (
        <div className="overflow-hidden rounded-md border border-border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted text-xs uppercase text-muted-foreground">
              <tr>
                <th className="w-10 px-3 py-3" />
                <th className="px-3 py-3">Account</th>
                <th className="px-3 py-3">Health Score</th>
                <th className="px-3 py-3">Health Status</th>
                <th className="px-3 py-3">Risk</th>
                <th className="px-3 py-3">Session</th>
                <th className="px-3 py-3">Email Verified</th>
                <th className="px-3 py-3">Karma</th>
                <th className="px-3 py-3">Last Evaluated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows.map(({ health: record, account }) => (
                <Fragment key={record.id}>
                  <tr className="align-top">
                    <td className="px-3 py-3">
                      <button
                        type="button"
                        aria-label="Toggle signals"
                        onClick={() =>
                          setExpandedAccountId(expandedAccountId === record.account_id ? null : record.account_id)
                        }
                      >
                        {expandedAccountId === record.account_id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      </button>
                    </td>
                    <td className="px-3 py-3 font-medium">{account?.nickname ?? record.account_id}</td>
                    <td className="px-3 py-3">{record.health_score}</td>
                    <td className="px-3 py-3"><HealthStatusBadge status={record.health_status} /></td>
                    <td className="px-3 py-3"><RiskBadge risk={record.risk_level} /></td>
                    <td className="px-3 py-3">{record.signals.session_valid ? "Valid" : "Invalid"}</td>
                    <td className="px-3 py-3">{record.signals.email_verified ? "Yes" : "No"}</td>
                    <td className="px-3 py-3">{formatKarma(record.signals)}</td>
                    <td className="px-3 py-3">{new Date(record.last_evaluated_at).toLocaleString()}</td>
                  </tr>
                  {expandedAccountId === record.account_id ? (
                    <tr>
                      <td colSpan={9} className="bg-muted/40 px-6 py-4">
                        <SignalsPanel record={record} account={account} />
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SignalsPanel({ record }: { record: AccountHealth; account?: Account }) {
  const signals = signalRows(record.signals);
  return (
    <div className="grid gap-2 md:grid-cols-2">
      {signals.map((signal) => (
        <div key={signal.label} className="flex items-center justify-between rounded-md bg-white px-3 py-2 text-sm">
          <span>{signal.label}</span>
          <span className={signal.ok ? "text-emerald-700" : "text-red-700"}>
            {signal.ok ? "✔" : "✘"} {signal.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function signalRows(signals: HealthSignals) {
  return [
    { label: "Session valid", ok: Boolean(signals.session_valid), value: signals.session_valid ? "Valid" : "Invalid" },
    { label: "Email verified", ok: Boolean(signals.email_verified), value: signals.email_verified ? "Yes" : "No" },
    { label: "Profile synced", ok: Boolean(signals.profile_synced), value: signals.profile_synced ? "Yes" : "No" },
    { label: "Username detected", ok: Boolean(signals.reddit_username), value: signals.reddit_username ? "Yes" : "No" },
    {
      label: "Workflow success rate",
      ok: signals.workflow_success_rate === null || signals.workflow_success_rate === undefined || signals.workflow_success_rate >= 0.8,
      value: signals.workflow_success_rate === null || signals.workflow_success_rate === undefined
        ? "No runs"
        : `${Math.round(signals.workflow_success_rate * 100)}%`
    },
    {
      label: "Recent activity",
      ok: signals.last_activity_hours !== null && signals.last_activity_hours !== undefined && signals.last_activity_hours <= 30 * 24,
      value: signals.last_activity_hours === null || signals.last_activity_hours === undefined
        ? "No activity in 30 days"
        : `${Math.round(signals.last_activity_hours)} hours ago`
    }
  ];
}

function formatKarma(signals: HealthSignals) {
  return `${signals.post_karma ?? 0} / ${signals.comment_karma ?? 0}`;
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
