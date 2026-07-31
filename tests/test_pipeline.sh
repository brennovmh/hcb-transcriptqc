#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

python_bin="${PYTHON:-python3}"
if ! "$python_bin" -c 'import pandas, pytest, yaml; assert __import__("platform").python_implementation() == "CPython"' 2>/dev/null; then
    if command -v conda >/dev/null 2>&1; then
        conda_python="$(conda info --base)/bin/python3"
        if "$conda_python" -c 'import pandas, pytest, yaml' 2>/dev/null; then
            python_bin="$conda_python"
        fi
    fi
fi

"$python_bin" -c 'import pandas, pytest, yaml; assert __import__("platform").python_implementation() == "CPython"'
"$python_bin" -m pytest -q

export PATH="$(dirname "$python_bin"):$PATH"
export NXF_OFFLINE=true
nextflow run main.nf -profile test -stub-run -ansi-log false
nextflow run main.nf -profile test,test_panel -stub-run -ansi-log false

test "$(find tests/results/tables -name '*.tsv' | wc -l)" -ge 16
test "$(find tests/results_panel/panel_qc -name '*.panel_metrics.tsv' | wc -l)" -eq 3
test -f tests/results/tables/overall_qc.tsv
test -f tests/results/tables/qc_failures.tsv
test "$(find tests/results/sample_reports -name '*.qc.html' | wc -l)" -eq 3
test "$(find tests/results_panel/sample_reports -name '*.qc.html' | wc -l)" -eq 3
awk -F '\t' 'NR > 1 { if ($2 != "hybrid_capture" || $4 != 800 || $5 != 850) exit 1 }' tests/results_panel/panel_qc/TEST01.panel_metrics.tsv
