#!/usr/bin/env python3
"""Merge sample JSON files into project-level summary tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


TABLE_MAP = {
    "overall_qc.tsv": [],
    "sequencing_metrics.tsv": ["total_read_pairs", "q30_percent"],
    "alignment_metrics.tsv": ["uniquely_mapped_percent", "duplication_percent"],
    "rnaseq_metrics.tsv": ["exonic_percent", "rrna_percent", "median_tin"],
    "expression_metrics.tsv": ["detected_genes_cpm1"],
    "housekeeping_metrics.tsv": ["housekeeping_detected_percent"],
    "panel_metrics.tsv": ["on_target_percent", "median_target_depth", "targets_covered_100x_percent"],
    "fusion_readiness_metrics.tsv": ["chimeric_reads_percent"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--outdir", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    failures = []
    for path in args.inputs:
        payload = json.loads(Path(path).read_text())
        row = {
            "sample": payload["sample"],
            "assay": payload["assay"],
            "batch": payload.get("batch", ""),
            "overall_status": payload["overall_status"],
        }
        for name, metric in payload["metrics"].items():
            row[name] = metric["value"]
        rows.append(row)
        if payload["failures"]:
            failures.append({"sample": payload["sample"], "failures": ",".join(payload["failures"])})

    frame = pd.DataFrame(rows)
    outdir = Path(args.outdir)
    frame.to_csv(outdir / "overall_qc.tsv", sep="\t", index=False)
    for filename, columns in TABLE_MAP.items():
        if filename == "overall_qc.tsv":
            continue
        keep = ["sample"] + [column for column in columns if column in frame.columns]
        subset = frame[keep] if keep else pd.DataFrame(columns=["sample"])
        subset.to_csv(outdir / filename, sep="\t", index=False)
    pd.DataFrame(failures or [{"sample": "", "failures": ""}]).to_csv(outdir / "qc_failures.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
