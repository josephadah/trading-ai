# Development Roadmap

Detailed week-by-week development plan with 20 hours per week commitment.

## Timeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT TIMELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Weeks 1-4:  Core Development (80 hours)                   │
│              └─ Data, Indicators, Backtesting              │
│                                                             │
│  Week 5:     Refinement & Optimization (20 hours)          │
│              └─ Strategy tuning, Testing                   │
│                                                             │
│  Weeks 6-7:  Paper Trading Setup (20 hours)                │
│              └─ Live data, Notifications, Journal          │
│                                                             │
│  Week 8+:    Forward Testing (ongoing)                     │
│              └─ Paper trading, Validation                  │
│                                                             │
│  Target:     Live trading decision by Month 3              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Week 1: Foundation & Data Pipeline

**Focus**: Get historical data into database

**Hours**: 20 hours

### Day 1-2: Environment Setup (6 hours)

**Tasks**:
- [ ] Install PostgreSQL and create database
- [ ] Set up Python virtual environment
- [ ] Install all dependencies from requirements.txt
- [ ] Create project directory structure
- [ ] Configure VS Code with Python extensions
- [ ] Test database connection

**Deliverables**:
- PostgreSQL running and accessible
- Virtual environment activated
- All packages installed
- `config.py` configured with database credentials

**Verification**:
```bash
python -c "import sqlalchemy; from database.connection import engine; print('Connected:', engine)"
```

### Day 3-4: Database Schema (8 hours)

**Tasks**:
- [ ] Create `database/models.py` with SQLAlchemy models
- [ ] Create `database/connection.py` for DB connection
- [ ] Write `scripts/setup_database.py` to create tables
- [ ] Create database schema (all tables)
- [ ] Write basic CRUD operations for market_data
- [ ] Test inserting and querying data

**Deliverables**:
- All 6 tables created (market_data, indicators, signals, backtest_trades, backtest_runs, live_trades)
- Connection module working
- Can insert/query test data

**Files to Create**:
- `database/__init__.py`
- `database/models.py`
- `database/connection.py`
- `scripts/setup_database.py`

### Day 5-7: Data Ingestion (6 hours)

**Tasks**:
- [ ] Create `ingestion/data_fetcher.py` (yfinance integration)
- [ ] Download 6 months OHLC for EUR/USD
- [ ] Download 6 months OHLC for GBP/USD
- [ ] Download 6 months OHLC for XAU/USD
- [ ] Create `ingestion/data_validator.py` (check for gaps, anomalies)
- [ ] Create `ingestion/data_loader.py` (load into database)
- [ ] Write `scripts/download_historical.py`

**Deliverables**:
- Script that downloads historical data
- Data validation (no gaps, reasonable prices)
- ~390 rows in market_data table (130 days × 3 pairs)

**Files to Create**:
- `ingestion/__init__.py`
- `ingestion/data_fetcher.py`
- `ingestion/data_validator.py`
- `ingestion/data_loader.py`
- `scripts/download_historical.py`

**Verification**:
```sql
SELECT symbol, COUNT(*) as days, MIN(timestamp), MAX(timestamp)
FROM market_data
GROUP BY symbol;
```

### Week 1 Checkpoint

**Status Check**:
- ✓ Database running with all tables
- ✓ 6 months of data for 3 pairs loaded
- ✓ Data validated (no gaps, clean prices)
- ✓ Can query data successfully

---

## Week 2: Indicators & Signal Generation

**Focus**: Calculate technical indicators and identify trade setups

**Hours**: 20 hours

### Day 1-2: Indicator Calculations (7 hours)

**Tasks**:
- [ ] Create `analysis/indicators.py`
- [ ] Implement EMA calculation (20 and 50 period)
- [ ] Implement RSI calculation (14 period)
- [ ] Implement ATR calculation (14 period)
- [ ] Test indicators against known values (TradingView)
- [ ] Create function to calculate all indicators for a dataset
- [ ] Store indicators in indicators table

**Deliverables**:
- Indicator functions working correctly
- Indicators calculated for all historical data
- Indicators table populated

**Files to Create**:
- `analysis/__init__.py`
- `analysis/indicators.py`

**Verification**:
```python
# Compare with TradingView for EUR/USD on specific date
# EMA(20), EMA(50), RSI(14) should match
```

### Day 3-5: Signal Generation Logic (8 hours)

**Tasks**:
- [ ] Create `analysis/signal_generator.py`
- [ ] Implement swing high/low detection
- [ ] Implement LONG entry criteria check
- [ ] Implement SHORT entry criteria check
- [ ] Calculate SL and TP for each signal
- [ ] Generate signals for historical data
- [ ] Store signals in signals table
- [ ] Add reasoning/notes for each signal

