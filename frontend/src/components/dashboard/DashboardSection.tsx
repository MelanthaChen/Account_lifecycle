import type { ReactNode } from "react";

interface DashboardSectionProps {
  action?: ReactNode;
  children: ReactNode;
  description?: string;
  title: string;
}

export function DashboardSection({ action, children, description, title }: DashboardSectionProps) {
  return (
    <section className="rounded-md border border-border bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-border px-4 py-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">{title}</h2>
          {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function DashboardEmptyState({ children }: { children: ReactNode }) {
  return <div className="px-4 py-10 text-center text-sm text-muted-foreground">{children}</div>;
}
