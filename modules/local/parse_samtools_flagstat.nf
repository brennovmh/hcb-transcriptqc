process PARSE_SAMTOOLS_FLAGSTAT {
    tag "${flagstat_file.baseName}"
    label 'process_low'
    publishDir "${params.outdir}/tables", mode: params.publish_mode

    input:
    path(flagstat_file)

    output:
    path("*.flagstat_metrics.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/parse_samtools_flagstat.py \
      --input ${flagstat_file} \
      --output ${flagstat_file.baseName}.flagstat_metrics.tsv
    """
}
