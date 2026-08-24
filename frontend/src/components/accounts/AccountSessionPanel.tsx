import { useEffect, useMemo, useRef, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  ExternalLink,
  Eye,
  Play,
  RefreshCw,
  ShieldCheck,
  Trash2
} from "lucide-react";

import { Button } from "../ui/button";
import {
  useCreateAccountSession,
  useDeleteAccountSession,
  useFinishAccountSession,
  useOpenAccountBrowser,
  useOpenAccountHome,
  useRefreshAccountSession,
  useValidateAccountSession
} from "../../hooks/useAccounts";
import { useAutomationJobs } from "../../hooks/useAutomationJobs";
import { cn } from "../../lib/utils";
import { useToast } from "../../store/useToast";
import type { Account } from "../../types/account";

interface AccountSessionPanelProps {
  account: Account;
}

export function AccountSessionPanel({ account }: AccountSessionPanelProps) {
  const { notify } = useToast();
  const queryClient = useQueryClient();
  const completedJobRef = useRef<string | null>(null);
  const createSession = useCreateAccountSession(account.id);
  const finishSession = useFinishAccountSession(account.id);
  const validate = useValidateAccountSession(account.id);
  const refresh = useRefreshAccountSession(account.id);
  const deleteSession = useDeleteAccountSession(account.id);
  const openBrowser = useOpenAccountBrowser(account.id);
  const openHome = useOpenAccountHome(account.id);
  const automationJobs = useAutomationJobs({ limit: 100 });
  const sessionJobs = useMemo(
    () =>
      (automationJobs.data ?? [])
        .filter((job) => job.account_id === account.id && SESSION_JOB_TYPES.has(job.job_type))
        .sort((a, b) => new Date(b.queued_at).getTime() - new Date(a.queued_at).getTime()),
    [account.id, automationJobs.data]
  );
  const latestSessionJob = sessionJobs[0];
  const hasActiveSessionJob = sessionJobs.some((job) => job.status === "QUEUED" || job.status === "RUNNING");

  const status = normalizeSessionStatus(account.session_status);
  const hasIdentity = Boolean(account.browser_profile_path || account.storage_directory || account.session_path);
  const isLoginPending = status === "LOGIN_REQUIRED";
  const isBusy = [
    createSession,
    finishSession,
    validate,
    refresh,
    deleteSession,
    openBrowser,
    openHome
  ].some((mutation) => mutation.isPending);
  const controlsDisabled = isBusy || hasActiveSessionJob;

  useEffect(() => {
    if (!latestSessionJob || !["SUCCESS", "FAILED", "CANCELLED"].includes(latestSessionJob.status)) {
      return;
    }
    if (completedJobRef.current === latestSessionJob.id) {
      return;
    }
    completedJobRef.current = latestSessionJob.id;
    queryClient.invalidateQueries({ queryKey: ["accounts"] });
    queryClient.invalidateQueries({ queryKey: ["accounts", account.id] });
  }, [account.id, latestSessionJob, queryClient]);

  return (
    <section className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <SessionItem label="Session Status" value={<SessionStatusBadge status={status} />} />
        <SessionItem label="Storage Directory" value={account.storage_directory ?? getStorageDirectory(account.session_path)} />
        <SessionItem label="Browser Profile" value={account.browser_profile_path ?? "Not created"} />
        <SessionItem label="Last Login" value={formatDate(account.last_login)} />
        <SessionItem label="Last Validation" value={formatDate(account.last_validation)} />
      </div>

      {isLoginPending ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Please complete login in the browser. When finished, click Finish Login.
        </div>
      ) : null}

      {latestSessionJob ? (
        <div className="rounded-md border border-border bg-slate-50 px-4 py-3 text-sm text-muted-foreground">
          Latest session job: {latestSessionJob.job_type.replaceAll("_", " ")} · {latestSessionJob.status}
        </div>
      ) : null}

      <div className="rounded-md border border-border bg-white p-4">
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            disabled={createSession.isPending || controlsDisabled}
            onClick={() =>
              createSession.mutate(undefined, {
                onSuccess: () => notify("Session login queued. The local agent will open the browser.", "success"),
                onError: () => notify("Unable to create session.", "error")
              })
            }
          >
            <Play size={16} />
            {createSession.isPending ? "Opening..." : "Create Session"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={finishSession.isPending || controlsDisabled || !isLoginPending}
            onClick={() =>
              finishSession.mutate(undefined, {
                onSuccess: (updated) =>
                  notify(`Session is ${normalizeSessionStatus(updated.session_status)}.`, "success"),
                onError: () => notify("Unable to finish login.", "error")
              })
            }
          >
            <CheckCircle2 size={16} />
            {finishSession.isPending ? "Finishing..." : "Finish Login"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={validate.isPending || controlsDisabled || !hasIdentity}
            onClick={() =>
              validate.mutate(undefined, {
                onSuccess: (updated) =>
                  notify(`Session is ${normalizeSessionStatus(updated.session_status)}.`, "success"),
                onError: () => notify("Unable to validate session.", "error")
              })
            }
          >
            <ShieldCheck size={16} />
            {validate.isPending ? "Validating..." : "Validate Session"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={refresh.isPending || controlsDisabled || !hasIdentity}
            onClick={() =>
              refresh.mutate(undefined, {
                onSuccess: () => notify("Session refreshed.", "success"),
                onError: () => notify("Unable to refresh session.", "error")
              })
            }
          >
            <RefreshCw size={16} className={refresh.isPending ? "animate-spin" : ""} />
            Refresh Session
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={openBrowser.isPending || controlsDisabled}
            onClick={() =>
              openBrowser.mutate(undefined, {
                onSuccess: () => notify("Open browser job queued.", "success"),
                onError: () => notify("Unable to open browser profile.", "error")
              })
            }
          >
            <Eye size={16} />
            {openBrowser.isPending ? "Browser Open..." : "Open Browser"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={openHome.isPending || controlsDisabled}
            onClick={() =>
              openHome.mutate(undefined, {
                onSuccess: () => notify(`Open ${platformLabel(account.platform)} job queued.`, "success"),
                onError: () => notify(`Unable to open ${platformLabel(account.platform)}.`, "error")
              })
            }
          >
            <ExternalLink size={16} />
            {openHome.isPending ? "Opening..." : `Open ${platformLabel(account.platform)}`}
          </Button>
          <Button
            type="button"
            variant="danger"
            disabled={deleteSession.isPending || controlsDisabled || !hasIdentity}
            onClick={() =>
              deleteSession.mutate(undefined, {
                onSuccess: () => notify("Session deleted.", "success"),
                onError: () => notify("Unable to delete session.", "error")
              })
            }
          >
            <Trash2 size={16} />
            Delete Session
          </Button>
        </div>
      </div>
    </section>
  );
}

function SessionItem({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="min-w-0 rounded-md border border-border bg-white p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-2 break-words text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}

function SessionStatusBadge({ status }: { status: string }) {
  const classes: Record<string, string> = {
    VALID: "bg-emerald-50 text-emerald-700 ring-emerald-200",
    INVALID: "bg-red-50 text-red-700 ring-red-200",
    FAILED: "bg-red-50 text-red-700 ring-red-200",
    EXPIRED: "bg-red-50 text-red-700 ring-red-200",
    MISSING: "bg-slate-100 text-slate-600 ring-slate-200",
    LOGIN_REQUIRED: "bg-amber-50 text-amber-700 ring-amber-200",
    LOGIN_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200",
    VALIDATION_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200",
    REFRESH_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200",
    DELETE_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200",
    OPEN_BROWSER_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200",
    OPEN_HOME_QUEUED: "bg-blue-50 text-blue-700 ring-blue-200"
  };

  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1",
        classes[status] ?? classes.MISSING
      )}
    >
      {status === "MISSING" ? "NOT LOGGED IN" : status.replaceAll("_", " ")}
    </span>
  );
}

function normalizeSessionStatus(value: string | null) {
  if (!value) {
    return "MISSING";
  }
  return value.toUpperCase().replaceAll(" ", "_");
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Never";
}

function getStorageDirectory(sessionPath: string | null) {
  if (!sessionPath) {
    return "Not created";
  }

  return sessionPath.endsWith("/storage_state.json")
    ? sessionPath.slice(0, -"/storage_state.json".length)
    : sessionPath;
}

function platformLabel(platform: string) {
  return platform === "reddit" ? "Reddit" : platform;
}

const SESSION_JOB_TYPES = new Set([
  "SESSION_LOGIN",
  "SESSION_VALIDATE",
  "SESSION_REFRESH",
  "SESSION_DELETE",
  "OPEN_BROWSER",
  "OPEN_HOME"
]);
