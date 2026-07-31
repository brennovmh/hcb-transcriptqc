#!/usr/bin/env python3
"""Validate RNA-QC samplesheets."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


VALID_ASSAYS = {"transcriptome", "panel"}
FASTQ_EXTENSIONS = (".fastq", ".fastq.gz", ".fq", ".fq.gz")
BAM_EXTENSIONS = (".bam",)


def existing_file(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = base_dir / path
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")
    return path


def has_valid_extension(path: str, extensions: Iterable[str]) -> bool:
    return any(path.endswith(ext) for ext in extensions)


def validate_row(row: dict[str, str], line_no: int, input_type: str, assay: str, base_dir: Path) -> None:
    sample = row.get("sample", "").strip()
    if not sample:
        raise ValueError(f"Line {line_no}: sample is required")
    row_assay = row.get("assay", "").strip()
    if row_assay not in VALID_ASSAYS:
        raise ValueError(f"Line {line_no}: invalid assay '{row_assay}'")
    if row_assay != assay:
        raise ValueError(f"Line {line_no}: assay '{row_assay}' is inconsistent with --assay '{assay}'")

    if input_type == "fastq":
        for column in ("fastq_1", "fastq_2"):
            value = row.get(column, "").strip()
            if not value:
                raise ValueError(f"Line {line_no}: {column} is required for FASTQ input")
            if not has_valid_extension(value, FASTQ_EXTENSIONS):
                raise ValueError(f"Line {line_no}: invalid FASTQ extension for {column}: {value}")
            existing_file(value, base_dir)
    else:
        bam = row.get("bam", "").strip()
        if not bam:
            raise ValueError(f"Line {line_no}: bam is required for BAM input")
        if not has_valid_extension(bam, BAM_EXTENSIONS):
            raise ValueError(f"Line {line_no}: invalid BAM extension: {bam}")
        bam_path = existing_file(bam, base_dir)
        bai = Path(f"{bam_path}.bai")
        if not bai.exists():
            alt = bam_path.with_suffix(".bai")
            if not alt.exists():
                raise ValueError(f"Line {line_no}: BAM index not found for {bam}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--input-type", required=True, choices=["fastq", "bam"])
    parser.add_argument("--assay", required=True, choices=sorted(VALID_ASSAYS))
    parser.add_argument("--panel-type", default="")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Samplesheet not found: {input_path}")
    if args.assay == "panel" and args.panel_type not in {"hybrid_capture", "amplicon"}:
        raise SystemExit("--panel-type must be provided for panel assays")
    if args.assay != "panel" and args.panel_type:
        raise SystemExit("--panel-type is only valid for panel assays")

    required = ["sample", "group", "batch", "assay"]
    required += ["fastq_1", "fastq_2"] if args.input_type == "fastq" else ["bam"]
    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    with input_path.open() as handle:
        reader = csv.DictReader(handle)
        missing_columns = [column for column in required if column not in (reader.fieldnames or [])]
        if missing_columns:
            raise SystemExit(f"Samplesheet is missing required columns: {', '.join(missing_columns)}")
        for line_no, row in enumerate(reader, start=2):
            validate_row(row, line_no, args.input_type, args.assay, Path(args.base_dir).resolve())
            sample = row["sample"].strip()
            if sample in seen:
                raise SystemExit(f"Duplicate sample detected: {sample}")
            seen.add(sample)
            cleaned = {key: (value or "").strip() for key, value in row.items()}
            rows.append(cleaned)

    if not rows:
        raise SystemExit("Samplesheet is empty")

    output_csv = Path(args.output_csv)
    with output_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    Path(args.output_json).write_text(json.dumps({"samples": rows}, indent=2))


if __name__ == "__main__":
    main()
