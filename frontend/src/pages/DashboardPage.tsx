import { Link } from "react-router-dom";
import { Plus, RefreshCw, Search } from "lucide-react";

import { AccountsTable } from "../components/AccountsTable";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useAccounts, useSyncAnyAccount } from "../hooks/useAccounts";
import { useAccountFilters } from "../store/useAccountFilters";

export function DashboardPage() {
  const { search, setSearch } = useAccountFilters();
  const accounts = useAccounts(search);
  const sync = useSyncAnyAccount();

  const activeCount = accounts.data?.filter((account) => account.status === "active").length ?? 0;
  const errorCount = accounts.data?.filter((account) => account.status === "error").length ?? 0;

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Reddit Accounts</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage identities, sync authorized activity, and inspect account health.
          </p>
        </div>
        <Link to="/accounts/new">
          <Button>
            <Plus size={16} />
            Add account
          </Button>
        </Link>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-md border border-border bg-white p-4">
          <div className="text-xs font-medium uppercase text-muted-foreground">Managed</div>
          <div className="mt-2 text-2xl font-semibold">{accounts.data?.length ?? 0}</div>
        </div>
        <div className="rounded-md border border-border bg-white p-4">
          <div className="text-xs font-medium uppercase text-muted-foreground">Active</div>
          <div className="mt-2 text-2xl font-semibold">{activeCount}</div>
        </div>
        <div className="rounded-md border border-border bg-white p-4">
          <div className="text-xs font-medium uppercase text-muted-foreground">Needs review</div>
          <div className="mt-2 text-2xl font-semibold">{errorCount}</div>
        </div>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-md flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 text-muted-foreground" size={16} />
          <Input
            className="pl-9"
            placeholder="Search accounts"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Button variant="secondary" onClick={() => accounts.refetch()}>
          <RefreshCw size={16} />
          Refresh
        </Button>
      </div>

      <AccountsTable
        accounts={accounts.data ?? []}
        onSync={(accountId) => sync.mutate(accountId)}
        syncingId={sync.isPending ? sync.variables : undefined}
      />
    </div>
  );
}
