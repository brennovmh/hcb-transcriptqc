process PARSE_STAR_LOG {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    tuple val(meta), path(log_file)

    output:
    path("${meta.id}.star_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_star_log.py \
      --input ${log_file} \
      --sample ${meta.id} \
      --output ${meta.id}.star_metrics.tsv
    """
}
