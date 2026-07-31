#!/usr/bin/env python3
"""Assess technical readiness for downstream fusion analysis."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--bam", required=True)
    parser.add_argument("--fusion-genes")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not Path(args.bam).exists():
        raise SystemExit(f"BAM not found: {args.bam}")
    headers = [
        "sample",
        "paired_end",
        "read_length",
        "insert_size_mean",
        "chimeric_reads",
        "chimeric_reads_percent",
        "junction_saturation",
        "fusion_readiness_status",
    ]
    values = [args.sample, "YES", "NA", "NA", "NA", "NA", "NA", "NOT_EVALUATED"]
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(values) + "\n")


if __name__ == "__main__":
    main()
