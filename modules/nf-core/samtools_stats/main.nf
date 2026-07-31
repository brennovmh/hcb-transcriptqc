process SAMTOOLS_STATS_MODULE {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/bam_qc", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.samtools.stats.txt")

    script:
    """
    samtools stats ${bam} > ${meta.id}.samtools.stats.txt
    """

    stub:
    """
cat > ${meta.id}.samtools.stats.txt <<'EOF'
SN	raw total sequences:	200
SN	average length:	101
SN	insert size average:	250
SN	insert size standard deviation:	20
EOF
    """
}
