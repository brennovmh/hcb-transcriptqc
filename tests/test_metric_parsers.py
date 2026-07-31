import gzip
import json
from pathlib import Path
import subprocess
import sys

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_script(script: str, *args: str) -> None:
    subprocess.run(
        [sys.executable, f"bin/{script}", *args],
        check=True,
        cwd=REPO_ROOT,
    )


def test_parse_fastp_json(tmp_path: Path) -> None:
    report = tmp_path / "fastp.json"
    report.write_text(
        json.dumps(
            {
                "summary": {
                    "before_filtering": {
                        "total_reads": 200,
                        "total_bases": 20200,
                        "q20_rate": 0.90,
                        "q30_rate": 0.80,
                        "gc_content": 0.45,
                        "read1_mean_length": 101,
                        "read2_mean_length": 101,
                    },
                    "after_filtering": {
                        "total_reads": 180,
                        "total_bases": 17820,
                        "q20_rate": 0.95,
                        "q30_rate": 0.90,
                        "gc_content": 0.46,
                        "read1_mean_length": 99,
                        "read2_mean_length": 99,
                    },
                },
                "filtering_result": {
                    "too_many_N_reads": 2,
                    "low_quality_reads": 12,
                    "too_short_reads": 6,
                },
                "duplication": {"rate": 0.12},
                "adapter_cutting": {"adapter_trimmed_reads": 30},
            }
        )
    )
    output = tmp_path / "fastp.tsv"

    run_script(
        "parse_fastp_json.py",
        "--input",
        str(report),
        "--sample",
        "S1",
        "--output",
        str(output),
    )

    row = pd.read_csv(output, sep="\t").iloc[0]
    assert row["sample"] == "S1"
    assert row["total_read_pairs"] == 90
    assert row["q30_percent"] == 90
    assert row["reads_removed"] == 20
    assert row["reads_retained_percent"] == 90
    assert row["duplication_percent"] == 12


def test_parse_picard_markduplicates(tmp_path: Path) -> None:
    metrics = tmp_path / "S1.markdup.metrics.txt"
    metrics.write_text(
        "## METRICS CLASS\tpicard.sam.DuplicationMetrics\n"
        "LIBRARY\tUNPAIRED_READS_EXAMINED\tREAD_PAIRS_EXAMINED\t"
        "PERCENT_DUPLICATION\n"
        "lib1\t0\t100\t0.12345\n"
    )
    output = tmp_path / "markdup.tsv"

    run_script(
        "parse_picard_markduplicates.py",
        "--input",
        str(metrics),
        "--output",
        str(output),
    )

    row = pd.read_csv(output, sep="\t").iloc[0]
    assert row["sample"] == "S1"
    assert row["duplication_percent"] == 12.345


def test_parse_picard_rnaseq_metrics(tmp_path: Path) -> None:
    metrics = tmp_path / "S1.rnaseq_metrics.txt"
    headers = [
        "PF_BASES",
        "PCT_RIBOSOMAL_BASES",
        "PCT_CODING_BASES",
        "PCT_UTR_BASES",
        "PCT_INTRONIC_BASES",
        "PCT_INTERGENIC_BASES",
        "MEDIAN_3PRIME_BIAS",
        "MEDIAN_5PRIME_BIAS",
        "MEDIAN_5PRIME_TO_3PRIME_BIAS",
    ]
    values = ["1000", "0.05", "0.45", "0.20", "0.20", "0.10", "0.8", "0.7", "0.875"]
    metrics.write_text(
        "## METRICS CLASS\tpicard.analysis.RnaSeqMetrics\n"
        + "\t".join(headers)
        + "\n"
        + "\t".join(values)
        + "\n"
    )
    output = tmp_path / "rnaseq.tsv"

    run_script(
        "parse_picard_rnaseq_metrics.py",
        "--input",
        str(metrics),
        "--output",
        str(output),
    )

    row = pd.read_csv(output, sep="\t").iloc[0]
    assert row["rrna_percent"] == 5
    assert row["exonic_percent"] == 65
    assert row["five_to_three_ratio"] == 0.875


def test_summarize_rseqc(tmp_path: Path) -> None:
    infer = tmp_path / "infer.txt"
    distribution = tmp_path / "distribution.txt"
    junction_annotation = tmp_path / "junction.xls"
    junction_saturation = tmp_path / "junction.r"
    duplication = tmp_path / "duplication.xls"
    tin = tmp_path / "tin.txt"
    output = tmp_path / "rseqc.tsv"

    infer.write_text("Fraction of reads explained by \"1++,1--,2+-,2-+\": 0.875\n")
    distribution.write_text("Group\tTotal_bases\nExons\t100\n")
    junction_annotation.write_text("100\t80\n")
    junction_saturation.write_text("# x y\n5\t20\n10\t95\n")
    duplication.write_text("Occurrence\tUniqReadNumber\tTotalReadNumber\n1\t90\t0.1\n")
    tin.write_text("# gene\tTIN\nGENE1\t40\nGENE2\t70\n")

    run_script(
        "summarize_rseqc.py",
        "--sample",
        "S1",
        "--infer",
        str(infer),
        "--distribution",
        str(distribution),
        "--junction-annotation",
        str(junction_annotation),
        "--junction-saturation",
        str(junction_saturation),
        "--duplication",
        str(duplication),
        "--tin",
        str(tin),
        "--output",
        str(output),
    )

    row = pd.read_csv(output, sep="\t").iloc[0]
    assert row["median_tin"] == 55
    assert row["transcripts_tin_gt50_percent"] == 50
    assert row["junction_annotated_percent"] == 80
    assert row["junction_saturation"] == 95
    assert row["strand_specificity"] == 0.875
    assert row["read_duplication_percent"] == 10


def test_calculate_target_coverage_from_gzipped_regions(tmp_path: Path) -> None:
    regions = tmp_path / "S1.regions.bed.gz"
    with gzip.open(regions, "wt") as handle:
        handle.write(
            "chr1\t0\t100\ttarget1\t0\n"
            "chr1\t100\t200\ttarget2\t40\n"
            "chr1\t200\t300\ttarget3\t100\n"
            "chr1\t300\t400\ttarget4\t1000\n"
        )
    output = tmp_path / "panel.tsv"

    run_script(
        "calculate_target_coverage.py",
        "--sample",
        "S1",
        "--regions",
        str(regions),
        "--panel-type",
        "hybrid_capture",
        "--output",
        str(output),
    )

    row = pd.read_csv(output, sep="\t").iloc[0]
    assert row["median_target_depth"] == 70
    assert row["mean_target_depth"] == 285
    assert row["targets_covered_20x_percent"] == 75
    assert row["targets_covered_100x_percent"] == 50
    assert row["targets_covered_1000x_percent"] == 25
    assert row["targets_without_coverage"] == 1
