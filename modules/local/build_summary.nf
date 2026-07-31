process BUILD_SUMMARY {
    tag "build_summary"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    val(json_files)

    output:
    path("overall_qc.tsv"), emit: overall
    path("sequencing_metrics.tsv"), emit: sequencing
    path("alignment_metrics.tsv"), emit: alignment
    path("rnaseq_metrics.tsv"), emit: rnaseq
    path("expression_metrics.tsv"), emit: expression
    path("housekeeping_metrics.tsv"), emit: housekeeping
    path("panel_metrics.tsv"), emit: panel
    path("fusion_readiness_metrics.tsv"), emit: fusion
    path("qc_failures.tsv"), emit: failures

    script:
    def inputs = json_files.collect { it.toString() }.join(' ')
    """
    python3 ${projectDir}/bin/merge_qc_tables.py \
      --inputs ${inputs} \
      --outdir .
    """
}
