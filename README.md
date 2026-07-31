# RNA-QC

<p align="center"><img src="assets/rna-qc-logo.svg" width="180" alt="RNA-QC logo"></p>
<p align="center"><strong>Controle técnico reprodutível para RNA-seq, WTS e painéis de RNA direcionados.</strong></p>

<p align="center"><img alt="Nextflow DSL2" src="https://img.shields.io/badge/Nextflow-DSL2-0f766e"> <img alt="Docker" src="https://img.shields.io/badge/containers-Docker-2496ed"> <img alt="Status" src="https://img.shields.io/badge/status-MVP%20em%20validação-f59e0b"></p>

## Visão geral

`rna-qc` é um pipeline Nextflow DSL2 para avaliar a qualidade técnica de amostras de RNA antes de expressão diferencial, análise de fusões ou interpretação biológica.

Suporta FASTQ paired-end ou BAM, transcriptoma bulk/WTS, painéis de RNA direcionados, captura híbrida e amplicons. Cada amostra recebe `PASS`, `WARNING`, `FAIL` ou `NOT_EVALUATED`, além de relatórios HTML/JSON, tabelas TSV, MultiQC e rastreabilidade.

O pipeline não faz chamada de fusões, expressão diferencial nem interpretação clínica. `fusion readiness` mede somente adequação técnica para uma análise posterior.

## Estado atual

- índice STAR GRCh38 preparado;
- perfis reais para WTS, Agilent customizado e TruSight RNA Fusion;
- validação de FASTQ e samplesheet;
- execução Docker em modo stub validada para os três desenhos;
- liftover do BED TruSight hg19 para hg38;
- suíte unitária local com 17 testes aprovados.

As primeiras execuções reais ainda precisam ser revisadas antes de uso clínico ou definição de limites de aceitação definitivos.

## Requisitos

- Linux;
- Nextflow `>=24.10`;
- Docker ou Singularity/Apptainer;
- pelo menos 32 GB de RAM para STAR; 48 GB é recomendado para GRCh38;
- espaço suficiente para FASTQs, índice, BAMs e relatórios;
- Python 3.12 para desenvolvimento/testes.

Os containers estão definidos em [`nextflow.config`](nextflow.config). O primeiro uso pode baixar imagens do Quay.io.

## Estrutura

```text
main.nf                    entrada do pipeline
workflows/                 workflow principal
subworkflows/              blocos FASTQ, alinhamento, expressão, painel e reporting
modules/local/             processos específicos do projeto
modules/nf-core/           wrappers de ferramentas
bin/                       parsers, validações e relatórios Python
conf/                      configurações e thresholds
assets/                    configuração MultiQC, logo e genes auxiliares
docs/                      métricas, outputs e validação
tests/                     testes unitários e dados stub
real_data/                 samplesheets e referências de validação
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

O validador verifica nomes duplicados, arquivos ausentes, extensão, índice BAM, campos obrigatórios, ensaio e consistência com os parâmetros da execução.

## Referências

Para FASTQ, são necessários FASTA, GTF compatível com os contigs, índice STAR, `refFlat` para transcriptoma e BED do desenho específico para painéis. Não misture BED hg19/hg38.

O TruSight incluído foi convertido para hg38 com o chain UCSC; 12 intervalos hg19 não convertidos estão preservados em `real_data/references/`.

## Perfis reais

### Transcriptoma WTS

Perfil: [`conf/real_wts.config`](conf/real_wts.config)

```bash
nextflow run main.nf -c conf/real_wts.config -profile docker -resume
```

### Agilent customizado

Perfil: [`conf/real_agilent.config`](conf/real_agilent.config). BED: [`real_data/references/custom_agilent.bed`](real_data/references/custom_agilent.bed).

```bash
nextflow run main.nf -c conf/real_agilent.config -profile docker -resume
```

### TruSight RNA Fusion

Perfil: [`conf/real_trusight.config`](conf/real_trusight.config). Usa o BED convertido para hg38 e a lista de genes TruSight.

```bash
nextflow run main.nf -c conf/real_trusight.config -profile docker -resume
```

Para uma nova rodada, copie o perfil correspondente e ajuste `input`, `outdir`, `targets` e o samplesheet. Não reutilize o BED de outro painel.

## Execução genérica

```bash
nextflow run main.nf \
  --input samplesheet.csv --input_type fastq --assay transcriptome \
  --fasta reference.fa --gtf annotation.gtf --ref_flat annotation.refFlat.txt \
  --star_index star_index --outdir results -profile docker
```

Para painel, acrescente `--panel_type hybrid_capture` ou `--panel_type amplicon` e `--targets panel_targets.hg38.bed`.

Antes de uma execução pesada, use `-stub-run`. Use `-resume` para continuar uma execução interrompida e um `outdir` novo para uma nova análise.

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

## Interpretação

- `PASS`: métricas avaliáveis sem falha crítica;
- `WARNING`: sem falha crítica, mas com alertas;
- `FAIL`: pelo menos uma métrica crítica falhou;
- `NOT_EVALUATED`: informação insuficiente.

Os thresholds em [`conf/thresholds.yaml`](conf/thresholds.yaml) são valores iniciais. Duplicação, housekeeping e reads quiméricos devem ser interpretados conforme o desenho do painel. Reads quiméricos isolados não demonstram uma fusão.

## Testes e desenvolvimento

```bash
/home/bioinfo/miniconda3/bin/python3 -m pytest -q
```

Novos processos ficam em `modules/local/`, wrappers em `modules/nf-core/`, parsers em `bin/`, classificação em `conf/thresholds.yaml` e fluxos em `subworkflows/`. Toda mudança em parser deve incluir fixture/teste.

## Limitações

Os primeiros runs reais ainda precisam de revisão de logs e parsers; alguns campos avançados permanecem `NA`; fusion readiness não substitui caller de fusão; thresholds não são limites clínicos universais; `PASS` técnico não equivale a adequação clínica ou biológica.

## Licença e citações

Consulte [`LICENSE`](LICENSE), [`CITATIONS.md`](CITATIONS.md) e [`CHANGELOG.md`](CHANGELOG.md).
