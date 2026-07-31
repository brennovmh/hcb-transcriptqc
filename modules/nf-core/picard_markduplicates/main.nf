process PICARD_MARKDUPLICATES_MODULE {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/picard", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.markdup.metrics.txt")

    script:
    """
    picard MarkDuplicates \
      I=${bam} \
      O=${meta.id}.markdup.bam \
      M=${meta.id}.markdup.metrics.txt \
      VALIDATION_STRINGENCY=SILENT \
      ASSUME_SORT_ORDER=coordinate \
      REMOVE_DUPLICATES=false
    """

    stub:
    """
cat > ${meta.id}.markdup.metrics.txt <<'EOF'
## METRICS CLASS	picard.sam.DuplicationMetrics
LIBRARY	UNPAIRED_READS_EXAMINED	READ_PAIRS_EXAMINED	SECONDARY_OR_SUPPLEMENTARY_RDS	UNMAPPED_READS	UNPAIRED_READ_DUPLICATES	READ_PAIR_DUPLICATES	READ_PAIR_OPTICAL_DUPLICATES	PERCENT_DUPLICATION	ESTIMATED_LIBRARY_SIZE
lib1	0	100	0	0	0	12	0	0.120000	1000
EOF
    """
}
