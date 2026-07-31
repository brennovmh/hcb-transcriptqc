#!/usr/bin/env python3
"""Parse Picard RNA-seq metrics into pipeline TSV."""

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
        if not line.startswith("PF_BASES\t"):
            continue
        headers = line.split("\t")
        for values_line in lines[index + 1 :]:
            if not values_line or values_line.startswith("#"):
                continue
            return dict(zip(headers, values_line.split("\t")))
    raise SystemExit(f"Picard RNA-seq metrics table not found: {path}")


def percent(row: dict[str, str], column: str) -> float:
    try:
        return round(float(row[column]) * 100, 3)
    except (KeyError, ValueError) as exc:
        raise SystemExit(f"invalid {column} in Picard RNA-seq metrics") from exc


def main() -> None:
    args = parse_args()
    row = read_metrics(Path(args.input))
    sample = Path(args.input).name.split(".")[0]
    output_row = {
        "sample": sample,
        "rrna_percent": percent(row, "PCT_RIBOSOMAL_BASES"),
        "coding_percent": percent(row, "PCT_CODING_BASES"),
        "utr_percent": percent(row, "PCT_UTR_BASES"),
        "intronic_percent": percent(row, "PCT_INTRONIC_BASES"),
        "intergenic_percent": percent(row, "PCT_INTERGENIC_BASES"),
        "exonic_percent": round(
            (
                float(row["PCT_CODING_BASES"])
                + float(row["PCT_UTR_BASES"])
            )
            * 100,
            3,
        ),
        "gene_body_3prime_bias": row.get("MEDIAN_3PRIME_BIAS", "NA"),
        "gene_body_5prime_bias": row.get("MEDIAN_5PRIME_BIAS", "NA"),
        "five_to_three_ratio": row.get("MEDIAN_5PRIME_TO_3PRIME_BIAS", "NA"),
    }
    with Path(args.output).open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(output_row),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow(output_row)


if __name__ == "__main__":
    main()
