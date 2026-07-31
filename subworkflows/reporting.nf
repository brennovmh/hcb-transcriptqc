include { CLASSIFY_QC } from '../modules/local/classify_qc'
include { BUILD_SUMMARY } from '../modules/local/build_summary'
include { MULTIQC_MODULE } from '../modules/nf-core/multiqc/main'
include { PREPARE_MULTIQC_INPUTS } from '../modules/local/prepare_multiqc_inputs'

process GENERATE_SAMPLE_REPORT {
    tag "${json_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/sample_reports", mode: params.publish_mode

    input:
    path(json_file)

    output:
    path("*.qc.html"), emit: reports

    script:
    def sample_id = json_file.baseName.replace('.qc','')
    """
    python3 ${projectDir}/bin/generate_sample_report.py \
      --input ${json_file} \
      --output ${sample_id}.qc.html
    """
}

workflow REPORTING {
    take:
    metadata
    fastq_metrics
    alignment_metrics
    rnaseq_metrics
    expression_metrics
    housekeeping_metrics
    panel_metrics
    fusion_metrics

    main:
    fastq_metric_files = fastq_metrics.collect()
    alignment_metric_files = alignment_metrics.collect()
    rnaseq_metric_files = rnaseq_metrics.collect()
    expression_metric_files = expression_metrics.collect()
    housekeeping_metric_files = housekeeping_metrics.collect()
    panel_metric_files = panel_metrics.collect()
    fusion_metric_files = fusion_metrics.collect()

    CLASSIFY_QC(metadata, fastq_metric_files, alignment_metric_files, rnaseq_metric_files, expression_metric_files, housekeeping_metric_files, panel_metric_files, fusion_metric_files)
    json_files = CLASSIFY_QC.out.jsons.collect()
    BUILD_SUMMARY(json_files)
    GENERATE_SAMPLE_REPORT(CLASSIFY_QC.out.jsons.flatten())

    if( !params.skip_multiqc ) {
        PREPARE_MULTIQC_INPUTS(
            BUILD_SUMMARY.out.overall,
            BUILD_SUMMARY.out.sequencing,
            BUILD_SUMMARY.out.alignment,
            BUILD_SUMMARY.out.rnaseq,
            BUILD_SUMMARY.out.expression,
            BUILD_SUMMARY.out.housekeeping,
            BUILD_SUMMARY.out.panel,
            BUILD_SUMMARY.out.fusion,
            BUILD_SUMMARY.out.failures
        )
        multiqc_inputs = fastq_metrics.mix(alignment_metrics).mix(rnaseq_metrics).mix(expression_metrics).mix(housekeeping_metrics).mix(panel_metrics).mix(fusion_metrics).mix(PREPARE_MULTIQC_INPUTS.out.custom).collect()
        MULTIQC_MODULE(multiqc_inputs)
    }

    emit:
    reports = GENERATE_SAMPLE_REPORT.out.reports
}
