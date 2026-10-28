# Databricks notebook source
# MAGIC %md
# MAGIC # 07 - Databricks App: Eurofarma sales
# MAGIC
# MAGIC Deploys the app whose source code is in the repository folder `app/`:
# MAGIC
# MAGIC * **Sales trend**: line chart of units sold per day, read from `eurofarma.gold.obt_sales` through a SQL warehouse
# MAGIC * **Projected sales**: line chart of `public.eurofarma_forecast` in Lakebase (written by notebook 06)
# MAGIC * **Chat**: conversation with the Genie space `genie_eurofarma` (notebook 04)
# MAGIC
# MAGIC The notebook is idempotent. It (1) creates the app with its resources (SQL warehouse, Genie space),
# MAGIC (2) grants the app's service principal read access in Unity Catalog and Lakebase, and (3) deploys the code.

# COMMAND ----------

# MAGIC %pip install "psycopg[binary]" --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("app_name", "eurofarma-app", "App name")
dbutils.widgets.text("warehouse_id", "9d8a677b3c55b8a7", "SQL warehouse id")
dbutils.widgets.text("genie_title", "genie_eurofarma", "Genie space title")
dbutils.widgets.text("lakebase_project", "eurofarma", "Lakebase project id")
dbutils.widgets.text("lakebase_database", "eurofarma", "Lakebase database")

# COMMAND ----------

import os

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound
from databricks.sdk.service.apps import App, AppDeployment, AppDeploymentMode, AppResource, AppResourceGenieSpace, AppResourceGenieSpaceGenieSpacePermission, AppResourceSqlWarehouse, AppResourceSqlWarehouseSqlWarehousePermission

APP_NAME = dbutils.widgets.get("app_name")
WAREHOUSE_ID = dbutils.widgets.get("warehouse_id")
GENIE_TITLE = dbutils.widgets.get("genie_title")
PROJECT = dbutils.widgets.get("lakebase_project")
DATABASE = dbutils.widgets.get("lakebase_database")

w = WorkspaceClient()
user = w.current_user.me().user_name

# The app source lives in <repo>/app; this notebook is <repo>/notebook/07-apps
nb_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
SOURCE_PATH = "/Workspace" + os.path.join(os.path.dirname(os.path.dirname(nb_path)), "app")
print("source:", SOURCE_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. App and resources

# COMMAND ----------

def find_genie_space(title):
    token = None
    while True:
        resp = w.api_client.do("GET", "/api/2.0/genie/spaces", query={"page_token": token} if token else None)
        for s in resp.get("spaces", []):
            if s.get("title") == title:
                return s["space_id"]
        token = resp.get("next_page_token")
        if not token:
            raise ValueError(f"Genie space {title!r} not found (run notebook 04 first)")


space_id = find_genie_space(GENIE_TITLE)
resources = [
    AppResource(name="sql-warehouse", sql_warehouse=AppResourceSqlWarehouse(
        id=WAREHOUSE_ID, permission=AppResourceSqlWarehouseSqlWarehousePermission.CAN_USE)),
    AppResource(name="genie-space", genie_space=AppResourceGenieSpace(
        name=GENIE_TITLE, space_id=space_id, permission=AppResourceGenieSpaceGenieSpacePermission.CAN_RUN)),
]

try:
    app = w.apps.get(APP_NAME)
    print("app exists:", APP_NAME)
except NotFound:
    app = w.apps.create_and_wait(App(
        name=APP_NAME, description="Eurofarma sales trends, forecast and Genie chat", resources=resources))
    print("app created:", APP_NAME)

sp = app.service_principal_client_id
print("service principal:", sp)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Grants for the app's service principal
# MAGIC The SQL warehouse and Genie space permissions come from the app resources; Unity Catalog and Lakebase need explicit grants.

# COMMAND ----------

spark.sql(f"GRANT USE CATALOG ON CATALOG eurofarma TO `{sp}`")
spark.sql(f"GRANT USE SCHEMA ON SCHEMA eurofarma.gold TO `{sp}`")
spark.sql(f"GRANT SELECT ON TABLE eurofarma.gold.obt_sales TO `{sp}`")
print("Unity Catalog grants done")

# COMMAND ----------

project_path = f"projects/{PROJECT}"
endpoint_path = f"{project_path}/branches/production/endpoints/primary"
host = w.api_client.do("GET", f"/api/2.0/postgres/{project_path}/branches/production/endpoints")["endpoints"][0]["status"]["hosts"]["host"]
token = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": endpoint_path})["token"]

with psycopg.connect(host=host, port=5432, dbname=DATABASE, user=user, password=token, sslmode="require", autocommit=True) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS databricks_auth")
    if not conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (sp,)).fetchone():
        conn.execute("SELECT databricks_create_role(%s, 'service_principal')", (sp,))
        print("postgres role created")
    conn.execute(f'GRANT CONNECT ON DATABASE "{DATABASE}" TO "{sp}"')
    conn.execute(f'GRANT USAGE ON SCHEMA public TO "{sp}"')
    conn.execute(f'GRANT SELECT ON public.eurofarma_forecast TO "{sp}"')
print("Lakebase grants done")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Deploy

# COMMAND ----------

deployment = w.apps.deploy_and_wait(
    APP_NAME, AppDeployment(source_code_path=SOURCE_PATH, mode=AppDeploymentMode.SNAPSHOT))
print("deployment:", deployment.status.state.value, "-", deployment.status.message)

app = w.apps.get(APP_NAME)
print("app status:", app.app_status.state.value, "| compute:", app.compute_status.state.value)
print("URL:", app.url)
displayHTML(f'<a href="{app.url}" target="_blank">Open {APP_NAME}</a>')
