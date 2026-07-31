process FUSION_READINESS {
    tag "${meta.id}"
    label 'process_low'
    publishDir "${params.outdir}/fusion_readiness", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)

    output:
    path("${meta.id}.fusion_readiness.tsv"), emit: metrics

    script:
    """
    python3 ${projectDir}/bin/calculate_fusion_readiness.py \
      --sample ${meta.id} \
      --bam ${bam} \
      ${params.fusion_genes ? "--fusion-genes ${params.fusion_genes}" : ""} \
      --output ${meta.id}.fusion_readiness.tsv
    """

    stub:
    """
    printf "sample\tpaired_end\tread_length\tinsert_size_mean\tchimeric_reads\tchimeric_reads_percent\tjunction_saturation\tfusion_readiness_status\n${meta.id}\tYES\t101\t250\t10\t0.01\t0.8\tPASS\n" > ${meta.id}.fusion_readiness.tsv
    """
}
