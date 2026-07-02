import type { LucideIcon } from "lucide-react";

interface ComingSoonPageProps {
  icon: LucideIcon;
  title: string;
}

export function ComingSoonPage({ icon: Icon, title }: ComingSoonPageProps) {
  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">{title}</h1>
      </div>
      <div className="rounded-md border border-border bg-white p-10 text-center">
        <Icon className="mx-auto mb-3 text-muted-foreground" size={28} />
        <div className="text-sm font-medium">Coming Soon</div>
      </div>
    </div>
  );
}
