from pathlib import Path
import subprocess
import sys

import pandas as pd


def test_parse_samtools_flagstat(tmp_path: Path) -> None:
    flagstat = tmp_path / "S1.flagstat.txt"
    flagstat.write_text(
        "200 + 0 in total (QC-passed reads + QC-failed reads)\n"
        "10 + 0 secondary\n"
        "5 + 0 supplementary\n"
        "170 + 0 properly paired (85.00% : N/A)\n"
    )
    output = tmp_path / "S1.flagstat_metrics.tsv"
    subprocess.run(
        [
            sys.executable,
            "bin/parse_samtools_flagstat.py",
            "--input",
            str(flagstat),
            "--output",
            str(output),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    frame = pd.read_csv(output, sep="\t")
    assert frame.loc[0, "properly_paired_percent"] == 85.0
    assert frame.loc[0, "secondary_reads_percent"] == 5.0
    assert frame.loc[0, "supplementary_reads_percent"] == 2.5


def test_parse_samtools_stats(tmp_path: Path) -> None:
    stats = tmp_path / "S1.samtools.stats.txt"
    stats.write_text(
        "SN\traw total sequences:\t200\n"
        "SN\taverage length:\t101\n"
        "SN\tinsert size average:\t250\n"
        "SN\tinsert size standard deviation:\t20\n"
    )
    output = tmp_path / "S1.samtools_stats_metrics.tsv"
    subprocess.run(
        [
            sys.executable,
            "bin/parse_samtools_stats.py",
            "--input",
            str(stats),
            "--output",
            str(output),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    frame = pd.read_csv(output, sep="\t")
    assert frame.loc[0, "raw_total_sequences"] == 200
    assert frame.loc[0, "insert_size_mean"] == 250
