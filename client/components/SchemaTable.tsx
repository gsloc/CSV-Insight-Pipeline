import type { ColumnSchema } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Badge, typeTone } from "@/components/ui/Badge";
import { fmtInt, fmtPct, cellToString } from "@/lib/format";

export function SchemaTable({ schema }: { schema: ColumnSchema[] }) {
  return (
    <Card>
      <CardHeader title="Inferred Schema" subtitle={`${schema.length} columns`} />
      <CardBody className="p-0">
        <div className="scroll-thin overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-400">
                <th className="px-5 py-2 font-medium">Column</th>
                <th className="px-3 py-2 font-medium">Type</th>
                <th className="px-3 py-2 font-medium">Non-null</th>
                <th className="px-3 py-2 font-medium">Missing</th>
                <th className="px-3 py-2 font-medium">Unique</th>
                <th className="px-5 py-2 font-medium">Sample values</th>
              </tr>
            </thead>
            <tbody>
              {schema.map((c) => (
                <tr key={c.name} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
                  <td className="px-5 py-2 font-medium text-slate-800">{c.name}</td>
                  <td className="px-3 py-2">
                    <Badge tone={typeTone(c.inferred_type)}>{c.inferred_type}</Badge>
                  </td>
                  <td className="px-3 py-2 text-slate-600">{fmtInt(c.non_null_count)}</td>
                  <td className="px-3 py-2">
                    <span className={c.null_pct > 0 ? "text-amber-600" : "text-slate-400"}>
                      {fmtPct(c.null_pct)}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-slate-600">{fmtInt(c.unique_count)}</td>
                  <td className="max-w-xs truncate px-5 py-2 text-xs text-slate-500">
                    {c.sample_values.map((v) => cellToString(v)).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardBody>
    </Card>
  );
}
