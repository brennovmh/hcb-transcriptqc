process CLASSIFY_QC {
    tag "classify_qc"
    label 'process_low'
    publishDir "${params.outdir}/json", mode: params.publish_mode

    input:
    path(metadata_csv)
    path fastq_metrics
    path alignment_metrics
    path rnaseq_metrics
    path expression_metrics
    path housekeeping_metrics
    path panel_metrics
    path fusion_metrics

    output:
    path("*.qc.json"), emit: jsons

    script:
    def inputs = (fastq_metrics + alignment_metrics + rnaseq_metrics + expression_metrics + housekeeping_metrics + panel_metrics + fusion_metrics).collect { it.toString() }.join(' ')
    """
    python3 ${projectDir}/bin/classify_sample_qc.py \
      --metadata ${metadata_csv} \
      --thresholds ${params.thresholds} \
      --assay ${params.assay} \
      ${params.panel_type ? "--panel-type ${params.panel_type}" : ""} \
      --inputs ${inputs}
    """
}
