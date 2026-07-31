process MULTIQC_MODULE {
    tag "multiqc"
    label 'process_low'
    publishDir "${params.outdir}/multiqc", mode: params.publish_mode

    input:
    path(inputs)

    output:
    path("multiqc_report.html")
    path("multiqc_data"), optional: true

    script:
    """
    multiqc . \
      --filename multiqc_report.html \
      --config ${params.multiqc_config}
    """

    stub:
    """
    mkdir -p multiqc_data
    printf "<html><body>MultiQC</body></html>\n" > multiqc_report.html
    """
}
