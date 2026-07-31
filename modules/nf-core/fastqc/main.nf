process FASTQC {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/fastqc", mode: params.publish_mode

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*_fastqc.zip"), path("*_fastqc.html")

    script:
    def args = reads instanceof List ? reads.join(' ') : reads
    """
    fastqc ${args}
    """

    stub:
    """
    touch ${meta.id}_fastqc.zip
    printf "<html><body>${meta.id}</body></html>\n" > ${meta.id}_fastqc.html
    """
}
