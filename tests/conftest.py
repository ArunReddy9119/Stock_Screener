# tests/conftest.py
import pytest
from datetime import date, timedelta
import pandas as pd


@pytest.fixture
def sample_price_data():
    today = date.today()
    return [
        {
            "Date": today - timedelta(days=3),
            "Open": 150.0,
            "High": 155.0,
            "Low": 149.0,
            "Close": 152.0,
            "Volume": 1000000,
        },
        {
            "Date": today - timedelta(days=2),
            "Open": 152.0,
            "High": 158.0,
            "Low": 151.0,
            "Close": 157.0,
            "Volume": 1200000,
        },
        {
            "Date": today - timedelta(days=1),
            "Open": 157.0,
            "High": 160.0,
            "Low": 156.0,
            "Close": 159.0,
            "Volume": 900000,
        },
        {
            "Date": today,
            "Open": 159.0,
            "High": 162.0,
            "Low": 158.0,
            "Close": 161.0,
            "Volume": 1100000,
        },
    ]


@pytest.fixture
def sample_fundamental_data():
    return [
        {
            "Date": date.today(),
            "ShareholderEquity": 1000000000,
            "SharesOutstanding": 10000000,
            "EnterpriseValue": 1200000000,  # ✅ Added missing field
        }
    ]


@pytest.fixture
def golden_crossover_df():
    dates = pd.date_range(end=date.today(), periods=250)
    # First 249 days: sma_50 < sma_200
    sma_50 = [100 + i * 0.1 for i in range(249)] + [130]  # Jump on last day
    sma_200 = [105 + i * 0.05 for i in range(250)]
    return pd.DataFrame(
        {"date": [d.date() for d in dates], "sma_50": sma_50, "sma_200": sma_200}
    )


@pytest.fixture
def death_cross_df():
    dates = pd.date_range(end=date.today(), periods=250)
    sma_50 = [130 - i * 0.05 for i in range(249)] + [100]  # Drop on last day
    sma_200 = [125 - i * 0.02 for i in range(250)]
    return pd.DataFrame(
        {"date": [d.date() for d in dates], "sma_50": sma_50, "sma_200": sma_200}
    )
