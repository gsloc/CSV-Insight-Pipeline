// Type definitions mirroring the FastAPI /analyze JSON contract.

export type MissingStrategy = "mean" | "median" | "mode" | "drop";
export type OutlierMethod = "iqr" | "zscore";
export type ColumnType =
  | "integer"
  | "float"
  | "datetime"
  | "boolean"
  | "categorical"
  | "text"
  | "empty";

export interface Meta {
  filename: string;
  rows: number;
  rows_clean: number;
  columns: number;
  encoding: string;
  encoding_confidence: number;
  header_generated: boolean;
  skipped_bad_rows: number;
  missing_strategy: MissingStrategy;
  outlier_method: OutlierMethod;
  warnings: string[];
  processing_ms: number;
}

export interface ColumnSchema {
  name: string;
  inferred_type: ColumnType;
  pandas_dtype: string;
  non_null_count: number;
  null_count: number;
  null_pct: number;
  unique_count: number;
  sample_values: unknown[];
  numeric_parse_ratio: number;
}

export interface ColumnQuality {
  column: string;
  inferred_type: ColumnType;
  null_count: number;
  null_pct: number;
  unique_count: number;
  constant: boolean;
  high_cardinality: boolean;
  mixed_type: boolean;
}

export interface OutlierReport {
  column: string;
  method: OutlierMethod;
  count: number;
  pct: number;
  lower_bound: number | null;
  upper_bound: number | null;
  threshold: number | null;
  indices: number[];
  sample_values: number[];
}

export interface DataQuality {
  rows: number;
  n_columns: number;
  total_cells: number;
  total_missing: number;
  missing_pct: number;
  duplicate_rows: number;
  columns: ColumnQuality[];
  outliers: OutlierReport[];
  outlier_method: OutlierMethod;
  warnings: string[];
  quality_score: number;
}

export interface Transformation {
  column: string;
  action: string;
  detail: string;
  count: number;
}

export interface CleaningLog {
  strategy: MissingStrategy;
  rows_before: number;
  rows_after: number;
  columns_after: number;
  duplicates_removed: number;
  transformations: Transformation[];
}

export interface SummaryStat {
  count: number;
  mean?: number;
  median?: number;
  std?: number;
  variance?: number;
  min?: number;
  max?: number;
  range?: number;
  skew?: number;
  percentiles?: Record<string, number>;
}

export interface CorrelationPair {
  x: string;
  y: string;
  corr: number;
}

export interface Correlation {
  method: string;
  columns: string[];
  matrix: (number | null)[][];
  pairs: CorrelationPair[];
}

export interface CategoricalSummary {
  unique: number;
  top: { value: string; count: number }[];
}

export interface HistogramSpec {
  type: "histogram";
  column: string;
  bins: { x0: number; x1: number; label: string; count: number }[];
}

export interface BarSpec {
  type: "bar";
  column: string;
  data: { category: string; count: number }[];
}

export interface ScatterSpec {
  type: "scatter";
  x: string;
  y: string;
  points: { x: number; y: number }[];
  corr?: number;
}

export type ChartSpec = HistogramSpec | BarSpec | ScatterSpec;

export interface Analysis {
  numeric_columns: string[];
  categorical_columns: string[];
  summary_statistics: Record<string, SummaryStat>;
  categorical_summaries: Record<string, CategoricalSummary>;
  correlation: Correlation | null;
  charts: ChartSpec[];
  single_column: boolean;
  has_correlation: boolean;
}

export interface Insights {
  headline: string;
  quality_score: number | null;
  key_findings: string[];
  anomalies: string[];
  recommended_actions: string[];
}

export interface Preview {
  columns: string[];
  rows: Record<string, unknown>[];
  total_rows: number;
}

export interface AnalyzeResponse {
  meta: Meta;
  schema: ColumnSchema[];
  data_quality: DataQuality;
  cleaning: CleaningLog;
  analysis: Analysis;
  insights: Insights;
  preview: Preview;
}
