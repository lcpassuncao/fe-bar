"""Eurofarma sales app: sales trend, sales forecast (Lakebase) and a chat with the Genie space."""
import os
import time
from functools import lru_cache

import psycopg
from databricks.sdk import WorkspaceClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

SOURCE_TABLE = "eurofarma.gold.obt_sales"
WAREHOUSE_ID = os.environ["DATABRICKS_WAREHOUSE_ID"]
SPACE_ID = os.environ["GENIE_SPACE_ID"]
LAKEBASE_ENDPOINT = os.environ["LAKEBASE_ENDPOINT"]
PGDATABASE = os.environ.get("PGDATABASE", "eurofarma")
MAX_ROWS = 50

app = FastAPI(title="Eurofarma Sales")
w = WorkspaceClient()  # service principal credentials injected by Databricks Apps


# ---------------------------------------------------------------- sales trend (SQL warehouse)
@app.get("/api/sales-trend")
def sales_trend():
    stmt = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        wait_timeout="50s",
        statement=f"""
            SELECT CAST(data_venda AS STRING) AS day,
                   CAST(SUM(quantidade) AS DOUBLE) AS quantity,
                   CAST(SUM(valor_total) AS DOUBLE) AS value
            FROM {SOURCE_TABLE}
            GROUP BY data_venda
            ORDER BY data_venda
        """,
    )
    if stmt.status.state.value != "SUCCEEDED":
        raise HTTPException(502, f"query failed: {stmt.status.error.message if stmt.status.error else stmt.status.state}")
    days = [{"day": r[0], "quantity": float(r[1]), "value": float(r[2])} for r in stmt.result.data_array or []]
    # 7-day moving average of the quantity
    for i, d in enumerate(days):
        window = days[max(0, i - 6): i + 1]
        d["quantity_ma7"] = sum(x["quantity"] for x in window) / len(window)
    return {"table": SOURCE_TABLE, "days": days}


# ---------------------------------------------------------------- forecast (Lakebase)
@lru_cache(maxsize=1)
def _lakebase_host() -> str:
    path = LAKEBASE_ENDPOINT.rsplit("/endpoints/", 1)[0]
    return w.api_client.do("GET", f"/api/2.0/postgres/{path}/endpoints")["endpoints"][0]["status"]["hosts"]["host"]


def _lakebase_connect():
    token = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": LAKEBASE_ENDPOINT})["token"]
    return psycopg.connect(
        host=_lakebase_host(), port=5432, dbname=PGDATABASE, user=w.config.client_id,
        password=token, sslmode="require", connect_timeout=15,
    )


@app.get("/api/forecast")
def forecast(sku: int | None = None):
    with _lakebase_connect() as conn:
        if sku is None:
            rows = conn.execute(
                "SELECT projected_date::text, sum(expected_quantity)::float8 FROM public.eurofarma_forecast "
                "GROUP BY projected_date ORDER BY projected_date"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT projected_date::text, expected_quantity::float8 FROM public.eurofarma_forecast "
                "WHERE sku_code = %s ORDER BY projected_date", (sku,)
            ).fetchall()
        skus = conn.execute(
            "SELECT sku_code, max(medication_name), sum(expected_quantity)::float8 AS total "
            "FROM public.eurofarma_forecast GROUP BY sku_code ORDER BY total DESC"
        ).fetchall()
    return {
        "sku": sku,
        "days": [{"day": r[0], "quantity": r[1]} for r in rows],
        "skus": [{"sku_code": r[0], "medication_name": r[1], "total": r[2]} for r in skus],
    }


# ---------------------------------------------------------------- chat with Genie
class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


def _genie(method: str, path: str, body: dict | None = None) -> dict:
    return w.api_client.do(method, f"/api/2.0/genie/spaces/{SPACE_ID}{path}", body=body)


@app.post("/api/chat")
def chat(req: ChatRequest):
    if req.conversation_id:
        msg = _genie("POST", f"/conversations/{req.conversation_id}/messages", {"content": req.message})
        conversation_id, message_id = req.conversation_id, msg["id"]
    else:
        msg = _genie("POST", "/start-conversation", {"content": req.message})
        conversation_id, message_id = msg["conversation_id"], msg["message_id"]

    base = f"/conversations/{conversation_id}/messages/{message_id}"
    deadline = time.time() + 120
    while True:
        m = _genie("GET", base)
        if m["status"] in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        if time.time() > deadline:
            raise HTTPException(504, "Genie took too long to answer")
        time.sleep(2)

    out = {"conversation_id": conversation_id, "status": m["status"], "text": None, "sql": None,
           "description": None, "columns": [], "rows": []}
    if m["status"] != "COMPLETED":
        out["text"] = (m.get("error") or {}).get("error") or f"Genie returned {m['status']}."
        return out
    for att in m.get("attachments", []):
        if att.get("text"):
            out["text"] = att["text"].get("content")
        if att.get("query"):
            out["sql"] = att["query"].get("query")
            out["description"] = att["query"].get("description")
            res = _genie("GET", f"{base}/attachments/{att['attachment_id']}/query-result")
            sr = res.get("statement_response", {})
            out["columns"] = [c["name"] for c in sr.get("manifest", {}).get("schema", {}).get("columns", [])]
            out["rows"] = (sr.get("result", {}).get("data_array") or [])[:MAX_ROWS]
    return out


# ---------------------------------------------------------------- frontend
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))
