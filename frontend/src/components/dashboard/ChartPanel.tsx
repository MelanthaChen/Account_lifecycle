import type { ReactNode } from "react";

interface ChartPanelProps {
  children: ReactNode;
  title: string;
}

export function ChartPanel({ children, title }: ChartPanelProps) {
  return (
    <section className="rounded-md border border-border bg-white p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-4 h-64">{children}</div>
    </section>
  );
}
