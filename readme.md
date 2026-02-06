# lab-small-files-problem

Laboratório PySpark para demonstrar o **problema de small files** (arquivos pequenos) e o impacto em performance.

---

## O que é este lab

- Arquivos de ~30KB (small files) são lidos com Spark.
- Você observa: partições, tempo, registros.
- Objetivo: ver como quantidade de arquivos e `maxPartitionBytes` afetam a execução.

---

## Pré-requisitos

- **Python** 3.10+
- **Java** 17 (recomendado)
- **Spark** 4.1.1 em `C:\spark-4.1.1-bin-hadoop3` (ou ajuste `SPARK_HOME` no script)
- **PySpark** 4.1.1

---

## Estrutura do projeto

```
lab-small-files-problem/
├── files/
│   ├── device/        # JSON de dispositivos (~30kb cada)
│   └── subscription/  # JSON de assinaturas (~30kb cada)
├── small-files-problem.py   # Script principal
├── generate-sample-data.py  # Gera dados de exemplo
├── requirements.txt
├── readme.md
└── QUICKSTART.md
```

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Como rodar

### 1. Gerar dados (se ainda não tiver JSON nas pastas)

```bash
python generate-sample-data.py
```

### 2. Executar o lab

```bash
python small-files-problem.py
```

A saída mostra: **máquina** (CPU, memória), **configuração Spark** e **estatísticas** (device, subscription, tempo total).

---

## Regras de carregamento (no script)

No `small-files-problem.py` há **3 regras**; deixe ativa só uma por vez:

| Regra | O que faz |
|-------|-----------|
| **1** | 1 arquivo (ex.: `device_2022_apr_01.json`) |
| **2** | X arquivos (defina `_x = 7` ou outro valor) |
| **3** | Todos os `.json` da pasta |

Comente/descomente os blocos no código para alternar entre elas.

---

## Configuração Spark no script

- **SPARK_HOME:** definido no início do script (ex.: `C:\spark-4.1.1-bin-hadoop3`).
- **maxPartitionBytes:** ex.: `10kb` (altere no `.config(...)` para testar 128mb, 1gb, etc.).

---

## O problema de small files (resumo)

- **Spark/HDFS** costumam trabalhar com blocos de ~128MB.
- Muitos arquivos pequenos (~30KB) geram muitas partições e tarefas → overhead e lentidão.
- Ajustar `spark.sql.files.maxPartitionBytes` e consolidar arquivos (ex.: Parquet) ajuda.

---

## Referências

- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)
- [Spark SQL Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

---

**lab-small-files-problem** — uso educacional.
