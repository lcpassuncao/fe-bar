# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC ## Databricks FE-BAR 
# MAGIC
# MAGIC * **Date**:  October, 28 2026
# MAGIC
# MAGIC * **Company** :  EUROFARMA
# MAGIC * **Sector**  :  Pharmaceutical Industry
# MAGIC * **Author**  :  Luis Assunção (Solution Architect Databricks)
# MAGIC * **Use Case**:  Optimization of distribution logistics for generic medicines
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # 03 - AI/BI Dashboard
# MAGIC
# MAGIC Creates (or updates) the Lakeview dashboard **Eurofarma - AIBI Vendas (obt_sales)** from
# MAGIC `dashboard/eurofarma_vendas.lvdash.json`, which is versioned in this repository.
# MAGIC
# MAGIC * Source table: `eurofarma.gold.obt_sales`
# MAGIC * Page **Vendas**: KPIs (Quantidade Vendida, Valor de Vendas, Ticket Médio) and charts
# MAGIC * Page **Mapa**: point map (latitude / longitude)
# MAGIC * Global filters: Fabricante, Tipo de Medicamento, UF, Cidade, Período

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "9d8a677b3c55b8a7", "SQL warehouse id")
dbutils.widgets.text("parent_path", "", "Parent folder (empty = your home folder)")

# COMMAND ----------

import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import Dashboard

DISPLAY_NAME = "Eurofarma - AIBI Vendas (obt_sales)"
warehouse_id = dbutils.widgets.get("warehouse_id")

w = WorkspaceClient()
parent_path = dbutils.widgets.get("parent_path") or f"/Users/{w.current_user.me().user_name}"

# This notebook lives in <repo>/notebook; the dashboard definition is in <repo>/dashboard
notebook_dir = os.path.dirname("/Workspace" + dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
definition = os.path.join(os.path.dirname(notebook_dir), "dashboard", "eurofarma_vendas.lvdash.json")
with open(definition, encoding="utf-8") as f:
    serialized = f.read()

# COMMAND ----------

existing = next(
    (d for d in w.lakeview.list() if d.display_name == DISPLAY_NAME and d.parent_path == parent_path),
    None,
)
spec = Dashboard(
    display_name=DISPLAY_NAME,
    warehouse_id=warehouse_id,
    parent_path=parent_path,
    serialized_dashboard=serialized,
)
if existing:
    dash = w.lakeview.update(existing.dashboard_id, spec)
    print("updated", dash.dashboard_id)
else:
    dash = w.lakeview.create(spec)
    print("created", dash.dashboard_id)

# COMMAND ----------

# Publishing is left as a manual choice (it shares the dashboard with embedded credentials):
# w.lakeview.publish(dash.dashboard_id, embed_credentials=True, warehouse_id=warehouse_id)
displayHTML(f'<a href="/dashboardsv3/{dash.dashboard_id}">Open dashboard</a>')
