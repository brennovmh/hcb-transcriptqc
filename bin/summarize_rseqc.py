#!/usr/bin/env python3
"""Summarize multiple RSeQC outputs into a single TSV row."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from statistics import median


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--infer", required=True)
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--junction-annotation", required=True)
    parser.add_argument("--junction-saturation", required=True)
    parser.add_argument("--duplication", required=True)
    parser.add_argument("--tin", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_infer(path: str) -> str:
    for line in Path(path).read_text().splitlines():
        if "Fraction of reads explained by" in line:
            return line.split(":")[-1].strip()
    return "NA"


def parse_junction_annotation(path: str) -> str:
    numbers = []
    for line in Path(path).read_text().splitlines():
        parts = line.strip().split()
        for part in parts:
            if part.replace(".", "", 1).isdigit():
                numbers.append(float(part))
    if len(numbers) >= 2 and numbers[0] > 0:
        return str(round(numbers[1] * 100 / numbers[0], 3))
    return "NA"


def parse_junction_saturation(path: str) -> str:
    values = []
    for line in Path(path).read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = re.split(r"\s+", line.strip())
        nums = [float(p) for p in parts if re.fullmatch(r"[\d.]+", p)]
        if nums:
            values.append(nums[-1])
    return str(values[-1]) if values else "NA"


def parse_duplication(path: str) -> str:
    for line in Path(path).read_text().splitlines():
        if "Total reads" in line or "Sequence Duplication Level" in line:
            continue
        parts = re.split(r"\s+", line.strip())
        nums = [float(p) for p in parts if re.fullmatch(r"[\d.]+", p)]
        if nums:
            return str(nums[-1] * 100 if nums[-1] <= 1 else nums[-1])
    return "NA"


def parse_tin(path: str) -> tuple[str, str]:
    values = []
    with Path(path).open() as handle:
        for line in handle:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip().split("\t")
            if len(parts) >= 2 and parts[1].replace(".", "", 1).isdigit():
                values.append(float(parts[1]))
    if not values:
        return "NA", "NA"
    gt50 = sum(v >= 50 for v in values) * 100 / len(values)
    return str(round(median(values), 3)), str(round(gt50, 3))


def main() -> None:
    args = parse_args()
    median_tin, gt50 = parse_tin(args.tin)
    headers = [
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
    values = [
        args.sample,
        median_tin,
        gt50,
        parse_junction_saturation(args.junction_saturation),
        parse_junction_annotation(args.junction_annotation),
        parse_infer(args.infer),
        "NA",
        "NA",
        "NA",
        parse_duplication(args.duplication),
    ]
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(values) + "\n")


if __name__ == "__main__":
    main()
