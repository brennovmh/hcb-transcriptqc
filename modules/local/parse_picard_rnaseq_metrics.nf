process PARSE_PICARD_RNASEQ_METRICS {
    tag "${metrics_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    path(metrics_file)

    output:
    path("*.picard_rnaseq.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_picard_rnaseq_metrics.py \
      --input ${metrics_file} \
      --output ${metrics_file.baseName}.picard_rnaseq.tsv
    """
}
