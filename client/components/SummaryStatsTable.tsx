import type { Analysis } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { fmtNum } from "@/lib/format";

export function SummaryStatsTable({ analysis }: { analysis: Analysis }) {
  const cols = analysis.numeric_columns.filter((c) => (analysis.summary_statistics[c]?.count ?? 0) > 0);

  if (cols.length === 0) {
    return (
      <Card>
        <CardHeader title="Summary Statistics" />
        <CardBody>
          <EmptyState title="No numeric columns" description="Summary statistics require at least one numeric column." icon="🔢" />
        </CardBody>
      </Card>
    );
  }

  const headers = ["Column", "Count", "Mean", "Median", "Std", "Min", "Max", "P25", "P75"];

  return (
    <Card>
      <CardHeader title="Summary Statistics" subtitle={`${cols.length} numeric columns`} />
      <CardBody className="p-0">
        <div className="scroll-thin overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                {headers.map((h) => (
                  <th key={h} className="px-4 py-2 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cols.map((c) => {
                const s = analysis.summary_statistics[c];
                return (
                  <tr key={c} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
                    <td className="px-4 py-2 font-medium text-slate-800">{c}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.count, 0)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.mean)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.median)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.std)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.min)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.max)}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.percentiles?.["25"])}</td>
                    <td className="px-4 py-2 text-slate-600">{fmtNum(s.percentiles?.["75"])}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardBody>
    </Card>
  );
}
