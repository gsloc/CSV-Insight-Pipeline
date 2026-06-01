import type { AnalyzeResponse, MissingStrategy, OutlierMethod } from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8100";

export async function analyzeCsv(
  file: File,
  missingStrategy: MissingStrategy,
  outlierMethod: OutlierMethod,
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("missing_strategy", missingStrategy);
  form.append("outlier_method", outlierMethod);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/v1/analyze`, { method: "POST", body: form });
  } catch (err) {
    throw new Error(
      `Could not reach the analysis API at ${API_BASE}. Is the backend running?`,
    );
  }

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}.`;
    try {
      const body = await res.json();
      if (body?.detail) {
        detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }

  return (await res.json()) as AnalyzeResponse;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}
