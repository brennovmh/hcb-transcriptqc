#!/usr/bin/env python3
"""Generate a simple standalone HTML QC report from sample JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(Path(args.input).read_text())
    rows = "\n".join(
        f"<tr><td>{metric}</td><td>{payload.get('value')}</td><td>{payload.get('status')}</td></tr>"
        for metric, payload in data["metrics"].items()
    )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{data['sample']} QC</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .status {{ font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem; text-align: left; }}
    th {{ background: #f0f0f0; }}
  </style>
</head>
<body>
  <h1>RNA QC report: {data['sample']}</h1>
  <p>Assay: {data['assay']}</p>
  <p>Batch: {data.get('batch', '')}</p>
  <p class="status">Overall status: {data['overall_status']}</p>
  <p>Justification: {data.get('justification', '')}</p>
  <h2>Metrics</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Warnings</h2>
  <p>{', '.join(data.get('warnings', [])) or 'None'}</p>
  <h2>Failures</h2>
  <p>{', '.join(data.get('failures', [])) or 'None'}</p>
  <h2>Not evaluated</h2>
  <p>{', '.join(data.get('not_evaluated', [])) or 'None'}</p>
  <h2>Provenance</h2>
  <p>Execution date: {data.get('execution_date', '')}</p>
</body>
</html>
"""
    Path(args.output).write_text(html)


if __name__ == "__main__":
    main()
