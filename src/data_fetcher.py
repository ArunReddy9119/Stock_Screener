# src/data_fetcher.py
import yfinance as yf
import pandas as pd
import logging
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List
from .models import RawPriceData, RawFundamentalData

logger = logging.getLogger(__name__)


def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch price and fundamental data for a given ticker.
    Implements fallbacks for missing fundamental data.
    Returns validated raw data.
    """
    yf_ticker = yf.Ticker(ticker)

    # Fetch price data (5y or max for recent IPOs)
    try:
        hist = yf_ticker.history(period="5y")
    except Exception as e:
        logger.error(f"Failed to fetch price data for {ticker}: {e}")
        raise

    if hist.empty:
        raise ValueError(f"No price history returned for {ticker}")

    # yfinance returns a DatetimeIndex with NO name → reset_index() creates column 'index'
    hist = hist.reset_index()  # Now has column named 'index'
    hist.rename(columns={"index": "Date"}, inplace=True)  # Rename to 'Date'

    # Ensure Date is date (not datetime)
    hist["Date"] = pd.to_datetime(hist["Date"]).dt.date

    # Validate and collect price records
    price_records: List[RawPriceData] = []
    for _, row in hist.iterrows():
        try:
            record = RawPriceData(
                Date=row["Date"],
                Open=Decimal(str(row["Open"]))
                if not pd.isna(row["Open"])
                else Decimal("0"),
                High=Decimal(str(row["High"]))
                if not pd.isna(row["High"])
                else Decimal("0"),
                Low=Decimal(str(row["Low"]))
                if not pd.isna(row["Low"])
                else Decimal("0"),
                Close=Decimal(str(row["Close"]))
                if not pd.isna(row["Close"])
                else Decimal("0"),
                Volume=int(row["Volume"]) if not pd.isna(row["Volume"]) else 0,
            )
            price_records.append(record)
        except Exception as e:
            logger.warning(
                f"Skipping invalid price row for {ticker} on {row.get('Date')}: {e}"
            )

    if not price_records:
        raise ValueError(f"No valid price records after validation for {ticker}")

    # Fundamental data strategy
    fundamental_source = "none"
    balance_sheet = None
    info = yf_ticker.info

    try:
        balance_sheet = yf_ticker.quarterly_balance_sheet
        if not balance_sheet.empty:
            fundamental_source = "quarterly"
        else:
            raise ValueError("Quarterly balance sheet empty")
    except Exception:
        try:
            balance_sheet = yf_ticker.balance_sheet
            if not balance_sheet.empty:
                fundamental_source = "annual"
            else:
                raise ValueError("Annual balance sheet empty")
        except Exception:
            logger.warning(f"No balance sheet data for {ticker}. Using info fallback.")
            fundamental_source = "info"

    # Extract fundamental records
    fundamental_records: List[RawFundamentalData] = []
    if fundamental_source in ["quarterly", "annual"]:
        balance_sheet = balance_sheet.T
        balance_sheet.index = pd.to_datetime(balance_sheet.index).date
        for report_date, row in balance_sheet.iterrows():
            rec = RawFundamentalData(
                Date=report_date,
                TotalAssets=Decimal(str(row.get("Total Assets", 0)))
                if pd.notna(row.get("Total Assets"))
                else None,
                TotalLiab=Decimal(str(row.get("Total Liab", 0)))
                if pd.notna(row.get("Total Liab"))
                else None,
                ShareholderEquity=Decimal(str(row.get("Total Stockholder Equity", 0)))
                if pd.notna(row.get("Total Stockholder Equity"))
                else None,
                SharesOutstanding=int(info.get("sharesOutstanding", 0))
                if info.get("sharesOutstanding")
                else None,
                MarketCap=Decimal(str(info.get("marketCap", 0)))
                if info.get("marketCap")
                else None,
                EnterpriseValue=Decimal(str(info.get("enterpriseValue", 0)))
                if info.get("enterpriseValue")
                else None,
            )
            fundamental_records.append(rec)
    else:
        # Fallback: use latest info as of last price date
        last_date = price_records[-1].Date if price_records else datetime.today().date()
        rec = RawFundamentalData(
            Date=last_date,
            SharesOutstanding=int(info.get("sharesOutstanding", 0))
            if info.get("sharesOutstanding")
            else None,
            MarketCap=Decimal(str(info.get("marketCap", 0)))
            if info.get("marketCap")
            else None,
            EnterpriseValue=Decimal(str(info.get("enterpriseValue", 0)))
            if info.get("enterpriseValue")
            else None,
        )
        fundamental_records = [rec]

    logger.info(f"Used {fundamental_source} fundamental data for {ticker}")

    return {
        "ticker": ticker,
        "price_data": price_records,
        "fundamental_data": fundamental_records,
        "fundamental_source": fundamental_source,
    }
