import { Eye, Play } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../ui/button";
import { DashboardEmptyState, DashboardSection } from "./DashboardSection";
import { cn } from "../../lib/utils";
import type { Account } from "../../types/account";
import type { Campaign, CampaignStatus } from "../../types/campaign";

interface RecentCampaignsTableProps {
  accounts: Account[];
  campaigns: Campaign[];
  isError: boolean;
  isLoading: boolean;
  isRunning: boolean;
  onRun: (campaign: Campaign) => void;
}

export function RecentCampaignsTable({
  accounts,
  campaigns,
  isError,
  isLoading,
  isRunning,
  onRun
}: RecentCampaignsTableProps) {
  const recentCampaigns = [...campaigns]
    .sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime())
    .slice(0, 6);

  return (
    <DashboardSection title="Recent Campaigns" description="Latest reusable execution plans.">
      {isLoading ? (
        <DashboardEmptyState>Loading campaigns...</DashboardEmptyState>
      ) : isError ? (
        <DashboardEmptyState>Unable to load campaigns.</DashboardEmptyState>
      ) : recentCampaigns.length === 0 ? (
        <DashboardEmptyState>No campaigns yet.</DashboardEmptyState>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="bg-muted/60 text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-4 py-3">Campaign</th>
                <th className="px-4 py-3">Accounts</th>
                <th className="px-4 py-3">Behavior Template</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recentCampaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td className="max-w-[220px] truncate px-4 py-3 font-medium">{campaign.name}</td>
                  <td className="px-4 py-3 text-muted-foreground">{accountNames(campaign, accounts)}</td>
                  <td className="px-4 py-3 text-muted-foreground">Workflow</td>
                  <td className="px-4 py-3">
                    <CampaignStatusBadge status={campaign.status} />
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(campaign.created_at)}</td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Button type="button" variant="secondary" disabled={isRunning} onClick={() => onRun(campaign)}>
                        <Play size={15} />
                        Run Again
                      </Button>
                      <Link
                        to={`/campaigns/${campaign.id}`}
                        className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium transition hover:bg-muted"
                      >
                        <Eye size={15} />
                        Open
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardSection>
  );
}

function CampaignStatusBadge({ status }: { status: CampaignStatus }) {
  const classes: Record<CampaignStatus, string> = {
    Draft: "bg-gray-100 text-gray-700",
    Ready: "bg-blue-50 text-blue-700",
    Running: "bg-amber-50 text-amber-700",
    Completed: "bg-emerald-50 text-emerald-700",
    Failed: "bg-red-50 text-red-700"
  };
  return <span className={cn("rounded px-2 py-1 text-xs font-medium", classes[status])}>{status}</span>;
}

function accountNames(campaign: Campaign, accounts: Account[]) {
  const names = accounts
    .filter((account) => campaign.account_ids.includes(account.id))
    .map((account) => account.nickname);
  return names.length ? names.join(", ") : `${campaign.account_ids.length} account(s)`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
