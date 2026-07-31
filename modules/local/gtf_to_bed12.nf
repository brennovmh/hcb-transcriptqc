process GTF_TO_BED12 {
    tag "gtf_to_bed12"
    label 'process_low'
    publishDir "${params.outdir}/pipeline_info", mode: params.publish_mode

    input:
    path(gtf_file)

    output:
    path("annotation.bed12"), emit: bed12

    script:
    """
    python3 ${projectDir}/bin/gtf_to_bed12.py \
      --gtf ${gtf_file} \
      --output annotation.bed12
    """
}
