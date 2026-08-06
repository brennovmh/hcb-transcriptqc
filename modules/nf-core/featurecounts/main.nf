process FEATURECOUNTS_MODULE {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/expression", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.featurecounts.txt"), emit: counts
    path("${meta.id}.featurecounts.txt.summary"), emit: summary

    script:
    """
    featureCounts \
      -T ${task.cpus} \
      -p \
      -a ${params.gtf} \
      -o ${meta.id}.featurecounts.txt \
      ${bam}
    """

    stub:
    """
    printf "Geneid\tChr\tStart\tEnd\tStrand\tLength\t${meta.id}\nACTB\tchr1\t1\t10\t+\t10\t100\nGAPDH\tchr1\t11\t20\t+\t10\t80\nHPRT1\tchr1\t21\t30\t+\t10\t50\n" > ${meta.id}.featurecounts.txt
    printf "Status\t${meta.id}\nAssigned\t230\nUnassigned_NoFeatures\t10\nUnassigned_Ambiguity\t5\n" > ${meta.id}.featurecounts.txt.summary
    """
}
