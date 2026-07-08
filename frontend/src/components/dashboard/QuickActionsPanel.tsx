import {
  BookOpen,
  ClipboardPlus,
  HeartPulse,
  Lightbulb,
  RefreshCw,
  UserPlus,
  Users
} from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "../ui/button";

interface QuickActionsPanelProps {
  evaluatingHealth: boolean;
  evaluatingRecommendations: boolean;
  onEvaluateHealth: () => void;
  onEvaluateRecommendations: () => void;
}

export function QuickActionsPanel({
  evaluatingHealth,
  evaluatingRecommendations,
  onEvaluateHealth,
  onEvaluateRecommendations
}: QuickActionsPanelProps) {
  return (
    <aside className="rounded-md border border-border bg-white p-4 shadow-sm">
      <div>
        <h2 className="text-base font-semibold">Quick Actions</h2>
        <p className="mt-1 text-sm text-muted-foreground">Control-center shortcuts for common review tasks.</p>
      </div>
      <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
        <QuickLink icon={UserPlus} label="New Account" to="/accounts" />
        <QuickLink icon={Users} label="Sync Profiles" to="/accounts" />
        <Button type="button" variant="secondary" disabled={evaluatingHealth} onClick={onEvaluateHealth}>
          <RefreshCw size={16} className={evaluatingHealth ? "animate-spin" : ""} />
          <HeartPulse size={16} />
          Evaluate Health
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={evaluatingRecommendations}
          onClick={onEvaluateRecommendations}
        >
          <RefreshCw size={16} className={evaluatingRecommendations ? "animate-spin" : ""} />
          <Lightbulb size={16} />
          Evaluate Recommendations
        </Button>
        <QuickLink icon={BookOpen} label="Open Behavior Library" to="/behavior-library" />
        <QuickLink icon={ClipboardPlus} label="Create Campaign" to="/campaigns" />
      </div>
    </aside>
  );
}

function QuickLink({ icon: Icon, label, to }: { icon: typeof UserPlus; label: string; to: string }) {
  return (
    <Link
      to={to}
      className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border bg-white px-3 text-sm font-medium transition hover:bg-muted"
    >
      <Icon size={16} />
      {label}
    </Link>
  );
}
