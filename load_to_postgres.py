import pandas as pd
import psycopg2

df = pd.read_csv("fake_transactions.csv")

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="expense_tracker",
    user="tracker",
    password="tracker_pass"
)
cur = conn.cursor()
cur.execute("TRUNCATE TABLE transactions")

cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        date DATE,
        category VARCHAR(50),
        description VARCHAR(100),
        amount NUMERIC(10,2)
    )
""")
conn.commit()

for _, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO transactions (date, category, description, amount)
        VALUES (%s, %s, %s, %s)
        """,
        (row["date"], row["category"], row["description"], row["amount"])
    )

conn.commit()
cur.close()
conn.close()

print("Done! All rows loaded into Postgres.")