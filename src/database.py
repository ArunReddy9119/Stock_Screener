from sqlalchemy import create_engine, Column, String, Date, Numeric, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.sqlite import insert
import pandas as pd
from typing import List
from .models import ProcessedDailyMetrics, SignalEvent

Base = declarative_base()

class DailyMetricsTable(Base):
    __tablename__ = 'daily_metrics'
    ticker = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Integer)
    sma_50 = Column(Numeric)
    sma_200 = Column(Numeric)
    week52_high = Column(Numeric)
    pct_from_52w_high = Column(Numeric)
    book_value_per_share = Column(Numeric)
    price_to_book = Column(Numeric)
    enterprise_value = Column(Numeric)

class SignalEventsTable(Base):
    __tablename__ = 'signal_events'
    ticker = Column(String, primary_key=True)
    date = Column(Date, primary_key=True)
    signal_type = Column(String)

def init_db(db_path: str):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine

def save_daily_metrics(engine, metrics: List[ProcessedDailyMetrics]):
    df = pd.DataFrame([m.model_dump() for m in metrics])
    df.to_sql('daily_metrics', engine, if_exists='append', index=False, method=upsert_metrics)

def upsert_metrics(table, conn, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=['ticker', 'date'])
    conn.execute(stmt)

def save_signal_events(engine, events: List[SignalEvent]):
    df = pd.DataFrame([e.model_dump() for e in events])
    df.to_sql('signal_events', engine, if_exists='append', index=False, method=upsert_signals)

def upsert_signals(table, conn, keys, data_iter):
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data)
    stmt = stmt.on_conflict_do_nothing(index_elements=['ticker', 'date'])
    conn.execute(stmt)