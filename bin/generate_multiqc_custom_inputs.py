#!/usr/bin/env python3
"""Generate MultiQC custom content tables from pipeline outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overall", required=True)
    parser.add_argument("--sequencing", required=True)
    parser.add_argument("--alignment", required=True)
    parser.add_argument("--rnaseq", required=True)
    parser.add_argument("--expression", required=True)
    parser.add_argument("--housekeeping", required=True)
    parser.add_argument("--panel", required=True)
    parser.add_argument("--fusion", required=True)
    parser.add_argument("--failures", required=True)
    return parser.parse_args()


def write_mqc(input_path: str, output_name: str, section_name: str, description: str) -> None:
    frame = pd.read_csv(input_path, sep="\t")
    out = Path(output_name)
    with out.open("w") as handle:
        handle.write(f"# id: {out.stem}\n")
        handle.write(f"# section_name: {section_name}\n")
        handle.write(f"# description: {description}\n")
        frame.to_csv(handle, sep="\t", index=False)


def main() -> None:
    args = parse_args()
    write_mqc(args.overall, "rna_qc_overview_mqc.tsv", "RNA QC Overview", "Sample-level RNA QC classification summary.")
    write_mqc(args.sequencing, "rna_qc_sequencing_mqc.tsv", "Sequencing Metrics", "Sequencing metrics parsed from fastp and related tools.")
    write_mqc(args.alignment, "rna_qc_alignment_mqc.tsv", "Alignment Metrics", "Alignment metrics parsed from STAR, samtools and Picard.")
    write_mqc(args.rnaseq, "rna_qc_rnaseq_mqc.tsv", "RNA-seq Metrics", "RNA-specific metrics from Picard and RSeQC.")
    write_mqc(args.expression, "rna_qc_expression_mqc.tsv", "Expression Metrics", "Expression breadth and assignment metrics from featureCounts.")
    write_mqc(args.housekeeping, "rna_qc_housekeeping_mqc.tsv", "Housekeeping QC", "Housekeeping gene detection and distribution metrics.")
    write_mqc(args.panel, "rna_qc_panel_mqc.tsv", "Panel Coverage", "Target coverage metrics for RNA panels.")
    write_mqc(args.fusion, "rna_qc_fusion_mqc.tsv", "Fusion Readiness", "Technical readiness metrics for downstream fusion analysis.")
    write_mqc(args.failures, "rna_qc_failures_mqc.tsv", "QC Failures", "Failed metrics by sample.")


if __name__ == "__main__":
    main()
