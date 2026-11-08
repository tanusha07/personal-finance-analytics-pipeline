from fastapi import FastAPI
import pandas as pd
import psycopg2

app = FastAPI(title="Expense Tracker API")


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="expense_tracker",
        user="tracker",
        password="tracker_pass"
    )


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