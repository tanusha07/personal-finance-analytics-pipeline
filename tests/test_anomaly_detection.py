import pandas as pd

from anomaly_detection import detect_anomalies


def build_frame():
    normal = [{"date": f"2026-01-{d:02d}", "category": "Groceries", "description": "Aldi",
               "amount": 30.0 + (d % 5), "txn_type": "Expense"} for d in range(1, 29)]
    outlier = {"date": "2026-02-01", "category": "Groceries", "description": "Big Shop",
               "amount": 900.0, "txn_type": "Expense"}
    rent = {"date": "2026-02-01", "category": "Rent", "description": "Monthly Rent",
            "amount": 880.0, "txn_type": "Expense"}
    income = {"date": "2026-02-02", "category": "Income", "description": "Payroll",
              "amount": 5000.0, "txn_type": "Income"}
    return pd.DataFrame(normal + [outlier, rent, income])


def test_obvious_outlier_is_flagged():
    _, anomalies = detect_anomalies(build_frame(), contamination=0.05)
    assert 900.0 in anomalies["amount"].tolist()


def test_income_is_never_analysed():
    expenses, _ = detect_anomalies(build_frame())
    assert (expenses["txn_type"] == "Expense").all()


def test_rent_is_excluded():
    expenses, anomalies = detect_anomalies(build_frame())
    assert "Rent" not in expenses["category"].tolist()
    assert "Rent" not in anomalies["category"].tolist()


def test_results_are_repeatable():
    a = detect_anomalies(build_frame())[1]
    b = detect_anomalies(build_frame())[1]
    assert a["amount"].tolist() == b["amount"].tolist()
