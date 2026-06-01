"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BarSpec } from "@/lib/types";

export function CategoricalBarChart({ spec }: { spec: BarSpec }) {
  const data = spec.data;
  const rotate = data.length > 5;
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 12, bottom: rotate ? 36 : 12, left: -12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
          <XAxis
            dataKey="category"
            tick={{ fontSize: 10 }}
            interval={0}
            angle={rotate ? -30 : 0}
            textAnchor={rotate ? "end" : "middle"}
            height={rotate ? 52 : 24}
          />
          <YAxis tick={{ fontSize: 10 }} allowDecimals={false} />
          <Tooltip
            cursor={{ fill: "rgba(16,185,129,0.06)" }}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
          />
          <Bar dataKey="count" fill="#10b981" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
