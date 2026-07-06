import { FormEvent, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Clock3, ExternalLink, Loader2, Send, ThumbsUp } from "lucide-react";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useAccounts } from "../hooks/useAccounts";
import { useCreateUpvoteRequest } from "../hooks/useUpvote";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { Account } from "../types/account";

interface LogEntry {
  id: number;
  message: string;
  tone: "default" | "success" | "error";
}

export function UpvotePage() {
  const accounts = useAccounts();
  const createRequest = useCreateUpvoteRequest();
  const { notify } = useToast();
  const [targetUrl, setTargetUrl] = useState("");
  const [accountId, setAccountId] = useState("");
  const [lastStatus, setLastStatus] = useState<"idle" | "received" | "error">("idle");
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: 1,
      message: "Waiting for an upvote request.",
      tone: "default"
    }
  ]);

  const activeAccounts = useMemo(
    () => (accounts.data ?? []).filter((account) => account.is_active),
    [accounts.data]
  );
  const selectedAccount = activeAccounts.find((account) => account.id === accountId) ?? null;

  function appendLog(message: string, tone: LogEntry["tone"] = "default") {
    setLogs((current) => [{ id: Date.now(), message, tone }, ...current].slice(0, 20));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!accountId || !targetUrl.trim()) {
      setLastStatus("error");
      appendLog("Target URL and account are required.", "error");
      notify("Target URL and account are required.", "error");
      return;
    }

    appendLog(`Submitting request for ${selectedAccount?.nickname ?? "selected account"}.`);
    createRequest.mutate(
      {
        account_id: accountId,
        target_url: targetUrl.trim()
      },
      {
        onSuccess: (response) => {
          setLastStatus("received");
          appendLog(`API accepted ${response.target_url}.`, "success");
          notify("Upvote request received.", "success");
        },
        onError: () => {
          setLastStatus("error");
          appendLog("API rejected the request. Check the URL and try again.", "error");
          notify("Unable to submit upvote request.", "error");
        }
      }
    );
  }

  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Upvote</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Prepare an upvote request for future execution.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <form onSubmit={handleSubmit} className="space-y-5 rounded-md border border-border bg-white p-5">
          <div className="space-y-2">
            <label htmlFor="target-url" className="text-sm font-medium">
              Target URL
            </label>
            <Input
              id="target-url"
              type="url"
              required
              placeholder="https://www.reddit.com/r/example/comments/..."
              value={targetUrl}
              onChange={(event) => setTargetUrl(event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="account" className="text-sm font-medium">
              Account
            </label>
            <select
              id="account"
              required
              value={accountId}
              onChange={(event) => setAccountId(event.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-white px-3 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/20 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={accounts.isLoading}
            >
              <option value="">{accounts.isLoading ? "Loading accounts..." : "Select account"}</option>
              {activeAccounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {formatAccountLabel(account)}
                </option>
              ))}
            </select>
            {accounts.isError ? (
              <p className="text-xs text-red-600">Unable to load accounts.</p>
            ) : activeAccounts.length === 0 && !accounts.isLoading ? (
              <p className="text-xs text-muted-foreground">No active accounts are available.</p>
            ) : null}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="submit"
              disabled={createRequest.isPending || accounts.isLoading || activeAccounts.length === 0}
            >
              {createRequest.isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              {createRequest.isPending ? "Submitting..." : "Start"}
            </Button>
            <span className="text-xs text-muted-foreground">MVP contract only. No Reddit action is executed.</span>
          </div>
        </form>

        <StatusCard status={lastStatus} account={selectedAccount} targetUrl={targetUrl} />
      </div>

      <section className="rounded-md border border-border bg-white">
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Clock3 size={16} className="text-muted-foreground" />
          <h2 className="text-sm font-semibold">Execution Log</h2>
        </div>
        <div className="divide-y divide-border">
          {logs.map((entry) => (
            <div key={entry.id} className="flex items-start gap-3 px-4 py-3 text-sm">
              <span
                className={cn(
                  "mt-1 h-2 w-2 flex-none rounded-full",
                  entry.tone === "success"
                    ? "bg-emerald-500"
                    : entry.tone === "error"
                      ? "bg-red-500"
                      : "bg-muted-foreground"
                )}
              />
              <span className={entry.tone === "error" ? "text-red-700" : "text-foreground"}>
                {entry.message}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function StatusCard({
  status,
  account,
  targetUrl
}: {
  status: "idle" | "received" | "error";
  account: Account | null;
  targetUrl: string;
}) {
  const statusConfig = {
    idle: {
      label: "Ready",
      description: "Submit a target URL and account to test the API contract.",
      icon: ThumbsUp,
      className: "border-border bg-white text-foreground"
    },
    received: {
      label: "Received",
      description: "The backend accepted the request and returned the expected response.",
      icon: CheckCircle2,
      className: "border-emerald-200 bg-emerald-50 text-emerald-800"
    },
    error: {
      label: "Needs Attention",
      description: "The request was not accepted. Review the form values.",
      icon: AlertCircle,
      className: "border-red-200 bg-red-50 text-red-800"
    }
  }[status];
  const Icon = statusConfig.icon;

  return (
    <aside className={cn("rounded-md border p-5", statusConfig.className)}>
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-white/70">
          <Icon size={18} />
        </div>
        <div>
          <h2 className="text-sm font-semibold">{statusConfig.label}</h2>
          <p className="mt-1 text-xs opacity-80">{statusConfig.description}</p>
        </div>
      </div>
      <div className="mt-5 space-y-3 text-sm">
        <StatusRow label="Account" value={account ? formatAccountLabel(account) : "None selected"} />
        <StatusRow label="Target" value={targetUrl.trim() || "No URL entered"} isUrl={Boolean(targetUrl.trim())} />
      </div>
    </aside>
  );
}

function StatusRow({ label, value, isUrl = false }: { label: string; value: string; isUrl?: boolean }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 flex min-w-0 items-center gap-2 break-all">
        <span>{value}</span>
        {isUrl ? <ExternalLink size={14} className="flex-none opacity-60" /> : null}
      </div>
    </div>
  );
}

function formatAccountLabel(account: Account) {
  return `${account.nickname} (${account.platform}:${account.username})`;
}
