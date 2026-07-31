#!/usr/bin/env python3
"""Convert GTF transcript models to Picard-compatible refFlat records."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ATTR_RE = re.compile(r'(\S+)\s+"([^"]+)"')


@dataclass
class Transcript:
    gene: str
    chrom: str
    strand: str
    exons: list[tuple[int, int]] = field(default_factory=list)
    cds: list[tuple[int, int]] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gtf", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_attributes(field: str) -> dict[str, str]:
    return {key: value for key, value in ATTR_RE.findall(field)}


def main() -> None:
    args = parse_args()
    transcripts: dict[str, Transcript] = {}
    skipped = defaultdict(int)

    with Path(args.gtf).open() as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9 or parts[2] not in {"exon", "CDS"}:
                continue
            chrom, _, feature, start, end, _, strand, _, attrs = parts
            attributes = parse_attributes(attrs)
            transcript_id = attributes.get("transcript_id")
            gene_name = attributes.get("gene_name") or attributes.get("gene_id")
            if not transcript_id or not gene_name:
                skipped["missing_id"] += 1
                continue
            transcript = transcripts.get(transcript_id)
            if transcript is None:
                transcript = Transcript(gene=gene_name, chrom=chrom, strand=strand)
                transcripts[transcript_id] = transcript
            elif (transcript.chrom, transcript.strand) != (chrom, strand):
                skipped["inconsistent"] += 1
                continue
            interval = (int(start) - 1, int(end))
            if feature == "exon":
                transcript.exons.append(interval)
            else:
                transcript.cds.append(interval)

    written = 0
    with Path(args.output).open("w") as output:
        for transcript_id, transcript in transcripts.items():
            if not transcript.exons:
                skipped["no_exons"] += 1
                continue
            exons = sorted(set(transcript.exons))
            tx_start = exons[0][0]
            tx_end = max(end for _, end in exons)
            if transcript.cds:
                cds_start = min(start for start, _ in transcript.cds)
                cds_end = max(end for _, end in transcript.cds)
            else:
                cds_start = tx_end
                cds_end = tx_end
            exon_starts = ",".join(str(start) for start, _ in exons) + ","
            exon_ends = ",".join(str(end) for _, end in exons) + ","
            output.write(
                "\t".join(
                    [
                        transcript.gene,
                        transcript_id,
                        transcript.chrom,
                        transcript.strand,
                        str(tx_start),
                        str(tx_end),
                        str(cds_start),
                        str(cds_end),
                        str(len(exons)),
                        exon_starts,
                        exon_ends,
                    ]
                )
                + "\n"
            )
            written += 1

    print(
        f"refFlat conversion: written={written} "
        f"missing_id={skipped['missing_id']} inconsistent={skipped['inconsistent']} "
        f"no_exons={skipped['no_exons']}",
        file=sys.stderr,
    )
    if not written:
        raise SystemExit("No transcript records were written")


if __name__ == "__main__":
    main()
