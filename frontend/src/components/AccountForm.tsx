import { FormEvent, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { Save } from "lucide-react";

import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import type { Account, AccountInput, AccountStatus, Platform } from "../types/account";

const statuses: AccountStatus[] = ["active", "paused", "error", "archived"];
const platforms: Platform[] = ["reddit"];

interface AccountFormProps {
  account?: Account | null;
  onSubmit: (input: AccountInput) => void;
  isPending?: boolean;
}

function buildInitialState(account?: Account | null): AccountInput {
  return {
    nickname: account?.nickname ?? "",
    platform: account?.platform ?? "reddit",
    username: account?.username ?? "",
    status: account?.status ?? "active",
    notes: account?.notes ?? "",
    is_active: account?.is_active ?? true,
    provider: account?.provider ?? account?.platform ?? "reddit",
    saved_username: account?.saved_username ?? account?.username ?? "",
    saved_password: "",
    remember_credentials: account?.remember_credentials ?? false,
    auto_login: account?.auto_login ?? false,
    launch_visible_browser: account?.launch_visible_browser ?? true
  };
}

export function AccountForm({ account, onSubmit, isPending }: AccountFormProps) {
  const initialState = useMemo(() => buildInitialState(account), [account]);
  const [form, setForm] = useState<AccountInput>(initialState);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    setForm(initialState);
    setSubmitted(false);
  }, [initialState]);

  const errors = {
    nickname: form.nickname.trim() ? "" : "Nickname is required.",
    platform: form.platform ? "" : "Platform is required.",
    username: form.username.trim() ? "" : "Username is required."
  };
  const hasErrors = Boolean(errors.nickname || errors.platform || errors.username);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitted(true);
    if (hasErrors) {
      return;
    }
    const payload: AccountInput = {
      ...form,
      nickname: form.nickname.trim(),
      username: form.username.trim(),
      notes: form.notes?.trim() ? form.notes.trim() : null,
      provider: form.provider?.trim() ? form.provider.trim() : form.platform,
      saved_username: form.saved_username?.trim() ? form.saved_username.trim() : null,
      saved_password: form.saved_password?.trim() ? form.saved_password : null
    };

    if (account && !form.saved_password?.trim()) {
      delete payload.saved_password;
    }

    onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nickname" error={submitted ? errors.nickname : ""}>
          <Input
            value={form.nickname}
            onChange={(event) => setForm({ ...form, nickname: event.target.value })}
            required
          />
        </Field>
        <Field label="Platform" error={submitted ? errors.platform : ""}>
          <select
            className="h-9 w-full rounded-md border border-border bg-white px-3 text-sm capitalize outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
            value={form.platform}
            onChange={(event) => setForm({ ...form, platform: event.target.value as Platform })}
            required
          >
            {platforms.map((platform) => (
              <option key={platform} value={platform}>
                {platform}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Username" error={submitted ? errors.username : ""}>
          <Input
            value={form.username}
            onChange={(event) => setForm({ ...form, username: event.target.value })}
            required
          />
        </Field>
        <Field label="Status">
          <select
            className="h-9 w-full rounded-md border border-border bg-white px-3 text-sm capitalize outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
            value={form.status}
            onChange={(event) => setForm({ ...form, status: event.target.value as AccountStatus })}
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <Field label="Notes">
        <Textarea
          value={form.notes ?? ""}
          onChange={(event) => setForm({ ...form, notes: event.target.value })}
          placeholder="Optional account context"
        />
      </Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Saved Username">
          <Input
            value={form.saved_username ?? ""}
            onChange={(event) => setForm({ ...form, saved_username: event.target.value })}
            placeholder="Optional login username"
          />
        </Field>
        <Field label="Saved Password">
          <Input
            type="password"
            value={form.saved_password ?? ""}
            onChange={(event) => setForm({ ...form, saved_password: event.target.value })}
            placeholder={account ? "Leave blank to keep existing" : "Optional login password"}
          />
        </Field>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <CheckboxField
          label="Active"
          checked={form.is_active}
          onChange={(checked) => setForm({ ...form, is_active: checked })}
        />
        <CheckboxField
          label="Remember Credentials"
          checked={form.remember_credentials}
          onChange={(checked) => setForm({ ...form, remember_credentials: checked })}
        />
        <CheckboxField
          label="Auto Login"
          checked={form.auto_login}
          onChange={(checked) => setForm({ ...form, auto_login: checked })}
        />
        <CheckboxField
          label="Launch Visible Browser"
          checked={form.launch_visible_browser}
          onChange={(checked) => setForm({ ...form, launch_visible_browser: checked })}
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={isPending}>
          <Save size={16} />
          {isPending ? "Saving..." : "Save account"}
        </Button>
      </div>
    </form>
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

function Field({
  children,
  error,
  label
}: {
  children: ReactNode;
  error?: string;
  label: string;
}) {
  return (
    <label className="space-y-1.5 text-sm font-medium">
      <span>{label}</span>
      {children}
      {error ? <span className="block text-xs text-red-600">{error}</span> : null}
    </label>
  );
}
