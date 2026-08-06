process HOUSEKEEPING_QC {
    tag "housekeeping"
    label 'process_low'
    publishDir "${params.outdir}/housekeeping", mode: params.publish_mode

    input:
    path(matrix_tsv)
    path(metadata_csv)

    output:
    path("housekeeping_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/calculate_housekeeping_qc.py \
      --matrix ${matrix_tsv} \
      --metadata ${metadata_csv} \
      --housekeeping ${params.housekeeping_genes} \
      --annotation ${params.gtf} \
      --output housekeeping_metrics.tsv
    """
}
