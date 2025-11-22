# System Architecture

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     TRADING SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Data Layer   │──────│   Database   │                   │
│  │              │      │  PostgreSQL  │                   │
│  │ - Ingestion  │      └──────────────┘                   │
│  │ - Validation │                                          │
│  │ - Storage    │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                          │
│  │ Analysis     │                                          │
│  │ Layer        │                                          │
│  │              │                                          │
│  │ - Indicators │                                          │
│  │ - Signals    │                                          │
│  │ - Patterns   │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │ Backtest     │      │  Strategy    │                   │
│  │ Engine       │◄─────│  Rules       │                   │
│  │              │      │              │                   │
│  │ - Execution  │      │ - Entry      │                   │
│  │ - P&L calc   │      │ - Exit       │                   │
│  │ - Metrics    │      │ - Position   │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                          │
│  │ Reporting    │                                          │
│  │ Layer        │                                          │
│  │              │                                          │
│  │ - Dashboard  │                                          │
│  │ - Charts     │                                          │
│  │ - Analytics  │                                          │
│  └──────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer

**Purpose**: Acquire, validate, and store market data

**Components**:
- `data_fetcher.py`: Downloads OHLC data from Yahoo Finance
- `data_validator.py`: Checks data quality (gaps, anomalies)
- `data_loader.py`: Loads validated data into database

**Data Flow**:
```
Yahoo Finance API → data_fetcher → data_validator → PostgreSQL
```

**Database Tables Used**:
- `market_data`: Raw OHLC prices

### 2. Analysis Layer

**Purpose**: Calculate technical indicators and generate signals

**Components**:
- `indicators.py`: EMA, RSI, ATR calculations
- `signal_generator.py`: Applies strategy rules to identify setups

**Processing Flow**:
```
market_data → calculate indicators → identify setups → generate signals
```

**Database Tables Used**:
- `market_data` (read)
- `indicators` (write)
- `signals` (write)

### 3. Strategy Layer

**Purpose**: Define trading rules and risk management

**Components**:
- `base_strategy.py`: Abstract strategy interface
- `ema_pullback_strategy.py`: Main trading strategy
- `risk_management.py`: Position sizing, SL/TP calculation

**Key Responsibilities**:
- Entry/exit rule definition
- Position size calculation (1% risk)
- Stop-loss and take-profit placement

### 4. Backtesting Layer

**Purpose**: Simulate historical trades and evaluate performance

**Components**:
- `backtest_engine.py`: Core simulation logic
- `trade_simulator.py`: Handles trade execution simulation
- `performance_metrics.py`: Calculates statistics

**Simulation Process**:
```
1. Load historical data + signals
2. For each signal:
   - Calculate position size
   - Simulate entry (next day open)
   - Track until SL or TP hit
   - Record outcome
3. Calculate aggregate metrics
```

**Database Tables Used**:
- `signals` (read)
- `market_data` (read)
- `backtest_trades` (write)
- `backtest_runs` (write)

### 5. Visualization Layer

**Purpose**: Display data, signals, and performance

**Components**:
- `charts.py`: Price charts with indicators
- `performance_plots.py`: Equity curves, drawdown
- `dashboard.py`: Interactive Streamlit dashboard (future)

## Database Schema

### Core Tables

**market_data**
- Stores raw OHLC price data
- One row per symbol per day
- Unique constraint on (symbol, timeframe, timestamp)

**indicators**
- Stores calculated technical indicators
- Links to market_data via foreign key
- Updated whenever new data arrives

**signals**
- Generated trading signals
- Includes entry, SL, TP, reasoning
- Status tracking (PENDING, EXECUTED, SKIPPED)

**backtest_trades**
- Simulated historical trades
- Complete trade lifecycle (entry to exit)
- P&L calculation and outcome

**backtest_runs**
- Groups trades by backtest execution
- Stores strategy parameters
- Aggregate performance metrics

**live_trades** (future)
- Paper and live trade tracking
- Similar to backtest_trades but for forward testing

## Data Flow Diagrams

### Historical Data Ingestion

```
┌─────────────┐
│ Yahoo       │
│ Finance API │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ data_fetcher│
│ .py         │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ data_       │
│ validator.py│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
│ market_data │
└─────────────┘
```

### Signal Generation

```
┌─────────────┐
│ market_data │
│ (PostgreSQL)│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ indicators  │
│ .py         │
│ (EMA, RSI)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ signal_     │
│ generator.py│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ signals     │
│ (PostgreSQL)│
└─────────────┘
```

### Backtesting

