import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { Account } from "../../types/account";
import { ChartPanel } from "./ChartPanel";

const colors = ["#2563eb", "#059669", "#f59e0b", "#dc2626"];

export function PlatformChart({ accounts }: { accounts: Account[] }) {
  const counts = accounts.reduce<Record<string, number>>((acc, account) => {
    acc[account.platform] = (acc[account.platform] ?? 0) + 1;
    return acc;
  }, {});
  const data = Object.entries(counts).map(([name, value]) => ({ name, value }));

  return (
    <ChartPanel title="Accounts by Platform">
      {data.length ? (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={54} outerRadius={86} paddingAngle={3}>
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <EmptyChartLabel />
      )}
    </ChartPanel>
  );
}

function EmptyChartLabel() {
  return <div className="flex h-full items-center justify-center text-sm text-muted-foreground">No data</div>;
}
