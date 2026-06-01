"use client";

import { useEffect, useState } from "react";
import { analyzeCsv, API_BASE, checkHealth } from "@/lib/api";
import type { AnalyzeResponse, MissingStrategy, OutlierMethod } from "@/lib/types";
import { FileUpload } from "@/components/FileUpload";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";

export default function Home() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth().then(setApiOnline);
  }, []);

  async function handleSubmit(file: File, strategy: MissingStrategy, method: OutlierMethod) {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeCsv(file, strategy, method);
      setResult(data);
      setApiOnline(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      checkHealth().then(setApiOnline);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <header className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            CSV Insight Pipeline
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Ingest → validate → clean → analyze. Automated data-quality reports & insights.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span
            className={`inline-block h-2 w-2 rounded-full ${
              apiOnline === null ? "bg-slate-300" : apiOnline ? "bg-emerald-500" : "bg-red-500"
            }`}
          />
          <span className="text-slate-500">
            {apiOnline === null ? "Checking API…" : apiOnline ? "API online" : "API offline"}
          </span>
        </div>
      </header>

      {apiOnline === false ? (
        <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Cannot reach the backend at <code className="rounded bg-red-100 px-1">{API_BASE}</code>. Start it with:{" "}
          <code className="rounded bg-red-100 px-1">cd server &amp;&amp; uvicorn app.main:app --reload</code>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
        {/* Left: controls */}
        <aside className="lg:sticky lg:top-8 lg:self-start">
          <FileUpload onSubmit={handleSubmit} loading={loading} />
        </aside>

        {/* Right: results */}
        <main className="min-w-0">
          {loading ? (
            <Spinner label="Crunching your data…" />
          ) : error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              <p className="font-semibold">Analysis failed</p>
              <p className="mt-1">{error}</p>
            </div>
          ) : result ? (
            <ResultsDashboard result={result} />
          ) : (
            <EmptyState
              title="Upload a CSV to begin"
              description="Your dataset will be profiled for schema, missing values, duplicates, outliers, correlations, and auto-generated charts — all processed server-side."
              icon="🧮"
            />
          )}
        </main>
      </div>

      <footer className="mt-12 border-t border-slate-200 pt-4 text-center text-xs text-slate-400">
        FastAPI + Pandas backend · Next.js + Recharts frontend
      </footer>
    </div>
  );
}
