process EXPRESSION_SUMMARY {
    tag "expression_summary"
    label 'process_low'
    publishDir "${params.outdir}/expression", mode: params.publish_mode

    input:
    path(count_files)
    path(metadata_csv)

    output:
    path("expression_matrix.tsv"), emit: matrix
    path("expression_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/calculate_expression_qc.py \
      --counts ${count_files.join(' ')} \
      --metadata ${metadata_csv} \
      --gtf ${params.gtf} \
      --matrix-output expression_matrix.tsv \
      --metrics-output expression_metrics.tsv
    """
}
