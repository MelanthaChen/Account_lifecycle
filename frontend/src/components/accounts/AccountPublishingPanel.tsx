import { ExternalLink, MessageSquare, RefreshCw, ThumbsUp } from "lucide-react";

import { useAutomationJobs } from "../../hooks/useAutomationJobs";
import type { Account } from "../../types/account";
import type { AutomationJob } from "../../types/automationJob";
import { Button } from "../ui/button";

export function AccountPublishingPanel({ account }: { account: Account }) {
  const jobs = useAutomationJobs({ limit: 200 });
  const accountJobs = (jobs.data ?? []).filter(
    (job) => job.account_id === account.id && ["COMMENT", "UPVOTE", "WORKFLOW"].includes(job.job_type)
  );

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Publishing Actions</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Queue-backed comment and vote operations executed for this account.
          </p>
        </div>
        <Button type="button" variant="secondary" onClick={() => jobs.refetch()}>
          <RefreshCw size={16} className={jobs.isFetching ? "animate-spin" : ""} />
          Refresh
        </Button>
      </div>

      {jobs.isLoading ? (
        <StatePanel title="Loading publishing jobs..." />
      ) : jobs.isError ? (
        <StatePanel title="Unable to load publishing jobs." tone="error" />
      ) : accountJobs.length === 0 ? (
        <StatePanel title="No publishing jobs recorded for this account." />
      ) : (
        <div className="overflow-hidden rounded-md border border-border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-3 py-3">Action</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3">Target</th>
                <th className="px-3 py-3">Queued</th>
                <th className="px-3 py-3">Finished</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {accountJobs.map((job) => (
                <tr key={job.id}>
                  <td className="px-3 py-3">
                    <div className="flex items-center gap-2 font-medium">
                      {job.job_type === "COMMENT" ? <MessageSquare size={15} /> : <ThumbsUp size={15} />}
                      {job.job_type}
                    </div>
                  </td>
                  <td className="px-3 py-3">{job.status}</td>
                  <td className="max-w-md truncate px-3 py-3">{targetUrl(job)}</td>
                  <td className="px-3 py-3">{formatDate(job.queued_at)}</td>
                  <td className="px-3 py-3">{formatDate(job.completed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function targetUrl(job: AutomationJob) {
  const payload = job.result_json?.payload;
  if (isRecord(payload) && typeof payload.url === "string") {
    return payload.url;
  }
  if (typeof job.result_json?.target_url === "string") {
    return job.result_json.target_url;
  }
  const metadata = job.result_json?.metadata;
  if (isRecord(metadata) && typeof metadata.target_url === "string") {
    return metadata.target_url;
  }
  return "No target URL recorded";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Not finished";
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-10 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-10 text-center text-sm text-muted-foreground"
      }
    >
      <ExternalLink className="mx-auto mb-2 text-muted-foreground" size={18} />
      {title}
    </div>
  );
}
