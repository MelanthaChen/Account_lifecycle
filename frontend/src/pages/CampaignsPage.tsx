import { FormEvent, useMemo, useState } from "react";
import { ClipboardList, Eye, Play, Plus, RefreshCw, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { useAccounts } from "../hooks/useAccounts";
import { useCampaigns, useCreateCampaign, useDeleteCampaign, useRunCampaign } from "../hooks/useCampaigns";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { Account } from "../types/account";
import type { Campaign, CampaignRunResponse, CampaignStatus } from "../types/campaign";

export function CampaignsPage() {
  const campaigns = useCampaigns();
  const accounts = useAccounts();
  const createCampaign = useCreateCampaign();
  const deleteCampaign = useDeleteCampaign();
  const runCampaign = useRunCampaign();
  const { notify } = useToast();
  const [isCreating, setIsCreating] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    target_url: "",
    account_ids: [] as string[]
  });
  const [lastRun, setLastRun] = useState<CampaignRunResponse | null>(null);

  const activeAccounts = useMemo(
    () => (accounts.data ?? []).filter((account) => account.is_active),
    [accounts.data]
  );
  const selectedAccounts = activeAccounts.filter((account) => form.account_ids.includes(account.id));
  const allSelected = activeAccounts.length > 0 && selectedAccounts.length === activeAccounts.length;

  function toggleAllAccounts(checked: boolean) {
    setForm((current) => ({
      ...current,
      account_ids: checked ? activeAccounts.map((account) => account.id) : []
    }));
  }

  function toggleAccount(accountId: string, checked: boolean) {
    setForm((current) => ({
      ...current,
      account_ids: checked
        ? current.account_ids.includes(accountId)
          ? current.account_ids
          : [...current.account_ids, accountId]
        : current.account_ids.filter((id) => id !== accountId)
    }));
  }

  function resetForm() {
    setForm({ name: "", description: "", target_url: "", account_ids: [] });
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (form.account_ids.length === 0) {
      notify("Select at least one account.", "error");
      return;
    }
    createCampaign.mutate(
      {
        name: form.name.trim(),
        description: form.description.trim() || null,
        platform: "reddit",
        action_type: "UPVOTE",
        target_url: form.target_url.trim(),
        account_ids: form.account_ids
      },
      {
        onSuccess: () => {
          notify("Campaign saved.", "success");
          resetForm();
          setIsCreating(false);
        },
        onError: () => notify("Unable to save campaign.", "error")
      }
    );
  }

  function runSelectedCampaign(campaign: Campaign) {
    setLastRun(null);
    runCampaign.mutate(campaign.id, {
      onSuccess: (response) => {
        setLastRun(response);
        notify(response.success ? "Campaign completed." : "Campaign finished with failures.", response.success ? "success" : "error");
      },
      onError: () => notify("Unable to run campaign.", "error")
    });
  }

  function removeCampaign(campaign: Campaign) {
    deleteCampaign.mutate(campaign.id, {
      onSuccess: () => notify("Campaign deleted.", "success"),
      onError: () => notify("Unable to delete campaign.", "error")
    });
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Campaigns</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Save reusable Reddit execution plans and run them sequentially.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={() => campaigns.refetch()}>
            <RefreshCw size={16} className={campaigns.isFetching ? "animate-spin" : ""} />
            Refresh
          </Button>
          <Button type="button" onClick={() => setIsCreating((value) => !value)}>
            <Plus size={16} />
            New Campaign
          </Button>
        </div>
      </div>

      {isCreating ? (
        <form onSubmit={handleSubmit} className="space-y-5 rounded-md border border-border bg-white p-5">
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Campaign Name">
              <Input
                required
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              />
            </Field>
            <Field label="Action Type">
              <select
                value="UPVOTE"
                disabled
                className="flex h-10 w-full rounded-md border border-input bg-muted px-3 text-sm outline-none"
              >
                <option value="UPVOTE">UPVOTE</option>
              </select>
            </Field>
          </div>
          <Field label="Description">
            <Textarea
              value={form.description}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
            />
          </Field>
          <Field label="Target URL">
            <Input
              type="url"
              required
              placeholder="https://www.reddit.com/r/test/"
              value={form.target_url}
              onChange={(event) => setForm((current) => ({ ...current, target_url: event.target.value }))}
            />
          </Field>
          <AccountSelector
            accounts={activeAccounts}
            selectedIds={form.account_ids}
            allSelected={allSelected}
            isLoading={accounts.isLoading}
            onToggleAll={toggleAllAccounts}
            onToggleAccount={toggleAccount}
          />
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={createCampaign.isPending || form.account_ids.length === 0}>
              Save
            </Button>
            <Button type="button" variant="secondary" onClick={() => setIsCreating(false)}>
              Cancel
            </Button>
          </div>
        </form>
      ) : null}

      {campaigns.isLoading ? (
        <StatePanel title="Loading campaigns..." />
      ) : campaigns.isError ? (
        <StatePanel title="Unable to load campaigns." tone="error" />
      ) : (campaigns.data ?? []).length === 0 ? (
        <StatePanel title="No campaigns yet." />
      ) : (
        <div className="grid gap-4">
          {(campaigns.data ?? []).map((campaign) => (
            <CampaignCard
              key={campaign.id}
              campaign={campaign}
              accounts={activeAccounts}
              isRunning={runCampaign.isPending}
              isDeleting={deleteCampaign.isPending}
              onRun={() => runSelectedCampaign(campaign)}
              onDelete={() => removeCampaign(campaign)}
            />
          ))}
        </div>
      )}

      {lastRun ? <RunResultPanel run={lastRun} /> : null}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="space-y-2">
      <span className="text-sm font-medium">{label}</span>
      {children}
    </label>
  );
}

