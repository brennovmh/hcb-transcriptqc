process TARGET_COVERAGE_QC {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/panel_qc", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai), path(regions_bed_gz), path(summary_txt), path(thresholds_bed_gz)

    output:
    path("${meta.id}.panel_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/calculate_target_coverage.py \
      --sample ${meta.id} \
      --regions ${regions_bed_gz} \
      --bam ${bam} \
      --targets ${params.targets} \
      --panel-type ${params.panel_type} \
      --output ${meta.id}.panel_metrics.tsv
    """

    stub:
    """
    printf "sample\tpanel_type\ton_target_percent\tmedian_target_depth\tmean_target_depth\ttargets_covered_20x_percent\ttargets_covered_50x_percent\ttargets_covered_100x_percent\ttargets_covered_500x_percent\ttargets_covered_1000x_percent\ttargets_without_coverage\n${meta.id}\t${params.panel_type}\t90\t800\t850\t100\t100\t95\t80\t70\t0\n" > ${meta.id}.panel_metrics.tsv
    """
}
