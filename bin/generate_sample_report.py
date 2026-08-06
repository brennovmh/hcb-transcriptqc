#!/usr/bin/env python3
"""Generate a simple standalone HTML QC report from sample JSON."""

from __future__ import annotations

import argparse
import json
import base64
from html import escape
from pathlib import Path

LOGO_PATH = Path(__file__).resolve().parents[1] / "images.jpeg"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(Path(args.input).read_text())
    if LOGO_PATH.exists():
        logo_uri = "data:image/jpeg;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode()
    else:
        logo_uri = ""
    labels = {"total_read_pairs": "Total read pairs", "on_target_percent": "On-target", "median_target_depth": "Median target depth", "targets_covered_100x_percent": "Targets ≥100×", "duplication_percent": "Duplication", "housekeeping_detected_percent": "Internal controls detected", "q30_percent": "Q30 reads", "uniquely_mapped_percent": "Uniquely mapped", "exonic_percent": "Exonic reads", "detected_genes_cpm1": "Genes detected (CPM ≥1)"}
    def pretty_metric(name: str) -> str:
        return labels.get(name, name.replace("_", " ").capitalize())

    def pretty_list(values: list[str]) -> str:
        return ", ".join(pretty_metric(value) for value in values) if values else "None"

    def format_value(metric: str, value: object) -> str:
        if value in (None, "", "NA"):
            return "NA"
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        if metric in {"total_read_pairs", "input_reads", "detected_genes_cpm1"}:
            return f"{number:,.0f}"
        rendered = f"{number:,.3f}".rstrip("0").rstrip(".")
        if metric == "median_target_depth":
            return f"{rendered}×"
        if metric.endswith("_percent") or metric in {"q30_percent", "uniquely_mapped_percent", "exonic_percent", "rrna_percent", "duplication_percent"}:
            return f"{rendered}%"
        return rendered

    rows = []
    for metric, payload in data["metrics"].items():
        status = str(payload.get("status", "NOT_EVALUATED"))
        rows.append(f'<tr><td>{escape(pretty_metric(metric))}</td><td>{escape(format_value(metric, payload.get("value", "NA")))}</td><td><span class="badge {status.lower()}">{escape(status)}</span></td></tr>')
    rows = "\n".join(rows)
    status = escape(str(data["overall_status"]))
    details = data.get("internal_control_details", {})
    gene_rows = []
    for item in str(details.get("gene_counts", "")).split(";"):
        if ":" in item:
            gene, count = item.split(":", 1)
            gene_rows.append(f"<tr><td>{escape(gene)}</td><td>{escape(format_value('gene_count', count))}</td></tr>")
    gene_table = "<table class=\"gene-table\"><thead><tr><th>Gene</th><th>Count</th></tr></thead><tbody>" + "".join(gene_rows) + "</tbody></table>" if gene_rows else "<p class=\"muted\">Not available</p>"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{data['sample']} QC</title>
  <style>
    :root {{ --ink:#17212b; --muted:#607080; --line:#dce4ea; --bg:#f5f8fa; --teal:#0f766e; --red:#b42318; --amber:#a15c00; --green:#18794e; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 Inter,Arial,sans-serif; }}
    .wrap {{ max-width:1000px; margin:0 auto; padding:32px 22px 48px; }}
    header {{ display:flex; justify-content:space-between; gap:20px; align-items:flex-start; margin-bottom:22px; }}
    .brand {{ display:flex; align-items:center; gap:16px; }} .brand img {{ width:112px; height:63px; object-fit:contain; border-radius:8px; background:white; }}
    .gene-table {{ margin-top:10px; }} .gene-table th, .gene-table td {{ padding:8px 12px; }} .gene-table tbody tr:nth-child(even) {{ background:#f7fafb; }}
    h1 {{ margin:0 0 4px; font-size:30px; letter-spacing:-.02em; }} h2 {{ margin:28px 0 10px; font-size:18px; }}
    .meta,.muted {{ color:var(--muted); }} .hero {{ background:white; border:1px solid var(--line); border-radius:14px; padding:22px; box-shadow:0 5px 18px #17324d0b; }}
    .status {{ font-weight:800; font-size:18px; padding:10px 14px; border-radius:10px; background:#eef2f5; white-space:nowrap; }}
    .status.fail {{ color:var(--red); background:#fff0ef; }} .status.warning {{ color:var(--amber); background:#fff7e8; }} .status.pass {{ color:var(--green); background:#edf9f2; }}
    table {{ border-collapse:collapse; width:100%; background:white; border:1px solid var(--line); border-radius:10px; overflow:hidden; }} th,td {{ border-bottom:1px solid var(--line); padding:11px 13px; text-align:left; }} th {{ background:#edf3f5; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }} tr:last-child td {{ border-bottom:0; }}
    .badge {{ display:inline-block; border-radius:999px; padding:2px 9px; font-size:11px; font-weight:800; letter-spacing:.04em; }} .badge.fail {{ color:var(--red); background:#ffe3e0; }} .badge.warning {{ color:var(--amber); background:#ffedc7; }} .badge.pass {{ color:var(--green); background:#dff5e8; }} .badge.not_evaluated {{ color:var(--muted); background:#e8edf0; }}
    .note {{ border-left:4px solid var(--teal); background:#eaf7f5; padding:12px 15px; border-radius:6px; }} .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }} .card {{ background:white; border:1px solid var(--line); border-radius:10px; padding:14px; }}
  </style>
</head>
<body><main class="wrap">
  <header><div class="brand"><img src="{logo_uri}" alt="HCB logo"><div><h1>RNA QC Report</h1><div class="meta">Sample <strong>{escape(data['sample'])}</strong> · Assay {escape(data['assay'])} · Batch {escape(str(data.get('batch', '') or '—'))}</div></div></div><div class="status {str(data['overall_status']).lower()}">{status}</div></header>
  <section class="hero"><strong>Technical conclusion</strong><p>{escape(pretty_list(data.get('failures', []) or data.get('warnings', [])) if (data.get('failures') or data.get('warnings')) else 'All evaluable indicators passed.')}</p><div class="note"><strong>Internal control interpretation:</strong> {escape(data.get('housekeeping_interpretation', 'See assay limitations.'))}</div></section>
  <h2>Metrics</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Internal control detail</h2><div class="card"><p><strong>Detected genes:</strong> {escape(details.get('detected_genes', '') or 'None')}</p>{gene_table}</div>
  <div class="grid"><div class="card"><strong>Warnings</strong><p>{escape(pretty_list(data.get('warnings', [])))}</p></div><div class="card"><strong>Failures</strong><p>{escape(pretty_list(data.get('failures', [])))}</p></div><div class="card"><strong>Not evaluated</strong><p>{escape(pretty_list(data.get('not_evaluated', [])))}</p></div></div>
  <h2>Provenance</h2><p class="muted">Execution date: {escape(str(data.get('execution_date', '')))} · Results are technical and do not replace clinical interpretation.</p>
</main></body>
</html>
"""
    Path(args.output).write_text(html)


if __name__ == "__main__":
    main()
