nextflow.enable.dsl = 2

include { RNA_QC } from './workflows/rna_qc'

workflow {
    RNA_QC()
}
