process PARSE_SAMTOOLS_STATS {
    tag "${stats_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    path(stats_file)

    output:
    path("*.samtools_stats_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_samtools_stats.py \
      --input ${stats_file} \
      --output ${stats_file.baseName}.samtools_stats_metrics.tsv
    """
}
