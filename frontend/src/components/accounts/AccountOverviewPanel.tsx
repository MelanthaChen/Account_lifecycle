import { StatusBadge } from "../ui/badge";
import type { Account } from "../../types/account";

export function AccountOverviewPanel({ account }: { account: Account }) {
  return (
    <section className="grid gap-4 lg:grid-cols-2">
      <DetailItem label="Nickname" value={account.nickname} />
      <DetailItem label="Platform" value={account.platform} className="capitalize" />
      <DetailItem label="Username" value={account.username} />
      <div className="rounded-md border border-border bg-white p-4">
        <div className="text-xs font-medium uppercase text-muted-foreground">Status</div>
        <div className="mt-2">
          <StatusBadge status={account.status} />
        </div>
      </div>
      <DetailItem label="Created" value={new Date(account.created_at).toLocaleString()} />
      <DetailItem label="Last Updated" value={new Date(account.updated_at).toLocaleString()} />
      <div className="rounded-md border border-border bg-white p-4 lg:col-span-2">
        <div className="text-xs font-medium uppercase text-muted-foreground">Notes</div>
        <div className="mt-2 text-sm text-foreground">{account.notes || "No notes."}</div>
      </div>
    </section>
  );
}

function DetailItem({
  className,
  label,
  value
}: {
  className?: string;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-border bg-white p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className={["mt-2 text-sm font-medium text-foreground", className].filter(Boolean).join(" ")}>
        {value}
      </div>
    </div>
  );
}
