"use client";

import { useRef, useState } from "react";
import type { MissingStrategy, OutlierMethod } from "@/lib/types";

const ACCEPTED = [".csv", ".tsv", ".txt"];

const STRATEGY_OPTIONS: { value: MissingStrategy; label: string }[] = [
  { value: "median", label: "Median (numeric) / mode" },
  { value: "mean", label: "Mean (numeric) / mode" },
  { value: "mode", label: "Mode (all columns)" },
  { value: "drop", label: "Drop rows with missing" },
];

const METHOD_OPTIONS: { value: OutlierMethod; label: string }[] = [
  { value: "iqr", label: "IQR (Tukey fences)" },
  { value: "zscore", label: "Z-score (|z| > 3)" },
];

function hasAcceptedExt(name: string): boolean {
  const lower = name.toLowerCase();
  return ACCEPTED.some((ext) => lower.endsWith(ext));
}

export function FileUpload({
  onSubmit,
  loading,
}: {
  onSubmit: (file: File, strategy: MissingStrategy, method: OutlierMethod) => void;
  loading: boolean;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [strategy, setStrategy] = useState<MissingStrategy>("median");
  const [method, setMethod] = useState<OutlierMethod>("iqr");
  const [dragOver, setDragOver] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const pick = (f: File | null | undefined) => {
    if (!f) return;
    if (!hasAcceptedExt(f.name)) {
      setLocalError(`Unsupported file type. Please upload one of: ${ACCEPTED.join(", ")}`);
      setFile(null);
      return;
    }
    setLocalError(null);
    setFile(f);
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          pick(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-8 text-center transition ${
          dragOver ? "border-blue-500 bg-blue-50/60" : "border-slate-300 hover:border-slate-400 hover:bg-slate-50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(",")}
          className="hidden"
          onChange={(e) => pick(e.target.files?.[0])}
        />
        <div className="mb-2 text-3xl">{file ? "📄" : "⬆️"}</div>
        {file ? (
          <p className="text-sm font-medium text-slate-800">
            {file.name} <span className="text-slate-400">({(file.size / 1024).toFixed(1)} KB)</span>
          </p>
        ) : (
          <>
            <p className="text-sm font-medium text-slate-700">Drop a CSV here, or click to browse</p>
            <p className="mt-1 text-xs text-slate-400">Accepts {ACCEPTED.join(", ")} · max 50 MB</p>
          </>
        )}
      </div>

      {localError ? <p className="mt-2 text-sm text-red-600">{localError}</p> : null}

      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Missing-value strategy</label>
          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value as MissingStrategy)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {STRATEGY_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Outlier method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value as OutlierMethod)}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {METHOD_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      <button
        disabled={!file || loading}
        onClick={() => file && onSubmit(file, strategy, method)}
        className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {loading ? "Analyzing…" : "Analyze dataset"}
      </button>

      <p className="mt-3 text-center text-xs text-slate-400">
        Try the bundled sample at <code className="rounded bg-slate-100 px-1 py-0.5">sample_data/sample_sales.csv</code>
      </p>
    </div>
  );
}
