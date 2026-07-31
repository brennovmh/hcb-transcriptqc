# RNA-QC

<p align="center"><img src="assets/rna-qc-logo.svg" width="180" alt="RNA-QC logo"></p>
<p align="center"><strong>Reproducible technical QC for RNA-seq, WTS, and targeted RNA panels.</strong></p>

<p align="center"><img alt="Nextflow DSL2" src="https://img.shields.io/badge/Nextflow-DSL2-0f766e"> <img alt="Docker" src="https://img.shields.io/badge/containers-Docker-2496ed"> <img alt="Status" src="https://img.shields.io/badge/status-MVP%20em%20validação-f59e0b"></p>

## Overview

`rna-qc` is a Nextflow DSL2 pipeline for assessing RNA sample technical quality before differential expression, fusion analysis, or biological interpretation.

It supports paired-end FASTQ or BAM, bulk/WTS transcriptomes, targeted RNA panels, hybrid capture, and amplicons. Each sample receives `PASS`, `WARNING`, `FAIL`, or `NOT_EVALUATED`, together with HTML/JSON reports, TSV tables, MultiQC, and provenance.

The pipeline does not call fusions, perform differential expression, or provide clinical interpretation. `fusion readiness` measures technical suitability for a downstream analysis only.

## Current status

- prepared GRCh38 STAR index;
- real-data profiles for WTS, custom Agilent, and TruSight RNA Fusion;
- FASTQ and samplesheet validation;
- Docker stub execution validated for all three assay designs;
- TruSight BED liftover from hg19 to hg38;
- local unit-test suite with 17 passing tests.

Initial real-data runs still require review before clinical use or final acceptance limits are defined.

## Requirements

- Linux;
- Nextflow `>=24.10`;
- Docker ou Singularity/Apptainer;
- at least 32 GB RAM for STAR; 48 GB is recommended for GRCh38;
- sufficient space for FASTQs, indexes, BAMs, and reports;
- Python 3.12 for development and testing.

Containers are defined in [`nextflow.config`](nextflow.config). The first run may download images from Quay.io.

## Repository layout

```text
main.nf                    entrada do pipeline
workflows/                 workflow principal
subworkflows/              FASTQ, alignment, expression, panel, and reporting blocks
modules/local/             project-specific processes
modules/nf-core/           wrappers de ferramentas
bin/                       Python parsers, validators, and reports
conf/                      configuration and thresholds
assets/                    MultiQC configuration, logo, and helper gene lists
docs/                      metrics, outputs, and validation
tests/                     unit tests and stub data
real_data/                 validation samplesheets and references
```

## Samplesheet

FASTQ:

```csv
sample,fastq_1,fastq_2,group,batch,assay
SAMPLE01,reads/SAMPLE01_R1.fastq.gz,reads/SAMPLE01_R2.fastq.gz,grupo1,lote1,transcriptome
```

BAM:

```csv
sample,bam,group,batch,assay
SAMPLE01,bam/SAMPLE01.bam,grupo1,lote1,transcriptome
```

The validator checks duplicate names, missing files, extensions, BAM indexes, required fields, assay type, and consistency with run parameters.

## References

FASTQ runs require a FASTA, contig-compatible GTF, STAR index, `refFlat` for transcriptome assays, and an assay-specific BED for panels. Do not mix hg19 and hg38 BED files.

The included TruSight BED was converted to hg38 with the UCSC chain; 12 unmapped hg19 intervals are preserved in `real_data/references/`.

## Real-data profiles

### WTS transcriptome

Perfil: [`conf/real_wts.config`](conf/real_wts.config)

```bash
nextflow run main.nf -c conf/real_wts.config -profile docker -resume
```

### Custom Agilent panel

Perfil: [`conf/real_agilent.config`](conf/real_agilent.config). BED: [`real_data/references/custom_agilent.bed`](real_data/references/custom_agilent.bed).

```bash
nextflow run main.nf -c conf/real_agilent.config -profile docker -resume
```

### TruSight RNA Fusion

Profile: [`conf/real_trusight.config`](conf/real_trusight.config). It uses the hg38-converted BED and the TruSight gene list.

```bash
nextflow run main.nf -c conf/real_trusight.config -profile docker -resume
```

Para uma nova rodada, copie o perfil correspondente e ajuste `input`, `outdir`, `targets` e o samplesheet. Não reutilize o BED de outro painel.

## Generic execution

```bash
nextflow run main.nf \
  --input samplesheet.csv --input_type fastq --assay transcriptome \
  --fasta reference.fa --gtf annotation.gtf --ref_flat annotation.refFlat.txt \
  --star_index star_index --outdir results -profile docker
```

For panels, add `--panel_type hybrid_capture` or `--panel_type amplicon` and `--targets panel_targets.hg38.bed`.

Before a heavy run, use `-stub-run`. Use `-resume` to continue an interrupted run and a new `outdir` for a new analysis.

## Outputs

```text
results/
├── fastqc/                 qualidade bruta e pós-trimming
├── fastp/                  reads filtrados e métricas JSON/HTML
├── alignment/              BAM, STAR logs, junctions e quimerismos
├── bam_qc/                 samtools flagstat/stats
├── picard/                 duplicação e métricas RNA-seq
├── expression/             featureCounts, matriz e métricas
├── housekeeping/           métricas de genes housekeeping
├── panel_qc/               profundidade por alvo e thresholds
├── fusion_readiness/       indicadores técnicos de fusão
├── sample_reports/         relatório HTML por amostra
├── json/                   classificação detalhada
├── tables/                 tabelas consolidadas TSV
├── multiqc/                relatório MultiQC
└── pipeline_info/          DAG, trace, timeline e metadata
```

Consulte [`docs/output.md`](docs/output.md) e [`docs/metrics.md`](docs/metrics.md).

## Interpretation

- `PASS`: métricas avaliáveis sem falha crítica;
- `WARNING`: sem falha crítica, mas com alertas;
- `FAIL`: pelo menos uma métrica crítica falhou;
- `NOT_EVALUATED`: informação insuficiente.

Os thresholds em [`conf/thresholds.yaml`](conf/thresholds.yaml) são valores iniciais. Duplicação, housekeeping e reads quiméricos devem ser interpretados conforme o desenho do painel. Reads quiméricos isolados não demonstram uma fusão.

## Testing and development

```bash
/home/bioinfo/miniconda3/bin/python3 -m pytest -q
```

Novos processos ficam em `modules/local/`, wrappers em `modules/nf-core/`, parsers em `bin/`, classificação em `conf/thresholds.yaml` e fluxos em `subworkflows/`. Toda mudança em parser deve incluir fixture/teste.

## Limitations

Os primeiros runs reais ainda precisam de revisão de logs e parsers; alguns campos avançados permanecem `NA`; fusion readiness não substitui caller de fusão; thresholds não são limites clínicos universais; `PASS` técnico não equivale a adequação clínica ou biológica.

## License and citations

Consulte [`LICENSE`](LICENSE), [`CITATIONS.md`](CITATIONS.md) e [`CHANGELOG.md`](CHANGELOG.md).
