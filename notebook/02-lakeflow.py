# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC
# MAGIC ## Databricks FE-BAR 
# MAGIC
# MAGIC * **Date**:  October, 28 2026
# MAGIC
# MAGIC * **Company** :  EUROFARMA
# MAGIC * **Sector**  :  Pharmaceutical Industry
# MAGIC * **Author**  :  Luis Assunção (Solution Architect Databricks)
# MAGIC * **Use Case**:  Optimization of distribution logistics for generic medicines

# COMMAND ----------

# MAGIC %md
# MAGIC # 02 - Lakeflow Spark Declarative Pipelines
# MAGIC
# MAGIC One source notebook shared by five pipelines. Each pipeline sets `eurofarma.layer`
# MAGIC (and, for bronze, `eurofarma.table`) to choose which tables it defines:
# MAGIC
# MAGIC | Pipeline | `eurofarma.layer` | `eurofarma.table` | Output |
# MAGIC | -- | -- | -- | -- |
# MAGIC | eurofarma_bronze_fact_sales | bronze | fact_sales | `eurofarma.bronze.fact_sales` |
# MAGIC | eurofarma_bronze_drugs | bronze | drugs | `eurofarma.bronze.drugs` |
# MAGIC | eurofarma_bronze_drugstore | bronze | drugstore | `eurofarma.bronze.drugstore` |
# MAGIC | eurofarma_silver | silver | - | `eurofarma.silver.{fact_sales, drugs, drugstore}` |
# MAGIC | eurofarma_gold | gold | - | `eurofarma.gold.obt_sales` |
# MAGIC
# MAGIC Source files are in the volume `/Volumes/eurofarma/bronze/rawdata/` (`drugs` is loaded from `drug.csv`).
# MAGIC
# MAGIC Run order: the three bronze pipelines, then silver, then gold.

# COMMAND ----------

from pyspark import pipelines as dp
from pyspark.sql import functions as F

LAYER = spark.conf.get("eurofarma.layer")
VOLUME = "/Volumes/eurofarma/bronze/rawdata/"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze - raw CSV ingested with Auto Loader (all columns kept as strings)

# COMMAND ----------

BRONZE_FILES = {
    "fact_sales": "fact_sales.csv",
    "drugs": "drug.csv",
    "drugstore": "drugstore.csv",
}


def define_bronze(table, filename):
    @dp.table(name=f"eurofarma.bronze.{table}", comment=f"Raw {filename}")
    def _bronze():
        return (
            spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.inferColumnTypes", "false")
            .option("header", "true")
            .option("pathGlobFilter", filename)
            .load(VOLUME)
            .withColumn("_source_file", F.col("_metadata.file_path"))
            .withColumn("_ingested_at", F.current_timestamp())
        )


if LAYER == "bronze":
    _table = spark.conf.get("eurofarma.table")
    define_bronze(_table, BRONZE_FILES[_table])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver - replica of bronze with the literal text `null` turned into NULL and columns typed

# COMMAND ----------

SILVER_TYPES = {
    "fact_sales": {
        "venda_id": "bigint",
        "data_venda": "date",
        "id_produto": "int",
        "quantidade": "int",
        "valor_unitario": "decimal(12,2)",
        "desconto_pct": "double",
        "valor_total": "decimal(14,2)",
    },
    "drugs": {
        "id_produto": "int",
        "data_vencimento_registro": "date",
    },
    "drugstore": {
        "capital_social": "decimal(18,2)",
        "latitude": "double",
        "longitude": "double",
    },
}


def define_silver(table, types):
    @dp.materialized_view(name=f"eurofarma.silver.{table}", comment=f"Typed replica of bronze.{table}")
    def _silver():
        df = spark.read.table(f"eurofarma.bronze.{table}")
        for c in df.columns:
            if c in ("_source_file", "_ingested_at"):
                continue
            col = F.when(F.trim(F.col(c)).isin("null", ""), F.lit(None)).otherwise(F.col(c))
            df = df.withColumn(c, col.cast(types[c]) if c in types else col)
        return df


if LAYER == "silver":
    for _t, _types in SILVER_TYPES.items():
        define_silver(_t, _types)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold - One Big Table
# MAGIC
# MAGIC `fact_sales` joined to `drugs` on `id_produto` and to `drugstore` on `cnpj14`.
# MAGIC LEFT joins keep every sale: about 25% of sales have a `cnpj14` that is not in `drugstore`.

# COMMAND ----------

if LAYER == "gold":

    @dp.materialized_view(
        name="eurofarma.gold.obt_sales",
        comment="One Big Table: fact_sales + drugs + drugstore",
    )
    def obt_sales():
        technical = ("_source_file", "_ingested_at", "_rescued_data")
        sales = spark.read.table("eurofarma.silver.fact_sales").drop(*technical)
        drugs = spark.read.table("eurofarma.silver.drugs").drop(*technical)
        stores = spark.read.table("eurofarma.silver.drugstore").drop(*technical)
        return sales.join(drugs, "id_produto", "left").join(stores, "cnpj14", "left")