```
┌─────────────┐     ┌─────────────┐
│ signals     │     │ market_data │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
       ┌─────────────────┐
       │ backtest_engine │
       │ .py             │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ trade_simulator │
       │ .py             │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ backtest_trades │
       │ (PostgreSQL)    │
       └─────────────────┘
```

## Key Design Decisions

### 1. Database Choice: PostgreSQL

**Rationale**:
- Production-ready for future scaling
- Excellent time-series data handling
- JSONB support for flexible strategy parameters
- Industry standard for financial applications

**Trade-offs**:
- Requires installation/setup (vs SQLite simplicity)
- Slightly more complex initial configuration
- Worth it for long-term robustness

### 2. Custom Backtesting vs Framework

**Decision**: Build custom backtest engine

**Rationale**:
- Strategy is simple (don't need framework complexity)
- Full understanding of every component
- Easier debugging and customization
- Learning opportunity

**Trade-offs**:
- More initial development time
- Might miss edge cases (mitigated by testing)
- No built-in optimizations (can add later)

### 3. Python Scripts vs Notebooks

**Decision**: Primary development in Python scripts

**Rationale**:
- Better version control
- Production-ready code structure
- Easier testing and CI/CD (future)
- Clear separation of concerns

**Trade-offs**:
- Less interactive exploration
- Notebooks still used for data exploration/analysis

### 4. Data Source: Yahoo Finance

**Decision**: yfinance as primary data source

**Rationale**:
- Completely free
- No API key management
- Sufficient for daily timeframe
- Reliable historical data

**Trade-offs**:
- Not real-time (acceptable for swing trading)
- Might need supplement for XAU/USD spot prices
- No tick-level data (not needed)

## Security Considerations

### Sensitive Data

- Database credentials stored in `.env` (not committed)
- API keys (if used) in environment variables
- No hardcoded passwords or secrets

### Data Validation

- Input validation on all external data
- SQL injection prevention (using ORM)
- Error handling for API failures

### Access Control

- Local development only (initially)
- Database user with minimal required privileges
- Read-only access for reporting/visualization

## Scalability Considerations

### Current Design (MVP)

- Single machine, local execution
- PostgreSQL on localhost
- Manual script execution

### Future Scaling Path

- Move database to cloud (AWS RDS, DigitalOcean)
- Containerize with Docker
- Schedule with cron or Airflow
- API layer for signal access
- Web dashboard deployment

## Performance Considerations

### Data Volume

- 6 months × 3 pairs × ~130 trading days = ~390 rows
- Indicators table similar size
- Signals: ~50-100 total (low volume)
- Backtests: ~50-100 trades per run

**Verdict**: Performance not a concern at this scale

### Query Optimization

- Indexes on (symbol, timestamp) for fast lookups
- Denormalization acceptable for reporting
- Batch inserts for efficiency

### Computation

- Indicator calculation: pandas vectorized operations (fast)
- Backtesting: sequential (acceptable for daily data)
- Can optimize later if needed

## Testing Strategy

### Unit Tests

- Test indicator calculations (EMA, RSI accuracy)
- Test signal generation logic
- Test position sizing calculations
- Test P&L calculations

### Integration Tests

- Test data pipeline (fetch → validate → load)
- Test end-to-end backtest execution
- Test database operations

### Validation Tests

- Compare indicators with TradingView/broker platform
- Validate backtest results manually on sample data
- Cross-check metrics calculations

## Error Handling

### Data Layer

- Handle API failures (retry logic)
- Validate data completeness (no gaps)
- Detect and flag anomalies

### Strategy Layer

- Handle edge cases (insufficient data for indicators)
- Validate signal parameters (SL distance, position size)
- Log all decisions for audit

### Backtest Layer

- Handle missing data gracefully
- Validate trade logic (no impossible fills)
- Catch and report calculation errors

## Logging Strategy

### Log Levels

- **DEBUG**: Detailed calculation steps
- **INFO**: Normal operations (data loaded, signals generated)
- **WARNING**: Anomalies detected, recoverable errors
- **ERROR**: Failures requiring attention

### Log Storage

- Console output during development
- File logging for production
- Separate logs per component

### Key Events to Log

- Data downloads (success/failure)
- Signal generation (with reasoning)
- Trade execution (entry/exit)
- Performance metrics
- Errors and exceptions

## Monitoring (Future)

- Database connection health
- Data freshness (last update time)
- Signal generation success rate
- System uptime
- Performance alerts (drawdown thresholds)

---

**Document Version**: 1.0
**Last Updated**: January 2025
