import { createBrowserRouter } from "react-router-dom";

import { AppLayout } from "./components/layout/AppLayout";
import { AccountDetailPage } from "./pages/AccountDetailPage";
import { AccountsPage } from "./pages/AccountsPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { DashboardPage } from "./pages/DashboardPage";
import { NewAccountPage } from "./pages/NewAccountPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "accounts", element: <AccountsPage /> },
      { path: "accounts/new", element: <NewAccountPage /> },
      { path: "accounts/:accountId", element: <AccountDetailPage /> },
      { path: "analytics", element: <AnalyticsPage /> }
    ]
  }
]);
