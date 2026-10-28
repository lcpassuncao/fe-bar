# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 06 - Sales forecasting model (MLflow + Unity Catalog + Lakebase)
# MAGIC
# MAGIC **Source:** `eurofarma.gold.obt_sales`
# MAGIC **Model:** `eurofarma.gold.sales_forecast_model` (Unity Catalog, alias `champion`)
# MAGIC **Output:** `public.eurofarma_forecast` in Lakebase (see notebook 05)
# MAGIC
# MAGIC ## Approach
# MAGIC Sales per SKU are very sparse (the best SKU sells on about 15 of ~290 days), so a model per SKU per day
# MAGIC would only fit noise. The notebook uses **top-down forecasting**, the usual choice for intermittent demand:
# MAGIC
# MAGIC 1. A gradient boosting model (Poisson loss) forecasts the **total daily quantity**
# MAGIC    from calendar features, lags and rolling means (recursive multi-step forecast).
# MAGIC 2. The total is allocated to the **top-N SKUs** by their share of volume in the last 180 days.
# MAGIC
# MAGIC The model is compared with two simple baselines on a time-based hold-out, and everything is tracked in MLflow
# MAGIC (parameters, metrics, data lineage, signature, input example) before being registered in Unity Catalog.
# MAGIC Because per-SKU daily expectations are far below one unit, `expected_quantity` is stored as `numeric(12,2)`.

# COMMAND ----------

# MAGIC %pip install "mlflow>=3" "psycopg[binary]" --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

dbutils.widgets.text("project_id", "eurofarma", "Lakebase project id")
dbutils.widgets.text("database", "eurofarma", "Postgres database")
dbutils.widgets.text("top_n_skus", "200", "Number of SKUs to forecast")
dbutils.widgets.text("horizon_days", "14", "Days to forecast (from today)")
dbutils.widgets.text("holdout_days", "28", "Hold-out days for evaluation")

# COMMAND ----------

import datetime as dt

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import psycopg
from databricks.sdk import WorkspaceClient
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.ensemble import HistGradientBoostingRegressor

SOURCE_TABLE = "eurofarma.gold.obt_sales"
MODEL_NAME = "eurofarma.gold.sales_forecast_model"
PROJECT_ID = dbutils.widgets.get("project_id")
DATABASE = dbutils.widgets.get("database")
TOP_N = int(dbutils.widgets.get("top_n_skus"))
HORIZON = int(dbutils.widgets.get("horizon_days"))
HOLDOUT = int(dbutils.widgets.get("holdout_days"))
SHARE_WINDOW_DAYS = 180

w = WorkspaceClient()
user = w.current_user.me().user_name
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(f"/Users/{user}/eurofarma_sales_forecast")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Data: total quantity per day

# COMMAND ----------

sales_sdf = spark.table(SOURCE_TABLE)
daily = (
    sales_sdf.groupBy("data_venda").sum("quantidade")
    .toDF("date", "qty").toPandas()
    .assign(date=lambda d: pd.to_datetime(d["date"]))
    .set_index("date")["qty"].astype("float64").sort_index()
)
# complete calendar: days without sales are 0
daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max(), freq="D"), fill_value=0.0)
last_date = daily.index.max()
print(f"{len(daily)} days, {daily.index.min().date()} to {last_date.date()}, mean {daily.mean():.0f}/day")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Features and recursive forecasting

# COMMAND ----------

FEATURES = ["dow", "dom", "month", "lag_1", "lag_7", "lag_14", "roll_7", "roll_28"]


def make_features(s: pd.Series) -> pd.DataFrame:
    """Calendar features + lags / rolling means that only use past values (no leakage)."""
    df = pd.DataFrame({"y": s})
    df["dow"] = s.index.dayofweek
    df["dom"] = s.index.day
    df["month"] = s.index.month
    df["lag_1"] = s.shift(1)
    df["lag_7"] = s.shift(7)
    df["lag_14"] = s.shift(14)
    df["roll_7"] = s.shift(1).rolling(7).mean()
    df["roll_28"] = s.shift(1).rolling(28).mean()
    df[FEATURES] = df[FEATURES].astype("float64")
    return df


