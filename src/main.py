# src/main.py
import argparse
import logging
import json
from pathlib import Path
from .config import load_config
from .data_fetcher import fetch_stock_data
from .processor import process_data
from .signals import detect_golden_crossover, detect_death_cross
from .database import init_db, save_daily_metrics, save_signal_events
from .models import SignalEvent


def main():
    parser = argparse.ArgumentParser(
        description="Run financial analysis pipeline for a given stock ticker."
    )
    parser.add_argument(
        "--ticker", required=True, help="Stock ticker (e.g., NVDA or RELIANCE.NS)"
    )
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    config = load_config()
    log_level = config.get("logging", {}).get("level", "INFO")
    logging.basicConfig(level=getattr(logging, log_level))
    logger = logging.getLogger(__name__)

    db_path = config.get("database", {}).get("path", "financial_data.db")
    engine = init_db(db_path)

    try:
        logger.info(f"Fetching data for {args.ticker}")
        raw = fetch_stock_data(args.ticker)

        logger.info("Processing data")
        processed = process_data(raw)

        import pandas as pd

        df_signals = pd.DataFrame([p.model_dump() for p in processed])

        logger.info("Detecting signals")
        golden_dates = detect_golden_crossover(df_signals)
        death_dates = detect_death_cross(df_signals)

        signal_events = []
        for d in golden_dates:
            signal_events.append(
                SignalEvent(ticker=args.ticker, signal_type="golden_crossover", date=d)
            )
        for d in death_dates:
            signal_events.append(
                SignalEvent(ticker=args.ticker, signal_type="death_cross", date=d)
            )

        logger.info("Saving to database")
        save_daily_metrics(engine, processed)
        save_signal_events(engine, signal_events)

        output_data = {
            "ticker": args.ticker,
            "daily_metrics": [m.model_dump() for m in processed],
            "signals": [s.model_dump() for s in signal_events],
        }

        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"✅ Analysis complete. Results saved to {args.output}")
        print(f"📈 Golden Crossovers: {len(golden_dates)}")
        print(f"📉 Death Crosses: {len(death_dates)}")

    except Exception as e:
        logger.error(f"Pipeline failed for {args.ticker}: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
