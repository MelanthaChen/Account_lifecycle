import { BarChart3 } from "lucide-react";

export function AnalyticsPage() {
  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">Select an account to inspect detailed activity.</p>
      </div>
      <div className="rounded-md border border-border bg-white p-10 text-center text-sm text-muted-foreground">
        <BarChart3 className="mx-auto mb-3" size={28} />
        Account-level analytics are available from each account detail page.
      </div>
    </div>
  );
}
