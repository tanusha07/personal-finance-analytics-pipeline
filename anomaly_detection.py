import pandas as pd
from sklearn.ensemble import IsolationForest

from db import get_connection

EXCLUDED_CATEGORIES = ["rent", "debt payment"]


def detect_anomalies(df, contamination=0.03):
    """Return (expenses, anomalies): Isolation Forest on expense amounts, skipping excluded categories."""
    expenses = df[df["txn_type"] == "Expense"].copy()
    expenses = expenses[~expenses["category"].str.lower().isin(EXCLUDED_CATEGORIES)]

    model = IsolationForest(contamination=contamination, random_state=42)
    # IsolationForest marks normal rows as 1 and anomalies as -1
    expenses["anomaly_score"] = model.fit_predict(expenses[["amount"]])
    expenses["is_anomaly"] = expenses["anomaly_score"] == -1
    return expenses, expenses[expenses["is_anomaly"]]


def main():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM cleaned_transactions", conn)
    expenses, anomalies = detect_anomalies(df)

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flagged_anomalies (
            id SERIAL PRIMARY KEY,
            date DATE,
            category VARCHAR(50),
            description VARCHAR(100),
            amount NUMERIC(10,2)
        )
    """)
    cur.execute("TRUNCATE TABLE flagged_anomalies")
    conn.commit()

    for _, row in anomalies.iterrows():
        cur.execute(
            """
            INSERT INTO flagged_anomalies (date, category, description, amount)
            VALUES (%s, %s, %s, %s)
            """,
            (row["date"], row["category"], row["description"], row["amount"])
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Found {len(anomalies)} anomalies out of {len(expenses)} expenses")


if __name__ == "__main__":
    main()
