from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def test_normalize_gtf_contigs_maps_primary_mitochondrial_and_alt(tmp_path: Path) -> None:
    fai = tmp_path / "reference.fa.fai"
    fai.write_text(
        "chr1\t100\t0\t100\t101\n"
        "chrM\t20\t102\t20\t21\n"
        "chrUn_KI270442v1\t50\t124\t50\t51\n"
    )
    gtf = tmp_path / "input.gtf"
    gtf.write_text(
        '1\ttest\texon\t1\t10\t.\t+\t.\tgene_id "G1"; transcript_id "T1";\n'
        'MT\ttest\texon\t1\t10\t.\t+\t.\tgene_id "G2"; transcript_id "T2";\n'
        'KI270442.1\ttest\texon\t1\t10\t.\t+\t.\tgene_id "G3"; transcript_id "T3";\n'
        'missing\ttest\texon\t1\t10\t.\t+\t.\tgene_id "G4"; transcript_id "T4";\n'
    )
    output = tmp_path / "output.gtf"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "bin/normalize_gtf_contigs.py"),
            "--input",
            str(gtf),
            "--fai",
            str(fai),
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    records = [line.split("\t", 1)[0] for line in output.read_text().splitlines() if not line.startswith("#")]
    assert records == ["chr1", "chrM", "chrUn_KI270442v1"]
    assert "unmapped=1" in result.stderr


def test_gtf_to_refflat_emits_zero_based_transcript_and_cds_coordinates(tmp_path: Path) -> None:
    gtf = tmp_path / "annotation.gtf"
    gtf.write_text(
        'chr1\ttest\texon\t11\t20\t.\t+\t.\tgene_id "G1"; transcript_id "T1"; gene_name "GENE1";\n'
        'chr1\ttest\tCDS\t13\t18\t.\t+\t0\tgene_id "G1"; transcript_id "T1"; gene_name "GENE1";\n'
        'chr1\ttest\texon\t31\t40\t.\t+\t.\tgene_id "G1"; transcript_id "T1"; gene_name "GENE1";\n'
    )
    output = tmp_path / "annotation.refFlat.txt"

    subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "bin/gtf_to_refflat.py"),
            "--gtf",
            str(gtf),
            "--output",
            str(output),
        ],
        check=True,
    )

    fields = output.read_text().rstrip().split("\t")
    assert fields[:9] == ["GENE1", "T1", "chr1", "+", "10", "40", "12", "18", "2"]
    assert fields[9:] == ["10,30,", "20,40,"]
