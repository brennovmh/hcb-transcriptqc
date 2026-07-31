import json
from pathlib import Path
import subprocess
import sys


def run_classification(
    tmp_path: Path,
    metric_value: str,
    assay: str = "transcriptome",
    panel_type: str = "",
    metric_column: str = "median_tin",
) -> dict:
    metadata = tmp_path / "meta.csv"
    metrics = tmp_path / "metrics.tsv"
    metadata.write_text("sample,group,batch,assay\nS1,g1,b1,transcriptome\n")
    values = {
        "total_read_pairs": "30000000",
        "uniquely_mapped_percent": "85",
        "exonic_percent": "65",
        "housekeeping_detected_percent": "100",
        "detected_genes_cpm1": "15000",
        "q30_percent": "90",
        "median_tin": "60",
    }
    values[metric_column] = metric_value
    metrics.write_text(
        "sample\ttotal_read_pairs\tuniquely_mapped_percent\texonic_percent\thousekeeping_detected_percent\tdetected_genes_cpm1\tq30_percent\tmedian_tin\n"
        f"S1\t{values['total_read_pairs']}\t{values['uniquely_mapped_percent']}\t{values['exonic_percent']}\t{values['housekeeping_detected_percent']}\t{values['detected_genes_cpm1']}\t{values['q30_percent']}\t{values['median_tin']}\n"
    )
    cmd = [
        sys.executable,
        "bin/classify_sample_qc.py",
        "--metadata",
        str(metadata),
        "--thresholds",
        "conf/thresholds.yaml",
        "--assay",
        assay,
        "--inputs",
        str(metrics),
    ]
    if panel_type:
        cmd.extend(["--panel-type", panel_type])
    subprocess.run(cmd, check=True, cwd=Path(__file__).resolve().parents[1])
    return json.loads((Path(__file__).resolve().parents[1] / "S1.qc.json").read_text())


def test_classification_pass(tmp_path: Path) -> None:
    payload = run_classification(tmp_path, "60")
    assert payload["overall_status"] == "PASS"


def test_classification_warning(tmp_path: Path) -> None:
    payload = run_classification(tmp_path, "40")
    assert payload["overall_status"] == "WARNING"


def test_classification_fail(tmp_path: Path) -> None:
    payload = run_classification(tmp_path, "60", metric_column="uniquely_mapped_percent")
    assert payload["overall_status"] == "FAIL"


def test_panel_amplicon_duplication_informational(tmp_path: Path) -> None:
    metadata = tmp_path / "meta.csv"
    metrics = tmp_path / "metrics.tsv"
    metadata.write_text("sample,group,batch,assay\nS1,g1,b1,panel\n")
    metrics.write_text("sample\ttotal_read_pairs\ton_target_percent\tmedian_target_depth\thousekeeping_detected_percent\tduplication_percent\nS1\t1500000\t90\t2000\t100\t99\n")
    subprocess.run(
        [
            sys.executable,
            "bin/classify_sample_qc.py",
            "--metadata",
            str(metadata),
            "--thresholds",
            "conf/thresholds.yaml",
            "--assay",
            "panel",
            "--panel-type",
            "amplicon",
            "--inputs",
            str(metrics),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    payload = json.loads((Path(__file__).resolve().parents[1] / "S1.qc.json").read_text())
    assert payload["overall_status"] == "PASS"


def test_panel_hybrid_capture_duplication_warning(tmp_path: Path) -> None:
    metadata = tmp_path / "meta.csv"
    metrics = tmp_path / "metrics.tsv"
    metadata.write_text("sample,group,batch,assay\nS1,g1,b1,panel\n")
    metrics.write_text("sample\ttotal_read_pairs\ton_target_percent\tmedian_target_depth\thousekeeping_detected_percent\tduplication_percent\ttargets_covered_100x_percent\nS1\t6000000\t90\t1000\t100\t70\t95\n")
    subprocess.run(
        [
            sys.executable,
            "bin/classify_sample_qc.py",
            "--metadata",
            str(metadata),
            "--thresholds",
            "conf/thresholds.yaml",
            "--assay",
            "panel",
            "--panel-type",
            "hybrid_capture",
            "--inputs",
            str(metrics),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    payload = json.loads((Path(__file__).resolve().parents[1] / "S1.qc.json").read_text())
    assert payload["overall_status"] == "WARNING"
