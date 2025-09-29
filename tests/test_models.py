# tests/test_models.py
import pytest
from decimal import Decimal
from datetime import date
from src.models import RawPriceData


def test_valid_price_data():
    data = RawPriceData(
        Date=date(2023, 1, 1),
        Open=Decimal("100.0"),
        High=Decimal("105.0"),
        Low=Decimal("99.0"),
        Close=Decimal("103.0"),
        Volume=1000000,
    )
    assert data.Close == Decimal("103.0")


def test_invalid_price_high_lt_low():
    with pytest.raises(ValueError, match="High must be >= Low"):
        RawPriceData(
            Date=date(2023, 1, 1),
            Open=Decimal("100.0"),
            High=Decimal("95.0"),  # < Low
            Low=Decimal("99.0"),
            Close=Decimal("97.0"),
            Volume=1000000,
        )


def test_fundamental_data_optional_fields():
    from src.models import RawFundamentalData

    data = RawFundamentalData(Date=date(2023, 1, 1))
    assert data.TotalAssets is None
