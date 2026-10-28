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
# MAGIC # 05 - Lakebase (Postgres)
# MAGIC
# MAGIC Creates a Lakebase Autoscaling project, a database `eurofarma` and the table
# MAGIC `eurofarma_forecast`, which stores the sales projection for the coming days:
# MAGIC
# MAGIC | Column | Type | Description |
# MAGIC | -- | -- | -- |
# MAGIC | `sku_code` | integer | SKU code (`id_produto` in `eurofarma.gold.obt_sales`) |
# MAGIC | `medication_name` | text | Medication name |
# MAGIC | `projected_date` | date | Date the projection refers to |
# MAGIC | `expected_quantity` | numeric(12,2) | Expected sales quantity (fractional: expected units per SKU per day are small) |
# MAGIC
# MAGIC The notebook is idempotent: re-running it does not recreate or change anything that exists.

# COMMAND ----------

# MAGIC %pip install "psycopg[binary]" --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("project_id", "eurofarma", "Lakebase project id")
dbutils.widgets.text("database", "eurofarma", "Postgres database")

# COMMAND ----------

import time
import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound

PROJECT_ID = dbutils.widgets.get("project_id")
DATABASE = dbutils.widgets.get("database")
BRANCH = "production"
ENDPOINT = "primary"

w = WorkspaceClient()
project_path = f"projects/{PROJECT_ID}"
branch_path = f"{project_path}/branches/{BRANCH}"
endpoint_path = f"{branch_path}/endpoints/{ENDPOINT}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Project (creates the `production` branch and `primary` read-write endpoint)

# COMMAND ----------

try:
    w.api_client.do("GET", f"/api/2.0/postgres/{project_path}")
    print("project exists:", project_path)
except NotFound:
    w.api_client.do(
        "POST", f"/api/2.0/postgres/projects?project_id={PROJECT_ID}",
        body={"spec": {"display_name": PROJECT_ID.capitalize()}},
    )
    print("project created:", project_path)

for _ in range(60):
    eps = w.api_client.do("GET", f"/api/2.0/postgres/{branch_path}/endpoints").get("endpoints", [])
    if eps and eps[0]["status"]["current_state"] == "ACTIVE":
        break
    time.sleep(10)
else:
    raise TimeoutError("endpoint did not become ACTIVE")
host = eps[0]["status"]["hosts"]["host"]
print("endpoint host:", host)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Database and table

# COMMAND ----------

user = w.current_user.me().user_name


def connect(dbname, autocommit=False):
    # OAuth token, valid for 1 hour
    token = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": endpoint_path})["token"]
    return psycopg.connect(
        host=host, port=5432, dbname=dbname, user=user, password=token, sslmode="require", autocommit=autocommit
    )


# CREATE DATABASE cannot run inside a transaction
with connect("postgres", autocommit=True) as conn:
    exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE,)).fetchone()
    if not exists:
        conn.execute(f'CREATE DATABASE "{DATABASE}"')
    print("database", DATABASE, "exists" if exists else "created")

# COMMAND ----------

with connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS public.eurofarma_forecast (
            sku_code          integer NOT NULL,
            medication_name   text    NOT NULL,
            projected_date    date    NOT NULL,
            expected_quantity numeric(12,2) NOT NULL CHECK (expected_quantity >= 0),
            PRIMARY KEY (sku_code, projected_date)
        )
        """
    )
    conn.execute("COMMENT ON TABLE public.eurofarma_forecast IS 'Sales projection for the coming days'")

# COMMAND ----------

with connect(DATABASE) as conn:
    cols = conn.execute(
        """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'eurofarma_forecast'
        ORDER BY ordinal_position
        """
    ).fetchall()
    n = conn.execute("SELECT count(*) FROM public.eurofarma_forecast").fetchone()[0]
display(spark.createDataFrame(cols, "column_name string, data_type string, is_nullable string"))
print("rows in eurofarma_forecast:", n)
