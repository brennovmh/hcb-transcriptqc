process MOSDEPTH_MODULE {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/panel_qc", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)
    path(targets_bed)

    output:
    tuple val(meta), path(bam), path(bai), path("${meta.id}.regions.bed.gz"), path("${meta.id}.mosdepth.summary.txt"), path("${meta.id}.thresholds.bed.gz")

    script:
    """
    mosdepth \
      --by ${targets_bed} \
      --thresholds 20,50,100,500,1000 \
      ${meta.id} \
      ${bam}
    """

    stub:
    """
printf "chr1\t1\t100\ttarget1\t850\nchr1\t101\t200\ttarget2\t650\n" | gzip -c > ${meta.id}.regions.bed.gz
printf "" | gzip -c > ${meta.id}.thresholds.bed.gz
cat > ${meta.id}.mosdepth.summary.txt <<'EOF'
chrom	length	bases	mean	min	max
chr1	200	200	750	650	850
EOF
    """
}
