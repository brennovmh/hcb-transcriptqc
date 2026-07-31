#!/usr/bin/env python3
"""Parse STAR Log.final.out into a TSV metrics file."""

from __future__ import annotations

import argparse
from pathlib import Path


KEY_MAP = {
    "Number of input reads": "input_reads",
    "Uniquely mapped reads %": "uniquely_mapped_percent",
    "Number of reads mapped to multiple loci": "multimapped_reads",
    "% of reads mapped to multiple loci": "multimapped_percent",
    "% of reads unmapped: too many mismatches": "unmapped_mismatches_percent",
    "% of reads unmapped: too short": "unmapped_short_percent",
    "% of reads unmapped: other": "unmapped_other_percent",
    "Mismatch rate per base, %": "mismatch_rate",
    "Deletion rate per base": "deletion_rate",
    "Insertion rate per base": "insertion_rate",
    "Number of splices: Total": "splice_junctions_total",
    "Number of splices: Annotated (sjdb)": "splice_junctions_annotated",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def coerce_value(value: str) -> str:
    return value.replace("%", "").strip()


def main() -> None:
    args = parse_args()
    metrics: dict[str, str] = {"sample": args.sample}
    with Path(args.input).open() as handle:
        for line in handle:
            if "|" not in line:
                continue
            key, value = [item.strip() for item in line.split("|", 1)]
            if key in KEY_MAP:
                metrics[KEY_MAP[key]] = coerce_value(value)
    total = float(metrics.get("splice_junctions_total", "0") or 0)
    annotated = float(metrics.get("splice_junctions_annotated", "0") or 0)
    metrics["splice_junctions_unannotated"] = f"{max(total - annotated, 0):.0f}"
    headers = list(metrics.keys())
    with Path(args.output).open("w") as handle:
        handle.write("\t".join(headers) + "\n")
        handle.write("\t".join(str(metrics[h]) for h in headers) + "\n")


if __name__ == "__main__":
    main()
