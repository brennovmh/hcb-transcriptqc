process PARSE_FASTP_METRICS {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    tuple val(meta), path(json_file), path(html_file)

    output:
    path("${meta.id}.fastp_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_fastp_json.py \
      --input ${json_file} \
      --sample ${meta.id} \
      --output ${meta.id}.fastp_metrics.tsv
    """
}
