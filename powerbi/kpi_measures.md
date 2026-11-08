# KPI Dashboard - Power BI setup

Tables used (Import mode, from the `expense_tracker` PostgreSQL database):
`cleaned_transactions`, `flagged_anomalies`, `spending_forecast`.

## 1. Measures (DAX)

In Power BI: right-click the `cleaned_transactions` table in the Data pane -> **New measure**, then paste one measure at a time.

```DAX
Total Income =
CALCULATE ( SUM ( cleaned_transactions[amount] ), cleaned_transactions[txn_type] = "Income" )
```

```DAX
Total Expenses =
CALCULATE ( SUM ( cleaned_transactions[amount] ), cleaned_transactions[txn_type] = "Expense" )
```

```DAX
Net Savings = [Total Income] - [Total Expenses]
```

```DAX
Savings Rate = DIVIDE ( [Net Savings], [Total Income] )
```

```DAX
Avg Daily Spend =
DIVIDE (
    [Total Expenses],
    DATEDIFF ( MIN ( cleaned_transactions[date] ), MAX ( cleaned_transactions[date] ), DAY ) + 1
)
```

```DAX
Top Spending Category =
VAR ByCategory =
    ADDCOLUMNS (
        VALUES ( cleaned_transactions[category] ),
        "@spend", [Total Expenses]
    )
VAR Top1 = TOPN ( 1, ByCategory, [@spend], DESC )
RETURN MAXX ( Top1, cleaned_transactions[category] )
```

```DAX
Anomalies Flagged = COUNTROWS ( flagged_anomalies )
```

```DAX
Forecast Next 30 Days = SUM ( spending_forecast[predicted_amount] )
```

Format: set **Savings Rate** to Percentage; the money measures to Currency ($).

## 2. Build the page

1. Add a new page and rename it `KPI Dashboard`.
2. Insert a **Card** visual for each of: Total Income, Total Expenses, Net Savings, Savings Rate, Avg Daily Spend, Top Spending Category, Anomalies Flagged, Forecast Next 30 Days. Put them in two rows of four.
3. Under the cards, add a **Clustered bar chart**: Axis = `category`, Values = `Total Expenses` (spend by category).
4. Add a **Line chart**: Axis = `date`, Values = `Total Expenses` (daily spend trend). Use the plain `date`, not the date hierarchy.
5. Click **Refresh**, then save (Ctrl+S).

## 3. Numbers to expect (seed 42 data, 437 rows)

| KPI | Expected |
|---|---|
| Total Income | $29,772.35 |
| Total Expenses | $16,369.24 |
| Net Savings | $13,403.11 |
| Savings Rate | 45.0% |
| Avg Daily Spend | about $54.20 |
| Top Spending Category | Rent ($8,711.03) |

The same numbers are available from the API at `GET /kpis`, which makes a handy cross-check.
