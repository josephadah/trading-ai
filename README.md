# AI-Powered Forex Trading System

A personal trading system that combines AI-driven analysis with human decision-making for forex trading. The system generates trading signals based on technical analysis, which are then manually reviewed and executed.

## Overview

This system is designed for **swing trading** on daily timeframes, focusing on three currency pairs:
- EUR/USD (Euro/US Dollar)
- GBP/USD (British Pound/US Dollar)
- XAU/USD (Gold/US Dollar)

### Key Features

- **Hybrid Trading Approach**: AI generates signals, human executes trades
- **Risk-First Design**: Fixed 1% risk per trade with position sizing
- **Backtesting Engine**: Validate strategies on historical data before live trading
- **Performance Analytics**: Comprehensive metrics and visualizations
- **Paper Trading Support**: Forward test strategies before risking capital

## Project Status

**Current Phase**: Initial Setup and Development

**Development Timeline**:
- Weeks 1-4: Build core system and backtesting engine
- Week 5: Strategy refinement and optimization
- Weeks 6-7: Paper trading setup
- Week 8+: Live paper trading and validation

## Technology Stack

- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **Data Source**: Yahoo Finance (yfinance)
- **Technical Analysis**: pandas-ta
- **Visualization**: Plotly, mplfinance
- **Dashboard**: Streamlit (future)

## Project Structure

```
trading-ai/
├── database/          # Database models and connection
├── ingestion/         # Data fetching and loading
├── analysis/          # Indicators and signal generation
├── strategy/          # Trading strategy implementation
├── backtesting/       # Backtest engine and metrics
├── visualization/     # Charts and dashboards
├── utils/             # Helper functions and constants
├── scripts/           # Automation and utility scripts
├── tests/             # Unit tests
└── data/              # Local data storage
```

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation and setup instructions.

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Download historical data
python scripts/download_historical.py

# Run backtest
python scripts/run_backtest.py
```

## Trading Strategy

The system implements a **Daily EMA Pullback Strategy**:

- **Timeframe**: Daily (1D)
- **Trend Filter**: 20 EMA and 50 EMA
- **Entry**: Pullbacks to 20 EMA with RSI confirmation
- **Risk/Reward**: 2.5:1 minimum
- **Position Sizing**: 1% risk per trade

See [STRATEGY.md](STRATEGY.md) for complete strategy details.

## Development Roadmap

Detailed week-by-week plan in [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)

## Risk Disclaimer

This system is for personal educational use only. Forex trading involves substantial risk of loss. Past performance does not guarantee future results. Only trade with capital you can afford to lose.

## License

Personal use only. Not for commercial distribution.

## Author

Built for personal forex trading validation and learning.

---

**Last Updated**: January 2025
