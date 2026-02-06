# lab-small-files-problem — Início rápido

## 1. Instalar

```bash
pip install -r requirements.txt
```

## 2. Gerar dados (arquivos JSON ~30kb)

```bash
python generate-sample-data.py
```

Cria arquivos em `files/device/` e `files/subscription/`.

## 3. Rodar o lab

```bash
python small-files-problem.py
```

Saída: informações da máquina, configuração Spark e estatísticas (registros, partições, tempo).

---

## Escolher quantos arquivos carregar

Edite `small-files-problem.py` e deixe **só uma** destas regras ativa:

- **Regra 1** – 1 arquivo (padrão).
- **Regra 2** – X arquivos: descomente o bloco da Regra 2 e defina `_x = 7` (ou outro número).
- **Regra 3** – Todos os `.json`: descomente o bloco da Regra 3.

---

## Requisitos

- Python 3.10+
- Java 17
- Spark 4.1.1 (caminho em `SPARK_HOME` no script, ex.: `C:\spark-4.1.1-bin-hadoop3`)

---

## Se der erro

- **PySpark / Spark:** instale `pyspark==4.1.1` e confira se a versão do Spark é 4.1.1.
- **Arquivos não encontrados:** rode antes `python generate-sample-data.py`.
- **Java:** verifique com `java -version` (recomendado Java 17).

Documentação completa: `readme.md`.
