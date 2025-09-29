# src/processor.py
import pandas as pd
from decimal import Decimal
from typing import List
from .models import ProcessedDailyMetrics

def process_data(raw_data: dict) -> List[ProcessedDailyMetrics]:
    ticker = raw_data["ticker"]
    
    # Convert price data to DataFrame
    price_records = raw_data["price_data"]
    price_df = pd.DataFrame([{
        "Date": r.Date,
        "Open": float(r.Open),
        "High": float(r.High),
        "Low": float(r.Low),
        "Close": float(r.Close),
        "Volume": r.Volume
    } for r in price_records])
    price_df["Date"] = pd.to_datetime(price_df["Date"])

    # Handle fundamentals
    fund_records = raw_data["fundamental_data"]
    if fund_records:
        fund_df = pd.DataFrame([{
            "Date": r.Date,
            "ShareholderEquity": float(r.ShareholderEquity) if r.ShareholderEquity is not None else None,
            "SharesOutstanding": r.SharesOutstanding,
            "EnterpriseValue": float(r.EnterpriseValue) if r.EnterpriseValue is not None else None
        } for r in fund_records])
        fund_df["Date"] = pd.to_datetime(fund_df["Date"])
        fund_df = fund_df.sort_values("Date").set_index("Date")
        daily_fund = fund_df.reindex(price_df["Date"], method="ffill").infer_objects().reset_index()
    else:
        daily_fund = pd.DataFrame({"Date": price_df["Date"]})

    # Merge
    df = pd.merge(price_df, daily_fund, on="Date", how="left")

    # Compute technical indicators (using float)
    df["sma_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["sma_200"] = df["Close"].rolling(window=200, min_periods=1).mean()
    df["week52_high"] = df["Close"].rolling(window=252, min_periods=1).max()
    df["pct_from_52w_high"] = (
        (df["Close"] - df["week52_high"]) / df["week52_high"] * 100
    )

    # Build final records with Decimal
    results = []
    for _, row in df.iterrows():
        try:
            # Reconstruct Decimals from float (safe for JSON/DB)
            close = Decimal(str(row["Close"])) if pd.notna(row["Close"]) else None
            week52_high = Decimal(str(row["week52_high"])) if pd.notna(row["week52_high"]) else None
            pct = Decimal(str(row["pct_from_52w_high"])) if pd.notna(row["pct_from_52w_high"]) else None

            # Fundamental ratios
            book_value_per_share = None
            price_to_book = None
            if pd.notna(row.get("ShareholderEquity")) and pd.notna(row.get("SharesOutstanding")) and row["SharesOutstanding"]:
                try:
                    bvps = row["ShareholderEquity"] / row["SharesOutstanding"]
                    book_value_per_share = Decimal(str(bvps))
                    if book_value_per_share and book_value_per_share > 0 and close:
                        price_to_book = close / book_value_per_share
                except (ZeroDivisionError, TypeError):
                    pass

            item = ProcessedDailyMetrics(
                ticker=ticker,
                date=row["Date"].date(),
                open=Decimal(str(row["Open"])) if pd.notna(row["Open"]) else Decimal('0'),
                high=Decimal(str(row["High"])) if pd.notna(row["High"]) else Decimal('0'),
                low=Decimal(str(row["Low"])) if pd.notna(row["Low"]) else Decimal('0'),
                close=close or Decimal('0'),
                volume=int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
                sma_50=Decimal(str(row["sma_50"])) if pd.notna(row["sma_50"]) else None,
                sma_200=Decimal(str(row["sma_200"])) if pd.notna(row["sma_200"]) else None,
                week52_high=week52_high,
                pct_from_52w_high=pct,
                book_value_per_share=book_value_per_share,
                price_to_book=price_to_book,
                enterprise_value=Decimal(str(row["EnterpriseValue"])) if pd.notna(row.get("EnterpriseValue")) else None
            )
            results.append(item)
        except Exception as e:
            continue  # skip bad rows

    return results