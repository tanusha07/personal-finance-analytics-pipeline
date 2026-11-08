from datetime import date

import generate_data


def test_same_seed_gives_same_data():
    assert generate_data.generate_rows(seed=42) == generate_data.generate_rows(seed=42)


def test_different_seed_gives_different_data():
    assert generate_data.generate_rows(seed=1) != generate_data.generate_rows(seed=2)


def test_default_run_matches_known_row_count():
    # The Airflow pipeline loads exactly this many rows; a change here means the data changed.
    assert len(generate_data.generate_rows()) == 437


def test_signs_match_category():
    for _, category, _, amount in generate_data.generate_rows():
        if category in ("income", "gig_income"):
            assert amount > 0
        else:
            assert amount < 0


def test_rent_only_on_first_of_month():
    rent_days = {r[0][8:10] for r in generate_data.generate_rows() if r[1] == "rent"}
    assert rent_days == {"01"}


def test_dates_stay_in_range_and_sorted():
    rows = generate_data.generate_rows()
    dates = [r[0] for r in rows]
    assert dates == sorted(dates)
    assert dates[0] >= generate_data.START.isoformat()
    assert dates[-1] <= generate_data.END.isoformat()


def test_write_csv_has_header_and_rows(tmp_path):
    rows = generate_data.generate_rows(start=date(2026, 1, 1), end=date(2026, 1, 31))
    out = tmp_path / "t.csv"
    generate_data.write_csv(rows, out)
    lines = out.read_text().splitlines()
    assert lines[0] == "date,category,description,amount"
    assert len(lines) == len(rows) + 1
