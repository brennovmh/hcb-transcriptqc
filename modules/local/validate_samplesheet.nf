process VALIDATE_SAMPLESHEET {
    tag "samplesheet"
    label 'process_low'
    publishDir "${params.outdir}/pipeline_info", mode: params.publish_mode

    input:
    path(samplesheet)
    val(input_type)
    val(assay)
    val(panel_type)

    output:
    path("validated_samplesheet.csv"), emit: metadata
    path("validated_samples.json"), emit: json

    script:
    """
    python3 ${projectDir}/bin/validate_samplesheet.py \
      --input ${samplesheet} \
      --base-dir ${projectDir} \
      --input-type ${input_type} \
      --assay ${assay} \
      ${panel_type ? "--panel-type ${panel_type}" : ""} \
      --output-csv validated_samplesheet.csv \
      --output-json validated_samples.json
    """
}
