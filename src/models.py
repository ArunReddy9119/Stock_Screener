from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional


class RawPriceData(BaseModel):
    Date: date
    Open: Decimal
    High: Decimal
    Low: Decimal
    Close: Decimal
    Volume: int

    from pydantic import model_validator

    @model_validator(mode="after")
    def check_high_ge_low(self):
        if self.High < self.Low:
            raise ValueError("High must be >= Low")
        return self


class RawFundamentalData(BaseModel):
    Date: date
    TotalAssets: Optional[Decimal] = None
    TotalLiab: Optional[Decimal] = None
    ShareholderEquity: Optional[Decimal] = None
    SharesOutstanding: Optional[int] = None
    MarketCap: Optional[Decimal] = None
    EnterpriseValue: Optional[Decimal] = None


class ProcessedDailyMetrics(BaseModel):
    ticker: str
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    sma_50: Optional[Decimal] = None
    sma_200: Optional[Decimal] = None
    week52_high: Optional[Decimal] = None
    pct_from_52w_high: Optional[Decimal] = None
    book_value_per_share: Optional[Decimal] = None
    price_to_book: Optional[Decimal] = None
    enterprise_value: Optional[Decimal] = None


class SignalEvent(BaseModel):
    ticker: str
    signal_type: str
    date: date
