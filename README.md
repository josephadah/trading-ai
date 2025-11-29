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

**Current Phase**: ✅ Week 2 Complete - Analysis Layer Implemented

**Progress**: 40% Complete (Weeks 1-2 of 8)

**Completed**:
- ✅ Week 1: Foundation & Data Pipeline (Nov 27, 2025)
- ✅ Week 2: Indicators & Signal Generation (Nov 28, 2025)

**Next**: Week 3 - Backtesting Engine

**Development Timeline**:
- ✅ Weeks 1-2: Foundation, data pipeline, indicators, signals
- Weeks 3-4: Build backtesting engine and performance metrics
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

## What's Implemented

### Data Pipeline ✅
- Historical data download from Yahoo Finance
- Data validation and quality checks
- PostgreSQL database storage
- **Status**: 383 records (6 months, 3 pairs) loaded

### Technical Analysis ✅
- EMA (20 & 50 period) calculations
- RSI (14 period) indicator
- ATR (14 period) volatility measure
- Swing high/low detection
- **Status**: 380 indicator records calculated

### Signal Generation ✅
- Complete EMA Pullback Strategy implementation
- LONG and SHORT entry criteria
- Dynamic stop-loss calculation
- Risk/reward validation (2.5:1 minimum)
- **Status**: Fully functional, conservative by design

### Visualization ✅
- Interactive candlestick charts (Plotly)
- EMA overlays and RSI subplots
- Professional HTML exports
- **Status**: 3 interactive charts created

### Database Schema ✅
- 6 tables created and operational
- Proper indexing and relationships
- **Status**: All tables active, 763 total records

## Quick Start

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed installation and setup instructions.

See [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) for complete implementation details.

```bash
# 1. Set up database (one-time)
python scripts/setup_database.py

# 2. Download historical data
python scripts/download_historical.py

# 3. Calculate indicators
python scripts/calculate_indicators.py

# 4. Generate trading signals
python scripts/generate_signals.py

# 5. Create interactive charts
python scripts/create_charts.py

# 6. View charts
# Open files in charts/ directory with your browser

# 7. Run comprehensive test suite
python scripts/run_all_tests.py
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
