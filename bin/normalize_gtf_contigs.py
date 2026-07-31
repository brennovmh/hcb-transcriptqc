#!/usr/bin/env python3
"""Normalize GTF contig names against a reference FASTA index."""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from collections import Counter
from pathlib import Path
from typing import TextIO


ACCESSION_RE = re.compile(r"(?:GL|KI)\d+v\d+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input GTF (plain text or .gz)")
    parser.add_argument("--fai", required=True, help="Reference FASTA .fai")
    parser.add_argument("--output", required=True, help="Normalized, uncompressed GTF")
    return parser.parse_args()


def open_gtf(path: Path) -> TextIO:
    if path.suffix == ".gz":
        return gzip.open(path, "rt")
    return path.open()


def load_contigs(fai: Path) -> tuple[set[str], dict[str, str]]:
    contigs: set[str] = set()
    accession_aliases: dict[str, str] = {}
    ambiguous: set[str] = set()

    with fai.open() as handle:
        for line in handle:
            contig = line.split("\t", 1)[0]
            if not contig:
                continue
            contigs.add(contig)
            match = ACCESSION_RE.search(contig)
            if match:
                alias = match.group(0).replace("v", ".")
                if alias in accession_aliases:
                    ambiguous.add(alias)
                else:
                    accession_aliases[alias] = contig

    for alias in ambiguous:
        accession_aliases.pop(alias, None)
    return contigs, accession_aliases


def map_contig(contig: str, reference: set[str], aliases: dict[str, str]) -> str | None:
    if contig in reference:
        return contig
    if contig == "MT" and "chrM" in reference:
        return "chrM"
    prefixed = f"chr{contig}"
    if prefixed in reference:
        return prefixed
    return aliases.get(contig)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    fai_path = Path(args.fai)
    output_path = Path(args.output)
    reference, aliases = load_contigs(fai_path)
    counts: Counter[str] = Counter()

    with open_gtf(input_path) as source, output_path.open("w") as output:
        output.write(f"#!contigs-normalized-against {fai_path}\n")
        for line in source:
            if line.startswith("#"):
                output.write(line)
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                counts["malformed"] += 1
                continue
            mapped = map_contig(parts[0], reference, aliases)
            if mapped is None:
                counts["unmapped"] += 1
                continue
            if mapped != parts[0]:
                counts["renamed"] += 1
            parts[0] = mapped
            output.write("\t".join(parts) + "\n")
            counts["written"] += 1

    print(
        "GTF normalization: "
        f"written={counts['written']} renamed={counts['renamed']} "
        f"unmapped={counts['unmapped']} malformed={counts['malformed']}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
