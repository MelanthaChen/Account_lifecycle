import { useNavigate, useParams } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowLeft, RefreshCw, Trash2 } from "lucide-react";

import { AccountForm } from "../components/AccountForm";
import { StatusBadge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  useAccount,
  useAccountAnalytics,
  useDeleteAccount,
  useSyncAccount,
  useSyncJobs,
  useUpdateAccount
} from "../hooks/useAccounts";

export function AccountDetailPage() {
  const { accountId = "" } = useParams();
  const navigate = useNavigate();
  const account = useAccount(accountId);
  const analytics = useAccountAnalytics(accountId);
  const jobs = useSyncJobs(accountId);
  const updateAccount = useUpdateAccount(accountId);
  const deleteAccount = useDeleteAccount();
  const sync = useSyncAccount(accountId);

  if (account.isLoading) {
    return <div className="py-16 text-center text-sm text-muted-foreground">Loading account...</div>;
  }

  if (!account.data) {
    return <div className="py-16 text-center text-sm text-muted-foreground">Account not found.</div>;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Button variant="ghost" className="-ml-3 mb-2" onClick={() => navigate("/")}>
            <ArrowLeft size={16} />
            Back
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold">{account.data.nickname}</h1>
            <StatusBadge status={account.data.status} />
          </div>
          <p className="mt-1 text-sm text-muted-foreground">u/{account.data.reddit_username}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" disabled={sync.isPending} onClick={() => sync.mutate()}>
            <RefreshCw size={16} className={sync.isPending ? "animate-spin" : ""} />
            Sync
          </Button>
          <Button
            variant="danger"
            onClick={() =>
              deleteAccount.mutate(accountId, {
                onSuccess: () => navigate("/")
              })
            }
          >
            <Trash2 size={16} />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-3">
            <Metric label="Posts" value={analytics.data?.total_posts ?? 0} />
            <Metric label="Comments" value={analytics.data?.total_comments ?? 0} />
            <Metric label="Total score" value={analytics.data?.total_score ?? 0} />
          </div>
          <div className="rounded-md border border-border bg-white p-4">
            <h2 className="text-sm font-semibold">Activity by day</h2>
            <div className="mt-4 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analytics.data?.activity_by_day ?? []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="activity" fill="#ef4d2f" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="rounded-md border border-border bg-white p-4">
            <h2 className="text-sm font-semibold">Top subreddits</h2>
            <div className="mt-4 space-y-3">
              {(analytics.data?.top_subreddits ?? []).map((subreddit) => (
                <div key={subreddit.name} className="flex items-center justify-between text-sm">
                  <span>r/{subreddit.name}</span>
                  <span className="font-medium">{subreddit.activity_count}</span>
                </div>
              ))}
              {analytics.data?.top_subreddits.length === 0 ? (
                <div className="text-sm text-muted-foreground">No subreddit activity yet.</div>
              ) : null}
            </div>
          </div>
        </section>
        <aside className="space-y-5">
          <div className="rounded-md border border-border bg-white p-4">
            <h2 className="mb-4 text-sm font-semibold">Account settings</h2>
            <AccountForm
              account={account.data}
              isPending={updateAccount.isPending}
              onSubmit={(input) => updateAccount.mutate(input)}
            />
          </div>
          <div className="rounded-md border border-border bg-white p-4">
            <h2 className="text-sm font-semibold">Sync jobs</h2>
            <div className="mt-4 space-y-3">
              {(jobs.data ?? []).map((job) => (
                <div key={job.id} className="rounded-md border border-border p-3 text-sm">
                  <div className="font-medium capitalize">{job.status}</div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(job.created_at).toLocaleString()}
                  </div>
                  {job.error ? <div className="mt-2 text-xs text-red-600">{job.error}</div> : null}
                </div>
              ))}
              {jobs.data?.length === 0 ? (
                <div className="text-sm text-muted-foreground">No sync jobs yet.</div>
              ) : null}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value.toLocaleString()}</div>
    </div>
  );
}