def recursive_forecast(model, history: pd.Series, days: int) -> pd.Series:
    s = history.copy()
    out = {}
    for _ in range(days):
        d = s.index[-1] + pd.Timedelta(days=1)
        s.loc[d] = np.nan
        yhat = max(float(model.predict(make_features(s).loc[[d], FEATURES])[0]), 0.0)
        s.loc[d] = yhat
        out[d] = yhat
    return pd.Series(out)


PARAMS = dict(loss="poisson", max_iter=200, learning_rate=0.05, max_depth=3, min_samples_leaf=10, random_state=42)


def fit(series: pd.Series) -> HistGradientBoostingRegressor:
    train = make_features(series).dropna()
    return HistGradientBoostingRegressor(**PARAMS).fit(train[FEATURES], train["y"])


def metrics(actual: pd.Series, pred: pd.Series, prefix: str) -> dict:
    err = (actual.values - pred.values)
    return {
        f"{prefix}_mae": float(np.abs(err).mean()),
        f"{prefix}_wape": float(np.abs(err).sum() / actual.sum()),
        f"{prefix}_bias": float(err.sum() / actual.sum()),
    }


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Time-based hold-out evaluation (multi-step, same recursion used in production) vs. baselines

# COMMAND ----------

train_s, test_s = daily.iloc[:-HOLDOUT], daily.iloc[-HOLDOUT:]
eval_model = fit(train_s)
pred_model = recursive_forecast(eval_model, train_s, HOLDOUT)
pred_mean28 = pd.Series(train_s.iloc[-28:].mean(), index=test_s.index)  # trailing 28-day mean
pred_snaive = pd.Series(np.tile(train_s.iloc[-7:].values, HOLDOUT // 7 + 1)[:HOLDOUT], index=test_s.index)  # repeat last week

eval_metrics = {
    **metrics(test_s, pred_model, "model"),
    **metrics(test_s, pred_mean28, "baseline_mean28"),
    **metrics(test_s, pred_snaive, "baseline_snaive7"),
}
display(pd.DataFrame(eval_metrics, index=["value"]).T.reset_index().rename(columns={"index": "metric"}))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Final training, MLflow tracking and registration in Unity Catalog

# COMMAND ----------

final_model = fit(daily)
X = make_features(daily).dropna()[FEATURES]
signature = infer_signature(X, final_model.predict(X))

with mlflow.start_run(run_name="hgb_poisson_total_daily_qty") as run:
    mlflow.log_input(mlflow.data.from_spark(sales_sdf, table_name=SOURCE_TABLE), context="training")
    mlflow.log_params({**PARAMS, "features": ",".join(FEATURES), "holdout_days": HOLDOUT,
                       "train_days": len(daily), "last_data_date": str(last_date.date())})
    mlflow.log_metrics(eval_metrics)
    mlflow.set_tags({"task": "demand_forecasting", "granularity": "total_daily_quantity", "source_table": SOURCE_TABLE})
    info = mlflow.sklearn.log_model(
        final_model,
        name="model",
        signature=signature,
        input_example=X.head(5),
        registered_model_name=MODEL_NAME,
    )

version = info.registered_model_version
client = MlflowClient()
client.update_registered_model(MODEL_NAME, description="Total daily sales quantity forecaster (gradient boosting, Poisson loss).")
client.update_model_version(MODEL_NAME, version, description=f"Trained on data up to {last_date.date()}. "
                            f"Hold-out WAPE {eval_metrics['model_wape']:.3f} vs trailing-mean baseline {eval_metrics['baseline_mean28_wape']:.3f}.")
client.set_registered_model_alias(MODEL_NAME, "champion", version)
print(f"registered {MODEL_NAME} version {version} (alias champion), run {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Forecast the coming days with the registered model and allocate to SKUs

# COMMAND ----------

model = mlflow.sklearn.load_model(f"models:/{MODEL_NAME}@champion")

today = pd.Timestamp(dt.date.today())
end = today + pd.Timedelta(days=HORIZON - 1)
steps = max((end - last_date).days, 1)
total_fc = recursive_forecast(model, daily, steps)
total_fc = total_fc[total_fc.index >= today]  # data may end before today: keep only the coming days
print(f"forecast {total_fc.index.min().date()} to {total_fc.index.max().date()}, mean {total_fc.mean():.0f}/day")

shares = spark.sql(f"""
    WITH w AS (SELECT * FROM {SOURCE_TABLE} WHERE data_venda > date_sub(DATE'{last_date.date()}', {SHARE_WINDOW_DAYS})),
         t AS (SELECT sum(quantidade) AS tot FROM w)
    SELECT id_produto AS sku_code,
           coalesce(max(nome_medicamento), 'Não informado') AS medication_name,
           sum(quantidade) / max(t.tot) AS share
    FROM w CROSS JOIN t
    GROUP BY id_produto
    ORDER BY sum(quantidade) DESC
    LIMIT {TOP_N}
""").toPandas()

forecast = (
    shares.merge(total_fc.rename("total").rename_axis("projected_date").reset_index(), how="cross")
    .assign(expected_quantity=lambda d: (d["share"] * d["total"]).round(2),
            projected_date=lambda d: d["projected_date"].dt.date)
    [["sku_code", "medication_name", "projected_date", "expected_quantity"]]
)
print(len(forecast), "rows;", forecast["sku_code"].nunique(), "SKUs;", f"top-N share of volume {shares['share'].sum():.1%}")
display(forecast.head(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Write the result to Lakebase (`public.eurofarma_forecast`)
# MAGIC The rows for the forecast dates are replaced in a single transaction, so the table always holds the latest run.

# COMMAND ----------

project_path = f"projects/{PROJECT_ID}"
endpoint_path = f"{project_path}/branches/production/endpoints/primary"
host = w.api_client.do("GET", f"/api/2.0/postgres/{project_path}/branches/production/endpoints")["endpoints"][0]["status"]["hosts"]["host"]
token = w.api_client.do("POST", "/api/2.0/postgres/credentials", body={"endpoint": endpoint_path})["token"]

rows = [(int(r.sku_code), r.medication_name, r.projected_date, float(r.expected_quantity)) for r in forecast.itertuples()]

with psycopg.connect(host=host, port=5432, dbname=DATABASE, user=user, password=token, sslmode="require") as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS public.eurofarma_forecast (
            sku_code          integer       NOT NULL,
            medication_name   text          NOT NULL,
            projected_date    date          NOT NULL,
            expected_quantity numeric(12,2) NOT NULL CHECK (expected_quantity >= 0),
            PRIMARY KEY (sku_code, projected_date)
        )
        """
    )
    # tables created by notebook 05 used integer: expected units per SKU per day are fractional
    conn.execute("ALTER TABLE public.eurofarma_forecast ALTER COLUMN expected_quantity TYPE numeric(12,2)")
    conn.execute("DELETE FROM public.eurofarma_forecast WHERE projected_date >= %s", (min(r[2] for r in rows),))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO public.eurofarma_forecast (sku_code, medication_name, projected_date, expected_quantity) "
            "VALUES (%s, %s, %s, %s)",
            rows,
        )
    n, d0, d1, total = conn.execute(
        "SELECT count(*), min(projected_date), max(projected_date), sum(expected_quantity) FROM public.eurofarma_forecast"
    ).fetchone()
print(f"eurofarma_forecast: {n} rows, {d0} to {d1}, total expected quantity {total}")

# COMMAND ----------

# DBTITLE 1,Check Lakebase forecast table
with psycopg.connect(host=host, port=5432, dbname=DATABASE, user=user, password=token, sslmode="require") as conn:
    display(pd.DataFrame(
        conn.execute("SELECT count(*), min(projected_date), max(projected_date), sum(expected_quantity)  FROM public.eurofarma_forecast").fetchall(),
        columns=["count", "min_projected_date", "max_projected_date", "sum_expected_quantity"],
    ))
