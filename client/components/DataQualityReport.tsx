import type { CleaningLog, DataQuality } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { fmtInt, fmtNum, fmtPct } from "@/lib/format";

export function DataQualityReport({
  dataQuality,
  cleaning,
}: {
  dataQuality: DataQuality;
  cleaning: CleaningLog;
}) {
  const dq = dataQuality;

  return (
    <div className="space-y-5">
      {dq.warnings.length > 0 ? (
        <Card className="border-amber-200 bg-amber-50/60">
          <CardBody>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-700">
              {dq.warnings.length} Warning{dq.warnings.length > 1 ? "s" : ""}
            </h4>
            <ul className="space-y-1 text-sm text-amber-800">
              {dq.warnings.map((w, i) => (
                <li key={i} className="flex gap-2">
                  <span>▲</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      ) : null}

      {/* Per-column quality */}
      <Card>
        <CardHeader title="Column Quality" subtitle="Missing values, cardinality, and flags" />
        <CardBody className="p-0">
          <div className="scroll-thin overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-5 py-2 font-medium">Column</th>
                  <th className="px-3 py-2 font-medium">Missing</th>
                  <th className="px-3 py-2 font-medium">Unique</th>
                  <th className="px-5 py-2 font-medium">Flags</th>
                </tr>
              </thead>
              <tbody>
                {dq.columns.map((c) => (
                  <tr key={c.column} className="border-b border-slate-50 last:border-0">
                    <td className="px-5 py-2 font-medium text-slate-800">{c.column}</td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className="h-full rounded-full bg-amber-400"
                            style={{ width: `${Math.min(100, c.null_pct)}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-500">{fmtPct(c.null_pct)}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2 text-slate-600">{fmtInt(c.unique_count)}</td>
                    <td className="px-5 py-2">
                      <div className="flex flex-wrap gap-1">
                        {c.constant ? <Badge tone="red">constant</Badge> : null}
                        {c.high_cardinality ? <Badge tone="violet">high-cardinality</Badge> : null}
                        {c.mixed_type ? <Badge tone="amber">mixed-type</Badge> : null}
                        {!c.constant && !c.high_cardinality && !c.mixed_type ? (
                          <span className="text-xs text-slate-300">—</span>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* Outliers */}
      <Card>
        <CardHeader title="Outliers" subtitle={`Detected via ${dq.outlier_method.toUpperCase()}`} />
        <CardBody className={dq.outliers.length ? "p-0" : ""}>
          {dq.outliers.length === 0 ? (
            <EmptyState title="No outliers detected" description="No numeric values fall outside the detection thresholds." icon="✅" />
          ) : (
            <div className="scroll-thin overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                    <th className="px-5 py-2 font-medium">Column</th>
                    <th className="px-3 py-2 font-medium">Count</th>
                    <th className="px-3 py-2 font-medium">%</th>
                    <th className="px-3 py-2 font-medium">Bounds / Threshold</th>
                    <th className="px-5 py-2 font-medium">Examples</th>
                  </tr>
                </thead>
                <tbody>
                  {dq.outliers.map((o) => (
                    <tr key={o.column} className="border-b border-slate-50 last:border-0">
                      <td className="px-5 py-2 font-medium text-slate-800">{o.column}</td>
                      <td className="px-3 py-2 text-slate-600">{fmtInt(o.count)}</td>
                      <td className="px-3 py-2 text-slate-600">{fmtPct(o.pct)}</td>
                      <td className="px-3 py-2 text-xs text-slate-500">
                        {o.method === "iqr"
                          ? `[${fmtNum(o.lower_bound)}, ${fmtNum(o.upper_bound)}]`
                          : `|z| > ${fmtNum(o.threshold)}`}
                      </td>
                      <td className="max-w-xs truncate px-5 py-2 text-xs text-slate-500">
                        {o.sample_values.map((v) => fmtNum(v)).join(", ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>

      {/* Cleaning transformations log */}
      <Card>
        <CardHeader
          title="Transformations Applied"
          subtitle={`Strategy: ${cleaning.strategy} · ${cleaning.rows_before} → ${cleaning.rows_after} rows`}
        />
        <CardBody className="p-0">
          <div className="scroll-thin max-h-72 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-5 py-2 font-medium">Action</th>
                  <th className="px-3 py-2 font-medium">Column</th>
                  <th className="px-5 py-2 font-medium">Detail</th>
                </tr>
              </thead>
              <tbody>
                {cleaning.transformations.map((t, i) => (
                  <tr key={i} className="border-b border-slate-50 last:border-0">
                    <td className="px-5 py-2">
                      <Badge tone="blue">{t.action}</Badge>
                    </td>
                    <td className="px-3 py-2 font-mono text-xs text-slate-600">{t.column}</td>
                    <td className="px-5 py-2 text-xs text-slate-500">{t.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
