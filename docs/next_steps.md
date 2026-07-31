# Próximas Etapas

## 1. Validação funcional com dados reais

- Executar o pipeline com um conjunto pequeno e válido de FASTQ paired-end em `-profile docker`.
- Executar o pipeline com um conjunto pequeno e válido de BAM em `-profile docker`.
- Validar os dois caminhos de ensaio:
  - `transcriptome`
  - `panel`
- Confirmar que os outputs obrigatórios são gerados em `results/`.
- Verificar se os nomes e formatos reais dos arquivos produzidos por `STAR`, `Picard`, `RSeQC`, `mosdepth` e `MultiQC` estão alinhados com os parsers atuais.

## 2. Endurecimento do módulo RSeQC

- Validar em execução real os comandos:
  - `infer_experiment.py`
  - `read_distribution.py`
  - `geneBody_coverage.py`
  - `junction_annotation.py`
  - `junction_saturation.py`
  - `read_duplication.py`
  - `tin.py`
- Ajustar o script [summarize_rseqc.py](/home/bioinfo/hcb-rnaseq-qc/bin/summarize_rseqc.py:1) para os formatos exatos produzidos pelas versões reais dos containers.
- Adicionar coleta de métricas adicionais quando disponíveis:
  - `inner_distance`
  - viés 5'
  - viés 3'
  - razão 5'/3'
  - saturação de junctions mais robusta

## 3. Endurecimento dos parsers de alignment

- Expandir o parser de `STAR Log.final.out` para incluir:
  - `uniquely mapped reads number`
  - `properly paired` quando inferível
  - mismatch/deletion/insertion com tipagem consistente
- Adicionar parser explícito para:
  - `SJ.out.tab`
  - `Chimeric.out.junction`
- Melhorar a consolidação de `samtools flagstat` e `samtools stats`.

## 4. Cobertura e métricas de painel

- Validar `mosdepth` com BED real e builds compatíveis.
- Adicionar:
  - `on-target percent`
  - cobertura por alvo
  - genes totalmente/parcialmente/não cobertos
  - contagem de alvos abaixo do mínimo
  - percentuais em `>=20x`, `>=50x`, `>=100x`, `>=500x`, `>=1000x`
- Implementar interpretação diferenciada para:
  - `panel_hybrid_capture`
  - `panel_amplicon`

## 5. Fusion readiness

- Parsear de forma mais completa:
  - `Chimeric.out.junction`
  - métricas de suplementares
  - comprimento de leitura
  - insert size
- Adicionar suporte a genes de fusão com cobertura e expressão por gene.
- Implementar leitura opcional de controles positivos.
- Melhorar a justificativa final de `fusion_readiness_status`.

## 6. Reporting e MultiQC

- Validar o carregamento dos arquivos `*_mqc.tsv` no `MultiQC` real.
- Refinar [assets/multiqc_config.yaml](/home/bioinfo/hcb-rnaseq-qc/assets/multiqc_config.yaml:1) e [assets/multiqc_custom_content.yaml](/home/bioinfo/hcb-rnaseq-qc/assets/multiqc_custom_content.yaml:1).
- Garantir seções para:
  - resumo geral
  - classificação por amostra
  - expressão
  - housekeeping
  - cobertura de painel
  - fusion readiness
- Melhorar o HTML por amostra com tabelas e gráficos adicionais.

## 7. Classificação e thresholds

- Revisar [conf/thresholds.yaml](/home/bioinfo/hcb-rnaseq-qc/conf/thresholds.yaml:1) com dados internos reais.
- Adicionar suporte mais rico para:
  - `range`
  - `informational`
  - métricas ausentes por contexto
- Diferenciar melhor métricas:
  - críticas
  - complementares
  - não aplicáveis

## 8. Testes

- [x] Adicionar testes unitários para:
  - `parse_fastp_json.py`
  - `parse_picard_markduplicates.py`
  - `parse_picard_rnaseq_metrics.py`
  - `summarize_rseqc.py`
  - `calculate_target_coverage.py`
- Adicionar testes de integração com dados mínimos reais.
- [x] Criar um teste stub de `panel` no profile de teste.
- Rodar um teste real com `-profile test,docker` quando os dados válidos estiverem disponíveis.

## 9. Troca progressiva para módulos nf-core oficiais

- Instalar os módulos oficiais com `nf-core modules install` em ambiente que tenha o CLI disponível.
- Comparar interfaces e outputs com os wrappers atuais em `modules/nf-core/`.
- Substituir gradualmente os wrappers locais pelos módulos oficiais quando a interface estiver estável.

## 10. Preparação para produção

- Adicionar captura explícita de versões das ferramentas.
- Gerar `software_versions.yml` de forma padronizada.
- Revisar labels de recursos (`process_low`, `process_medium`, `process_high`, `process_high_memory`).
- Refinar mensagens de erro para referências inválidas, GTF incompatível e BAM corrompido.
- Preparar CI para:
  - `pytest`
  - `nextflow -stub-run`
  - teste rápido com containers
