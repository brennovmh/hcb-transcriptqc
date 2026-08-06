process SAMTOOLS_INDEX_MODULE {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/alignment", mode: params.publish_mode

    input:
    tuple val(meta), path(bam)

    output:
    tuple val(meta), path(bam), path("${meta.id}.sorted.bam.bai"), emit: indexed_bam

    script:
    """
    samtools index ${bam}
    """

    stub:
    """
    touch ${bam}.bai
    """
}
