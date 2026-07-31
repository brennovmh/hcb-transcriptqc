process PARSE_PICARD_MARKDUPLICATES {
    tag "${metrics_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    path(metrics_file)

    output:
    path("*.picard_markdup.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_picard_markduplicates.py \
      --input ${metrics_file} \
      --output ${metrics_file.baseName}.picard_markdup.tsv
    """
}