**Deliverables**:
- Signal generation logic complete
- Can identify valid setups in historical data
- Signals stored with entry, SL, TP prices

**Files to Create**:
- `analysis/signal_generator.py`

**Expected Results**:
- ~30-60 signals across 6 months for 3 pairs
- Each signal has complete trade parameters

### Day 6-7: Visualization (5 hours)

**Tasks**:
- [ ] Create `visualization/charts.py`
- [ ] Implement candlestick chart with indicators
- [ ] Mark signals on charts (arrows for entries)
- [ ] Create function to plot specific pair/date range
- [ ] Manually verify 5-10 signals look correct
- [ ] Screenshot and document sample signals

**Deliverables**:
- Can visualize price + indicators + signals
- Visual confirmation signals are sensible

**Files to Create**:
- `visualization/__init__.py`
- `visualization/charts.py`

### Week 2 Checkpoint

**Status Check**:
- ✓ Indicators calculated correctly
- ✓ Signal generation working
- ✓ 30-60 historical signals identified
- ✓ Visual verification passed

---

## Week 3: Backtesting Engine

**Focus**: Simulate trades and calculate performance

**Hours**: 20 hours

### Day 1-3: Core Backtest Logic (10 hours)

**Tasks**:
- [ ] Create `backtesting/backtest_engine.py`
- [ ] Implement trade entry simulation (next day open)
- [ ] Implement SL/TP exit logic (check daily high/low)
- [ ] Handle realistic fills (account for spread)
- [ ] Track open positions
- [ ] Close positions when SL or TP hit
- [ ] Test on single signal first, then batch

**Deliverables**:
- Backtest engine can simulate trades
- Handles multiple concurrent positions
- Exits executed correctly

**Files to Create**:
- `backtesting/__init__.py`
- `backtesting/backtest_engine.py`
- `backtesting/trade_simulator.py`

**Logic Flow**:
```
1. Load all signals
2. For each signal:
   a. Get entry price (next day open + spread)
   b. Calculate position size
   c. Walk through subsequent days
   d. Check if SL hit (day low <= SL)
   e. Check if TP hit (day high >= TP)
   f. Exit when either triggers
   g. Calculate P&L
3. Store all trades in backtest_trades
```

### Day 4-5: Position Sizing & P&L (6 hours)

**Tasks**:
- [ ] Create `strategy/risk_management.py`
- [ ] Implement position size calculator
- [ ] Calculate pip value for each pair
- [ ] Calculate P&L in both pips and dollars
- [ ] Handle edge cases (SL too wide, position too small)
- [ ] Test position sizing with different account sizes

**Deliverables**:
- Position sizing accurate
- P&L calculations verified
- All trades have correct lot size

**Files to Create**:
- `strategy/__init__.py`
- `strategy/risk_management.py`
- `strategy/base_strategy.py`

### Day 6-7: Testing & Debugging (4 hours)

**Tasks**:
- [ ] Run full backtest on 6 months data
- [ ] Debug any issues (incorrect fills, missing exits)
- [ ] Validate sample trades manually
- [ ] Check for look-ahead bias
- [ ] Verify spread costs applied correctly
- [ ] Document backtest assumptions

**Deliverables**:
- Backtest runs successfully
- All trades in backtest_trades table
- Manual verification passed

**Create**:
- `scripts/run_backtest.py`

### Week 3 Checkpoint

**Status Check**:
- ✓ Backtest engine working
- ✓ All historical signals simulated
- ✓ Trades stored in database
- ✓ P&L calculated correctly

---

## Week 4: Analytics & Reporting

**Focus**: Calculate metrics and visualize performance

**Hours**: 20 hours

### Day 1-2: Performance Metrics (6 hours)

**Tasks**:
- [ ] Create `backtesting/performance_metrics.py`
- [ ] Calculate win rate
- [ ] Calculate profit factor
- [ ] Calculate maximum drawdown
- [ ] Calculate expectancy
- [ ] Calculate average win/loss
- [ ] Calculate consecutive wins/losses
- [ ] Generate performance summary

**Deliverables**:
- Complete metrics calculated
- Performance summary report
- Metrics stored in backtest_runs table

**Files to Create**:
- `backtesting/performance_metrics.py`

**Key Metrics**:
```
- Total Trades
- Win Rate (%)
- Profit Factor
- Max Drawdown (%)
- Expectancy ($/trade)
- Avg Win / Avg Loss
- Largest Win / Largest Loss
- Risk/Reward Ratio
```

