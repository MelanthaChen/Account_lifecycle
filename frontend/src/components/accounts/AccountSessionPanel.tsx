import { LogIn, RefreshCw, ShieldCheck, Trash2 } from "lucide-react";

import { Button } from "../ui/button";
import {
  useDeleteAccountSession,
  useLoginAccount,
  useRefreshAccountSession,
  useValidateAccountSession
} from "../../hooks/useAccounts";
import { useToast } from "../../store/useToast";
import type { Account } from "../../types/account";

interface AccountSessionPanelProps {
  account: Account;
}

export function AccountSessionPanel({ account }: AccountSessionPanelProps) {
  const { notify } = useToast();
  const login = useLoginAccount(account.id);
  const validate = useValidateAccountSession(account.id);
  const refresh = useRefreshAccountSession(account.id);
  const deleteSession = useDeleteAccountSession(account.id);
  const storageDirectory = getStorageDirectory(account.session_path);

  return (
    <section className="space-y-5">
      <div className="grid gap-4 lg:grid-cols-2">
        <SessionItem label="Session Status" value={account.session_status ?? "unknown"} />
        <SessionItem label="Storage Directory" value={storageDirectory} />
        <SessionItem label="Last Login" value={formatDate(account.last_login)} />
        <SessionItem label="Last Validation" value={formatDate(account.last_validation)} />
        <SessionItem label="Browser Profile" value={account.browser_profile ?? account.username} />
        <SessionItem label="Provider" value={account.provider ?? account.platform} />
      </div>

      <div className="rounded-md border border-border bg-white p-4">
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            disabled={login.isPending}
            onClick={() =>
              login.mutate(undefined, {
                onSuccess: () => notify("Login session saved.", "success"),
                onError: () => notify("Login is not available yet.", "error")
              })
            }
          >
            <LogIn size={16} />
            {login.isPending ? "Opening..." : "Login"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={validate.isPending}
            onClick={() =>
              validate.mutate(undefined, {
                onSuccess: () => notify("Session validated.", "success"),
                onError: () => notify("Session validation is not available yet.", "error")
              })
            }
          >
            <ShieldCheck size={16} />
            {validate.isPending ? "Validating..." : "Validate Session"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={refresh.isPending}
            onClick={() =>
              refresh.mutate(undefined, {
                onSuccess: () => notify("Session refresh requested.", "success"),
                onError: () => notify("Unable to refresh session.", "error")
              })
            }
          >
            <RefreshCw size={16} className={refresh.isPending ? "animate-spin" : ""} />
            Refresh Session
          </Button>
          <Button
            type="button"
            variant="danger"
            disabled={deleteSession.isPending}
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

function SessionItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-2 break-words text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : "Never";
}

function getStorageDirectory(sessionPath: string | null) {
  if (!sessionPath) {
    return "Not created";
  }

  return sessionPath.endsWith("/state.json")
    ? sessionPath.slice(0, -"/state.json".length)
    : sessionPath;
}
