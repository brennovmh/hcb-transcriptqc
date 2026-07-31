from pathlib import Path
import subprocess
import sys

import pandas as pd


def test_housekeeping_qc(tmp_path: Path) -> None:
    matrix = tmp_path / "matrix.tsv"
    metadata = tmp_path / "meta.csv"
    hk = tmp_path / "hk.tsv"
    matrix.write_text("gene\tS1\tS2\tS3\nACTB\t10\t10\t10\nGAPDH\t5\t5\t5\nHPRT1\t1\t2\t3\n")
    metadata.write_text("sample,group,batch,assay\nS1,g,b,transcriptome\nS2,g,b,transcriptome\nS3,g,b,transcriptome\n")
    hk.write_text("gene\nACTB\nGAPDH\nHPRT1\n")
    output = tmp_path / "hk_metrics.tsv"
    subprocess.run(
        [
            sys.executable,
            "bin/calculate_housekeeping_qc.py",
            "--matrix",
            str(matrix),
            "--metadata",
            str(metadata),
            "--housekeeping",
            str(hk),
            "--output",
            str(output),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    frame = pd.read_csv(output, sep="\t")
    assert set(frame["sample"]) == {"S1", "S2", "S3"}
    assert (frame["housekeeping_detected_percent"] == 100.0).all()
