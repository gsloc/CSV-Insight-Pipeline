import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { CorrelationHeatmap } from "./CorrelationHeatmap";

describe("<CorrelationHeatmap />", () => {
  it("renders the empty-state message when correlation is null", () => {
    const { container } = render(<CorrelationHeatmap correlation={null} />);

    expect(screen.getByText(/correlation unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/at least two numeric columns/i)).toBeInTheDocument();

    // The heatmap matrix should not render in the fallback state.
    expect(container.querySelector("table")).toBeNull();
  });

  it("renders the empty-state message when there are fewer than 2 numeric columns", () => {
    const { container } = render(
      <CorrelationHeatmap
        correlation={{ method: "pearson", columns: ["only"], matrix: [[1]], pairs: [] }}
      />,
    );

    expect(screen.getByText(/correlation unavailable/i)).toBeInTheDocument();
    expect(container.querySelector("table")).toBeNull();
  });
});
