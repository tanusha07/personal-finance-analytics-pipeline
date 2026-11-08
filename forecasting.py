import pandas as pd
import psycopg2
from prophet import Prophet

# Connect to Postgres
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="expense_tracker",
    user="tracker",
    password="tracker_pass"
)

# Pull cleaned data, only expenses
df = pd.read_sql("SELECT * FROM cleaned_transactions WHERE txn_type = 'Expense'", conn)

# Group spending by day, since Prophet wants one total per date
daily = df.groupby("date")["amount"].sum().reset_index()

# Prophet requires specific column names: ds (date) and y (value)
daily = daily.rename(columns={"date": "ds", "amount": "y"})

# Build and train the forecasting model
model = Prophet()
model.fit(daily)

# Ask it to predict 30 days into the future
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Save the forecast results to a new table
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS spending_forecast (
        id SERIAL PRIMARY KEY,
        date DATE,
        predicted_amount NUMERIC(10,2)
    )
""")
cur.execute("TRUNCATE TABLE spending_forecast")
conn.commit()

for _, row in forecast[["ds", "yhat"]].tail(30).iterrows():
    cur.execute(
        "INSERT INTO spending_forecast (date, predicted_amount) VALUES (%s, %s)",
        (row["ds"].date(), round(row["yhat"], 2))
    )

conn.commit()
cur.close()
conn.close()

print("Forecast saved for the next 30 days")