### Day 3-4: Performance Visualization (7 hours)

**Tasks**:
- [ ] Create `visualization/performance_plots.py`
- [ ] Create equity curve chart
- [ ] Create drawdown chart
- [ ] Create monthly P&L breakdown
- [ ] Create win/loss distribution
- [ ] Create per-pair performance comparison
- [ ] Generate PDF report (optional)

**Deliverables**:
- All performance charts
- Visual analysis of backtest results

**Files to Create**:
- `visualization/performance_plots.py`

### Day 5-7: Dashboard & Documentation (7 hours)

**Tasks**:
- [ ] Create `visualization/dashboard.py` (Streamlit)
- [ ] Dashboard: Overview page (key metrics)
- [ ] Dashboard: Trade log (table of all trades)
- [ ] Dashboard: Charts page (equity, drawdown)
- [ ] Dashboard: Signal explorer (view signals on price charts)
- [ ] Write user guide for running backtests
- [ ] Document findings and observations

**Deliverables**:
- Working Streamlit dashboard
- Can explore all backtest results
- User documentation complete

**Files to Create**:
- `visualization/dashboard.py`
- `docs/USER_GUIDE.md`

### Week 4 Checkpoint

**Status Check**:
- ✓ All metrics calculated
- ✓ Performance charts created
- ✓ Dashboard functional
- ✓ Can analyze backtest thoroughly

**Decision Point**: Is strategy viable? (Win rate, profit factor, drawdown acceptable?)

---

## Week 5: Refinement & Optimization

**Focus**: Improve strategy based on backtest results

**Hours**: 20 hours

### Day 1-3: Results Analysis (10 hours)

**Tasks**:
- [ ] Analyze per-pair performance
  - Which pair performs best?
  - Which has most signals?
  - Which has best win rate?
- [ ] Identify losing patterns
  - What do losing trades have in common?
  - Time of day? Market conditions?
- [ ] Review winning patterns
  - What makes winners successful?
  - Any additional filters needed?
- [ ] Test parameter variations
  - Different EMA periods (10/30, 20/50, 50/200)
  - Different RSI thresholds
  - Different R/R ratios (2:1, 2.5:1, 3:1)
- [ ] Document findings in notebook

**Deliverables**:
- Performance analysis report
- Identified improvements
- Parameter test results

**Create**:
- Analysis notebook or report

### Day 4-5: Strategy Improvements (6 hours)

**Tasks**:
- [ ] Implement best parameter changes
- [ ] Add filters if needed (trend strength, volatility)
- [ ] Update signal generation logic
- [ ] Re-run backtest with improvements
- [ ] Compare before/after results
- [ ] Choose final strategy version

**Deliverables**:
- Optimized strategy parameters
- Improved backtest results
- Final strategy documented

### Day 6-7: Testing & Validation (4 hours)

**Tasks**:
- [ ] Write unit tests for indicators
- [ ] Write unit tests for signal generation
- [ ] Write unit tests for position sizing
- [ ] Write unit tests for P&L calculations
- [ ] Code cleanup and documentation
- [ ] Final backtest run

**Deliverables**:
- Test suite passing
- Clean, documented code
- Production-ready backtest system

**Files to Create**:
- `tests/test_indicators.py`
- `tests/test_strategy.py`
- `tests/test_backtest.py`

### Week 5 Checkpoint

**Status Check**:
- ✓ Strategy optimized
- ✓ Tests written and passing
- ✓ Code clean and documented
- ✓ Ready for forward testing

---

## Week 6-7: Paper Trading Setup

**Focus**: Prepare for real-time forward testing

**Hours**: 20 hours total (10 per week)

### Week 6: Real-Time Data & Signals (10 hours)

**Tasks**:
- [ ] Create daily data update script
- [ ] Set up scheduled task (Windows Task Scheduler)
- [ ] Create real-time signal checker
- [ ] Build paper trading module
- [ ] Set up Telegram bot for notifications
- [ ] Test end-to-end flow

**Deliverables**:
- Daily data updates automated
- Signal notifications working
- Paper trading ready

**Files to Create**:
- `scripts/update_daily_data.py`
- `scripts/check_signals.py`
- `scripts/send_notification.py`

### Week 7: Trade Journal & Execution (10 hours)

**Tasks**:
- [ ] Create trade execution interface
- [ ] Build trade journal template (spreadsheet or DB)
- [ ] Set up manual trade entry process
- [ ] Create daily routine checklist
- [ ] Practice with demo account
- [ ] Begin paper trading

