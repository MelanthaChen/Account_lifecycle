import { Link, NavLink, Outlet } from "react-router-dom";
import { BarChart3, Github, LayoutDashboard, Users } from "lucide-react";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-white lg:block">
        <Link to="/" className="flex h-16 items-center gap-3 border-b border-border px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Users size={19} />
          </div>
          <div>
            <div className="text-sm font-semibold">Account Lifecycle</div>
            <div className="text-xs text-muted-foreground">Reddit workspace</div>
          </div>
        </Link>
        <nav className="space-y-1 p-3 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 ${
                isActive ? "bg-muted font-medium" : "text-muted-foreground hover:bg-muted"
              }`
            }
          >
            <LayoutDashboard size={16} />
            Dashboard
          </NavLink>
          <NavLink
            to="/accounts"
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 ${
                isActive ? "bg-muted font-medium" : "text-muted-foreground hover:bg-muted"
              }`
            }
          >
            <Github size={16} />
            Accounts
          </NavLink>
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-md px-3 py-2 ${
                isActive ? "bg-muted font-medium" : "text-muted-foreground hover:bg-muted"
              }`
            }
          >
            <BarChart3 size={16} />
            Analytics
          </NavLink>
        </nav>
      </aside>
      <main className="lg:pl-64">
        <div className="mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
