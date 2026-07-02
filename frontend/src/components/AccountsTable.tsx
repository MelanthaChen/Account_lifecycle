import { Edit3, Trash2 } from "lucide-react";

import { Button } from "./ui/button";
import { StatusBadge } from "./ui/badge";
import type { Account } from "../types/account";

interface AccountsTableProps {
  accounts: Account[];
  onDelete: (account: Account) => void;
  onEdit: (account: Account) => void;
}

export function AccountsTable({ accounts, onDelete, onEdit }: AccountsTableProps) {
  return (
    <div className="overflow-hidden rounded-md border border-border bg-white">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="border-b border-border bg-muted/60 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Nickname</th>
              <th className="px-4 py-3">Platform</th>
              <th className="px-4 py-3">Username</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Last Sync</th>
              <th className="w-32 px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {accounts.map((account) => (
              <tr key={account.id} className="hover:bg-muted/40">
                <td className="px-4 py-3">
                  <div className="font-medium">{account.nickname}</div>
                  {account.notes ? (
                    <div className="mt-0.5 max-w-xs truncate text-xs text-muted-foreground">
                      {account.notes}
                    </div>
                  ) : null}
                </td>
                <td className="px-4 py-3 capitalize text-muted-foreground">{account.platform}</td>
                <td className="px-4 py-3 text-muted-foreground">{account.username}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={account.status} />
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {account.last_sync ? new Date(account.last_sync).toLocaleString() : "Never"}
                </td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-1">
                    <Button
                      type="button"
                      variant="ghost"
                      className="h-8 w-8 px-0"
                      title="Edit account"
                      onClick={() => onEdit(account)}
                    >
                      <Edit3 size={15} />
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      className="h-8 w-8 px-0 text-red-700 hover:bg-red-50"
                      title="Delete account"
                      onClick={() => onDelete(account)}
                    >
                      <Trash2 size={15} />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
