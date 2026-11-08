import pandas as pd

from clean_data import clean_transactions


def sample():
    return pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "category": ["  rent ", "gig_income", "groceries"],
        "description": ["  monthly rent", "UBER driver payout", "aldi"],
        "amount": [-880.5, 64.49, -20.0],
    })


def test_income_and_expense_labels():
    out = clean_transactions(sample())
    assert list(out["txn_type"]) == ["Expense", "Income", "Expense"]


def test_amounts_become_positive():
    out = clean_transactions(sample())
    assert (out["amount"] > 0).all()
    assert out["amount"].tolist() == [880.5, 64.49, 20.0]


def test_text_is_trimmed_and_title_cased():
    out = clean_transactions(sample())
    assert out["category"].tolist() == ["Rent", "Gig_Income", "Groceries"]
    assert out["description"].tolist() == ["Monthly Rent", "Uber Driver Payout", "Aldi"]


def test_input_frame_is_not_modified():
    df = sample()
    clean_transactions(df)
    assert df["amount"].tolist() == [-880.5, 64.49, -20.0]
