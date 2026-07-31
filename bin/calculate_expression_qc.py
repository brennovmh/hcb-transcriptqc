#!/usr/bin/env python3
"""Build expression matrix and sample-level expression QC metrics."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", nargs="*")
    parser.add_argument("--metadata")
    parser.add_argument("--gtf")
    parser.add_argument("--matrix-output")
    parser.add_argument("--metrics-output")
    parser.add_argument("--mode", default="standard")
    parser.add_argument("--sample", default="")
    parser.add_argument("--output", default="")
    return parser.parse_args()


def load_featurecounts_table(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t", comment="#")
    sample_col = frame.columns[-1]
    return frame.rename(columns={frame.columns[0]: "gene", sample_col: Path(path).name.split(".")[0]})[["gene", Path(path).name.split(".")[0]]]


def load_featurecounts_summary(path: str) -> tuple[str, dict[str, float]]:
    frame = pd.read_csv(path, sep="\t")
    sample = frame.columns[-1]
    return Path(path).name.split(".")[0], {str(row["Status"]): float(row[sample]) for _, row in frame.iterrows()}


def compute_cpm(series: pd.Series) -> pd.Series:
    total = series.sum()
    return series * 1_000_000 / total if total else series * 0


def main() -> None:
    args = parse_args()
    if args.mode == "rseqc_stub":
        Path(args.output).write_text("sample\tgene_body_5prime_bias\tgene_body_3prime_bias\tmedian_tin\n" f"{args.sample}\t0.95\t1.05\tNA\n")
        return

    if not args.counts:
        raise SystemExit("No count files were provided")
    count_paths = [path for path in args.counts if path.endswith(".featurecounts.txt")]
    summary_paths = [path for path in args.counts if path.endswith(".featurecounts.summary")]
    if not count_paths:
        raise SystemExit("No featureCounts count tables were provided")
    tables = [load_featurecounts_table(path) for path in count_paths]
    matrix = tables[0]
    for table in tables[1:]:
        matrix = matrix.merge(table, on="gene", how="outer")
    matrix = matrix.fillna(0)
    matrix.to_csv(args.matrix_output, sep="\t", index=False)
    summary_map = dict(load_featurecounts_summary(path) for path in summary_paths) if summary_paths else {}

    rows = []
    sample_columns = [column for column in matrix.columns if column != "gene"]
    for sample in sample_columns:
        counts = matrix[sample].astype(float)
        cpm = compute_cpm(counts)
        total = counts.sum()
        detected_1 = int((counts >= 1).sum())
        detected_10 = int((counts >= 10).sum())
        detected_cpm1 = int((cpm >= 1).sum())
        top10 = counts.sort_values(ascending=False).head(10).sum()
        top100 = counts.sort_values(ascending=False).head(100).sum()
        probabilities = counts[counts > 0] / total if total else pd.Series(dtype=float)
        entropy = float(-(probabilities * probabilities.map(math.log2)).sum()) if len(probabilities) else math.nan
        rows.append(
            {
                "sample": sample,
                "total_counts": round(total, 3),
                "detected_genes_counts1": detected_1,
                "detected_genes_counts10": detected_10,
                "detected_genes_cpm1": detected_cpm1,
                "detected_genes_tpm1": "NA",
                "assigned_reads_percent": round(summary_map.get(sample, {}).get("Assigned", total) * 100 / sum(summary_map.get(sample, {}).values()), 3) if summary_map.get(sample) else 100.0,
                "unassigned_reads_percent": round(sum(value for key, value in summary_map.get(sample, {}).items() if key.startswith("Unassigned")) * 100 / sum(summary_map.get(sample, {}).values()), 3) if summary_map.get(sample) else 0.0,
                "ambiguous_reads_percent": round(summary_map.get(sample, {}).get("Unassigned_Ambiguity", 0) * 100 / sum(summary_map.get(sample, {}).values()), 3) if summary_map.get(sample) else 0.0,
                "multimapping_reads_percent": round(summary_map.get(sample, {}).get("Unassigned_MultiMapping", 0) * 100 / sum(summary_map.get(sample, {}).values()), 3) if summary_map.get(sample) else 0.0,
                "top10_expression_percent": round(top10 * 100 / total, 3) if total else 0.0,
                "top100_expression_percent": round(top100 * 100 / total, 3) if total else 0.0,
                "expression_entropy": round(entropy, 6) if not math.isnan(entropy) else "NA",
            }
        )
    pd.DataFrame(rows).to_csv(args.metrics_output, sep="\t", index=False)


if __name__ == "__main__":
    main()
