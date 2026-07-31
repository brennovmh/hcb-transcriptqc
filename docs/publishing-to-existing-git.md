# Publicar em um repositório Git existente

Este projeto contém referências grandes e FASTQs reais. Antes de publicar, confirme que os dados estão autorizados e não envie arquivos brutos, BAMs ou índices pesados ao repositório.

## 1. Conferir o estado local

```bash
cd /home/bioinfo/hcb-rnaseq-qc
git status --short --branch
git remote -v
git branch --show-current
```

Para este projeto, o repositório remoto é:

```text
https://github.com/brennovmh/hcb-transcriptqc.git
```

Como a pasta de trabalho atual contém um diretório `.git` incompleto, não tente reaproveitá-lo. Clone o repositório existente em uma nova pasta:

```bash
cd /home/bioinfo
git clone https://github.com/brennovmh/hcb-transcriptqc.git hcb-transcriptqc-git
rsync -av --exclude='.git' --exclude='work' \
  /home/bioinfo/hcb-rnaseq-qc/ \
  /home/bioinfo/hcb-transcriptqc-git/
cd /home/bioinfo/hcb-transcriptqc-git
git status --short --branch
```

Se preferir SSH, use `git@github.com:brennovmh/hcb-transcriptqc.git` no comando `git clone`.

## 2. Proteger dados grandes ou sensíveis

Revise o `.gitignore` antes do primeiro `git add`. Uma base segura para este projeto é:

```gitignore
real_data/*/*.fastq.gz
real_data/results*/
work/
references/star_*/
*.bam
*.bai
*.cram
```

Mantenha no Git apenas scripts, configurações, documentação, BEDs autorizados e pequenos fixtures de teste.

## 3. Sincronizar sem sobrescrever trabalho remoto

```bash
git fetch origin
git branch -a
git switch -c docs/rna-qc-readme
```

Se a branch principal já tiver trabalho que precisa ser incorporado, faça isso explicitamente:

```bash
git pull --rebase origin main
```

Troque `main` pelo nome real da branch principal. Não use `git push --force` neste fluxo.

## 4. Revisar e testar a mudança

```bash
git diff -- README.md assets/rna-qc-logo.svg docs/publishing-to-existing-git.md
/home/bioinfo/miniconda3/bin/python3 -m pytest -q
git status --short
```

## 5. Criar commit e publicar

```bash
git add README.md assets/ docs/ conf/ bin/ modules/ subworkflows/ main.nf nextflow.config tests/
git commit -m "docs: document RNA-QC workflows"
git push -u origin docs/rna-qc-readme
```

Depois, abra um Pull Request para a branch principal. No PR, informe que os testes passaram e que os FASTQs, resultados e índices foram mantidos fora do commit.

## Se o repositório remoto já tiver arquivos

Não faça `git init` às cegas. Primeiro clone o repositório em outra pasta, copie apenas as alterações desejadas ou configure o remoto no diretório atual e compare o histórico:

```bash
git fetch origin
git log --oneline --decorate -5 origin/main
git diff origin/main...HEAD
```

Se houver conflito de histórico, pare e resolva-o manualmente antes de qualquer push.
