process STAR_ALIGN {
    tag "${meta.id}"
    label 'process_high'
    publishDir "${params.outdir}/alignment", mode: params.publish_mode

    input:
    tuple val(meta), path(r1), path(r2)

    output:
    tuple val(meta), path("${meta.id}.sorted.bam"), path("${meta.id}.sorted.bam.bai"), emit: bam
    tuple val(meta), path("${meta.id}.Log.final.out"), path("${meta.id}.SJ.out.tab"), path("${meta.id}.Chimeric.out.junction"), path("${meta.id}.ReadsPerGene.out.tab"), emit: reports

    script:
    """
    STAR \
      --runThreadN ${task.cpus} \
      --genomeDir ${params.star_index} \
      --readFilesIn ${r1} ${r2} \
      --readFilesCommand zcat \
      --outFileNamePrefix ${meta.id}. \
      --outSAMtype BAM SortedByCoordinate \
      --outSAMattributes NH HI AS nM NM MD ch \
      --outSAMstrandField intronMotif \
      --quantMode GeneCounts \
      --chimOutType Junctions SeparateSAMold \
      --chimSegmentMin ${params.star_chimSegmentMin} \
      --chimJunctionOverhangMin ${params.star_chimJunctionOverhangMin} \
      --chimScoreMin ${params.star_chimScoreMin} \
      --chimScoreDropMax ${params.star_chimScoreDropMax} \
      --chimScoreSeparation ${params.star_chimScoreSeparation} \
      --chimSegmentReadGapMax ${params.star_chimSegmentReadGapMax} \
      --alignSJDBoverhangMin ${params.star_alignSJDBoverhangMin} \
      --alignMatesGapMax ${params.star_alignMatesGapMax} \
      --alignIntronMax ${params.star_alignIntronMax} \
      --alignSJstitchMismatchNmax ${params.star_alignSJstitchMismatchNmax}
    mv ${meta.id}.Aligned.sortedByCoord.out.bam ${meta.id}.sorted.bam
    samtools index ${meta.id}.sorted.bam
    """

    stub:
    """
touch ${meta.id}.sorted.bam ${meta.id}.sorted.bam.bai
cat > ${meta.id}.Log.final.out <<'EOF'
                            Number of input reads | 200
                    Uniquely mapped reads number | 160
                         Uniquely mapped reads % | 80.00%
           Number of reads mapped to multiple loci | 20
                % of reads mapped to multiple loci | 10.00%
     % of reads unmapped: too many mismatches | 1.00%
               % of reads unmapped: too short | 5.00%
                   % of reads unmapped: other | 4.00%
                  Mismatch rate per base, % | 0.30%
                     Deletion rate per base | 0.01%
                    Insertion rate per base | 0.01%
                       Number of splices: Total | 100
            Number of splices: Annotated (sjdb) | 80
EOF
printf "chr1\t1\t2\n" > ${meta.id}.SJ.out.tab
printf "chr1\t10\tchr2\t20\n" > ${meta.id}.Chimeric.out.junction
printf "N_unmapped\t0\n" > ${meta.id}.ReadsPerGene.out.tab
    """
}
