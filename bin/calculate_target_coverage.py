#!/usr/bin/env python3
"""Create panel coverage QC metrics from mosdepth region output."""

from __future__ import annotations

import argparse
import gzip
from pathlib import Path
from statistics import median
from typing import TextIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--regions", required=True)
    parser.add_argument("--panel-type", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def open_text(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(str(path), mode="rt")
    return path.open()


def read_region_depths(path: Path) -> list[float]:
    if not path.exists():
        raise SystemExit(f"mosdepth regions file not found: {path}")

    depths = []
    with open_text(path) as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip().split("\t")
            try:
                depth = float(parts[-1])
            except (IndexError, ValueError):
                if line_number == 1 and parts[-1].strip().lower() in {"mean", "depth"}:
                    continue
                raise SystemExit(
                    f"invalid mosdepth regions row at {path}:{line_number}: "
                    "expected numeric depth in the last column"
                )
            depths.append(depth)
    return depths


def main() -> None:
    args = parse_args()
    depths = read_region_depths(Path(args.regions))
    headers = [
        "sample",
        "panel_type",
        "on_target_percent",
        "median_target_depth",
        "mean_target_depth",
        "targets_covered_20x_percent",
        "targets_covered_50x_percent",
        "targets_covered_100x_percent",
        "targets_covered_500x_percent",
        "targets_covered_1000x_percent",
        "targets_without_coverage",
    ]
    if not depths:
        values = [args.sample, args.panel_type, "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
    else:
        mean = sum(depths) / len(depths)
        thresholds = {
            20: sum(depth >= 20 for depth in depths) * 100 / len(depths),
            50: sum(depth >= 50 for depth in depths) * 100 / len(depths),
            100: sum(depth >= 100 for depth in depths) * 100 / len(depths),
            500: sum(depth >= 500 for depth in depths) * 100 / len(depths),
            1000: sum(depth >= 1000 for depth in depths) * 100 / len(depths),
        }
        values = [args.sample, args.panel_type, "NA", round(median(depths), 3), round(mean, 3), round(thresholds[20], 3), round(thresholds[50], 3), round(thresholds[100], 3), round(thresholds[500], 3), round(thresholds[1000], 3), sum(depth == 0 for depth in depths)]
    Path(args.output).write_text("\t".join(headers) + "\n" + "\t".join(map(str, values)) + "\n")


if __name__ == "__main__":
    main()
