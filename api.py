from fastapi import FastAPI
import pandas as pd

from db import get_connection

app = FastAPI(title="Expense Tracker API")


def run_query(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    # Convert dates to text so they can be sent as JSON
    for col in df.columns:
        if str(df[col].dtype).startswith("datetime") or df[col].dtype == "object":
            df[col] = df[col].astype(str)
    return df.to_dict(orient="records")


@app.get("/")
def home():
    return {"message": "Expense Tracker API is running"}


@app.get("/transactions")
def get_transactions(limit: int = 20):
    return run_query(f"SELECT * FROM cleaned_transactions ORDER BY date DESC LIMIT {int(limit)}")


@app.get("/summary")
def get_summary():
    return run_query("""
        SELECT txn_type, COUNT(*) AS num_transactions, ROUND(SUM(amount), 2) AS total_amount
        FROM cleaned_transactions
        GROUP BY txn_type
    """)


@app.get("/anomalies")
def get_anomalies():
    return run_query("SELECT * FROM flagged_anomalies ORDER BY date DESC")


@app.get("/forecast")
def get_forecast():
    return run_query("SELECT * FROM spending_forecast ORDER BY date")

@app.get("/kpis")
def get_kpis():
    """Headline numbers for the KPI dashboard: income, expenses, savings, anomalies, forecast."""
    return run_query("""
        SELECT
            ROUND(SUM(CASE WHEN txn_type = 'Income' THEN amount ELSE 0 END), 2) AS total_income,
            ROUND(SUM(CASE WHEN txn_type = 'Expense' THEN amount ELSE 0 END), 2) AS total_expenses,
            ROUND(SUM(CASE WHEN txn_type = 'Income' THEN amount ELSE -amount END), 2) AS net_savings,
            ROUND(100.0 * SUM(CASE WHEN txn_type = 'Income' THEN amount ELSE -amount END)
                  / NULLIF(SUM(CASE WHEN txn_type = 'Income' THEN amount ELSE 0 END), 0), 1) AS savings_rate_pct,
            ROUND(SUM(CASE WHEN txn_type = 'Expense' THEN amount ELSE 0 END)
                  / (MAX(date) - MIN(date) + 1), 2) AS avg_daily_spend,
            (SELECT COUNT(*) FROM flagged_anomalies) AS anomalies_flagged,
            (SELECT ROUND(SUM(predicted_amount), 2) FROM spending_forecast) AS forecast_next_30_days
        FROM cleaned_transactions
    """)
