import type { ReactNode } from "react";

export function EmptyState({
  title,
  description,
  icon,
}: {
  title: string;
  description?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white/60 py-16 text-center">
      <div className="mb-3 text-4xl">{icon ?? "📊"}</div>
      <h3 className="text-base font-semibold text-slate-800">{title}</h3>
      {description ? <p className="mt-1 max-w-md px-4 text-sm text-slate-500">{description}</p> : null}
    </div>
  );
}
