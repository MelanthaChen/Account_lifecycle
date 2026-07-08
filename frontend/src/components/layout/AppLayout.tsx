import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  Activity,
  BarChart3,
  BookOpen,
  ClipboardList,
  HeartPulse,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  ThumbsUp,
  Users
} from "lucide-react";

import { cn } from "../../lib/utils";

const navigation = [
  { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { label: "Accounts", path: "/accounts", icon: Users },
  { label: "Activity", path: "/activity", icon: Activity },
  { label: "Upvote", path: "/upvote", icon: ThumbsUp },
  { label: "Campaigns", path: "/campaigns", icon: ClipboardList },
  { label: "Behavior Library", path: "/behavior-library", icon: BookOpen },
  { label: "Health", path: "/health", icon: HeartPulse },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
  { label: "Settings", path: "/settings", icon: Settings }
];

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/accounts": "Accounts",
  "/activity": "Activity",
  "/upvote": "Upvote",
  "/campaigns": "Campaigns",
  "/behavior-library": "Behavior Library",
  "/health": "Health",
  "/analytics": "Analytics",
  "/settings": "Settings"
};

export function AppLayout() {
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] ?? "Account Intelligence";

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-border px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck size={19} />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold">Account Intelligence</div>
            <div className="text-xs text-muted-foreground">Operations workspace</div>
          </div>
        </div>
        <nav className="space-y-1 p-3 text-sm">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 transition",
                  isActive
                    ? "bg-muted font-medium text-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )
              }
            >
              <item.icon size={16} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-border bg-white/95 backdrop-blur">
          <div className="flex h-16 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
            <div>
              <div className="text-sm font-semibold">{pageTitle}</div>
              <div className="text-xs text-muted-foreground">Account Management MVP</div>
            </div>
            <div className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              FastAPI connected
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto border-t border-border px-3 py-2 text-sm lg:hidden">
            {navigation.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    "flex flex-none items-center gap-2 rounded-md px-3 py-2",
                    isActive ? "bg-muted font-medium" : "text-muted-foreground"
                  )
                }
              >
                <item.icon size={15} />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
