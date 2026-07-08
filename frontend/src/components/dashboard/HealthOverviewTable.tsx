import { useNavigate } from "react-router-dom";

import { HealthStatusBadge, RiskBadge } from "../health/HealthBadges";
import { DashboardEmptyState, DashboardSection } from "./DashboardSection";
import type { Account } from "../../types/account";
import type { AccountHealth } from "../../types/health";

interface HealthOverviewTableProps {
  accounts: Account[];
  health: AccountHealth[];
  isError: boolean;
  isLoading: boolean;
}

export function HealthOverviewTable({ accounts, health, isError, isLoading }: HealthOverviewTableProps) {
  const navigate = useNavigate();
  const accountMap = new Map(accounts.map((account) => [account.id, account]));
  const rows = health
    .map((record) => ({ record, account: accountMap.get(record.account_id) }))
    .sort((left, right) => left.record.health_score - right.record.health_score);

  return (
    <DashboardSection
      title="Account Health Overview"
      description="Lowest scores appear first so operational risk stays visible."
    >
      {isLoading ? (
        <DashboardEmptyState>Loading health...</DashboardEmptyState>
      ) : isError ? (
        <DashboardEmptyState>Unable to load health.</DashboardEmptyState>
      ) : rows.length === 0 ? (
        <DashboardEmptyState>No health evaluations yet.</DashboardEmptyState>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="bg-muted/60 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Account</th>
                <th className="px-4 py-3">Health Score</th>
                <th className="px-4 py-3">Health Status</th>
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Last Evaluated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows.map(({ account, record }) => (
                <tr
                  key={record.id}
                  className="cursor-pointer transition hover:bg-muted/60"
                  onClick={() => navigate(`/accounts/${record.account_id}`)}
                >
                  <td className="px-4 py-3 font-medium">{account?.nickname ?? record.account_id}</td>
                  <td className="px-4 py-3">
                    <span className={scoreClass(record.health_score)}>{record.health_score}</span>
                  </td>
                  <td className="px-4 py-3">
                    <HealthStatusBadge status={record.health_status} />
                  </td>
                  <td className="px-4 py-3">
                    <RiskBadge risk={record.risk_level} />
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(record.last_evaluated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardSection>
  );
}

function scoreClass(score: number) {
  if (score >= 80) {
    return "font-semibold text-emerald-700";
  }
  if (score >= 50) {
    return "font-semibold text-amber-700";
  }
  return "font-semibold text-red-700";
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
