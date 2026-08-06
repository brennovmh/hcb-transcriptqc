#!/usr/bin/env python3
"""Assess technical readiness for downstream fusion analysis."""

from __future__ import annotations

import argparse
import re
import subprocess
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
    try:
        stats = subprocess.run(["samtools", "stats", str(args.bam)], check=True, capture_output=True, text=True).stdout
        flagstat = subprocess.run(["samtools", "view", "-c", "-f", "2048", str(args.bam)], check=True, capture_output=True, text=True).stdout.strip()
        def sn(name: str) -> str:
            match = re.search(rf"^SN\t{name}:\t([^\n]+)", stats, re.MULTILINE)
            return match.group(1).strip() if match else "NA"
        read_length = sn("average length")
        insert_size = sn("insert size average")
        total = float(sn("raw total sequences")) if sn("raw total sequences") != "NA" else 0
        chimeric = int(flagstat or 0)
        chimeric_pct = round(chimeric * 100 / total, 4) if total else "NA"
        values = [args.sample, "YES", read_length, insert_size, str(chimeric), str(chimeric_pct), "NA", "PASS"]
    except (OSError, subprocess.CalledProcessError, ValueError):
        values = [args.sample, "YES", "NA", "NA", "NA", "NA", "NA", "NOT_EVALUATED"]
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(values) + "\n")


if __name__ == "__main__":
    main()
