#!/usr/bin/env python3
"""Parse fastp JSON into per-sample TSV metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--sample", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(Path(args.input).read_text())
    before = data.get("summary", {}).get("before_filtering", {})
    after = data.get("summary", {}).get("after_filtering", {})
    filtering = data.get("filtering_result", {})
    duplication = data.get("duplication", {})
    adapters = data.get("adapter_cutting", {})

    before_reads = float(before.get("total_reads", 0))
    after_reads = float(after.get("total_reads", 0))
    denom = before_reads if before_reads else 1.0
    headers = [
        "sample",
        "total_reads",
        "total_read_pairs",
        "total_bases",
        "q20_percent",
        "q30_percent",
        "gc_percent",
        "mean_read_length",
        "adapter_trimmed_reads",
        "reads_removed",
        "reads_retained_after_trimming",
        "reads_retained_percent",
        "duplication_percent",
        "n_failed_reads",
        "low_quality_reads",
        "too_short_reads",
    ]
    values = [
        args.sample,
        int(after_reads or before_reads),
        round((after_reads or before_reads) / 2, 3),
        after.get("total_bases", before.get("total_bases", "NA")),
        round(float(after.get("q20_rate", before.get("q20_rate", 0))) * 100, 3),
        round(float(after.get("q30_rate", before.get("q30_rate", 0))) * 100, 3),
        round(float(after.get("gc_content", before.get("gc_content", 0))) * 100, 3),
        round((float(after.get("read1_mean_length", before.get("read1_mean_length", 0))) + float(after.get("read2_mean_length", before.get("read2_mean_length", 0)))) / 2, 3),
        adapters.get("adapter_trimmed_reads", 0),
        int(before_reads - after_reads),
        int(after_reads),
        round(after_reads * 100 / denom, 3),
        round(float(duplication.get("rate", 0)) * 100, 3),
        filtering.get("too_many_N_reads", 0),
        filtering.get("low_quality_reads", 0),
        filtering.get("too_short_reads", 0),
    ]
    Path(args.output).write_text("\t".join(map(str, headers)) + "\n" + "\t".join(map(str, values)) + "\n")


if __name__ == "__main__":
    main()
