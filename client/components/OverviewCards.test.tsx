import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { OverviewCards } from "./OverviewCards";
import type { AnalyzeResponse } from "@/lib/types";

// Minimal-but-typed builder filling only the fields OverviewCards reads.
function buildResult(score: number): AnalyzeResponse {
  return {
    meta: {
      filename: "sample.csv",
      rows: 100,
      rows_clean: 95,
      columns: 5,
      encoding: "utf-8",
      encoding_confidence: 1,
      header_generated: false,
      skipped_bad_rows: 0,
      missing_strategy: "median",
      outlier_method: "iqr",
      warnings: [],
      processing_ms: 42,
    },
    schema: [],
    data_quality: {
      rows: 95,
      n_columns: 5,
      total_cells: 475,
      total_missing: 5,
      missing_pct: 1.05,
      duplicate_rows: 0,
      columns: [],
      outliers: [],
      outlier_method: "iqr",
      warnings: [],
      quality_score: score,
    },
    cleaning: {
      strategy: "median",
      rows_before: 100,
      rows_after: 95,
      columns_after: 5,
      duplicates_removed: 0,
      transformations: [],
    },
    analysis: {
      numeric_columns: ["a", "b"],
      categorical_columns: [],
      summary_statistics: {},
      categorical_summaries: {},
      correlation: null,
      charts: [],
      single_column: false,
      has_correlation: false,
    },
    insights: {
      headline: "",
      quality_score: score,
      key_findings: [],
      anomalies: [],
      recommended_actions: [],
    },
    preview: { columns: [], rows: [], total_rows: 0 },
  };
}

describe("<OverviewCards /> quality-ring threshold colors", () => {
  it("renders emerald tone for scores ≥ 80", () => {
    const { container } = render(<OverviewCards result={buildResult(85)} />);
    expect(container.querySelector(".text-emerald-600")).not.toBeNull();
    expect(container.querySelector(".stroke-emerald-500")).not.toBeNull();
    expect(container.querySelector(".text-amber-600")).toBeNull();
    expect(container.querySelector(".text-red-600")).toBeNull();
  });

  it("renders amber tone for scores ≥ 60 and < 80", () => {
    const { container } = render(<OverviewCards result={buildResult(70)} />);
    expect(container.querySelector(".text-amber-600")).not.toBeNull();
    expect(container.querySelector(".stroke-amber-500")).not.toBeNull();
    expect(container.querySelector(".text-emerald-600")).toBeNull();
    expect(container.querySelector(".text-red-600")).toBeNull();
  });

  it("renders red tone for scores < 60", () => {
    const { container } = render(<OverviewCards result={buildResult(40)} />);
    expect(container.querySelector(".text-red-600")).not.toBeNull();
    expect(container.querySelector(".stroke-red-500")).not.toBeNull();
    expect(container.querySelector(".text-emerald-600")).toBeNull();
    expect(container.querySelector(".text-amber-600")).toBeNull();
  });
});
