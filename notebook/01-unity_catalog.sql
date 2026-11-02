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

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## ABAC on `eurofarma.gold.obt_sales.email`
-- MAGIC
-- MAGIC Attribute-based access control driven by a governed tag:
-- MAGIC
-- MAGIC 1. Governed tag `pii` (allowed value `email`)
-- MAGIC 2. Tag `pii = email` on the `email` column
-- MAGIC 3. Masking function `eurofarma.gold.mask_email`
-- MAGIC 4. ABAC column-mask policy: applies to all account users, **except** `luis.assuncao@databricks.com`, who sees the clear value

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # Governed tags are account-level objects: create the `pii` tag policy (needs permission to create governed tags)
-- MAGIC from databricks.sdk import WorkspaceClient
-- MAGIC from databricks.sdk.service.tags import TagPolicy, Value
-- MAGIC
-- MAGIC w = WorkspaceClient()
-- MAGIC try:
-- MAGIC     w.tag_policies.create_tag_policy(
-- MAGIC         tag_policy=TagPolicy(tag_key="pii", description="Personally identifiable information", values=[Value(name="email")])
-- MAGIC     )
-- MAGIC except Exception as e:
-- MAGIC     print(f"pii tag policy not created (it may already exist): {e}")

-- COMMAND ----------

ALTER TABLE eurofarma.gold.obt_sales ALTER COLUMN email SET TAGS ('pii' = 'email');

-- COMMAND ----------

CREATE OR REPLACE FUNCTION eurofarma.gold.mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC mask: hides the email value'
RETURN CASE WHEN email IS NULL THEN NULL ELSE '*****' END;

-- COMMAND ----------

CREATE OR REPLACE POLICY mask_pii_email
ON TABLE eurofarma.gold.obt_sales
COMMENT 'Mask columns tagged pii=email for everyone except luis.assuncao@databricks.com'
COLUMN MASK eurofarma.gold.mask_email
TO `account users`
EXCEPT `luis.assuncao@databricks.com`
FOR TABLES
MATCH COLUMNS hasTagValue('pii', 'email') AS email_col
ON COLUMN email_col;

-- COMMAND ----------

SELECT cnpj14, email FROM eurofarma.gold.obt_sales LIMIT 10;
