import type { AnalyzeResponse } from "@/lib/types";
import { fmtInt, fmtNum } from "@/lib/format";

function scoreTone(score: number): { text: string; ring: string } {
  if (score >= 80) return { text: "text-emerald-600", ring: "stroke-emerald-500" };
  if (score >= 60) return { text: "text-amber-600", ring: "stroke-amber-500" };
  return { text: "text-red-600", ring: "stroke-red-500" };
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
      {hint ? <p className="mt-0.5 text-xs text-slate-500">{hint}</p> : null}
    </div>
  );
}

export function OverviewCards({ result }: { result: AnalyzeResponse }) {
  const { meta, data_quality, analysis } = result;
  const score = data_quality.quality_score;
  const tone = scoreTone(score);
  const circumference = 2 * Math.PI * 26;
  const offset = circumference * (1 - Math.max(0, Math.min(100, score)) / 100);
  const outlierCells = data_quality.outliers.reduce((sum, o) => sum + o.count, 0);

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {/* Quality score ring */}
      <div className="col-span-2 row-span-1 flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm sm:col-span-3 lg:col-span-2">
        <div className="relative h-16 w-16 shrink-0">
          <svg viewBox="0 0 64 64" className="h-16 w-16 -rotate-90">
            <circle cx="32" cy="32" r="26" fill="none" stroke="#e2e8f0" strokeWidth="8" />
            <circle
              cx="32"
              cy="32"
              r="26"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={tone.ring}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <span className={`absolute inset-0 flex items-center justify-center text-sm font-bold ${tone.text}`}>
            {Math.round(score)}
          </span>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Data Quality</p>
          <p className={`text-lg font-semibold ${tone.text}`}>{fmtNum(score, 1)} / 100</p>
          <p className="text-xs text-slate-500">{meta.filename}</p>
        </div>
      </div>

      <Stat label="Rows" value={fmtInt(meta.rows_clean)} hint={`${fmtInt(meta.rows)} raw → cleaned`} />
      <Stat label="Columns" value={fmtInt(meta.columns)} hint={`${analysis.numeric_columns.length} numeric`} />
      <Stat label="Missing" value={`${fmtNum(data_quality.missing_pct, 1)}%`} hint={`${fmtInt(data_quality.total_missing)} cells`} />
      <Stat label="Duplicates" value={fmtInt(data_quality.duplicate_rows)} hint="exact row matches" />
      <Stat label="Outliers" value={fmtInt(outlierCells)} hint={`via ${data_quality.outlier_method.toUpperCase()}`} />
      <Stat label="Processed" value={`${fmtNum(meta.processing_ms, 0)} ms`} hint={`encoding: ${meta.encoding}`} />
    </div>
  );
}
