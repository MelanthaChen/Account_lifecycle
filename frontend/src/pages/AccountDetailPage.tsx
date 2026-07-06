import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import { AccountActivityPanel } from "../components/accounts/AccountActivityPanel";
import { AccountOverviewPanel } from "../components/accounts/AccountOverviewPanel";
import { AccountSessionPanel } from "../components/accounts/AccountSessionPanel";
import {
  AccountWorkspaceTabs,
  type AccountWorkspaceTab
} from "../components/accounts/AccountWorkspaceTabs";
import { Button } from "../components/ui/button";
import { useAccount } from "../hooks/useAccounts";

export function AccountDetailPage() {
  const navigate = useNavigate();
  const { accountId = "" } = useParams();
  const account = useAccount(accountId);
  const [activeTab, setActiveTab] = useState<AccountWorkspaceTab>("overview");

  if (account.isLoading) {
    return <StatePanel title="Loading account..." />;
  }

  if (account.isError || !account.data) {
    return <StatePanel title="Account not found." tone="error" />;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Button type="button" variant="ghost" className="-ml-3 mb-2" onClick={() => navigate("/accounts")}>
            <ArrowLeft size={16} />
            Accounts
          </Button>
          <h1 className="text-2xl font-semibold">{account.data.nickname}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {account.data.platform} account workspace for {account.data.username}
          </p>
        </div>
      </div>

      <AccountWorkspaceTabs activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "overview" ? <AccountOverviewPanel account={account.data} /> : null}
      {activeTab === "session" ? <AccountSessionPanel account={account.data} /> : null}
      {activeTab === "activity" ? <AccountActivityPanel account={account.data} /> : null}
      {activeTab === "publishing" ? <PlaceholderPanel title="Publishing" /> : null}
      {activeTab === "analytics" ? <PlaceholderPanel title="Analytics" /> : null}
      {activeTab === "settings" ? <PlaceholderPanel title="Settings" /> : null}
    </div>
  );
}

function PlaceholderPanel({ title }: { title: string }) {
  return (
    <section className="rounded-md border border-border bg-white p-10 text-center">
      <div className="text-sm font-medium">{title}</div>
      <div className="mt-1 text-sm text-muted-foreground">Coming Soon</div>
    </section>
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