**Deliverables**:
- Trade journal ready
- Execution process defined
- First paper trades logged

**Files to Create**:
- `scripts/log_trade.py`
- `templates/trade_journal.xlsx`

### Weeks 6-7 Checkpoint

**Status Check**:
- ✓ Real-time data updating
- ✓ Signals generated daily
- ✓ Notifications working
- ✓ Paper trading active

---

## Week 8+: Forward Testing & Iteration

**Focus**: Validate strategy in real market conditions

**Hours**: 5-10 hours per week (ongoing)

### Daily Tasks (30-60 min)

**Morning/Afternoon Routine**:
- [ ] Check open positions
- [ ] Review new signals from system
- [ ] Validate signals manually
- [ ] Execute paper trades if valid
- [ ] Update trade journal
- [ ] Review market conditions

### Weekly Tasks (2-3 hours)

**Weekly Review**:
- [ ] Analyze week's performance
- [ ] Compare to backtest expectations
- [ ] Update strategy notes
- [ ] Adjust if needed
- [ ] Review charts and patterns

### Monthly Tasks (4-5 hours)

**Monthly Analysis**:
- [ ] Full performance review
- [ ] Calculate all metrics
- [ ] Compare forward test vs backtest
- [ ] Decision: Continue, adjust, or go live
- [ ] Update strategy documentation

### Paper Trading Targets

**Minimum Requirements Before Live Trading**:
- ✓ 30+ days of forward testing
- ✓ 10-15 paper trades executed
- ✓ Results within ±25% of backtest expectations
- ✓ Comfortable with execution process
- ✓ Following rules consistently
- ✓ Positive expectancy maintained

---

## Milestones & Decision Points

### Milestone 1: End of Week 4
**Goal**: Backtest complete and analyzed

**Decision**: Is strategy profitable in backtest?
- **YES**: Proceed to optimization (Week 5)
- **NO**: Revise strategy or test alternative approach

### Milestone 2: End of Week 5
**Goal**: Optimized strategy validated

**Decision**: Ready for forward testing?
- **YES**: Proceed to paper trading setup (Weeks 6-7)
- **NO**: Further refinement needed

### Milestone 3: End of Month 2
**Goal**: 4 weeks of paper trading complete

**Decision**: Results match backtest?
- **YES**: Continue paper trading
- **NO**: Investigate discrepancies, adjust strategy

### Milestone 4: End of Month 3
**Goal**: 8-12 weeks of paper trading complete

**Decision**: Go live with real money?
- **YES**: Start with minimal position sizes
- **NO**: Continue paper trading or revise strategy

---

## Risk Management Throughout Development

### Week 1-5: Development Phase
- No money at risk
- Focus on learning and building
- Take time to understand each component

### Week 6-7: Setup Phase
- Still no money at risk
- Practice execution process
- Get comfortable with tools

### Week 8+: Paper Trading
- **Still no money at risk**
- Prove the strategy works forward
- Build confidence and discipline

### Month 4+: Live Trading (if validated)
- **Minimal capital at risk**
- Start small (1-2 trades max)
- Scale only if consistent

---

## Tools & Resources Needed by Week

### Week 1
- PostgreSQL installed
- Python environment
- VS Code configured
- yfinance library

### Week 2
- pandas-ta for indicators
- plotly for charts
- Jupyter (optional, for exploration)

### Week 3
- Backtesting logic complete
- No new tools needed

### Week 4
- Streamlit for dashboard
- Reporting libraries

### Week 5
- pytest for testing
- Code quality tools (black, flake8)

### Week 6-7
- Telegram bot (python-telegram-bot)
- Windows Task Scheduler
- Demo trading account

### Week 8+
- Trading journal (Excel/DB)
- Market calendar (for news awareness)
- Ongoing discipline

---

## Success Criteria

### Technical Success
- [ ] All code working without errors
- [ ] Tests passing
- [ ] Database operational
- [ ] Backtests reproducible

### Strategic Success
- [ ] Positive expectancy in backtest
- [ ] Acceptable drawdown (<20%)
- [ ] Profitable in forward test
- [ ] Matches expectations

### Operational Success
- [ ] Process fits in 2-3 hour window
- [ ] Can execute trades smoothly
- [ ] Following rules consistently
- [ ] Comfortable with system

### Personal Success
- [ ] Learned valuable skills
- [ ] Understand forex trading better
- [ ] Built working system
- [ ] Made informed decision (trade or not)

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Timeline**: 8-12 weeks to live trading decision
