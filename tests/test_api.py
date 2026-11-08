from fastapi.testclient import TestClient

import api

client = TestClient(api.app)


def fake_query(rows):
    captured = {}

    def run(sql):
        captured["sql"] = sql
        return rows

    return run, captured


def test_home(monkeypatch):
    r = client.get("/")
    assert r.status_code == 200
    assert "running" in r.json()["message"]


def test_summary_returns_rows(monkeypatch):
    run, _ = fake_query([{"txn_type": "Expense", "num_transactions": 2, "total_amount": 10.0}])
    monkeypatch.setattr(api, "run_query", run)
    r = client.get("/summary")
    assert r.status_code == 200
    assert r.json()[0]["txn_type"] == "Expense"


def test_transactions_applies_limit(monkeypatch):
    run, captured = fake_query([])
    monkeypatch.setattr(api, "run_query", run)
    client.get("/transactions?limit=5")
    assert "LIMIT 5" in captured["sql"]


def test_transactions_rejects_non_integer_limit(monkeypatch):
    run, _ = fake_query([])
    monkeypatch.setattr(api, "run_query", run)
    # blocks SQL injection through the limit parameter
    assert client.get("/transactions?limit=1;DROP TABLE x").status_code == 422


def test_anomalies_and_forecast_endpoints(monkeypatch):
    run, captured = fake_query([])
    monkeypatch.setattr(api, "run_query", run)
    assert client.get("/anomalies").status_code == 200
    assert "flagged_anomalies" in captured["sql"]
    assert client.get("/forecast").status_code == 200
    assert "spending_forecast" in captured["sql"]


def test_kpis_endpoint(monkeypatch):
    run, captured = fake_query([{"total_income": 100.0, "total_expenses": 40.0}])
    monkeypatch.setattr(api, "run_query", run)
    r = client.get("/kpis")
    assert r.status_code == 200
    assert r.json()[0]["total_income"] == 100.0
    for table in ("cleaned_transactions", "flagged_anomalies", "spending_forecast"):
        assert table in captured["sql"]
