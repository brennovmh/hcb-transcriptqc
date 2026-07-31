#!/usr/bin/env python3
"""Parse samtools stats output into TSV metrics."""

from __future__ import annotations

import argparse
from pathlib import Path


KEYS = {
    "raw total sequences:": "raw_total_sequences",
    "average length:": "average_read_length",
    "insert size average:": "insert_size_mean",
    "insert size standard deviation:": "insert_size_sd",
    "average quality:": "average_quality",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample = Path(args.input).name.split(".")[0]
    metrics: dict[str, str] = {"sample": sample}
    for line in Path(args.input).read_text().splitlines():
        if not line.startswith("SN\t"):
            continue
        _, key, value = line.split("\t", 2)
        key = key.strip()
        if key in KEYS:
            metrics[KEYS[key]] = value.strip()
    headers = list(metrics.keys())
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(str(metrics[h]) for h in headers) + "\n")


if __name__ == "__main__":
    main()
