import type { ReactNode } from "react";
import type { ColumnType } from "@/lib/types";

export type Tone = "slate" | "blue" | "green" | "amber" | "red" | "violet";

const tones: Record<Tone, string> = {
  slate: "bg-slate-100 text-slate-700",
  blue: "bg-blue-100 text-blue-700",
  green: "bg-emerald-100 text-emerald-700",
  amber: "bg-amber-100 text-amber-800",
  red: "bg-red-100 text-red-700",
  violet: "bg-violet-100 text-violet-700",
};

export function Badge({ children, tone = "slate" }: { children: ReactNode; tone?: Tone }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function typeTone(t: ColumnType): Tone {
  switch (t) {
    case "integer":
    case "float":
      return "blue";
    case "datetime":
      return "violet";
    case "categorical":
      return "green";
    case "boolean":
      return "amber";
    default:
      return "slate";
  }
}
