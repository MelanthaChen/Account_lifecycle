import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { Account, AccountStatus } from "../../types/account";
import { ChartPanel } from "./ChartPanel";

const statuses: AccountStatus[] = ["active", "paused", "error", "archived"];

export function StatusChart({ accounts }: { accounts: Account[] }) {
  const data = statuses.map((status) => ({
    status,
    accounts: accounts.filter((account) => account.status === status).length
  }));

  return (
    <ChartPanel title="Account Status">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="status" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="accounts" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartPanel>
  );
}
