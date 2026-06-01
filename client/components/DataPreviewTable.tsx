"use client";

import { useMemo, useState } from "react";
import type { Preview } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { cellToString } from "@/lib/format";

export function DataPreviewTable({
  preview,
  categoricalColumns,
}: {
  preview: Preview;
  categoricalColumns: string[];
}) {
  const [search, setSearch] = useState("");
  const [filterCol, setFilterCol] = useState("");
  const [filterVal, setFilterVal] = useState("");

  const filterableCols = categoricalColumns.filter((c) => preview.columns.includes(c));

  const distinctValues = useMemo(() => {
    if (!filterCol) return [];
    const set = new Set<string>();
    for (const row of preview.rows) set.add(cellToString(row[filterCol]));
    return Array.from(set).sort();
  }, [filterCol, preview.rows]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return preview.rows.filter((row) => {
      if (filterCol && filterVal && cellToString(row[filterCol]) !== filterVal) return false;
      if (!q) return true;
      return preview.columns.some((c) => cellToString(row[c]).toLowerCase().includes(q));
    });
  }, [preview, search, filterCol, filterVal]);

  return (
    <Card>
      <CardHeader
        title="Cleaned Data Preview"
        subtitle={`Showing ${filtered.length} of ${preview.rows.length} sampled rows (dataset total: ${preview.total_rows})`}
      />
      <CardBody className="space-y-4">
        {/* Interactive filter controls */}
        <div className="flex flex-wrap items-end gap-3">
          <div className="flex-1 min-w-[180px]">
            <label className="mb-1 block text-xs font-medium text-slate-500">Search</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter rows by any value…"
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          {filterableCols.length > 0 ? (
            <>
              <div className="min-w-[140px]">
                <label className="mb-1 block text-xs font-medium text-slate-500">Slice by column</label>
                <select
                  value={filterCol}
                  onChange={(e) => {
                    setFilterCol(e.target.value);
                    setFilterVal("");
                  }}
                  className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">— none —</option>
                  {filterableCols.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
              <div className="min-w-[140px]">
                <label className="mb-1 block text-xs font-medium text-slate-500">Value</label>
                <select
                  value={filterVal}
                  onChange={(e) => setFilterVal(e.target.value)}
                  disabled={!filterCol}
                  className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm disabled:bg-slate-50 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">— all —</option>
                  {distinctValues.map((v) => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </div>
            </>
          ) : null}
          {(search || filterCol || filterVal) ? (
            <button
              onClick={() => {
                setSearch("");
                setFilterCol("");
                setFilterVal("");
              }}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
            >
              Reset
            </button>
          ) : null}
        </div>

        {filtered.length === 0 ? (
          <EmptyState title="No matching rows" description="Try adjusting your filters." icon="🔍" />
        ) : (
          <div className="scroll-thin max-h-[28rem] overflow-auto rounded-lg border border-slate-100">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-slate-50">
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400">
                  {preview.columns.map((c) => (
                    <th key={c} className="whitespace-nowrap px-4 py-2 font-medium">{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((row, i) => (
                  <tr key={i} className="border-t border-slate-50 hover:bg-slate-50/60">
                    {preview.columns.map((c) => (
                      <td key={c} className="whitespace-nowrap px-4 py-1.5 text-slate-700">
                        {cellToString(row[c])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
