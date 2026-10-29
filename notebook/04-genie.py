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
# MAGIC # 04 - Genie space
# MAGIC
# MAGIC Creates (or updates) the Genie space **genie_eurofarma** ("Commercial conversational agent")
# MAGIC on top of `eurofarma.gold.obt_sales`, with sample questions such as
# MAGIC *"What are the top 5 best-selling medications from the manufacturer Eurofarma?"*.
# MAGIC
# MAGIC The space is created with the Genie REST API (`/api/2.0/genie/spaces`).

# COMMAND ----------

dbutils.widgets.text("warehouse_id", "9d8a677b3c55b8a7", "SQL warehouse id")

# COMMAND ----------

import json
from databricks.sdk import WorkspaceClient

TITLE = "genie_eurofarma"
DESCRIPTION = "Commercial conversational agent"

# serialized_space: table, column descriptions, instructions, sample questions and example SQL
SERIALIZED_SPACE = r"""
{
  "version": 2,
  "config": {
    "sample_questions": [
      {
        "id": "0afbc8aad528406ab26c4e20816a0e6e",
        "question": [
          "How did monthly sales value evolve in 2026?"
        ]
      },
      {
        "id": "445d1c0a025e4bc884c1f22b263a061c",
        "question": [
          "Which are the top 10 manufacturers by sales value?"
        ]
      },
      {
        "id": "64e9f6445c78469197323b7843360d61",
        "question": [
          "What is the average ticket by sales channel?"
        ]
      },
      {
        "id": "782917713c7c4313894499cfaaf2e253",
        "question": [
          "What is the total sales value by state (UF)?"
        ]
      },
      {
        "id": "d1e27d2dcf8d404b86db61d3293925a8",
        "question": [
          "What are the top 5 best-selling medications from the manufacturer Eurofarma?"
        ]
      }
    ]
  },
  "data_sources": {
    "tables": [
      {
        "identifier": "eurofarma.gold.obt_sales",
        "column_configs": [
          {
            "column_name": "canal_venda",
            "enable_format_assistance": true,
            "description": [
              "Sales channel."
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "categoria_regulatoria",
            "enable_format_assistance": true,
            "description": [
              "Drug type / regulatory category (e.g. GENÉRICO, SIMILAR, NOVO)."
            ],
            "synonyms": [
              "drug type",
              "type"
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "cidade",
            "enable_format_assistance": true,
            "description": [
              "City of the drugstore."
            ],
            "synonyms": [
              "city"
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "classe_terapeutica",
            "enable_format_assistance": true,
            "description": [
              "Therapeutic class."
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "cnpj14",
            "enable_format_assistance": true,
            "description": [
              "14-digit CNPJ of the drugstore that bought the product."
            ]
          },
          {
            "column_name": "data_venda",
            "enable_format_assistance": true,
            "description": [
              "Sale date."
            ],
            "synonyms": [
              "sale date",
              "date"
            ]
          },
          {
            "column_name": "desconto_pct",
            "enable_format_assistance": true,
            "description": [
              "Discount applied (fraction, 0 to 1)."
            ]
          },
          {
            "column_name": "empresa_detentora_registro",
            "enable_format_assistance": true,
            "description": [
              "Drug manufacturer (registration holder)."
            ],
            "synonyms": [
              "manufacturer",
              "laboratory",
              "lab"
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "forma_pagamento",
            "enable_format_assistance": true,
            "description": [
              "Payment method."
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "id_produto",
            "enable_format_assistance": true,
            "description": [
              "Drug (product) identifier."
            ]
          },
          {
            "column_name": "latitude",
            "enable_format_assistance": true,
            "description": [
              "Drugstore latitude."
            ]
          },
          {
            "column_name": "longitude",
            "enable_format_assistance": true,
            "description": [
              "Drugstore longitude."
            ]
          },
          {
            "column_name": "nome_fantasia",
            "enable_format_assistance": true,
            "description": [
              "Drugstore trade name."
            ]
          },
          {
            "column_name": "nome_medicamento",
            "enable_format_assistance": true,
            "description": [
              "Drug (medication) name."
            ],
            "synonyms": [
              "medication",
              "drug",
              "product"
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "principio_ativo",
            "enable_format_assistance": true,
            "description": [
              "Active ingredient."
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "quantidade",
            "enable_format_assistance": true,
            "description": [
              "Units sold."
            ],
            "synonyms": [
              "sales quantity",
              "units"
            ]
          },
          {
            "column_name": "razao_social",
            "enable_format_assistance": true,
            "description": [
              "Drugstore legal name."
            ]
          },
          {
            "column_name": "uf",
            "enable_format_assistance": true,
            "description": [
              "Brazilian state (UF) of the drugstore. NULL when the drugstore is not in the registry."
            ],
            "synonyms": [
              "state",
              "region"
            ],
            "enable_entity_matching": true
          },
          {
            "column_name": "valor_total",
            "enable_format_assistance": true,
            "description": [
              "Total sale value in BRL (sales value / revenue)."
            ],
            "synonyms": [
              "sales value",
              "revenue"
            ]
          },
          {
            "column_name": "valor_unitario",
            "enable_format_assistance": true,
            "description": [
              "Unit price in BRL."
            ]
          },
          {
            "column_name": "venda_id",
            "enable_format_assistance": true,
            "description": [
              "Unique sale identifier."
            ]
          }
        ]
      }
    ]
  },
  "instructions": {
    "text_instructions": [
      {
        "id": "7d1b7aeaea3944f3b5c596393e0a75e3",
        "content": [
          "This space answers commercial questions about drug sales in Brazil using one denormalized table, eurofarma.gold.obt_sales (one row per sale: sale + drug + drugstore). Currency is BRL. Sales value = SUM(valor_total); sales quantity = SUM(quantidade); average ticket = SUM(valor_total) / COUNT(DISTINCT venda_id). 'Best-selling' means highest SUM(quantidade) unless the user asks for value. The manufacturer is empresa_detentora_registro; Eurofarma is stored as 'EUROFARMA LABORATÓRIOS S.A.', so match it with upper(empresa_detentora_registro) LIKE '%EUROFARMA%'. Drug type is categoria_regulatoria. Location columns (uf, cidade, latitude, longitude) come from the drugstore registry and are NULL for about 25% of sales. Answer in the user's language and state the filters and period used."
        ]
      }
    ],
    "example_question_sqls": [
      {
        "id": "2e3aba224f9c4e0ca7d9027c639ae38f",
        "question": [
          "How did monthly sales value evolve in 2026?"
        ],
        "sql": [
          "SELECT DATE_TRUNC('MONTH', data_venda) AS mes, SUM(valor_total) AS valor_vendas FROM eurofarma.gold.obt_sales WHERE year(data_venda) = 2026 GROUP BY 1 ORDER BY 1"
        ]
      },
      {
        "id": "55e0100c51c84b53a8a5faf200b791f0",
        "question": [
          "Which are the top 10 manufacturers by sales value?"
        ],
        "sql": [
          "SELECT empresa_detentora_registro, SUM(valor_total) AS valor_vendas FROM eurofarma.gold.obt_sales GROUP BY empresa_detentora_registro ORDER BY valor_vendas DESC LIMIT 10"
        ]
      },
      {
        "id": "a1c62706a67a4d52b8c7696ee133c502",
        "question": [
          "What is the average ticket by sales channel?"
        ],
        "sql": [
          "SELECT canal_venda, SUM(valor_total) / COUNT(DISTINCT venda_id) AS ticket_medio FROM eurofarma.gold.obt_sales GROUP BY canal_venda ORDER BY ticket_medio DESC"
        ]
      },
      {
        "id": "c5aa971e0d8d470ba2aabcd069dc8e24",
        "question": [
          "What are the top 5 best-selling medications from the manufacturer Eurofarma?"
        ],
        "sql": [
          "SELECT nome_medicamento, SUM(quantidade) AS total_quantidade FROM eurofarma.gold.obt_sales WHERE upper(empresa_detentora_registro) LIKE '%EUROFARMA%' GROUP BY nome_medicamento ORDER BY total_quantidade DESC LIMIT 5"
        ]
      },
      {
        "id": "f50cd9abf5824c6789a8fca59bd5420f",
        "question": [
          "What is the total sales value by state (UF)?"
        ],
        "sql": [
          "SELECT uf, SUM(valor_total) AS valor_vendas FROM eurofarma.gold.obt_sales WHERE uf IS NOT NULL GROUP BY uf ORDER BY valor_vendas DESC"
        ]
      }
    ]
  }
}
"""

