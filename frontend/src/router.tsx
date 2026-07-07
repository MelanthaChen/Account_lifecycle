import { Navigate, createBrowserRouter } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { AccountDetailPage } from "./pages/AccountDetailPage";
import { ActivityPage } from "./pages/ActivityPage";
import { AccountsPage } from "./pages/AccountsPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { CampaignsPage } from "./pages/CampaignsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { SettingsPage } from "./pages/SettingsPage";
import { UpvotePage } from "./pages/UpvotePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "accounts", element: <AccountsPage /> },
      { path: "accounts/:accountId", element: <AccountDetailPage /> },
      { path: "activity", element: <ActivityPage /> },
      { path: "upvote", element: <UpvotePage /> },
      { path: "campaigns", element: <CampaignsPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "settings", element: <SettingsPage /> }
    ]
  }
]);
