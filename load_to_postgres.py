import os

import pandas as pd

from db import get_connection

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_transactions.csv")


def main():
    df = pd.read_csv(CSV_PATH)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            date DATE,
            category VARCHAR(50),
            description VARCHAR(100),
            amount NUMERIC(10,2)
        )
    """)
    # Idempotent load: clear old rows first so re-running never creates duplicates
    cur.execute("TRUNCATE TABLE transactions")
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


if __name__ == "__main__":
    main()
