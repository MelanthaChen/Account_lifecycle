import { Link } from "react-router-dom";
import { ExternalLink, MoreHorizontal, RefreshCw } from "lucide-react";

import { Button } from "./ui/button";
import { StatusBadge } from "./ui/badge";
import type { Account } from "../types/account";

interface AccountsTableProps {
  accounts: Account[];
  onSync: (accountId: string) => void;
  syncingId?: string;
}

export function AccountsTable({ accounts, onSync, syncingId }: AccountsTableProps) {
  return (
    <div className="overflow-hidden rounded-md border border-border bg-white">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-border bg-muted/60 text-xs uppercase text-muted-foreground">
          <tr>
            <th className="px-4 py-3">Account</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Last sync</th>
            <th className="px-4 py-3">Notes</th>
            <th className="w-28 px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {accounts.map((account) => (
            <tr key={account.id} className="hover:bg-muted/40">
              <td className="px-4 py-3">
                <Link to={`/accounts/${account.id}`} className="font-medium hover:underline">
                  {account.nickname}
                </Link>
                <div className="text-xs text-muted-foreground">u/{account.reddit_username}</div>
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={account.status} />
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {account.last_sync ? new Date(account.last_sync).toLocaleString() : "Never"}
              </td>
              <td className="max-w-sm truncate px-4 py-3 text-muted-foreground">{account.notes}</td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-1">
                  <Button
                    variant="ghost"
                    className="h-8 w-8 px-0"
                    title="Sync account"
                    onClick={() => onSync(account.id)}
                    disabled={syncingId === account.id}
                  >
                    <RefreshCw size={16} className={syncingId === account.id ? "animate-spin" : ""} />
                  </Button>
                  <Link to={`/accounts/${account.id}`} title="Open account">
                    <Button variant="ghost" className="h-8 w-8 px-0">
                      <ExternalLink size={16} />
                    </Button>
                  </Link>
                  <Button variant="ghost" className="h-8 w-8 px-0" title="More">
                    <MoreHorizontal size={16} />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {accounts.length === 0 ? (
        <div className="px-4 py-12 text-center text-sm text-muted-foreground">No accounts found.</div>
      ) : null}
    </div>
  );
}
