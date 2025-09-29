# tests/test_processor.py
from src.processor import process_data
from decimal import Decimal


def test_process_data_with_valid_inputs(sample_price_data, sample_fundamental_data):
    class MockRecord:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    raw_data = {
        "ticker": "TEST",
        "price_data": [MockRecord(**d) for d in sample_price_data],
        "fundamental_data": [MockRecord(**d) for d in sample_fundamental_data],
        "fundamental_source": "quarterly",
    }

    result = process_data(raw_data)
    assert len(result) == 4
    # Check BVPS = 1000000000 / 10000000 = 100
    # The last row should have book_value_per_share and price_to_book set
    assert result[-1].book_value_per_share == Decimal("100")
    assert result[-1].price_to_book == Decimal("1.61")  # 161 / 100


def test_process_handles_missing_fundamentals(sample_price_data):
    class MockRecord:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    raw_data = {
        "ticker": "TEST",
        "price_data": [MockRecord(**d) for d in sample_price_data],
        "fundamental_data": [],
        "fundamental_source": "none",
    }

    result = process_data(raw_data)
    assert len(result) == 4
    assert result[0].book_value_per_share is None
