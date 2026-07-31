process PARSE_RSEQC_METRICS {
    tag "${summary_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    path(summary_file)

    output:
    path("*.rseqc.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_rseqc_metrics.py \
      --input ${summary_file} \
      --output ${summary_file.baseName}.rseqc.tsv
    """
}
