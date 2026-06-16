import "@testing-library/jest-dom/vitest";
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// With Vitest's `globals: false`, Testing Library's automatic afterEach cleanup
// (which it normally registers via the global jest/vitest expect) does not fire.
// Register it ourselves so each test starts with a fresh DOM.
afterEach(() => cleanup());

// jsdom doesn't provide ResizeObserver; Recharts' ResponsiveContainer uses it.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
if (typeof globalThis.ResizeObserver === "undefined") {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (globalThis as any).ResizeObserver = ResizeObserverStub;
}
