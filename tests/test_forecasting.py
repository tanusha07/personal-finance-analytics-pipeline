import pandas as pd
import pytest

from forecasting import prepare_daily


def test_prepare_daily_sums_per_day_with_prophet_columns():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "amount": [10.0, 5.0, 7.5],
    })
    daily = prepare_daily(df)
    assert list(daily.columns) == ["ds", "y"]
    assert daily["y"].tolist() == [15.0, 7.5]


def test_forecast_returns_requested_number_of_days():
    pytest.importorskip("prophet")
    from forecasting import build_forecast

    days = pd.date_range("2026-01-01", periods=60)
    df = pd.DataFrame({"date": days, "amount": [20 + (i % 7) for i in range(60)]})
    out = build_forecast(df, periods=30)
    assert len(out) == 30
    assert out["ds"].min() > days.max()
