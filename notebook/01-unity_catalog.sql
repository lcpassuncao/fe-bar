-- Databricks notebook source
-- MAGIC %md
-- MAGIC ## Databricks FE-BAR 
-- MAGIC
-- MAGIC * **Date**:  October, 28 2026
-- MAGIC
-- MAGIC * **Company** :  EUROFARMA
-- MAGIC * **Sector**  :  Pharmaceutical Industry
-- MAGIC * **Author**  :  Luis Assunção (Solution Architect Databricks)
-- MAGIC * **Use Case**:  Sales and demand-forecasting for generic medicines

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # 01 - Unity Catalog setup (governance)
-- MAGIC
-- MAGIC Creates the `eurofarma` catalog, the `bronze`, `silver` and `gold` schemas,
-- MAGIC and the `rawdata` volume (in `bronze`) that receives the raw files.

-- COMMAND ----------

CREATE CATALOG IF NOT EXISTS eurofarma
COMMENT 'Eurofarma project catalog';

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS eurofarma.bronze COMMENT 'Raw ingested data';

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS eurofarma.silver COMMENT 'Cleaned and conformed data';

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS eurofarma.gold COMMENT 'Business-level aggregates';

-- COMMAND ----------

CREATE VOLUME IF NOT EXISTS eurofarma.bronze.rawdata COMMENT 'Raw files landed from GitHub (rawdata/)';

-- COMMAND ----------

SHOW SCHEMAS IN eurofarma;

-- COMMAND ----------

SHOW VOLUMES IN eurofarma.bronze;
