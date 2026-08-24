import { FormEvent, useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Clock3, ExternalLink, Loader2, Send, ThumbsUp } from "lucide-react";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useAccounts } from "../hooks/useAccounts";
import { useAutomationJobs } from "../hooks/useAutomationJobs";
import { useCreateUpvoteRequest } from "../hooks/useUpvote";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { Account } from "../types/account";
import type { AutomationJob } from "../types/automationJob";

interface LogEntry {
  id: number;
  message: string;
  tone: "default" | "success" | "error";
}

export function UpvotePage() {
  const accounts = useAccounts();
  const createRequest = useCreateUpvoteRequest();
  const automationJobs = useAutomationJobs({ limit: 200 });
  const { notify } = useToast();
  const [targetUrl, setTargetUrl] = useState("");
  const [accountIds, setAccountIds] = useState<string[]>([]);
  const [jobIds, setJobIds] = useState<string[]>([]);
  const [queuedJobs, setQueuedJobs] = useState<AutomationJob[]>([]);
  const [lastStatus, setLastStatus] = useState<"idle" | "running" | "success" | "error">("idle");
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: 1,
      message: "Waiting for an upvote execution.",
      tone: "default"
    }
  ]);

  const activeAccounts = useMemo(
    () => (accounts.data ?? []).filter((account) => account.is_active),
    [accounts.data]
  );
  const selectedAccounts = activeAccounts.filter((account) => accountIds.includes(account.id));
  const allSelected = activeAccounts.length > 0 && selectedAccounts.length === activeAccounts.length;
  const trackedJobs = useMemo(() => {
    if (jobIds.length === 0) {
      return [];
    }
    const latestJobs = automationJobs.data ?? [];
    return jobIds.map((jobId) => latestJobs.find((job) => job.id === jobId) ?? queuedJobs.find((job) => job.id === jobId)).filter(Boolean) as AutomationJob[];
  }, [automationJobs.data, jobIds, queuedJobs]);

  useEffect(() => {
    if (jobIds.length === 0 || trackedJobs.length === 0) {
      return;
    }

    setLogs(buildJobLogs(trackedJobs));
    const allFinished = trackedJobs.every((job) => ["SUCCESS", "FAILED", "CANCELLED"].includes(job.status));
    if (!allFinished) {
      setLastStatus("running");
      return;
    }

    const allSucceeded = trackedJobs.every((job) => {
      const result = readUpvoteResult(job);
      return job.status === "SUCCESS" && result?.opened === true && result?.clicked === true;
    });
    setLastStatus(allSucceeded ? "success" : "error");
  }, [jobIds.length, trackedJobs]);

  function appendLog(message: string, tone: LogEntry["tone"] = "default") {
    setLogs((current) => [{ id: Date.now() + Math.random(), message, tone }, ...current].slice(0, 40));
  }

  function toggleAllAccounts(checked: boolean) {
    setAccountIds(checked ? activeAccounts.map((account) => account.id) : []);
  }

  function toggleAccount(accountId: string, checked: boolean) {
    setAccountIds((current) => {
      if (checked) {
        return current.includes(accountId) ? current : [...current, accountId];
      }
      return current.filter((id) => id !== accountId);
    });
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (accountIds.length === 0 || !targetUrl.trim()) {
      setLastStatus("error");
      appendLog("Target URL and at least one account are required.", "error");
      notify("Target URL and at least one account are required.", "error");
      return;
    }

    setLastStatus("running");
    setLogs([{ id: Date.now(), message: "Creating automation jobs...", tone: "default" }]);
    createRequest.mutate(
      {
        account_ids: accountIds,
        target_url: targetUrl.trim()
      },
      {
        onSuccess: (response) => {
          const jobs = response.jobs.map((job) => ({
            ...job,
            job_type: "UPVOTE",
            campaign_id: null,
            workflow_id: null,
            queued_at: new Date().toISOString(),
            started_at: null,
            completed_at: null,
            worker_id: null,
            result_json: {
              target_url: response.target_url,
              account: job.account,
              logs: [{ message: `Queued upvote job for ${job.account}.`, level: "info" }]
            },
            error: null
          }));
          setQueuedJobs(jobs);
          setJobIds(response.jobs.map((job) => job.id));
          setLogs(buildJobLogs(jobs));
          notify("Upvote jobs queued for the automation agent.", "success");
          void automationJobs.refetch();
        },
        onError: () => {
          setLastStatus("error");
          appendLog("Execution failed. Check account sessions and the target URL.", "error");
          notify("Unable to execute upvote preparation.", "error");
        }
      }
    );
  }

  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Upvote</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Open a Reddit URL with selected account sessions and click one upvote control.
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

          <div className="space-y-3">
            <div className="text-sm font-medium">Accounts</div>
            <div className="rounded-md border border-border bg-white">
              <label className="flex cursor-pointer items-center gap-3 border-b border-border px-3 py-2 text-sm font-medium">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={(event) => toggleAllAccounts(event.target.checked)}
                  disabled={accounts.isLoading || activeAccounts.length === 0}
                  className="h-4 w-4 rounded border-border"
                />
                All Accounts
              </label>
              <div className="max-h-64 overflow-y-auto">
                {activeAccounts.map((account) => (
                  <label
                    key={account.id}
                    className="flex cursor-pointer items-center gap-3 px-3 py-2 text-sm hover:bg-muted"
                  >
                    <input
                      type="checkbox"
                      checked={accountIds.includes(account.id)}
                      onChange={(event) => toggleAccount(account.id, event.target.checked)}
                      className="h-4 w-4 rounded border-border"
                    />
                    <span className="min-w-0 truncate">{formatAccountLabel(account)}</span>
                  </label>
                ))}
              </div>
            </div>
            {accounts.isError ? (
              <p className="text-xs text-red-600">Unable to load accounts.</p>
            ) : activeAccounts.length === 0 && !accounts.isLoading ? (
              <p className="text-xs text-muted-foreground">No active accounts are available.</p>
            ) : accountIds.length === 0 ? (
              <p className="text-xs text-muted-foreground">Select at least one account.</p>
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
            <span className="text-xs text-muted-foreground">Runs selected accounts sequentially.</span>
          </div>
        </form>

        <StatusCard status={lastStatus} accounts={selectedAccounts} targetUrl={targetUrl} />
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
  accounts,
  targetUrl
}: {
  status: "idle" | "running" | "success" | "error";
  accounts: Account[];
  targetUrl: string;
}) {
  const statusConfig = {
    idle: {
      label: "Ready",
      description: "Submit a target URL and one or more accounts.",
      icon: ThumbsUp,
      className: "border-border bg-white text-foreground"
    },
    running: {
      label: "Running",
      description: "Selected accounts are being processed sequentially.",
      icon: Loader2,
      className: "border-blue-200 bg-blue-50 text-blue-800"
    },
    success: {
      label: "Complete",
      description: "The upvote action completed for the selected accounts.",
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
        <StatusRow label="Accounts" value={formatSelectedAccounts(accounts)} />
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

function formatSelectedAccounts(accounts: Account[]) {
  if (accounts.length === 0) {
    return "None selected";
  }
  return accounts.map((account) => account.nickname).join(", ");
}

function formatReason(reason: string | null) {
  const labels: Record<string, string> = {
    login_required: "Login required",
    button_not_found: "Button not found",
    click_failed: "Click failed",
    verification_failed: "Verification failed",
    navigation_failed: "Navigation failed",
    account_not_found: "Account not found"
  };
  return reason ? (labels[reason] ?? reason) : "Execution failed";
}

function buildJobLogs(jobs: AutomationJob[]): LogEntry[] {
  const entries: LogEntry[] = jobs.flatMap((job) => {
    const account = readAccountName(job);
    const payloadLogs = readPayloadLogs(job);
    if (payloadLogs.length > 0) {
      return payloadLogs.map((entry, index) => ({
        id: stableLogId(job.id, index),
        message: `${account}: ${entry.message}`,
        tone: logTone(entry.level)
      }));
    }
    return [
      {
        id: stableLogId(job.id, 0),
        message: `${account}: ${job.status.toLowerCase()}.`,
        tone: job.status === "FAILED" || job.status === "CANCELLED" ? "error" : "default"
      }
    ];
  });
  return entries.reverse();
}

function readPayloadLogs(job: AutomationJob): Array<{ message: string; level?: string }> {
  const logs = job.result_json?.logs;
  if (!Array.isArray(logs)) {
    if (job.status === "RUNNING") {
      return [{ message: "Automation agent is running this job.", level: "info" }];
    }
    if (job.status === "QUEUED") {
      return [{ message: "Waiting for an automation agent.", level: "info" }];
    }
    if (job.error) {
      return [{ message: job.error, level: "error" }];
    }
    return [];
  }
  const parsedLogs: Array<{ message: string; level?: string }> = [];
  logs.forEach((entry) => {
    if (!entry || typeof entry !== "object") {
      return;
    }
      const value = entry as Record<string, unknown>;
      const message = String(value.message ?? "");
      if (!message) {
        return;
      }
      parsedLogs.push({
        message: String(value.message ?? ""),
        level: typeof value.level === "string" ? value.level : undefined
      });
  });
  return parsedLogs;
}

function readUpvoteResult(job: AutomationJob) {
  const result = job.result_json?.result;
  if (!result || typeof result !== "object") {
    return null;
  }
  return result as { opened?: boolean; clicked?: boolean; verified?: boolean; reason?: string | null };
}

function readAccountName(job: AutomationJob) {
  const result = readUpvoteResult(job);
  if (result && "account" in result && typeof result.account === "string") {
    return result.account;
  }
  const account = job.result_json?.account;
  return typeof account === "string" ? account : job.account_id;
}

function logTone(level?: string): LogEntry["tone"] {
  if (level === "success") {
    return "success";
  }
  if (level === "error") {
    return "error";
  }
  return "default";
}

function stableLogId(jobId: string, index: number) {
  let total = index;
  for (const character of jobId) {
    total = (total * 31 + character.charCodeAt(0)) % Number.MAX_SAFE_INTEGER;
  }
  return total;
}
