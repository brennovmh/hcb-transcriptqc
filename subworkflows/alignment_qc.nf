include { PARSE_STAR_LOG } from '../modules/local/parse_star_log'
include { SAMTOOLS_FLAGSTAT_MODULE } from '../modules/nf-core/samtools_flagstat/main'
include { SAMTOOLS_STATS_MODULE } from '../modules/nf-core/samtools_stats/main'
include { PICARD_MARKDUPLICATES_MODULE } from '../modules/nf-core/picard_markduplicates/main'
include { PARSE_PICARD_MARKDUPLICATES } from '../modules/local/parse_picard_markduplicates'
include { PARSE_SAMTOOLS_FLAGSTAT } from '../modules/local/parse_samtools_flagstat'
include { PARSE_SAMTOOLS_STATS } from '../modules/local/parse_samtools_stats'

workflow ALIGNMENT_QC {
    take:
    bams

    main:
    // STAR writes Log.final.out alongside the published BAM. Resolve it
    // from the configured output directory rather than the transient BAM
    // symlink directory, which may not contain the report file.
    star_logs = bams.map { meta, bam, bai ->
        tuple(meta, file("${params.outdir}/alignment/${meta.id}.Log.final.out"))
    }.filter { meta, log -> log.exists() }

    PARSE_STAR_LOG(star_logs)
    SAMTOOLS_FLAGSTAT_MODULE(bams)
    SAMTOOLS_STATS_MODULE(bams)
    PICARD_MARKDUPLICATES_MODULE(bams)
    PARSE_SAMTOOLS_FLAGSTAT(SAMTOOLS_FLAGSTAT_MODULE.out)
    PARSE_SAMTOOLS_STATS(SAMTOOLS_STATS_MODULE.out)
    PARSE_PICARD_MARKDUPLICATES(PICARD_MARKDUPLICATES_MODULE.out)

    emit:
    bams = bams
    alignment_metrics = PARSE_STAR_LOG.out.metrics.mix(PARSE_SAMTOOLS_FLAGSTAT.out.metrics).mix(PARSE_SAMTOOLS_STATS.out.metrics).mix(PARSE_PICARD_MARKDUPLICATES.out.metrics)
}
