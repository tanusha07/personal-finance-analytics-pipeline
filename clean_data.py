import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="expense_tracker",
    user="tracker",
    password="tracker_pass"
)

df = pd.read_sql("SELECT * FROM transactions", conn)

df["description"] = df["description"].str.strip().str.title()
df["category"] = df["category"].str.strip().str.title()

df["txn_type"] = df["amount"].apply(lambda x: "Income" if x > 0 else "Expense")

df["amount"] = df["amount"].abs()

cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS cleaned_transactions (
        id SERIAL PRIMARY KEY,
        date DATE,
        category VARCHAR(50),
        description VARCHAR(100),
        amount NUMERIC(10,2),
        txn_type VARCHAR(10)
    )
""")
conn.commit()

cur.execute("TRUNCATE TABLE cleaned_transactions")
conn.commit()

for _, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO cleaned_transactions (date, category, description, amount, txn_type)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (row["date"], row["category"], row["description"], row["amount"], row["txn_type"])
    )

conn.commit()
cur.close()
conn.close()

print("Done! Cleaned data loaded into cleaned_transactions table.")