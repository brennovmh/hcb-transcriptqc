#!/usr/bin/env python3
"""Generate compact RSeQC-like outputs for test/stub runs."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--plot", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    Path(args.output).write_text(
        "sample\tmedian_tin\ttranscripts_tin_gt50_percent\tjunction_saturation\tjunction_annotated_percent\tstrand_specificity\tgene_body_5prime_bias\tgene_body_3prime_bias\tfive_to_three_ratio\tread_duplication_percent\n"
        f"{args.sample}\t60\t80\t0.82\t78\tFR\t0.95\t1.05\t0.90\t12\n"
    )
    Path(args.plot).write_text("position\tcoverage\n1\t0.95\n50\t1.00\n100\t1.05\n")


if __name__ == "__main__":
    main()
