"use client";

import { useMemo, useState } from "react";
import type { ChartSpec } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { HistogramChart } from "@/components/charts/HistogramChart";
import { CategoricalBarChart } from "@/components/charts/CategoricalBarChart";
import { ScatterPlot } from "@/components/charts/ScatterPlot";

const TYPE_LABELS: Record<ChartSpec["type"], string> = {
  histogram: "Histograms",
  bar: "Categoricals",
  scatter: "Scatter",
};

function chartTitle(spec: ChartSpec): string {
  if (spec.type === "scatter") {
    return `${spec.x} vs ${spec.y}${spec.corr !== undefined ? ` (r=${spec.corr.toFixed(2)})` : ""}`;
  }
  return spec.column;
}

function renderChart(spec: ChartSpec) {
  switch (spec.type) {
    case "histogram":
      return <HistogramChart spec={spec} />;
    case "bar":
      return <CategoricalBarChart spec={spec} />;
    case "scatter":
      return <ScatterPlot spec={spec} />;
  }
}

export function ChartGrid({ charts }: { charts: ChartSpec[] }) {
  const presentTypes = useMemo(
    () => Array.from(new Set(charts.map((c) => c.type))) as ChartSpec["type"][],
    [charts],
  );
  const [active, setActive] = useState<Set<ChartSpec["type"]>>(new Set(presentTypes));

  if (charts.length === 0) {
    return (
      <EmptyState
        title="No charts to display"
        description="Charts are generated automatically from numeric and categorical columns."
        icon="📈"
      />
    );
  }

  const visible = charts.filter((c) => active.has(c.type));

  const toggle = (t: ChartSpec["type"]) => {
    setActive((prev) => {
      const next = new Set(prev);
      if (next.has(t)) {
        next.delete(t);
      } else {
        next.add(t);
      }
      // Never allow an empty selection (would hide everything).
      return next.size === 0 ? new Set(presentTypes) : next;
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-400">Show:</span>
        {presentTypes.map((t) => {
          const on = active.has(t);
          return (
            <button
              key={t}
              onClick={() => toggle(t)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                on
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200"
              }`}
            >
              {TYPE_LABELS[t]}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {visible.map((spec, i) => (
          <Card key={`${spec.type}-${i}`} className="animate-fade-in">
            <CardHeader title={chartTitle(spec)} subtitle={TYPE_LABELS[spec.type]} />
            <CardBody>{renderChart(spec)}</CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
}
