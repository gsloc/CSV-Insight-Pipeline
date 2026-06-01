"""Rule-based executive insight generation.

Deterministic (no LLM dependency) so insights are reproducible and testable.
Consumes the artifacts produced by the validation + analysis services.
"""
from __future__ import annotations

from typing import Dict, List


def generate_insights(*, meta: dict, schema: List[dict], data_quality: dict, analysis: dict) -> dict:
    findings: List[str] = []
    anomalies: List[str] = []
    recommendations: List[str] = []

    rows = meta.get("rows_clean", meta.get("rows", 0))
    cols = len(schema)
    headline = f"Dataset contains {rows} rows and {cols} columns after cleaning."

    # Column type breakdown
    type_counts: Dict[str, int] = {}
    for c in schema:
        type_counts[c["inferred_type"]] = type_counts.get(c["inferred_type"], 0) + 1
    findings.append("Column types: " + ", ".join(f"{v} {k}" for k, v in sorted(type_counts.items())))

    dq = data_quality
    # Missing values
    for c in dq.get("columns", []):
        if c["null_pct"] >= 20:
            anomalies.append(f"Column '{c['column']}' has {c['null_pct']:.1f}% missing values.")
            recommendations.append(
                f"Consider imputing or dropping '{c['column']}' ({c['null_pct']:.1f}% missing)."
            )

    # Duplicates
    if dq.get("duplicate_rows", 0) > 0:
        anomalies.append(f"{dq['duplicate_rows']} duplicate row(s) detected.")
        recommendations.append(
            f"Remove {dq['duplicate_rows']} duplicate row(s) to avoid skewed statistics."
        )

    # Outliers
    for o in dq.get("outliers", []):
        if o.get("pct", 0) >= 5:
            anomalies.append(f"Column '{o['column']}' has {o['count']} outliers ({o['pct']:.1f}%).")
            recommendations.append(
                f"Investigate {o['count']} outliers in '{o['column']}' (method={o['method']})."
            )

    # Constant columns
    for c in dq.get("columns", []):
        if c.get("constant"):
            anomalies.append(f"Column '{c['column']}' is constant (single value).")
            recommendations.append(f"Drop constant column '{c['column']}' — it carries no signal.")

    # Correlations -> key drivers
    corr = analysis.get("correlation")
    if corr and corr.get("pairs"):
        strong = [p for p in corr["pairs"] if abs(p["corr"]) >= 0.7]
        for p in strong[:5]:
            findings.append(
                f"Strong correlation between '{p['x']}' and '{p['y']}' (r={p['corr']:.2f})."
            )
        if strong:
            recommendations.append(
                "Strongly correlated features may be redundant; consider dimensionality reduction."
            )

    # Dispersion driver
    stats = analysis.get("summary_statistics", {})
    ranked = sorted(((c, v) for c, v in stats.items() if "std" in v),
                    key=lambda kv: kv[1]["std"], reverse=True)
    if ranked:
        top = ranked[0]
        findings.append(f"'{top[0]}' shows the highest dispersion (std={top[1]['std']:.2f}).")

    if not anomalies:
        anomalies.append("No major data-quality anomalies detected.")
    if not recommendations:
        recommendations.append("Data looks clean — proceed to modeling or reporting.")

    return {
        "headline": headline,
        "quality_score": dq.get("quality_score"),
        "key_findings": findings,
        "anomalies": anomalies,
        "recommended_actions": recommendations,
    }
