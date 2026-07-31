#!/usr/bin/env python3
"""Calculate housekeeping gene QC summaries."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--housekeeping", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def calculate_cpm(counts: pd.Series) -> pd.Series:
    total = counts.sum()
    return counts * 1_000_000 / total if total else counts * 0


def main() -> None:
    args = parse_args()
    matrix = pd.read_csv(args.matrix, sep="\t")
    metadata = pd.read_csv(args.metadata)
    hk = pd.read_csv(args.housekeeping, sep="\t")
    genes = [gene for gene in hk["gene"].dropna().astype(str).tolist() if gene]
    if not genes:
        raise SystemExit("No valid housekeeping genes were provided")

    subset = matrix[matrix["gene"].isin(genes)].copy()
    if subset.empty:
        raise SystemExit("None of the housekeeping genes were found in the expression matrix")

    sample_columns = [column for column in matrix.columns if column != "gene"]
    rows = []
    for sample in sample_columns:
        values = subset[sample].astype(float)
        cpm = calculate_cpm(matrix[sample].astype(float)).loc[subset.index]
        detected = int((values >= 1).sum())
        expected = len(genes)
        row = {
            "sample": sample,
            "housekeeping_expected": expected,
            "housekeeping_detected": detected,
            "housekeeping_detected_percent": round(detected * 100 / expected, 3) if expected else 0.0,
            "housekeeping_mean_count": round(values.mean(), 3),
            "housekeeping_median_count": round(values.median(), 3),
            "housekeeping_min_count": round(values.min(), 3),
            "housekeeping_max_count": round(values.max(), 3),
            "housekeeping_mean_cpm": round(cpm.mean(), 3),
            "housekeeping_below_limit": int((values < 10).sum()),
            "housekeeping_cv": round(values.std(ddof=0) / values.mean(), 6) if values.mean() else math.nan,
            "housekeeping_iqr": round(values.quantile(0.75) - values.quantile(0.25), 3),
            "housekeeping_outlier": "NO",
        }
        batch = metadata.loc[metadata["sample"] == sample, "batch"]
        row["batch"] = batch.iloc[0] if not batch.empty else ""
        rows.append(row)

    result = pd.DataFrame(rows)
    if len(result) >= 3:
        batch_median = result["housekeeping_median_count"].median()
        batch_std = result["housekeeping_median_count"].std(ddof=0) or 1.0
        result["housekeeping_sample_zscore"] = (result["housekeeping_median_count"] - batch_median) / batch_std
    else:
        result["housekeeping_sample_zscore"] = "NA"

    result.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
