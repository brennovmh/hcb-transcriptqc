from pathlib import Path
import subprocess
import sys


def test_validate_samplesheet_success(tmp_path: Path) -> None:
    samplesheet = tmp_path / "samples.csv"
    r1 = tmp_path / "a_R1.fastq.gz"
    r2 = tmp_path / "a_R2.fastq.gz"
    r1.write_text("x")
    r2.write_text("x")
    samplesheet.write_text(
        "sample,fastq_1,fastq_2,group,batch,assay\n"
        f"S1,{r1},{r2},g1,b1,transcriptome\n"
    )
    out_csv = tmp_path / "validated.csv"
    out_json = tmp_path / "validated.json"
    subprocess.run(
        [
            sys.executable,
            "bin/validate_samplesheet.py",
            "--input",
            str(samplesheet),
            "--input-type",
            "fastq",
            "--assay",
            "transcriptome",
            "--output-csv",
            str(out_csv),
            "--output-json",
            str(out_json),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert out_csv.exists()
    assert out_json.exists()


def test_validate_samplesheet_duplicate_fails(tmp_path: Path) -> None:
    bam = tmp_path / "a.bam"
    bai = tmp_path / "a.bam.bai"
    bam.write_text("x")
    bai.write_text("x")
    samplesheet = tmp_path / "samples.csv"
    samplesheet.write_text(
        "sample,bam,group,batch,assay\n"
        f"S1,{bam},g1,b1,transcriptome\n"
        f"S1,{bam},g1,b1,transcriptome\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            "bin/validate_samplesheet.py",
            "--input",
            str(samplesheet),
            "--input-type",
            "bam",
            "--assay",
            "transcriptome",
            "--output-csv",
            str(tmp_path / "validated.csv"),
            "--output-json",
            str(tmp_path / "validated.json"),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Duplicate sample" in (result.stderr + result.stdout)
