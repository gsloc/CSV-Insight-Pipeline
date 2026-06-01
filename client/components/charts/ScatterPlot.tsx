"use client";

import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ScatterSpec } from "@/lib/types";

export function ScatterPlot({ spec }: { spec: ScatterSpec }) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 8, right: 12, bottom: 24, left: -8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
          <XAxis
            type="number"
            dataKey="x"
            name={spec.x}
            tick={{ fontSize: 10 }}
            label={{ value: spec.x, position: "insideBottom", offset: -8, fontSize: 11, fill: "#64748b" }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name={spec.y}
            tick={{ fontSize: 10 }}
            label={{ value: spec.y, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" }}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
          />
          <Scatter data={spec.points} fill="#7c3aed" fillOpacity={0.6} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
