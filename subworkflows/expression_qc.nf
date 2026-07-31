include { HOUSEKEEPING_QC } from '../modules/local/housekeeping_qc'
include { EXPRESSION_SUMMARY } from '../modules/local/expression_summary'
include { FEATURECOUNTS_MODULE } from '../modules/nf-core/featurecounts/main'

workflow EXPRESSION_QC {
    take:
    bams
    metadata

    main:
    FEATURECOUNTS_MODULE(bams)
    count_inputs = FEATURECOUNTS_MODULE.out.counts.mix(FEATURECOUNTS_MODULE.out.summary).collect()
    EXPRESSION_SUMMARY(count_inputs, metadata)
    HOUSEKEEPING_QC(EXPRESSION_SUMMARY.out.matrix, metadata)

    emit:
    expression_metrics = EXPRESSION_SUMMARY.out.metrics
    housekeeping_metrics = HOUSEKEEPING_QC.out.metrics
}
