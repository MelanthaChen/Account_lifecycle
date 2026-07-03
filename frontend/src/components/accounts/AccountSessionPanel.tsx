import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  ExternalLink,
  Eye,
  KeyRound,
  LogIn,
  LogOut,
  RefreshCw,
  ShieldCheck,
  Trash2
} from "lucide-react";

import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  useDeleteAccountSession,
  useLoginAccount,
  useLogoutAccountSession,
  useOpenAccountBrowser,
  useOpenAccountHome,
  useRefreshAccountSession,
  useValidateAccountSession
} from "../../hooks/useAccounts";
import { cn } from "../../lib/utils";
import { useToast } from "../../store/useToast";
import type { Account, AccountLoginInput } from "../../types/account";

interface AccountSessionPanelProps {
  account: Account;
}

export function AccountSessionPanel({ account }: AccountSessionPanelProps) {
  const { notify } = useToast();
  const login = useLoginAccount(account.id);
  const validate = useValidateAccountSession(account.id);
  const refresh = useRefreshAccountSession(account.id);
  const deleteSession = useDeleteAccountSession(account.id);
  const logout = useLogoutAccountSession(account.id);
  const openBrowser = useOpenAccountBrowser(account.id);
  const openHome = useOpenAccountHome(account.id);

  const [loginForm, setLoginForm] = useState<AccountLoginInput>({
    username: account.saved_username ?? account.username,
    password: "",
    remember_credentials: account.remember_credentials,
    auto_login: account.auto_login,
    launch_visible_browser: account.launch_visible_browser
  });

  const status = normalizeSessionStatus(account.session_status);
  const hasIdentity = Boolean(account.browser_profile_path || account.storage_directory || account.session_path);
  const isBusy = [
    login,
    validate,
    refresh,
    deleteSession,
    logout,
    openBrowser,
    openHome
  ].some((mutation) => mutation.isPending);

  const details = useMemo(
    () => [
      ["Session Status", <SessionStatusBadge key="status" status={status} />],
      ["Storage Directory", account.storage_directory ?? getStorageDirectory(account.session_path)],
      ["Browser Profile", account.browser_profile_path ?? "Not created"],
      ["Saved Username", account.saved_username ?? "Not saved"],
      ["Remember Credentials", account.remember_credentials ? "Enabled" : "Disabled"],
      ["Auto Login", account.auto_login ? "Enabled" : "Disabled"],
      ["Visible Browser", account.launch_visible_browser ? "Enabled" : "Disabled"],
      ["Last Login", formatDate(account.last_login)],
      ["Last Validation", formatDate(account.last_validation)]
    ],
    [account, status]
  );

  function submitLogin() {
    const payload: AccountLoginInput = {
      ...loginForm,
      username: loginForm.username?.trim() ? loginForm.username.trim() : null,
      password: loginForm.password?.trim() ? loginForm.password : null
    };

    login.mutate(payload, {
      onSuccess: (updated) => {
        notify(`Session is ${normalizeSessionStatus(updated.session_status)}.`, "success");
      },
      onError: () => notify("Unable to complete login.", "error")
    });
  }

  return (
    <section className="space-y-5">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
        <div className="grid gap-4 md:grid-cols-2">
          {details.map(([label, value]) => (
            <SessionItem key={label as string} label={label as string} value={value} />
          ))}
        </div>

        <div className="rounded-md border border-border bg-white p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <KeyRound size={16} />
            Login
          </div>
          <div className="mt-4 space-y-3">
            <Input
              value={loginForm.username ?? ""}
              onChange={(event) => setLoginForm({ ...loginForm, username: event.target.value })}
              placeholder="Username"
            />
            <Input
              type="password"
              value={loginForm.password ?? ""}
              onChange={(event) => setLoginForm({ ...loginForm, password: event.target.value })}
              placeholder={account.saved_username ? "Password or saved password" : "Password"}
            />
            <div className="space-y-2">
              <CheckboxField
                label="Remember Credentials"
                checked={Boolean(loginForm.remember_credentials)}
                onChange={(checked) => setLoginForm({ ...loginForm, remember_credentials: checked })}
              />
              <CheckboxField
                label="Auto Login"
                checked={Boolean(loginForm.auto_login)}
                onChange={(checked) => setLoginForm({ ...loginForm, auto_login: checked })}
              />
              <CheckboxField
                label="Launch Visible Browser"
                checked={Boolean(loginForm.launch_visible_browser)}
                onChange={(checked) => setLoginForm({ ...loginForm, launch_visible_browser: checked })}
              />
            </div>
            <Button type="button" className="w-full" disabled={login.isPending} onClick={submitLogin}>
              <LogIn size={16} />
              {login.isPending ? "Logging in..." : "Login"}
            </Button>
          </div>
        </div>
      </div>

      <div className="rounded-md border border-border bg-white p-4">
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="secondary"
            disabled={validate.isPending || !hasIdentity}
            onClick={() =>
              validate.mutate(undefined, {
                onSuccess: (updated) =>
                  notify(`Session is ${normalizeSessionStatus(updated.session_status)}.`, "success"),
                onError: () => notify("Unable to validate session.", "error")
              })
            }
          >
            <ShieldCheck size={16} />
            {validate.isPending ? "Validating..." : "Validate"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={refresh.isPending || !hasIdentity}
            onClick={() =>
              refresh.mutate(undefined, {
                onSuccess: () => notify("Session refreshed.", "success"),
                onError: () => notify("Unable to refresh session.", "error")
              })
            }
          >
            <RefreshCw size={16} className={refresh.isPending ? "animate-spin" : ""} />
            Refresh
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={logout.isPending || !hasIdentity}
            onClick={() =>
              logout.mutate(undefined, {
                onSuccess: () => notify("Logged out of browser identity.", "success"),
                onError: () => notify("Unable to log out.", "error")
              })
            }
          >
            <LogOut size={16} />
            Logout
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={openBrowser.isPending || isBusy}
            onClick={() =>
              openBrowser.mutate(undefined, {
                onSuccess: () => notify("Browser profile closed.", "success"),
                onError: () => notify("Unable to open browser profile.", "error")
              })
            }
          >
            <Eye size={16} />
            {openBrowser.isPending ? "Browser open..." : "Open Browser"}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={openHome.isPending || isBusy}
            onClick={() =>
              openHome.mutate(undefined, {
                onSuccess: () => notify(`${account.platform} closed.`, "success"),
                onError: () => notify(`Unable to open ${account.platform}.`, "error")
              })
            }
          >
            <ExternalLink size={16} />
            {openHome.isPending ? "Open..." : `Open ${platformLabel(account.platform)}`}
          </Button>
          <Button
            type="button"
            variant="danger"
            disabled={deleteSession.isPending || !hasIdentity}
            onClick={() =>
              deleteSession.mutate(undefined, {
                onSuccess: () => notify("Browser identity files deleted.", "success"),
                onError: () => notify("Unable to delete browser identity.", "error")
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
    NOT_LOGGED_IN: "bg-slate-100 text-slate-600 ring-slate-200",
    LOGIN_REQUIRED: "bg-amber-50 text-amber-700 ring-amber-200"
  };

  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1",
        classes[status] ?? classes.NOT_LOGGED_IN
      )}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}

function CheckboxField({
  checked,
  label,
  onChange
}: {
  checked: boolean;
  label: string;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="inline-flex items-center gap-2 text-sm font-medium">
      <input
        type="checkbox"
        className="h-4 w-4 rounded border-border accent-primary"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
      />
      {label}
    </label>
  );
}

function normalizeSessionStatus(value: string | null) {
  if (!value) {
    return "NOT_LOGGED_IN";
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

  return sessionPath.endsWith("/state.json")
    ? sessionPath.slice(0, -"/state.json".length)
    : sessionPath;
}

function platformLabel(platform: string) {
  return platform === "reddit" ? "Reddit" : platform;
}
