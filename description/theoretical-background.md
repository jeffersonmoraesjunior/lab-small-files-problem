# Fundamentação Teórica — lab-small-files-problem

Base teórica para o laboratório **lab-small-files-problem**: o que são small files, por que são um problema e como o Spark lida com eles.

---

## O que são Small Files?

**Small files** são arquivos bem menores que o tamanho de bloco típico do armazenamento ou do Spark.

| Sistema / contexto      | Tamanho de referência |
|-------------------------|------------------------|
| HDFS                    | 128 MB                 |
| S3, GCS, Blob           | 64–128 MB (recomendado)|
| Spark (maxPartitionBytes) | 128 MB (padrão)     |
| **Este lab**            | ~30 KB por arquivo     |

Classificação prática:
- Pequeno: &lt; 10 MB  
- Médio: 10–100 MB  
- Grande: 100 MB–1 GB  

No lab, trabalhamos com arquivos pequenos (~30 KB) para simular o problema.

---

## Por que Small Files são um Problema?

### 1. Overhead de metadados

- **HDFS:** o NameNode guarda metadados de cada arquivo em memória (~150 bytes por arquivo). Muitos arquivos = muito uso de memória e listagens mais lentas.
- **Cloud (S3, GCS, Blob):** listar ou acessar muitos arquivos vira muitas requisições HTTP, mais latência e custo.

### 2. Uma task por arquivo

No Spark, ao ler arquivos:

- Cada arquivo (ou conjunto de arquivos que caiba em uma partição) vira **pelo menos uma task**.
- Cada task tem custo fixo: inicialização, serialização, comunicação com o driver (ordem de dezenas a centenas de ms).

Exemplo:
- 1000 arquivos de 30 KB → 1000 tasks → a maior parte do tempo pode ser overhead, não processamento útil.
- 1 arquivo de 128 MB → 1 task → tempo gasto de forma mais eficiente.

### 3. Subutilização de recursos

- Cluster com poucos “slots” (ex.: 20) e muitas tasks (ex.: 1000) → várias “ondas” de execução e muito tempo de agendamento.
- Executor com vários GB de memória processando um arquivo de 30 KB → memória quase toda ociosa.

### 4. I/O ineficiente

- Muitos arquivos = muitas aberturas/fechamentos e acessos “pulando” no disco.
- Poucos arquivos grandes = leitura mais sequencial e melhor uso de cache.

---

## Impacto em números (exemplo)

- **Cenário:** 10.000 arquivos de ~30 KB (total ~300 MB), cluster com 10 slots.
- **Sem otimização:** 10.000 tasks, ~100 ms de overhead por task → ~1000 s só de overhead.
- **Com consolidação:** 3 arquivos de ~128 MB → 3 tasks → overhead de centenas de ms.
- Resultado típico: **redução de tempo na ordem de dezenas a centenas de vezes** quando se evita o efeito de small files.

No lab você observa isso variando: 1 arquivo, X arquivos e “todos” os arquivos, e vendo partições e tempo na saída do script.

---

## Configurações do Spark relevantes no lab

### spark.sql.files.maxPartitionBytes

- **O que faz:** tamanho máximo de dados que uma partição pode ter ao ler arquivos. O Spark tende a agrupar vários arquivos pequenos em uma partição até esse limite.
- **No script:** você pode testar valores como `10kb`, `128mb`, `1gb` no `.config("spark.sql.files.maxPartitionBytes", "10kb")`.
- **Efeito:** valor maior → menos partições e menos tasks ao ler muitos small files; valor menor → mais partições.

### spark.sql.files.openCostInBytes

- Custo “virtual” de abrir um arquivo (padrão 4 MB). Usado pelo Spark para decidir como agrupar arquivos. Aumentar esse valor tende a favorecer mais agrupamento.

### spark.default.parallelism

- Número padrão de partições em operações como shuffle. No lab em `local[1]` o paralelismo padrão é 1.

---

## Estratégias de solução (resumo)

1. **Consolidação**
   - `coalesce(N)` ou `repartition(N)` ao escrever, para gerar menos arquivos maiores.
   - Pipeline: raw (muitos small files) → leitura + coalesce/repartition → escrita em menos arquivos (ex.: Parquet).

2. **Formatos otimizados**
   - **Parquet / ORC:** compressão, leitura colunar e menos arquivos maiores.
   - No lab os dados são JSON; em produção costuma-se consolidar em Parquet/ORC.

3. **Particionamento**
   - `write.partitionBy("coluna")` para organizar por data, categoria etc., mantendo partições com tamanho razoável (ex.: 64–128 MB).

4. **Compactação periódica**
   - Job que lê muitos small files, reparticiona e grava em menos arquivos (e em formato colunar, se possível).

---

## Métricas que o lab mostra

O script **small-files-problem.py** já exibe métricas alinhadas à teoria:

- **Registros** lidos (device e subscription).
- **Partições** criadas (refletem maxPartitionBytes e quantidade de arquivos).
- **Tempo** por leitura e tempo total.

Interpretação rápida:
- Mais arquivos (Regra 2 ou 3) com mesmo `maxPartitionBytes` → tendência a mais partições e mais tempo.
- Aumentar `maxPartitionBytes` (ex.: 10kb → 128mb ou 1gb) → tendência a menos partições e, em muitos casos, menor tempo ao ler muitos small files.

---

## Boas práticas em uma frase

- **Tamanho alvo:** arquivos entre 64 MB e 128 MB (ou conforme padrão do seu storage).
- **Formato:** preferir Parquet/ORC para dados analíticos.
- **Particionar** por colunas usadas em filtros (ex.: data).
- **Monitorar** quantidade e tamanho de arquivos para evitar acúmulo de small files.

---

## Referências

- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)
- [Spark SQL Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
- [Parquet](https://parquet.apache.org/docs/)
- Documentação do lab: `readme.md`, `QUICKSTART.md`.

---

Este documento é a base teórica do **lab-small-files-problem**. Use-o para interpretar os resultados dos experimentos (1 arquivo, X arquivos, todos) e o efeito de `maxPartitionBytes`.
