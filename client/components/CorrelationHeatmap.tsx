import type { Correlation } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { fmtNum } from "@/lib/format";

function corrColor(v: number | null): string {
  if (v === null || Number.isNaN(v)) return "#f8fafc";
  const a = Math.min(1, Math.abs(v));
  return v >= 0
    ? `rgba(37, 99, 235, ${0.1 + 0.75 * a})`
    : `rgba(220, 38, 38, ${0.1 + 0.75 * a})`;
}

export function CorrelationHeatmap({ correlation }: { correlation: Correlation | null }) {
  if (!correlation || correlation.columns.length < 2) {
    return (
      <Card>
        <CardHeader title="Correlation Matrix" />
        <CardBody>
          <EmptyState
            title="Correlation unavailable"
            description="A correlation matrix needs at least two numeric columns. This dataset has fewer, so this view is skipped."
            icon="🔗"
          />
        </CardBody>
      </Card>
    );
  }

  const { columns, matrix, pairs } = correlation;
  const showText = columns.length <= 12;

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader title="Correlation Matrix" subtitle={`${correlation.method} · ${columns.length} numeric columns`} />
        <CardBody className="scroll-thin overflow-x-auto">
          <table className="border-separate" style={{ borderSpacing: 2 }}>
            <thead>
              <tr>
                <th className="p-1" />
                {columns.map((c) => (
                  <th key={c} className="p-1 align-bottom">
                    <div className="mx-auto h-20 w-6 origin-bottom -rotate-45 whitespace-nowrap text-left text-xs text-slate-500">
                      {c}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row, i) => (
                <tr key={columns[i]}>
                  <td className="whitespace-nowrap pr-2 text-right text-xs font-medium text-slate-600">
                    {columns[i]}
                  </td>
                  {row.map((v, j) => (
                    <td
                      key={j}
                      className="h-10 w-10 rounded text-center text-[10px] font-medium"
                      style={{
                        backgroundColor: corrColor(v),
                        color: v !== null && Math.abs(v) > 0.55 ? "white" : "#475569",
                      }}
                      title={`${columns[i]} × ${columns[j]} = ${v === null ? "n/a" : v.toFixed(3)}`}
                    >
                      {showText ? (v === null ? "—" : fmtNum(v, 2)) : ""}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      {pairs.length > 0 ? (
        <Card>
          <CardHeader title="Strongest Relationships" subtitle="Ranked by absolute correlation" />
          <CardBody className="space-y-2">
            {pairs.slice(0, 8).map((p, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="w-44 shrink-0 truncate text-sm text-slate-700">
                  {p.x} ↔ {p.y}
                </span>
                <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className={`absolute top-0 h-full rounded-full ${p.corr >= 0 ? "bg-blue-500" : "bg-red-500"}`}
                    style={{ width: `${Math.abs(p.corr) * 100}%`, left: 0 }}
                  />
                </div>
                <span className="w-14 shrink-0 text-right text-sm font-medium tabular-nums text-slate-600">
                  {p.corr.toFixed(2)}
                </span>
              </div>
            ))}
          </CardBody>
        </Card>
      ) : null}
    </div>
  );
}