# COMMAND ----------

w = WorkspaceClient()
warehouse_id = dbutils.widgets.get("warehouse_id")
parent_path = f"/Workspace/Users/{w.current_user.me().user_name}"

existing = None
page_token = None
while True:
    resp = w.api_client.do("GET", "/api/2.0/genie/spaces", query={"page_token": page_token} if page_token else None)
    existing = next((s for s in resp.get("spaces", []) if s.get("title") == TITLE), None)
    page_token = resp.get("next_page_token")
    if existing or not page_token:
        break

payload = {
    "title": TITLE,
    "description": DESCRIPTION,
    "warehouse_id": warehouse_id,
    "serialized_space": json.dumps(json.loads(SERIALIZED_SPACE), ensure_ascii=False),
}
if existing:
    space_id = existing["space_id"]
    w.api_client.do("PATCH", f"/api/2.0/genie/spaces/{space_id}", body=payload)
    print("updated", space_id)
else:
    payload["parent_path"] = parent_path
    space_id = w.api_client.do("POST", "/api/2.0/genie/spaces", body=payload)["space_id"]
    print("created", space_id)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Try it
# MAGIC Open the space (Genie in the left menu) and ask, for example:
# MAGIC * What are the top 5 best-selling medications from the manufacturer Eurofarma?
# MAGIC * What is the total sales value by state (UF)?
# MAGIC * What is the average ticket by sales channel?
# MAGIC * Which are the top 10 manufacturers by sales value?
# MAGIC * How did monthly sales value evolve in 2026?

