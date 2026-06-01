"use client";

import { useState } from "react";
import type { AnalyzeResponse } from "@/lib/types";
import { OverviewCards } from "@/components/OverviewCards";
import { InsightsPanel } from "@/components/InsightsPanel";
import { SchemaTable } from "@/components/SchemaTable";
import { SummaryStatsTable } from "@/components/SummaryStatsTable";
import { ChartGrid } from "@/components/ChartGrid";
import { DataQualityReport } from "@/components/DataQualityReport";
import { CorrelationHeatmap } from "@/components/CorrelationHeatmap";
import { DataPreviewTable } from "@/components/DataPreviewTable";

type TabId = "overview" | "charts" | "quality" | "correlation" | "data";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "charts", label: "Charts" },
  { id: "quality", label: "Data Quality" },
  { id: "correlation", label: "Correlation" },
  { id: "data", label: "Data" },
];

export function ResultsDashboard({ result }: { result: AnalyzeResponse }) {
  const [tab, setTab] = useState<TabId>("overview");
  const { meta, analysis } = result;

  return (
    <div className="space-y-5">
      <OverviewCards result={result} />

      {meta.warnings.length > 0 ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50/70 px-4 py-3 text-sm text-blue-800">
          <span className="font-medium">Ingestion notes:</span> {meta.warnings.join(" · ")}
        </div>
      ) : null}

      {/* Tab navigation */}
      <div className="flex gap-1 overflow-x-auto border-b border-slate-200">
        {TABS.map((t) => {
          const isCorr = t.id === "correlation";
          const corrDisabled = isCorr && !analysis.has_correlation;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition ${
                tab === t.id
                  ? "text-blue-600"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {t.label}
              {corrDisabled ? <span className="ml-1 text-xs text-slate-300">(n/a)</span> : null}
              {tab === t.id ? (
                <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-blue-600" />
              ) : null}
            </button>
          );
        })}
      </div>

      <div className="animate-fade-in">
        {tab === "overview" ? (
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
            <InsightsPanel insights={result.insights} />
            <SummaryStatsTable analysis={analysis} />
            <div className="lg:col-span-2">
              <SchemaTable schema={result.schema} />
            </div>
          </div>
        ) : null}

        {tab === "charts" ? <ChartGrid charts={analysis.charts} /> : null}

        {tab === "quality" ? (
          <DataQualityReport dataQuality={result.data_quality} cleaning={result.cleaning} />
        ) : null}

        {tab === "correlation" ? <CorrelationHeatmap correlation={analysis.correlation} /> : null}

        {tab === "data" ? (
          <DataPreviewTable preview={result.preview} categoricalColumns={analysis.categorical_columns} />
        ) : null}
      </div>
    </div>
  );
}
