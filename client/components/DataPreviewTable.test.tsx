import { describe, it, expect } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { DataPreviewTable } from "./DataPreviewTable";
import type { Preview } from "@/lib/types";

const PREVIEW: Preview = {
  columns: ["name", "region"],
  rows: [
    { name: "alice", region: "north" },
    { name: "bob", region: "south" },
    { name: "carol", region: "north" },
    { name: "dave", region: "west" },
  ],
  total_rows: 4,
};

function bodyRowCount() {
  // The table body lives inside a <table>. Count <tbody> > <tr>.
  const table = document.querySelector("table");
  if (!table) return 0;
  return table.querySelectorAll("tbody tr").length;
}

describe("<DataPreviewTable />", () => {
  it("renders every row by default", () => {
    render(<DataPreviewTable preview={PREVIEW} categoricalColumns={["region"]} />);

    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("bob")).toBeInTheDocument();
    expect(screen.getByText("carol")).toBeInTheDocument();
    expect(screen.getByText("dave")).toBeInTheDocument();
    expect(bodyRowCount()).toBe(4);
  });

  it("filters rows by free-text search across all columns", async () => {
    const user = userEvent.setup();
    render(<DataPreviewTable preview={PREVIEW} categoricalColumns={["region"]} />);

    await user.type(screen.getByRole("textbox"), "alice");

    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.queryByText("bob")).not.toBeInTheDocument();
    expect(screen.queryByText("carol")).not.toBeInTheDocument();
    expect(screen.queryByText("dave")).not.toBeInTheDocument();
    expect(bodyRowCount()).toBe(1);
  });

  it("restricts rows further by the slice-by-column selector", async () => {
    const user = userEvent.setup();
    render(<DataPreviewTable preview={PREVIEW} categoricalColumns={["region"]} />);

    // Two <select>s: [0] slice-by-column, [1] value.
    const selects = screen.getAllByRole("combobox");
    await user.selectOptions(selects[0], "region");
    await user.selectOptions(selects[1], "north");

    expect(screen.getByText("alice")).toBeInTheDocument();
    expect(screen.getByText("carol")).toBeInTheDocument();
    expect(screen.queryByText("bob")).not.toBeInTheDocument();
    expect(screen.queryByText("dave")).not.toBeInTheDocument();
    expect(bodyRowCount()).toBe(2);
  });

  it("combines search and slice filters with AND logic", async () => {
    const user = userEvent.setup();
    render(<DataPreviewTable preview={PREVIEW} categoricalColumns={["region"]} />);

    // "ali" matches only alice (carol contains "a" but not "ali").
    await user.type(screen.getByRole("textbox"), "ali");

    const selects = screen.getAllByRole("combobox");
    await user.selectOptions(selects[0], "region");
    await user.selectOptions(selects[1], "north");

    expect(screen.getByText("alice")).toBeInTheDocument();
    // Carol is north (passes slice) but doesn't contain "ali" (fails search).
    expect(screen.queryByText("carol")).not.toBeInTheDocument();
    // Bob is "ali"-free (fails search) AND south (fails slice).
    expect(screen.queryByText("bob")).not.toBeInTheDocument();
    expect(bodyRowCount()).toBe(1);
  });
});