# COMMAND ----------

displayHTML(f'<a href="/genie/rooms/{space_id}">Open genie_eurofarma</a>')

# COMMAND ----------

# DBTITLE 1,Download Genie space execution log
# Download the execution log (conversations + messages + generated SQL) of genie_eurofarma
import json
import pandas as pd
from datetime import datetime, timezone
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

LOG_SPACE_ID = "01f1d318a7291675a3a21b99e59bab22"  # from the Genie room URL

def _paged(path, key, query=None):
    query = dict(query or {})
    while True:
        resp = w.api_client.do("GET", path, query=query)
        yield from resp.get(key, [])
        token = resp.get("next_page_token")
        if not token:
            break
        query["page_token"] = token

def _ts(ms):
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc) if ms else None

base = f"/api/2.0/genie/spaces/{LOG_SPACE_ID}/conversations"
conversations = list(_paged(base, "conversations", {"page_size": 100, "include_all": "true"}))
print(f"{len(conversations)} conversations found")

rows = []
for c in conversations:
    cid = c.get("conversation_id") or c.get("id")
    try:
        messages = list(_paged(f"{base}/{cid}/messages", "messages", {"page_size": 100}))
    except Exception as e:
        print(f"Could not read messages of conversation {cid}: {e}")
        messages = []
    for m in messages:
        attachments = m.get("attachments") or [{}]
        for a in attachments:
            q = a.get("query") or {}
            rows.append({
                "conversation_id": cid,
                "conversation_title": c.get("title"),
                "message_id": m.get("message_id") or m.get("id"),
                "user_id": str(m.get("user_id") or c.get("user_id") or ""),
                "created_at": _ts(m.get("created_timestamp")),
                "status": m.get("status"),
                "question": m.get("content"),
                "attachment_id": a.get("attachment_id"),
                "generated_sql": q.get("query"),
                "sql_description": q.get("description"),
                "statement_id": q.get("statement_id") or (q.get("query_result_metadata") or {}).get("statement_id"),
                "row_count": (q.get("query_result_metadata") or {}).get("row_count"),
                "text_answer": (a.get("text") or {}).get("content"),
                "error": json.dumps(m.get("error"), ensure_ascii=False) if m.get("error") else None,
            })

log_pdf = pd.DataFrame(rows)
print(f"{len(log_pdf)} log rows")

# Use the download button of the result table to export as CSV/Excel
if not log_pdf.empty:
    display(log_pdf.sort_values("created_at"))

# COMMAND ----------


