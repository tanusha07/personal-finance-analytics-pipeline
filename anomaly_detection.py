import pandas as pd
import psycopg2
from sklearn.ensemble import IsolationForest

# Connect to Postgres
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="expense_tracker",
    user="tracker",
    password="tracker_pass"
)

# Pull the cleaned data
df = pd.read_sql("SELECT * FROM cleaned_transactions", conn)

# Only look at expenses (not income) for anomaly detection
expenses = df[df["txn_type"] == "Expense"].copy()
excluded_categories = ["rent", "debt payment"]
expenses = expenses[~expenses["category"].str.lower().isin(excluded_categories)]

# The model needs numbers, so we just use the amount for now
model = IsolationForest(contamination=0.03, random_state=42)
expenses["anomaly_score"] = model.fit_predict(expenses[["amount"]])

# IsolationForest marks normal rows as 1 and anomalies as -1
expenses["is_anomaly"] = expenses["anomaly_score"].apply(lambda x: True if x == -1 else False)

# Save flagged anomalies back to a new table
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

anomalies = expenses[expenses["is_anomaly"]]

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