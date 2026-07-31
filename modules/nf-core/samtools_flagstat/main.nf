process SAMTOOLS_FLAGSTAT_MODULE {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/bam_qc", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.flagstat.txt")

    script:
    """
    samtools flagstat ${bam} > ${meta.id}.flagstat.txt
    """

    stub:
    """
cat > ${meta.id}.flagstat.txt <<'EOF'
200 + 0 in total (QC-passed reads + QC-failed reads)
10 + 0 secondary
5 + 0 supplementary
170 + 0 properly paired (85.00% : N/A)
EOF
    """
}
