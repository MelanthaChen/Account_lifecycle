import { useMemo, useState } from "react";
import { Plus, RefreshCw, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { AccountDialog } from "../components/AccountDialog";
import { AccountsTable } from "../components/AccountsTable";
import { AlertDialog } from "../components/ui/alert-dialog";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useCreateAccount, useDeleteAccount, useUpdateAccount, useAccounts } from "../hooks/useAccounts";
import { useAccountFilters } from "../store/useAccountFilters";
import { useToast } from "../store/useToast";
import type { Account, AccountInput } from "../types/account";

export function AccountsPage() {
  const navigate = useNavigate();
  const accounts = useAccounts();
  const createAccount = useCreateAccount();
  const updateAccount = useUpdateAccount();
  const deleteAccount = useDeleteAccount();
  const { notify } = useToast();
  const { search, setSearch } = useAccountFilters();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Account | null>(null);

  const filteredAccounts = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) {
      return accounts.data ?? [];
    }
    return (accounts.data ?? []).filter((account) =>
      [account.nickname, account.username, account.platform].some((value) =>
        value.toLowerCase().includes(term)
      )
    );
  }, [accounts.data, search]);

  function openCreateDialog() {
    setEditingAccount(null);
    setDialogOpen(true);
  }

  function openEditDialog(account: Account) {
    setEditingAccount(account);
    setDialogOpen(true);
  }

  function handleSubmit(input: AccountInput) {
    if (editingAccount) {
      updateAccount.mutate(
        { accountId: editingAccount.id, input },
        {
          onSuccess: () => {
            notify("Account updated.", "success");
            setDialogOpen(false);
            setEditingAccount(null);
          },
          onError: () => notify("Unable to update account.", "error")
        }
      );
      return;
    }

    createAccount.mutate(input, {
      onSuccess: () => {
        notify("Account added.", "success");
        setDialogOpen(false);
      },
      onError: () => notify("Unable to add account.", "error")
    });
  }

  function confirmDelete() {
    if (!deleteTarget) {
      return;
    }
    deleteAccount.mutate(deleteTarget.id, {
      onSuccess: () => {
        notify("Account deleted.", "success");
        setDeleteTarget(null);
      },
      onError: () => notify("Unable to delete account.", "error")
    });
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Accounts</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage account records connected to the intelligence platform.
          </p>
        </div>
        <Button type="button" onClick={openCreateDialog}>
          <Plus size={16} />
          Add Account
        </Button>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 text-muted-foreground" size={16} />
          <Input
            className="pl-9"
            placeholder="Search by nickname, username, or platform"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Button type="button" variant="secondary" onClick={() => accounts.refetch()}>
          <RefreshCw size={16} className={accounts.isFetching ? "animate-spin" : ""} />
          Refresh
        </Button>
      </div>

      {accounts.isLoading ? (
        <StatePanel title="Loading accounts..." />
      ) : accounts.isError ? (
        <StatePanel title="Unable to load accounts." tone="error" />
      ) : filteredAccounts.length === 0 ? (
        <StatePanel title={search ? "No accounts match your search." : "No accounts yet."} />
      ) : (
        <AccountsTable
          accounts={filteredAccounts}
          onEdit={openEditDialog}
          onDelete={setDeleteTarget}
          onOpen={(account) => navigate(`/accounts/${account.id}`)}
        />
      )}

      <AccountDialog
        account={editingAccount}
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) {
            setEditingAccount(null);
          }
        }}
        onSubmit={handleSubmit}
        isPending={createAccount.isPending || updateAccount.isPending}
      />

      <AlertDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => {
          if (!open) {
            setDeleteTarget(null);
          }
        }}
        title="Delete account?"
        description={
          deleteTarget
            ? `This will permanently remove ${deleteTarget.nickname} from the platform.`
            : "This account will be permanently removed."
        }
        isPending={deleteAccount.isPending}
        onConfirm={confirmDelete}
      />
    </div>
  );
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-12 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-12 text-center text-sm text-muted-foreground"
      }
    >
      {title}
    </div>
  );
}
