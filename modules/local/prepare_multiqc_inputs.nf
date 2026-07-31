process PREPARE_MULTIQC_INPUTS {
    tag "prepare_multiqc"
    label 'process_low'
    publishDir "${params.outdir}/multiqc", mode: params.publish_mode

    input:
    path(overall_qc)
    path(sequencing_metrics)
    path(alignment_metrics)
    path(rnaseq_metrics)
    path(expression_metrics)
    path(housekeeping_metrics)
    path(panel_metrics)
    path(fusion_metrics)
    path(qc_failures)

    output:
    path("*_mqc.tsv"), emit: custom

    script:
    """
    python3 ${projectDir}/bin/generate_multiqc_custom_inputs.py \
      --overall ${overall_qc} \
      --sequencing ${sequencing_metrics} \
      --alignment ${alignment_metrics} \
      --rnaseq ${rnaseq_metrics} \
      --expression ${expression_metrics} \
      --housekeeping ${housekeeping_metrics} \
      --panel ${panel_metrics} \
      --fusion ${fusion_metrics} \
      --failures ${qc_failures}
    """
}
