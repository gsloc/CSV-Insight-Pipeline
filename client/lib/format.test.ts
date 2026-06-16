import { describe, it, expect } from "vitest";
import { fmtNum } from "./format";

describe("fmtNum", () => {
  it("returns the em-dash placeholder for missing or non-finite values", () => {
    expect(fmtNum(null)).toBe("—");
    expect(fmtNum(undefined)).toBe("—");
    expect(fmtNum(NaN)).toBe("—");
    expect(fmtNum(Infinity)).toBe("—");
    expect(fmtNum(-Infinity)).toBe("—");
  });

  it("switches to scientific notation for very small magnitudes (< 1e-3)", () => {
    const out = fmtNum(0.0005);
    expect(out).toMatch(/e/i);
  });

  it("switches to scientific notation for very large magnitudes (>= 1e7)", () => {
    const out = fmtNum(9.999e8);
    expect(out).toMatch(/e/i);
  });

  it("does not use scientific notation for zero", () => {
    // The implementation explicitly exempts 0 from the small-magnitude branch.
    expect(fmtNum(0)).not.toMatch(/e/i);
    expect(fmtNum(0)).toBe("0");
  });

  it("formats normal-magnitude numbers as locale decimals (default 2 digits)", () => {
    const out = fmtNum(1234.5678);
    expect(out).not.toMatch(/e/i);
    // Locale-tolerant: contains the integer digits and rounds the fraction to 2 places.
    expect(out).toMatch(/1.?234/);
    expect(out).toMatch(/57/);
  });

  it("respects an explicit digits argument", () => {
    const out = fmtNum(1234.5678, 4);
    expect(out).not.toMatch(/e/i);
    expect(out).toMatch(/5678/);
  });
});
