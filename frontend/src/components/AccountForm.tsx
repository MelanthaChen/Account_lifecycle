import { FormEvent, useState } from "react";
import { Save } from "lucide-react";

import { Button } from "./ui/button";
import { Input } from "./ui/input";
import type { Account, AccountInput, AccountStatus } from "../types/account";

const statuses: AccountStatus[] = ["active", "paused", "error", "archived"];

interface AccountFormProps {
  account?: Account;
  onSubmit: (input: AccountInput) => void;
  isPending?: boolean;
}

export function AccountForm({ account, onSubmit, isPending }: AccountFormProps) {
  const [form, setForm] = useState<AccountInput>({
    nickname: account?.nickname ?? "",
    reddit_username: account?.reddit_username ?? "",
    status: account?.status ?? "active",
    notes: account?.notes ?? "",
    is_active: account?.is_active ?? true
  });

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit(form);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="space-y-1.5 text-sm font-medium">
          Nickname
          <Input
            value={form.nickname}
            onChange={(event) => setForm({ ...form, nickname: event.target.value })}
            required
          />
        </label>
        <label className="space-y-1.5 text-sm font-medium">
          Reddit username
          <Input
            value={form.reddit_username}
            onChange={(event) => setForm({ ...form, reddit_username: event.target.value })}
            required
          />
        </label>
      </div>
      <div className="grid gap-4 sm:grid-cols-[220px_1fr]">
        <label className="space-y-1.5 text-sm font-medium">
          Status
          <select
            className="h-9 w-full rounded-md border border-border bg-white px-3 text-sm capitalize"
            value={form.status}
            onChange={(event) => setForm({ ...form, status: event.target.value as AccountStatus })}
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
        <label className="space-y-1.5 text-sm font-medium">
          Notes
          <Input
            value={form.notes ?? ""}
            onChange={(event) => setForm({ ...form, notes: event.target.value })}
          />
        </label>
      </div>
      <label className="inline-flex items-center gap-2 text-sm font-medium">
        <input
          type="checkbox"
          checked={form.is_active}
          onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
        />
        Active
      </label>
      <div className="flex justify-end">
        <Button type="submit" disabled={isPending}>
          <Save size={16} />
          Save
        </Button>
      </div>
    </form>
  );
}
