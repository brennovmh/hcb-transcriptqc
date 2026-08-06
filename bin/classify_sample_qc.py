#!/usr/bin/env python3
"""Classify RNA QC metrics per sample using YAML thresholds."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--thresholds", required=True)
    parser.add_argument("--assay", required=True)
    parser.add_argument("--panel-type", default="")
    parser.add_argument("--inputs", nargs="*", default=[])
    return parser.parse_args()


def pick_threshold_block(args: argparse.Namespace, data: dict[str, Any]) -> dict[str, Any]:
    if args.assay == "transcriptome":
        return data["transcriptome"]
    key = "panel_hybrid_capture" if args.panel_type == "hybrid_capture" else "panel_amplicon"
    return data[key]


def merge_metrics(paths: list[str]) -> pd.DataFrame:
    frames = []
    for path in paths:
        path_obj = Path(path)
        if not path_obj.exists() or path_obj.name.startswith("NO_"):
            continue
        frame = pd.read_csv(path_obj, sep="\t")
        # Keep pre-alignment fastp duplication separate from the final QC
        # duplication metric. The classification field is reserved for the
        # post-alignment Picard estimate.
        if "fastp_metrics" in path_obj.name and "duplication_percent" in frame.columns:
            frame = frame.rename(columns={"duplication_percent": "fastp_duplication_percent"})
        if "sample" in frame.columns:
            frames.append(frame)
    if not frames:
        return pd.DataFrame(columns=["sample"])
    # Each process emits one row per sample.  Prefer the last non-null value
    # when a metric is emitted by more than one QC stage: alignment-derived
    # metrics (e.g. Picard duplication) arrive after pre-alignment fastp
    # metrics and are the appropriate values for final classification.
    result = pd.concat(frames, ignore_index=True, sort=False)
    grouped = result.groupby("sample", as_index=False, sort=False)
    rows = []
    for sample, frame in grouped:
        row = {"sample": sample}
        for column in result.columns:
            if column == "sample":
                continue
            values = frame[column].dropna()
            if not values.empty:
                row[column] = values.iloc[-1]
        rows.append(row)
    return pd.DataFrame(rows)


def evaluate_metric(value: Any, spec: dict[str, Any]) -> str:
    if pd.isna(value) or value in {"NA", "NOT_EVALUATED", ""}:
        return "NOT_EVALUATED"
    direction = spec.get("direction", "informational")
    if direction == "informational":
        return "PASS"
    numeric = float(value)
    warning = spec.get("warning")
    fail = spec.get("fail")
    if direction == "minimum":
        if fail is not None and numeric < float(fail):
            return "FAIL"
        if warning is not None and numeric < float(warning):
            return "WARNING"
        return "PASS"
    if direction == "maximum":
        if fail is not None and numeric > float(fail):
            return "FAIL"
        if warning is not None and numeric > float(warning):
            return "WARNING"
        return "PASS"
    if direction == "range":
        low_warn, high_warn = warning
        low_fail, high_fail = fail
        if numeric < low_fail or numeric > high_fail:
            return "FAIL"
        if numeric < low_warn or numeric > high_warn:
            return "WARNING"
        return "PASS"
    return "NOT_EVALUATED"


def overall_status(metric_statuses: dict[str, str], threshold_block: dict[str, Any], require_complete: bool = False) -> tuple[str, list[str], list[str], list[str]]:
    warnings = [key for key, value in metric_statuses.items() if value == "WARNING"]
    failures = [key for key, value in metric_statuses.items() if value == "FAIL"]
    not_evaluated = [key for key, value in metric_statuses.items() if value == "NOT_EVALUATED"]
    critical_failures = [metric for metric in failures if threshold_block.get(metric, {}).get("critical", False)]
    if critical_failures:
        return "FAIL", warnings, failures, not_evaluated
    if warnings or failures:
        return "WARNING", warnings, failures, not_evaluated
    # A sample cannot be approved when one or more required QC indicators
    # could not be evaluated. This prevents a partial metric set (for
    # example, a single passing value) from producing an unjustified PASS.
    if require_complete and not_evaluated:
        return "NOT_EVALUATED", warnings, failures, not_evaluated
    if metric_statuses:
        return "PASS", warnings, failures, not_evaluated
    return "NOT_EVALUATED", warnings, failures, not_evaluated


def main() -> None:
    args = parse_args()
    metadata = pd.read_csv(args.metadata)
    thresholds = yaml.safe_load(Path(args.thresholds).read_text())
    threshold_block = pick_threshold_block(args, thresholds)
    metrics = merge_metrics(args.inputs)
    merged = metadata.merge(metrics, on="sample", how="left")

    for _, row in merged.iterrows():
        sample = row["sample"]
        metric_map = {}
        metric_statuses = {}
        for metric_name, spec in threshold_block.items():
            value = row[metric_name] if metric_name in row else "NA"
            status = evaluate_metric(value, spec)
            metric_statuses[metric_name] = status
            metric_map[metric_name] = {
                "value": None if pd.isna(value) else value,
                "unit": "%",
                "status": status,
                "threshold_warning": spec.get("warning"),
                "threshold_fail": spec.get("fail"),
                "critical": spec.get("critical", False),
            }
        status, warnings, failures, not_evaluated = overall_status(metric_statuses, threshold_block, require_complete=args.assay == "panel")
        payload = {
            "sample": sample,
            "assay": row["assay"],
            "batch": row.get("batch", ""),
            "overall_status": status,
            "classification_assay_type": args.assay if args.assay == "transcriptome" else f"panel_{args.panel_type}",
            "housekeeping_interpretation": (
                "Canonical housekeeping genes assessed against the transcriptome reference."
                if args.assay == "transcriptome"
                else "Panel-specific internal expression controls selected for strong target capture; they are not universal housekeeping genes."
            ),
            "internal_control_details": {
                "detected_genes": str(row.get("housekeeping_detected_genes", "")),
                "gene_counts": str(row.get("housekeeping_gene_counts", "")),
                "expected": row.get("housekeeping_expected", "NA"),
            },
            "metrics": metric_map,
            "warnings": warnings,
            "failures": failures,
            "not_evaluated": not_evaluated,
            "justification": "; ".join(failures if failures else warnings) if (failures or warnings) else "All evaluable metrics passed",
            "software_versions": {},
            "execution_date": date.today().isoformat(),
        }
        Path(f"{sample}.qc.json").write_text(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
