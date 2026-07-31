#!/usr/bin/env python3
"""Parse samtools flagstat output into TSV metrics."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def first_int(text: str) -> int:
    match = re.search(r"^\s*(\d+)", text)
    return int(match.group(1)) if match else 0


def first_percent(text: str) -> float | str:
    match = re.search(r"\(([\d.]+)%", text)
    return float(match.group(1)) if match else "NA"


def main() -> None:
    args = parse_args()
    sample = Path(args.input).name.split(".")[0]
    metrics: dict[str, int | float | str] = {
        "sample": sample,
        "reads_total_flagstat": "NA",
        "properly_paired_percent": "NA",
        "secondary_reads_percent": "NA",
        "supplementary_reads_percent": "NA",
    }
    lines = Path(args.input).read_text().splitlines()
    total = None
    secondary = 0
    supplementary = 0
    for line in lines:
        if " in total " in line:
            total = first_int(line)
            metrics["reads_total_flagstat"] = total
        elif " secondary" in line:
            secondary = first_int(line)
        elif " supplementary" in line:
            supplementary = first_int(line)
        elif " properly paired " in line:
            metrics["properly_paired_percent"] = first_percent(line)
    if total and total > 0:
        metrics["secondary_reads_percent"] = round(secondary * 100 / total, 3)
        metrics["supplementary_reads_percent"] = round(supplementary * 100 / total, 3)
    headers = list(metrics.keys())
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(map(str, [metrics[h] for h in headers])) + "\n")


if __name__ == "__main__":
    main()
