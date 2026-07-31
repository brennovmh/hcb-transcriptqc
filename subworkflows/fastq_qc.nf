include { FASTQC as FASTQC_RAW } from '../modules/nf-core/fastqc/main'
include { FASTP } from '../modules/nf-core/fastp/main'
include { FASTQC as FASTQC_TRIMMED } from '../modules/nf-core/fastqc/main'
include { STAR_ALIGN } from '../modules/nf-core/star_align/main'
include { PARSE_FASTP_METRICS } from '../modules/local/parse_fastp_metrics'

workflow FASTQ_QC {
    take:
    samples

    main:
    if( !params.skip_fastqc ) {
        FASTQC_RAW(samples)
    }
    FASTP(samples)
    PARSE_FASTP_METRICS(FASTP.out.reports)
    if( !params.skip_fastqc ) {
        trimmed_for_fastqc = FASTP.out.reads.map { meta, r1, r2 -> tuple(meta, [r1, r2]) }
        FASTQC_TRIMMED(trimmed_for_fastqc)
    }
    STAR_ALIGN(FASTP.out.reads)

    emit:
    bams = STAR_ALIGN.out.bam
    metrics = PARSE_FASTP_METRICS.out.metrics.mix(STAR_ALIGN.out.reports.map { meta, log, sj, chim, counts -> log })
}
