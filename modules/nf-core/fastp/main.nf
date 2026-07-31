process FASTP {
    tag "${meta.id}"
    label 'process_medium'
    publishDir "${params.outdir}/fastp", mode: params.publish_mode

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("${meta.id}.R1.trimmed.fastq.gz"), path("${meta.id}.R2.trimmed.fastq.gz"), emit: reads
    tuple val(meta), path("${meta.id}.fastp.json"), path("${meta.id}.fastp.html"), emit: reports

    script:
    def disable = params.trim_reads ? '' : '--disable_adapter_trimming --disable_quality_filtering --disable_length_filtering'
    """
    fastp \
      --in1 ${reads[0]} \
      --in2 ${reads[1]} \
      --out1 ${meta.id}.R1.trimmed.fastq.gz \
      --out2 ${meta.id}.R2.trimmed.fastq.gz \
      --json ${meta.id}.fastp.json \
      --html ${meta.id}.fastp.html \
      --thread ${task.cpus} \
      ${disable}
    """

    stub:
    """
touch ${meta.id}.R1.trimmed.fastq.gz ${meta.id}.R2.trimmed.fastq.gz
cat > ${meta.id}.fastp.json <<'EOF'
{
  "summary": {
    "before_filtering": {
      "total_reads": 200,
      "total_bases": 20200,
      "q20_rate": 0.95,
      "q30_rate": 0.9,
      "gc_content": 0.48,
      "read1_mean_length": 101,
      "read2_mean_length": 101
    },
    "after_filtering": {
      "total_reads": 180,
      "total_bases": 18180,
      "q20_rate": 0.97,
      "q30_rate": 0.92,
      "gc_content": 0.48,
      "read1_mean_length": 101,
      "read2_mean_length": 101
    }
  },
  "filtering_result": {
    "passed_filter_reads": 180,
    "low_quality_reads": 10,
    "too_many_N_reads": 5,
    "too_short_reads": 5
  },
  "duplication": {
    "rate": 0.12
  },
  "adapter_cutting": {
    "adapter_trimmed_reads": 12
  }
}
EOF
printf "<html><body>fastp</body></html>\n" > ${meta.id}.fastp.html
    """
}
