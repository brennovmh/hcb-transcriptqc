process SOFTWARE_VERSIONS {
    tag "software_versions"
    label 'process_low'
    publishDir "${params.outdir}/pipeline_info", mode: params.publish_mode

    output:
    path "software_versions.yml"

    script:
    """
    cat > software_versions.yml <<'EOF'
    pipeline: rna-qc
    nextflow: 26.04.6
    fastqc: 0.12.1
    fastp: 0.24.0
    star: 2.7.11b
    samtools: 1.22.1
    picard: 3.4.0
    subread_featureCounts: 2.1.1
    mosdepth: 0.3.11
    multiqc: 1.30
    rseqc: 5.0.4
    reference_build: GRCh38
    EOF
    """
}
