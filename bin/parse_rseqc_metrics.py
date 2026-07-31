#!/usr/bin/env python3
"""Normalize RSeQC summary TSV into pipeline metrics TSV."""

from __future__ import annotations

import argparse

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.input, sep="\t")
    expected = [
        "sample",
        "median_tin",
        "transcripts_tin_gt50_percent",
        "junction_saturation",
        "junction_annotated_percent",
        "strand_specificity",
        "gene_body_5prime_bias",
        "gene_body_3prime_bias",
        "five_to_three_ratio",
        "read_duplication_percent",
    ]
    for column in expected:
        if column not in frame.columns:
            frame[column] = "NA"
    frame[expected].to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
