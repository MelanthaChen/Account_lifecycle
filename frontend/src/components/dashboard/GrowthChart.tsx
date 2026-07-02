import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartPanel } from "./ChartPanel";

const growthData = [
  { month: "Jan", accounts: 2 },
  { month: "Feb", accounts: 4 },
  { month: "Mar", accounts: 5 },
  { month: "Apr", accounts: 8 },
  { month: "May", accounts: 11 },
  { month: "Jun", accounts: 14 }
];

export function GrowthChart() {
  return (
    <ChartPanel title="Recent Growth">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={growthData}>
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="accounts"
            stroke="#059669"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartPanel>
  );
}
