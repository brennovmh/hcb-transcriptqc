include { TARGET_COVERAGE_QC } from '../modules/local/target_coverage_qc'
include { MOSDEPTH_MODULE } from '../modules/nf-core/mosdepth/main'

workflow PANEL_QC {
    take:
    bams
    metadata
    expression_metrics

    main:
    target_bed = Channel.value(file(params.targets))
    MOSDEPTH_MODULE(bams, target_bed)
    TARGET_COVERAGE_QC(MOSDEPTH_MODULE.out)

    emit:
    panel_metrics = TARGET_COVERAGE_QC.out.metrics
}
