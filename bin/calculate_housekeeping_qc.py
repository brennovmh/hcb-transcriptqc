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
    parser.add_argument("--annotation", default="")
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
    symbols = {}
    if args.annotation:
        import re
        for line in Path(args.annotation).open():
            if "gene_id \"" not in line or "gene_name \"" not in line:
                continue
            gid = re.search(r'gene_id "([^"]+)"', line)
            gname = re.search(r'gene_name "([^"]+)"', line)
            if gid and gname:
                symbols[gid.group(1)] = gname.group(1)
    if not genes:
        sample_columns = [column for column in matrix.columns if column != "gene"]
        rows = [{
            "sample": sample,
            "housekeeping_expected": 0,
            "housekeeping_detected": 0,
            "housekeeping_detected_percent": math.nan,
            "housekeeping_mean_count": math.nan,
            "housekeeping_median_count": math.nan,
            "housekeeping_min_count": math.nan,
            "housekeeping_max_count": math.nan,
            "housekeeping_mean_cpm": math.nan,
            "housekeeping_below_limit": math.nan,
            "housekeeping_cv": math.nan,
            "housekeeping_iqr": math.nan,
            "housekeeping_outlier": "NOT_EVALUATED",
            "housekeeping_detected_genes": "",
            "housekeeping_gene_counts": "",
            "batch": "",
            "housekeeping_sample_zscore": "NA",
        } for sample in sample_columns]
        pd.DataFrame(rows).to_csv(args.output, sep="\t", index=False)
        return

    subset = matrix[matrix["gene"].isin(genes)].copy()
    if subset.empty:
        # GTFs may expose Ensembl gene IDs while the housekeeping list uses
        # symbols. Preserve the report with an explicit unevaluable result;
        # failing the whole run would hide the alignment and expression QC.
        sample_columns = [column for column in matrix.columns if column != "gene"]
        rows = []
        for sample in sample_columns:
            batch = metadata.loc[metadata["sample"] == sample, "batch"]
            rows.append({
                "sample": sample,
                "housekeeping_expected": len(genes),
                "housekeeping_detected": 0,
                "housekeeping_detected_percent": math.nan,
                "housekeeping_mean_count": math.nan,
                "housekeeping_median_count": math.nan,
                "housekeeping_min_count": math.nan,
                "housekeeping_max_count": math.nan,
                "housekeeping_mean_cpm": math.nan,
                "housekeeping_below_limit": math.nan,
                "housekeeping_cv": math.nan,
                "housekeeping_iqr": math.nan,
                "housekeeping_outlier": "NOT_EVALUATED",
                "batch": batch.iloc[0] if not batch.empty else "",
                "housekeeping_sample_zscore": "NA",
            })
        pd.DataFrame(rows).to_csv(args.output, sep="\t", index=False)
        return

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
            "housekeeping_detected_genes": ",".join(symbols.get(str(g), str(g)) for g, v in zip(subset["gene"], values) if v >= 1),
            "housekeeping_gene_counts": ";".join(f"{symbols.get(str(g), str(g))}:{v:g}" for g, v in zip(subset["gene"], values)),
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
