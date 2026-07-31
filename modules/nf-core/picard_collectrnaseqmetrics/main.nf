process PICARD_COLLECT_RNASEQ_METRICS_MODULE {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/picard", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.rnaseq_metrics.txt")

    script:
    """
    picard CollectRnaSeqMetrics \
      I=${bam} \
      O=${meta.id}.rnaseq_metrics.txt \
      REF_FLAT=${params.ref_flat ?: params.gtf} \
      STRAND=${params.strandness == 'auto' ? 'NONE' : params.strandness.toUpperCase()}
    """

    stub:
    """
cat > ${meta.id}.rnaseq_metrics.txt <<'EOF'
## METRICS CLASS	picard.analysis.directed.RnaSeqMetrics
PF_BASES	PF_ALIGNED_BASES	RIBOSOMAL_BASES	CODING_BASES	UTR_BASES	INTRONIC_BASES	INTERGENIC_BASES	PCT_RIBOSOMAL_BASES	PCT_CODING_BASES	PCT_UTR_BASES	PCT_INTRONIC_BASES	PCT_INTERGENIC_BASES	MEDIAN_3PRIME_BIAS	MEDIAN_5PRIME_BIAS	MEDIAN_5PRIME_TO_3PRIME_BIAS
20000	18000	1000	12000	2000	2500	1500	0.05	0.6667	0.1111	0.1389	0.0833	1.05	0.95	0.90
EOF
    """
}
