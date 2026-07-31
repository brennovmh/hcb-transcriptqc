include { FUSION_READINESS } from '../modules/local/fusion_readiness'

workflow FUSION_READINESS_QC {
    take:
    bams
    metadata
    expression_metrics

    main:
    FUSION_READINESS(bams)

    emit:
    fusion_metrics = FUSION_READINESS.out.metrics
}
