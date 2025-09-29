
# Financial Analyzer

A Python-based financial analysis pipeline for processing, analyzing, and generating trading signals from historical price and fundamental data.

---

## Features
- Data ingestion and merging of price and fundamental data
- Calculation of technical indicators (e.g., moving averages)
- Book value and price-to-book ratio computation
- Detection of golden cross and death cross signals
- Modular, test-driven design with Pytest
- CLI interface powered by Typer
- Pydantic models for robust data validation

---

## Features

- **Multi-Market Support**: Handles US stocks (AAPL, MSFT) and international markets (RELIANCE.NS)
- **Robust Data Fetching**: 3-step fallback strategy for unreliable fundamental data
- **Technical Analysis**: 50-day and 200-day SMAs, 52-week high calculations
- **Signal Detection**: Golden cross and death cross detection with edge case handling
- **Database Persistence**: SQLite with idempotent operations and UNIQUE constraints
- **Production Ready**: Comprehensive error handling, logging, and type hints

## Architecture

### Core Modules

- **`models.py`**: Pydantic schemas for data validation
- **`data_fetcher.py`**: API calls with fallback strategy for unreliable data
- **`processor.py`**: Data merging and technical indicator calculations
- **`signals.py`**: Golden cross and death cross detection
- **`database.py`**: SQLite operations with idempotent inserts
- **`main.py`**: CLI interface with Typer

### Design Decisions

#### 1. Forward-Fill Strategy for Fundamentals
**Problem**: Daily price data vs quarterly/annual fundamental data frequency mismatch.

**Solution**: Forward-fill quarterly fundamentals to daily prices using `pd.merge_asof()`.

**Rationale**: 
- Fundamental metrics (book value, enterprise value) are relatively stable
- They don't change daily, so using the most recent available value is reasonable
- This approach ensures every daily price has fundamental context
- Standard practice in financial analysis

#### 2. 3-Step Fallback Strategy for Fundamentals
**Problem**: Unreliable fundamental data from different sources.

**Solution**: Hierarchical fallback:
1. Quarterly balance sheet (highest priority, most recent)
2. Annual balance sheet (fallback for older data)
3. Info dictionary (last resort, single data point)

#### 3. Multi-Market Ticker Handling
**Problem**: Different ticker formats for different markets.

**Solution**: No hardcoded ticker formats - gracefully handle:
- US stocks: `AAPL`, `MSFT`
- Indian stocks: `RELIANCE.NS`
- Recent IPOs with limited history

#### 4. Database Design with Idempotency
**Problem**: Preventing duplicate data and handling re-runs.

**Solution**: 
- UNIQUE constraints on `(ticker, date)` and `(ticker, date, type)`
- SQLite `INSERT OR REPLACE` for idempotent operations
- Proper error handling for constraint violations


## Quick Start


### Prerequisites
- Python 3.9+
- Poetry (recommended) or uv package manager


### Installation

```sh
git clone <repo-url>
cd financial_analyzer
poetry install
```


### Configuration
Copy `config.yaml.example` to `config.yaml` and edit as needed for your data sources and settings.


### Usage
- **Run the CLI:**
  ```sh
  poetry run python src/main.py [OPTIONS]
  ```
  Use `--help` to see available commands and options.


### Output
The analysis generates:
1. **JSON Export**: Structured analysis results with signals and metrics
2. **Database**: SQLite database with daily metrics and signal events
3. **Logs**: Comprehensive logging of the analysis process

Example output structure:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2024-01-15T10:30:00",
  "data_summary": {
    "total_days": 1250,
    "price_range": {
      "start_date": "2019-01-15",
      "end_date": "2024-01-15"
    },
    "signals_detected": {
      "golden_crosses": 3,
      "death_crosses": 2
    }
  },
  "signals": [
    {
      "date": "2023-03-15",
      "type": "golden",
      "sma_50": 150.25,
      "sma_200": 149.80,
      "note": "50-day SMA crossed above 200-day SMA"
    }
  ],
  "latest_metrics": [...]
}
```


## Development
- All code is in the `src/` directory.
- Tests are in the `tests/` directory and use Pytest fixtures.
- Data models use Pydantic v2 for validation.

### Running Tests
```sh
poetry run pytest
```

### Code Quality
```sh
ruff check --fix
ruff format
```


### Project Structure
```
financial_analyzer/
│
├── src/
│   ├── config.py           # Configuration management
│   ├── data_fetcher.py     # Data fetching utilities
│   ├── database.py         # Database interaction
│   ├── main.py             # CLI entry point
│   ├── models.py           # Pydantic data models
│   ├── processor.py        # Data processing logic
│   ├── signals.py          # Signal detection logic
│   └── __init__.py
│
├── tests/                  # Unit and integration tests
│   ├── conftest.py         # Test fixtures
│   ├── test_processor.py   # Processor tests
│   ├── test_signals.py     # Signal detection tests
│   └── ...
│
├── config.yaml             # User configuration
├── config.yaml.example     # Example configuration
├── financial_data.db       # SQLite database (generated)
├── financial_analyzer.log  # Log file (generated)
├── pyproject.toml          # Poetry project file
├── poetry.lock             # Poetry lock file
└── README.md               # Project documentation
```

## Database Schema

### Tables

1. **`tickers`**: Basic ticker information
   - `id` (Primary Key)
   - `ticker` (Unique)
   - `inserted_at`

2. **`daily_metrics`**: All calculated metrics
   - `id` (Primary Key)
   - `ticker`, `date` (Unique constraint)
   - Price data: `open`, `high`, `low`, `close`, `volume`
   - Technical indicators: `sma_50`, `sma_200`, `week52_high`, `pct_from_high`
   - Fundamental ratios: `book_value`, `bvps`, `price_to_book`, `enterprise_value`
   - Metadata: `fund_source`

3. **`signal_events`**: Detected signals
   - `id` (Primary Key)
   - `ticker`, `date`, `type` (Unique constraint)
   - Signal details: `note`

## Error Handling

The system handles various edge cases:

- **Insufficient Data**: Graceful handling of recent IPOs with limited history
- **Missing Fundamentals**: Continues processing with partial data
- **API Failures**: Comprehensive error logging and fallback strategies
- **Data Quality Issues**: Validation with Pydantic models and error reporting

## Production Standards

- ✅ Type hints for all functions
- ✅ Google-style docstrings for all public functions
- ✅ Logging instead of print statements
- ✅ Comprehensive error handling
- ✅ Idempotent database operations
- ✅ UNIQUE constraints to prevent duplicates
- ✅ Forward-fill strategy documentation
- ✅ Multi-market ticker support
- ✅ Edge case handling for signal detection


## License
MIT License

## Authors
- Your Name Here

---
*This project is for educational and research purposes. Not financial advice.*
