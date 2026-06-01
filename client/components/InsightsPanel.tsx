import type { Insights } from "@/lib/types";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";

function List({ items, icon, tone }: { items: string[]; icon: string; tone: string }) {
  if (items.length === 0) return null;
  return (
    <ul className="space-y-1.5">
      {items.map((text, i) => (
        <li key={i} className="flex gap-2 text-sm text-slate-700">
          <span className={`mt-0.5 shrink-0 ${tone}`}>{icon}</span>
          <span>{text}</span>
        </li>
      ))}
    </ul>
  );
}

export function InsightsPanel({ insights }: { insights: Insights }) {
  return (
    <Card>
      <CardHeader title="Executive Summary" subtitle="Automated, rule-based insights" />
      <CardBody className="space-y-5">
        <p className="rounded-lg bg-slate-50 px-4 py-3 text-sm font-medium text-slate-800">
          {insights.headline}
        </p>

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-600">Key Findings</h4>
          <List items={insights.key_findings} icon="◆" tone="text-blue-500" />
        </section>

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-amber-600">Anomalies</h4>
          <List items={insights.anomalies} icon="▲" tone="text-amber-500" />
        </section>

        <section>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-600">Recommended Actions</h4>
          <List items={insights.recommended_actions} icon="✓" tone="text-emerald-500" />
        </section>
      </CardBody>
    </Card>
  );
}
