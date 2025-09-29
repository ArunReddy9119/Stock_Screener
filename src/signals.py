from typing import List
from datetime import date
import pandas as pd


def detect_golden_crossover(df: pd.DataFrame) -> List[date]:
    if "sma_50" not in df.columns or "sma_200" not in df.columns:
        return []
    df = df.copy()
    df["prev_sma_50"] = df["sma_50"].shift(1)
    df["prev_sma_200"] = df["sma_200"].shift(1)
    crossover = (df["sma_50"] > df["sma_200"]) & (
        df["prev_sma_50"] <= df["prev_sma_200"]
    )
    return df[crossover]["date"].dropna().tolist()


def detect_death_cross(df: pd.DataFrame) -> List[date]:
    if "sma_50" not in df.columns or "sma_200" not in df.columns:
        return []
    df = df.copy()
    df["prev_sma_50"] = df["sma_50"].shift(1)
    df["prev_sma_200"] = df["sma_200"].shift(1)
    cross = (df["sma_50"] < df["sma_200"]) & (df["prev_sma_50"] >= df["prev_sma_200"])
    return df[cross]["date"].dropna().tolist()
