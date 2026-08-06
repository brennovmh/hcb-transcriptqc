include { VALIDATE_SAMPLESHEET } from '../modules/local/validate_samplesheet'
include { FASTQ_QC } from '../subworkflows/fastq_qc'
include { ALIGNMENT_QC } from '../subworkflows/alignment_qc'
include { TRANSCRIPTOME_QC } from '../subworkflows/transcriptome_qc'
include { PANEL_QC } from '../subworkflows/panel_qc'
include { EXPRESSION_QC } from '../subworkflows/expression_qc'
include { FUSION_READINESS_QC } from '../subworkflows/fusion_readiness_qc'
include { REPORTING } from '../subworkflows/reporting'
include { SOFTWARE_VERSIONS } from '../modules/local/software_versions'

workflow RNA_QC {
    main:
    if( !params.input ) error "Missing required parameter: --input"
    if( !params.input_type ) error "Missing required parameter: --input_type"
    if( !params.assay ) error "Missing required parameter: --assay"
    if( !['fastq','bam'].contains(params.input_type) ) error "--input_type must be 'fastq' or 'bam'"
    if( !['transcriptome','panel'].contains(params.assay) ) error "--assay must be 'transcriptome' or 'panel'"
    if( params.input_type == 'fastq' && !params.star_index ) error "--star_index is required for FASTQ input"
    if( !params.fasta ) error "Missing required parameter: --fasta"
    if( !params.gtf ) error "Missing required parameter: --gtf"
    if( params.assay == 'panel' && !params.targets ) error "--targets is required for panel assays"
    if( params.assay == 'panel' && !['hybrid_capture','amplicon'].contains(params.panel_type) ) {
        error "--panel_type must be 'hybrid_capture' or 'amplicon' for panel assays"
    }

    validated = VALIDATE_SAMPLESHEET(
        file(params.input),
        params.input_type,
        params.assay,
        params.panel_type ?: ''
    )

    metadata = validated.metadata
    samples = metadata.splitCsv(header: true).map { row ->
        def meta = [id: row.sample, sample: row.sample, group: row.group ?: '', batch: row.batch ?: '', assay: row.assay]
        if( params.input_type == 'fastq' ) {
            tuple(meta, [file(row.fastq_1), file(row.fastq_2)])
        } else {
            def bam = file(row.bam)
            def bai = file(row.bam + '.bai')
            tuple(meta, bam, bai)
        }
    }

    fastq_outputs = params.input_type == 'fastq' ? FASTQ_QC(samples) : null
    bam_inputs = params.input_type == 'fastq' ? fastq_outputs.bams : samples

    alignment_outputs = ALIGNMENT_QC(bam_inputs)
    expression_outputs = EXPRESSION_QC(alignment_outputs.bams, metadata)
    transcriptome_outputs = params.assay == 'transcriptome' ? TRANSCRIPTOME_QC(alignment_outputs.bams, metadata, expression_outputs.expression_metrics) : null
    panel_outputs = params.assay == 'panel' ? PANEL_QC(alignment_outputs.bams, metadata, expression_outputs.expression_metrics) : null
    fusion_outputs = FUSION_READINESS_QC(alignment_outputs.bams, metadata, expression_outputs.expression_metrics)

    REPORTING(
        metadata,
        fastq_outputs?.metrics ?: Channel.of(file("${projectDir}/assets/NO_FASTQ")),
        alignment_outputs.alignment_metrics,
        transcriptome_outputs?.rnaseq_metrics ?: Channel.of(file("${projectDir}/assets/NO_RNASEQ")),
        expression_outputs.expression_metrics,
        expression_outputs.housekeeping_metrics,
        panel_outputs?.panel_metrics ?: Channel.of(file("${projectDir}/assets/NO_PANEL")),
        fusion_outputs.fusion_metrics
    )
    SOFTWARE_VERSIONS()
}
