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

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Row Level Security (RLS) on `eurofarma.gold.obt_sales`
-- MAGIC
-- MAGIC Row filter on the `uf` column: each user only sees the rows of the state that
-- MAGIC matches their account group (`group_<uf>`), e.g. a member of `group_rj` only sees `uf = 'RJ'`.
-- MAGIC
-- MAGIC * Groups expected: `group_ac`, `group_al`, ... `group_to` (one per UF).
-- MAGIC * Rows with `uf IS NULL` are not visible to any group.
-- MAGIC * A user that belongs to no `group_<uf>` sees no rows.

-- COMMAND ----------

CREATE OR REPLACE FUNCTION eurofarma.gold.rls_uf(uf STRING)
RETURNS BOOLEAN
COMMENT 'RLS: a row is visible only to the account group group_<uf> (e.g. group_rj sees UF = RJ)'
RETURN is_account_group_member(concat('group_', lower(uf)));

-- COMMAND ----------

-- obt_sales is a materialized view produced by the eurofarma_gold pipeline
ALTER MATERIALIZED VIEW eurofarma.gold.obt_sales SET ROW FILTER eurofarma.gold.rls_uf ON (uf);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Validation: run as a member of `group_rj`, the query below must return only `RJ`.

-- COMMAND ----------

SELECT uf, COUNT(*) AS linhas
FROM eurofarma.gold.obt_sales
GROUP BY uf
ORDER BY uf;
