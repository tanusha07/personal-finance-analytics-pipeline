"""Regression test for the duplicate-load bug: running the load twice must not double the rows."""
import load_to_postgres


class FakeCursor:
    def __init__(self, log):
        self.log = log

    def execute(self, sql, params=None):
        self.log.append(" ".join(sql.split()))

    def close(self):
        pass


class FakeConn:
    def __init__(self):
        self.log = []

    def cursor(self):
        return FakeCursor(self.log)

    def commit(self):
        pass

    def close(self):
        pass


def run_load(monkeypatch, tmp_path):
    csv_file = tmp_path / "t.csv"
    csv_file.write_text("date,category,description,amount\n2026-01-01,rent,Monthly Rent,-880.0\n")
    conn = FakeConn()
    monkeypatch.setattr(load_to_postgres, "CSV_PATH", str(csv_file))
    monkeypatch.setattr(load_to_postgres, "get_connection", lambda: conn)
    load_to_postgres.main()
    return conn.log


def test_table_is_cleared_before_inserting(monkeypatch, tmp_path):
    log = run_load(monkeypatch, tmp_path)
    truncate = next(i for i, s in enumerate(log) if s.startswith("TRUNCATE TABLE transactions"))
    first_insert = next(i for i, s in enumerate(log) if s.startswith("INSERT INTO transactions"))
    assert truncate < first_insert


def test_table_is_created_before_truncate(monkeypatch, tmp_path):
    # TRUNCATE on a missing table would crash the very first run
    log = run_load(monkeypatch, tmp_path)
    create = next(i for i, s in enumerate(log) if s.startswith("CREATE TABLE IF NOT EXISTS transactions"))
    truncate = next(i for i, s in enumerate(log) if s.startswith("TRUNCATE TABLE transactions"))
    assert create < truncate
