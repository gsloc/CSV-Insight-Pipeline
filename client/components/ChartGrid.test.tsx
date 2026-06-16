import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChartGrid } from "./ChartGrid";
import type { ChartSpec } from "@/lib/types";

const SPECS: ChartSpec[] = [
  {
    type: "histogram",
    column: "score",
    bins: [{ x0: 0, x1: 1, label: "0–1", count: 3 }],
  },
  {
    type: "bar",
    column: "region",
    data: [{ category: "north", count: 2 }],
  },
  {
    type: "scatter",
    x: "units",
    y: "revenue",
    points: [{ x: 1, y: 10 }],
    corr: 0.9,
  },
];

describe("<ChartGrid />", () => {
  it("renders one filter pill per distinct chart type", () => {
    render(<ChartGrid charts={SPECS} />);

    expect(screen.getByRole("button", { name: /histograms/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /categoricals/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^scatter$/i })).toBeInTheDocument();
  });

  it("shows every chart card by default", () => {
    render(<ChartGrid charts={SPECS} />);

    // Each spec's title appears in its card header.
    expect(screen.getByText("score")).toBeInTheDocument();
    expect(screen.getByText("region")).toBeInTheDocument();
    expect(screen.getByText(/units vs revenue/i)).toBeInTheDocument();
  });

  it("enforces the never-empty invariant: deselecting all pills resets to all-selected", async () => {
    const user = userEvent.setup();
    render(<ChartGrid charts={SPECS} />);

    const histPill = screen.getByRole("button", { name: /histograms/i });
    const barPill = screen.getByRole("button", { name: /categoricals/i });
    const scatterPill = screen.getByRole("button", { name: /^scatter$/i });

    // Toggle every pill off, in order.
    await user.click(histPill);
    await user.click(barPill);
    await user.click(scatterPill);

    // After the third (would-be-empty) click, the toggle handler resets to all-selected.
    // All three card titles should be visible again.
    expect(screen.getByText("score")).toBeInTheDocument();
    expect(screen.getByText("region")).toBeInTheDocument();
    expect(screen.getByText(/units vs revenue/i)).toBeInTheDocument();
  });
});
