import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/components/ui/Card";
import { money } from "@/lib/formatters";

export type RevenueTrendPoint = {
  period: string;
  revenue: number;
};

type RevenueGranularity = "daily" | "monthly";

function parsePeriod(value: string): Date | null {
  const normalized = /^\d{4}-\d{2}$/.test(value) ? `${value}-01` : value;

  const date = new Date(`${normalized}T00:00:00`);

  return Number.isNaN(date.getTime()) ? null : date;
}

function formatPeriod(value: string, granularity: RevenueGranularity): string {
  const date = parsePeriod(value);
  if (!date) return value;

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: granularity === "daily" ? "numeric" : undefined,
    year: granularity === "monthly" ? "numeric" : undefined,
  }).format(date);
}

export function RevenueChart({
  data,
  granularity,
}: {
  data: RevenueTrendPoint[];
  granularity: RevenueGranularity;
}) {
  const description =
    granularity === "daily"
      ? "Daily purchase revenue for the selected acquisition scope"
      : "Monthly purchase revenue for the selected acquisition scope";

  return (
    <Card className="p-5">
      <div className="mb-4">
        <h3 className="font-semibold">Revenue trend</h3>
        <p className="text-sm opacity-60">{description}</p>
      </div>

      <div className="h-72">
        <ResponsiveContainer>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="period"
              tick={{ fontSize: 11 }}
              minTickGap={35}
              tickFormatter={(value: string) =>
                formatPeriod(value, granularity)
              }
            />

            <YAxis
              tick={{ fontSize: 11 }}
              width={70}
              tickFormatter={(value: number) => money(value).replace(".00", "")}
            />

            <Tooltip
              labelFormatter={(value) =>
                formatPeriod(String(value), granularity)
              }
              formatter={(value) => money(Number(value))}
            />

            <Area
              type="monotone"
              dataKey="revenue"
              fill="hsl(var(--primary)/.15)"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