function AccountSelector({
  accounts,
  selectedIds,
  allSelected,
  isLoading,
  onToggleAll,
  onToggleAccount
}: {
  accounts: Account[];
  selectedIds: string[];
  allSelected: boolean;
  isLoading: boolean;
  onToggleAll: (checked: boolean) => void;
  onToggleAccount: (accountId: string, checked: boolean) => void;
}) {
  return (
    <div className="space-y-3">
      <div className="text-sm font-medium">Accounts</div>
      <div className="rounded-md border border-border bg-white">
        <label className="flex cursor-pointer items-center gap-3 border-b border-border px-3 py-2 text-sm font-medium">
          <input
            type="checkbox"
            checked={allSelected}
            disabled={isLoading || accounts.length === 0}
            onChange={(event) => onToggleAll(event.target.checked)}
            className="h-4 w-4 rounded border-border"
          />
          All Accounts
        </label>
        <div className="max-h-64 overflow-y-auto">
          {accounts.map((account) => (
            <label key={account.id} className="flex cursor-pointer items-center gap-3 px-3 py-2 text-sm hover:bg-muted">
              <input
                type="checkbox"
                checked={selectedIds.includes(account.id)}
                onChange={(event) => onToggleAccount(account.id, event.target.checked)}
                className="h-4 w-4 rounded border-border"
              />
              <span className="min-w-0 truncate">{account.nickname}</span>
              <span className="text-xs text-muted-foreground">{account.username}</span>
            </label>
          ))}
        </div>
      </div>
      {selectedIds.length === 0 ? <p className="text-xs text-muted-foreground">Select at least one account.</p> : null}
    </div>
  );
}

function CampaignCard({
  campaign,
  accounts,
  isRunning,
  isDeleting,
  onRun,
  onDelete
}: {
  campaign: Campaign;
  accounts: Account[];
  isRunning: boolean;
  isDeleting: boolean;
  onRun: () => void;
  onDelete: () => void;
}) {
  const selectedNames = accounts
    .filter((account) => campaign.account_ids.includes(account.id))
    .map((account) => account.nickname)
    .join(", ");
  return (
    <article className="rounded-md border border-border bg-white p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <ClipboardList size={17} className="text-muted-foreground" />
            <h2 className="text-base font-semibold">{campaign.name}</h2>
            <StatusBadge status={campaign.status} />
          </div>
          {campaign.description ? <p className="text-sm text-muted-foreground">{campaign.description}</p> : null}
          <div className="break-all text-sm">{campaign.target_url}</div>
          <div className="text-xs text-muted-foreground">
            {campaign.action_type} · {selectedNames || `${campaign.account_ids.length} account(s)`}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" onClick={onRun} disabled={isRunning}>
            <Play size={16} />
            {isRunning ? "Running..." : "Run"}
          </Button>
          <Link
            to={`/campaigns/${campaign.id}`}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium transition hover:bg-muted"
          >
            <Eye size={16} />
            Open
          </Link>
          <Button type="button" variant="danger" onClick={onDelete} disabled={isDeleting}>
            <Trash2 size={16} />
            Delete
          </Button>
        </div>
      </div>
    </article>
  );
}

function StatusBadge({ status }: { status: CampaignStatus }) {
  const classes: Record<CampaignStatus, string> = {
    Draft: "bg-gray-100 text-gray-700",
    Ready: "bg-blue-50 text-blue-700",
    Running: "bg-amber-50 text-amber-700",
    Completed: "bg-emerald-50 text-emerald-700",
    Failed: "bg-red-50 text-red-700"
  };
  return <span className={cn("rounded px-2 py-1 text-xs font-medium", classes[status])}>{status}</span>;
}

function RunResultPanel({ run }: { run: CampaignRunResponse }) {
  return (
    <section className="rounded-md border border-border bg-white p-5">
      <div className="mb-4">
        <h2 className="text-base font-semibold">Run Result</h2>
        <p className="text-sm text-muted-foreground">Campaign {run.campaign_id}</p>
      </div>
      <div className="divide-y divide-border">
        {run.results.map((accountResult) => (
          <div key={accountResult.account} className="py-3 text-sm">
            <div className="font-medium">{accountResult.account}</div>
            <div className="mt-2 space-y-1">
              {accountResult.steps.map((step) => (
                <div key={step.action_type} className="flex items-center justify-between gap-4">
                  <span>{step.action_type}</span>
                  <span className={step.success ? "text-emerald-700" : "text-red-700"}>
                    {step.success ? "Success" : formatReason(step.reason ?? "failed")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
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

function formatReason(reason: string) {
  const labels: Record<string, string> = {
    login_required: "Login Required",
    button_not_found: "Button Not Found",
    click_failed: "Click Failed",
    verification_failed: "Verification Failed",
    navigation_failed: "Navigation Failed",
    account_not_found: "Account Not Found"
  };
  return labels[reason] ?? reason;
}
