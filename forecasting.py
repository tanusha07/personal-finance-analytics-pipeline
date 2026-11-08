import pandas as pd

from db import get_connection


def prepare_daily(df):
    """Total expense per day, in the ds/y column format Prophet expects."""
    daily = df.groupby("date")["amount"].sum().reset_index()
    return daily.rename(columns={"date": "ds", "amount": "y"})


def build_forecast(df, periods=30):
    """Fit Prophet on daily expense totals and return the next `periods` days (ds, yhat)."""
    from prophet import Prophet  # imported here so the rest of the module works without Prophet

    daily = prepare_daily(df)
    model = Prophet()
    model.fit(daily)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[["ds", "yhat"]].tail(periods)


def main():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM cleaned_transactions WHERE txn_type = 'Expense'", conn)
    next_30 = build_forecast(df, periods=30)

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

    for _, row in next_30.iterrows():
        cur.execute(
            "INSERT INTO spending_forecast (date, predicted_amount) VALUES (%s, %s)",
            (row["ds"].date(), round(row["yhat"], 2))
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Forecast saved for the next 30 days")


if __name__ == "__main__":
    main()
