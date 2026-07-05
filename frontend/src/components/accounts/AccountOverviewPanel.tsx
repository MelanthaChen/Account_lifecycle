import { RefreshCw } from "lucide-react";

import { Button } from "../ui/button";
import { StatusBadge } from "../ui/badge";
import { useSyncAccountProfile } from "../../hooks/useAccounts";
import { useToast } from "../../store/useToast";
import type { Account } from "../../types/account";

export function AccountOverviewPanel({ account }: { account: Account }) {
  const syncProfile = useSyncAccountProfile(account.id);
  const { notify } = useToast();

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
