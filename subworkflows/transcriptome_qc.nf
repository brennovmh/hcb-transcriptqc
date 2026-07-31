include { PICARD_COLLECT_RNASEQ_METRICS_MODULE } from '../modules/nf-core/picard_collectrnaseqmetrics/main'
include { PARSE_PICARD_RNASEQ_METRICS } from '../modules/local/parse_picard_rnaseq_metrics'
include { PARSE_RSEQC_METRICS } from '../modules/local/parse_rseqc_metrics'
include { GTF_TO_BED12 } from '../modules/local/gtf_to_bed12'

process RSEQC_TRANSCRIPTOME {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/rseqc", mode: params.publish_mode

    input:
    tuple val(meta), path(bam), path(bai)
    path(bed12)

    output:
    path("${meta.id}.rseqc.summary.tsv"), emit: metrics
    path("${meta.id}.geneBodyCoverage.txt"), emit: plots

    when:
    !params.skip_rseqc

    script:
    """
    infer_experiment.py -i ${bam} -r ${bed12} > ${meta.id}.infer_experiment.txt
    read_distribution.py -i ${bam} -r ${bed12} > ${meta.id}.read_distribution.txt
    junction_annotation.py -i ${bam} -r ${bed12} -o ${meta.id}.junction_annotation
    junction_saturation.py -i ${bam} -r ${bed12} -o ${meta.id}.junction_saturation
    read_duplication.py -i ${bam} -o ${meta.id}.read_duplication
    tin.py -i ${bam} -r ${bed12} > ${meta.id}.tin.txt
    geneBody_coverage.py -i ${bam} -r ${bed12} -o ${meta.id}.geneBodyCoverage
    python3 ${projectDir}/bin/summarize_rseqc.py \
      --sample ${meta.id} \
      --infer ${meta.id}.infer_experiment.txt \
      --distribution ${meta.id}.read_distribution.txt \
      --junction-annotation ${meta.id}.junction_annotation.junction.xls \
      --junction-saturation ${meta.id}.junction_saturation.r \
      --duplication ${meta.id}.read_duplication.pos.DupRate.xls \
      --tin ${meta.id}.tin.txt \
      --output ${meta.id}.rseqc.summary.tsv
    cp ${meta.id}.geneBodyCoverage.geneBodyCoverage.txt ${meta.id}.geneBodyCoverage.txt
    """

    stub:
    """
    python3 ${projectDir}/bin/run_rseqc_stub.py \
      --sample ${meta.id} \
      --output ${meta.id}.rseqc.summary.tsv \
      --plot ${meta.id}.geneBodyCoverage.txt
    """
}

workflow TRANSCRIPTOME_QC {
    take:
    bams
    metadata
    expression_metrics

    main:
    GTF_TO_BED12(file(params.gtf))
    PICARD_COLLECT_RNASEQ_METRICS_MODULE(bams)
    PARSE_PICARD_RNASEQ_METRICS(PICARD_COLLECT_RNASEQ_METRICS_MODULE.out)
    if( !params.skip_rseqc ) {
        RSEQC_TRANSCRIPTOME(bams, GTF_TO_BED12.out.bed12)
        PARSE_RSEQC_METRICS(RSEQC_TRANSCRIPTOME.out.metrics)
    }

    emit:
    rnaseq_metrics = params.skip_rseqc ? PARSE_PICARD_RNASEQ_METRICS.out.metrics : PARSE_PICARD_RNASEQ_METRICS.out.metrics.mix(PARSE_RSEQC_METRICS.out.metrics)
}
