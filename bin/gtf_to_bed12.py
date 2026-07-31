#!/usr/bin/env python3
"""Convert a GTF file to a minimal BED12 transcript model for RSeQC."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


ATTR_RE = re.compile(r'(\S+)\s+"([^"]+)"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gtf", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_attributes(field: str) -> dict[str, str]:
    return {key: value for key, value in ATTR_RE.findall(field)}


def main() -> None:
    args = parse_args()
    transcripts: dict[str, dict[str, object]] = {}
    exons: dict[str, list[tuple[int, int]]] = defaultdict(list)
    with Path(args.gtf).open() as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip().split("\t")
            if len(parts) < 9 or parts[2] != "exon":
                continue
            chrom, _, _, start, end, _, strand, _, attrs = parts
            attr_map = parse_attributes(attrs)
            transcript_id = attr_map.get("transcript_id") or attr_map.get("gene_id")
            gene_name = attr_map.get("gene_name") or attr_map.get("gene_id") or transcript_id
            if not transcript_id:
                continue
            transcripts[transcript_id] = {"chrom": chrom, "strand": strand, "gene": gene_name}
            exons[transcript_id].append((int(start) - 1, int(end)))
    lines = []
    for transcript_id, transcript in transcripts.items():
        tx_exons = sorted(exons[transcript_id])
        tx_start = tx_exons[0][0]
        tx_end = tx_exons[-1][1]
        block_sizes = ",".join(str(end - start) for start, end in tx_exons) + ","
        block_starts = ",".join(str(start - tx_start) for start, _ in tx_exons) + ","
        lines.append(
            "\t".join(
                [
                    str(transcript["chrom"]),
                    str(tx_start),
                    str(tx_end),
                    f"{transcript['gene']}|{transcript_id}",
                    "0",
                    str(transcript["strand"]),
                    str(tx_start),
                    str(tx_end),
                    "0",
                    str(len(tx_exons)),
                    block_sizes,
                    block_starts,
                ]
            )
        )
    if not lines:
        raise SystemExit("No exon records were found in the GTF")
    Path(args.output).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
