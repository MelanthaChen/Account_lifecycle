import { Activity, BarChart3, FileText, Settings, UserRound, WalletCards } from "lucide-react";

import { cn } from "../../lib/utils";

export type AccountWorkspaceTab =
  | "overview"
  | "session"
  | "activity"
  | "publishing"
  | "analytics"
  | "settings";

const tabs: Array<{ id: AccountWorkspaceTab; label: string; icon: typeof UserRound }> = [
  { id: "overview", label: "Overview", icon: UserRound },
  { id: "session", label: "Session", icon: WalletCards },
  { id: "activity", label: "Activity", icon: Activity },
  { id: "publishing", label: "Publishing", icon: FileText },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
  { id: "settings", label: "Settings", icon: Settings }
];

interface AccountWorkspaceTabsProps {
  activeTab: AccountWorkspaceTab;
  onTabChange: (tab: AccountWorkspaceTab) => void;
}

export function AccountWorkspaceTabs({ activeTab, onTabChange }: AccountWorkspaceTabsProps) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-border">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={cn(
            "flex flex-none items-center gap-2 border-b-2 px-3 py-3 text-sm transition",
            activeTab === tab.id
              ? "border-primary font-medium text-foreground"
              : "border-transparent text-muted-foreground hover:text-foreground"
          )}
          onClick={() => onTabChange(tab.id)}
        >
          <tab.icon size={15} />
          {tab.label}
        </button>
      ))}
    </div>
  );
}
