#!/usr/bin/env python3
"""Parse Picard MarkDuplicates metrics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def read_metrics(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("LIBRARY\t"):
            continue
        headers = line.split("\t")
        for values_line in lines[index + 1 :]:
            if not values_line or values_line.startswith("#"):
                continue
            return dict(zip(headers, values_line.split("\t")))
    raise SystemExit(f"Picard MarkDuplicates metrics table not found: {path}")


def main() -> None:
    args = parse_args()
    metrics = read_metrics(Path(args.input))
    try:
        duplication_percent = round(float(metrics["PERCENT_DUPLICATION"]) * 100, 3)
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"invalid PERCENT_DUPLICATION in {args.input}") from exc

    sample = Path(args.input).name.split(".")[0]
    with Path(args.output).open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["sample", "duplication_percent"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(
            {
                "sample": sample,
                "duplication_percent": duplication_percent,
            }
        )


if __name__ == "__main__":
    main()
