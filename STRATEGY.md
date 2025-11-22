# Trading Strategy Documentation

## Strategy Overview

**Name**: Daily EMA Pullback Strategy

**Type**: Trend-Following Swing Trading

**Timeframe**: Daily (1D)

**Pairs**: EUR/USD, GBP/USD, XAU/USD

**Risk per Trade**: 1% of capital

**Target Risk/Reward**: 2.5:1 minimum

## Strategy Philosophy

This is a hybrid system where:
- **AI/System**: Identifies setups, generates signals
- **Human**: Reviews signals, executes trades

**Core Principle**: Trade with the trend, buy pullbacks in uptrends, sell rallies in downtrends.

## Complete Strategy Rules

### Entry Criteria (LONG Position)

ALL conditions must be met:

**1. Trend Qualification**
```
✓ Price > 20 EMA
✓ Price > 50 EMA
✓ 20 EMA > 50 EMA (EMAs aligned)
```

**2. Pullback Identification**
```
✓ Price pulled back to touch or approach 20 EMA
✓ Price stayed above 50 EMA (didn't break trend)
✓ Recent candle low touched 20 EMA (±10 pips tolerance)
```

**3. Momentum Confirmation**
```
✓ RSI(14) between 40-60 (not extreme)
✓ Previous candle closed BULLISH (up)
```

**4. Entry Trigger**
```
✓ Current candle closes above 20 EMA
✓ Current close > previous close (higher)
✓ Bullish candle formation
```

**5. Risk Management Check**
```
✓ Clear swing low within last 10 candles
✓ Stop-loss distance between 30-60 pips
✓ Position size calculation feasible
```

### Entry Criteria (SHORT Position)

Inverse of LONG criteria:

**1. Trend Qualification**
```
✓ Price < 20 EMA
✓ Price < 50 EMA
✓ 20 EMA < 50 EMA
```

**2. Pullback Identification**
```
✓ Price rallied to touch 20 EMA
✓ Price stayed below 50 EMA
✓ Recent candle high touched 20 EMA (±10 pips tolerance)
```

**3. Momentum Confirmation**
```
✓ RSI(14) between 40-60
✓ Previous candle closed BEARISH (down)
```

**4. Entry Trigger**
```
✓ Current candle closes below 20 EMA
✓ Current close < previous close (lower)
✓ Bearish candle formation
```

**5. Risk Management Check**
```
✓ Clear swing high within last 10 candles
✓ Stop-loss distance between 30-60 pips
✓ Position size calculation feasible
```

## Exit Rules

### Stop-Loss Placement

**For LONG positions:**
```
Stop-Loss = Recent Swing Low - Buffer

Where:
- Recent Swing Low = Lowest low in last 5-10 candles
- Buffer = 5-10 pips below swing low (accounts for spread/slippage)
- Maximum SL distance = 60 pips
- Minimum SL distance = 30 pips
```

**For SHORT positions:**
```
Stop-Loss = Recent Swing High + Buffer

Where:
- Recent Swing High = Highest high in last 5-10 candles
- Buffer = 5-10 pips above swing high
```

### Take-Profit Placement

```
Take-Profit = Entry Price + (SL Distance × R:R Ratio)

Where:
- R:R Ratio = 2.5:1 (minimum)
- Can use 3:1 for small account to offset spread costs

Example (LONG):
Entry = 1.0850
SL = 1.0810 (40 pips below)
TP = 1.0850 + (40 × 2.5) = 1.0950 (100 pips above)
```

### Trailing Stop (Optional)

```
When trade reaches 1.5:1 (1.5x risk):
- Move SL to break-even (entry price)

When trade reaches 2:1 (2x risk):
- Move SL to lock in 1:1 profit
- Or trail by 20 EMA on daily chart
```

### Early Exit Conditions

Exit trade immediately if:
```
1. Major trend reversal (price closes opposite side of both EMAs)
2. Significant news event against position
3. Risk management rule triggered (max daily loss)
```

## Position Sizing

### Fixed Percentage Risk Method

```
Position Size (lots) = Risk Amount / (SL Distance in pips × Pip Value)

Where:
- Risk Amount = Account Balance × Risk Per Trade %
- Risk Per Trade % = 1.0% (fixed)
- SL Distance = Entry to Stop-Loss in pips
- Pip Value = depends on lot size and pair

Example:
Account = $800
Risk = 1% = $8
SL Distance = 40 pips
Pip Value (0.01 lot EUR/USD) = $0.10

Position Size = $8 / (40 × $0.10) = 2 micro lots (0.02 lots)
```

### Position Size Limits

```
Minimum: 0.01 lots (micro lot)
Maximum: Based on 1% risk (calculated dynamically)

For small accounts (<$1000):
- Use micro lots (0.01)
- Consider nano lots (0.001) if broker offers
```

### Pip Value Reference

```
EUR/USD:
- 1 standard lot (1.00): $10/pip
- 1 mini lot (0.10): $1/pip
- 1 micro lot (0.01): $0.10/pip

GBP/USD:
- Same as EUR/USD

XAU/USD (Gold):
- 1 standard lot: $10/pip
- 1 micro lot: $0.10/pip
- Note: Higher margin requirement
```

## Technical Indicators

### Exponential Moving Average (EMA)

**20 EMA**: Short-term trend
- Acts as dynamic support in uptrends
- Acts as dynamic resistance in downtrends
- Entry zone for pullbacks

**50 EMA**: Medium-term trend
- Defines overall trend direction
- Major support/resistance level
- Filter to avoid choppy markets

**Calculation**:
```
EMA = (Close - EMA_previous) × Multiplier + EMA_previous

Where:
Multiplier = 2 / (Period + 1)

For 20 EMA: Multiplier = 2/21 = 0.0952
For 50 EMA: Multiplier = 2/51 = 0.0392
```

### Relative Strength Index (RSI)

**Period**: 14

**Purpose**: Momentum filter (not overbought/oversold in this strategy)

**Range**: 0-100
- Below 30: Oversold (avoid new LONG entries)
- Above 70: Overbought (avoid new SHORT entries)
- 40-60: Neutral zone (preferred for entries)

**Calculation**:
```
RSI = 100 - [100 / (1 + RS)]

Where:
RS = Average Gain / Average Loss (over 14 periods)
```

### Average True Range (ATR)

**Period**: 14

**Purpose**: Volatility measurement for stop-loss sizing

**Usage**:
```
Optional: Set SL at 1.5 × ATR below entry (LONG)

Example:
ATR = 0.0050 (50 pips)
SL Distance = 1.5 × 50 = 75 pips (might be too wide for small account)
```

## Trading Hours

### Optimal Trading Windows

**Your Available Time (WAT):**
- 8am-11am WAT = 7am-10am UTC (London open)
- 12pm-3pm WAT = 11am-2pm UTC (London/NY overlap)

**Best Sessions for Each Pair:**

**EUR/USD:**
- London Session (8am-4pm UTC) - Highest volume
- NY Session (1pm-9pm UTC) - Good volume
- Your windows: EXCELLENT timing

**GBP/USD:**
- London Session (8am-12pm UTC) - Most volatile
- London/NY Overlap (1pm-4pm UTC) - Best liquidity
- Your windows: PERFECT timing

**XAU/USD (Gold):**
- London/NY Overlap (1pm-4pm UTC) - Highest volume
- All sessions active (global commodity)
- Your windows: GOOD timing

**Daily Routine:**
```
Daily Analysis Time: 30-60 minutes

1. Review open positions (5 min)
   - Check if TP/SL hit
   - Update trailing stops if needed

2. Check for new signals (15-20 min)
   - System scans for setups
   - Review each signal manually
   - Validate against strategy rules

3. Execute trades (10-15 min)
   - Calculate position size
   - Place order with SL/TP
   - Log in trading journal

4. Update journal (10 min)
   - Screenshot chart
   - Document reasoning
   - Note market conditions
```

## Strategy Performance Expectations

### Realistic Targets

**Win Rate**: 45-55%
- Not chasing high win rates
- Focus on good risk/reward

**Profit Factor**: 1.5-2.5
- Gross Profit / Gross Loss
- Above 1.5 is profitable

**Risk/Reward**: 2.5:1 average
- Compensates for spread costs
- Allows for <50% win rate profitability

**Maximum Drawdown**: <20%
- Expect 3-5 consecutive losses
- 1% risk × 5 = 5% drawdown (manageable)

**Monthly Returns**: 2-5% (if strategy works)
- Not expecting huge gains
- Consistency over moonshots
- Focus on capital preservation

### Trade Frequency

**Expected Signals**: 2-5 per week across 3 pairs

**Breakdown**:
- EUR/USD: 1-2 setups per week
- GBP/USD: 1-2 setups per week
- XAU/USD: 0-1 setups per week (more selective)

**Monthly**: 10-20 trades total

**Average Hold Time**: 2-7 days per trade

## Strategy Filters (Optional)

### Additional Entry Filters

**Volume Filter**:
```
✓ Current volume > 20-day average (if data available)
✓ Indicates genuine interest in move
```

**Trend Strength Filter**:
```
✓ ADX > 20 (trend present)
✓ Avoids choppy, ranging markets
```

**Time Filter**:
```
✓ Avoid entries on Friday (weekend risk)
✓ Avoid major news events (NFP, FOMC, etc.)
```

## Risk Management Rules

### Per-Trade Limits

```
Maximum Risk per Trade: 1%
Maximum Position Size: Calculated based on SL
No exceptions to stop-loss placement
```

### Daily Limits

```
Maximum Trades per Day: 2
Maximum Daily Loss: 2% (stop trading if hit)
Maximum Open Positions: 3 (one per pair)
```

### Weekly/Monthly Limits

```
Maximum Weekly Loss: 5% (reduce size next week)
Maximum Monthly Loss: 10% (stop trading, review strategy)
```

### Capital Allocation

```
Trading Capital: $800 (initial)
Reserve: Keep some cash for margin calls (if needed)
Don't trade entire balance at once
```

## Psychology & Discipline

### Trading Rules

```
✓ Follow the system, don't override signals
✓ Accept losses as part of the process
✓ Never revenge trade after a loss
✓ Don't move stop-loss further away (only closer)
✓ Take profits at target (don't get greedy)
✓ Review every trade (win or lose)
```

### When NOT to Trade

```
✗ Emotionally compromised (angry, stressed)
✗ After hitting daily loss limit
✗ During major unexpected news
✗ When signal doesn't meet ALL criteria
✗ When too busy to monitor properly
```

## Strategy Evolution

### Phase 1: Validation (Months 1-3)

- Trade strategy as defined
- Track all metrics
- No modifications during testing
- Goal: Validate if approach works

### Phase 2: Optimization (Months 4-6)

- Analyze what works best
- Adjust parameters if needed
- Test improvements in backtest
- Implement gradually

### Phase 3: Scaling (Months 6+)

- If profitable, add capital
- Maintain 1% risk (position size increases naturally)
- Consider additional pairs
- Refine and improve

## Example Trade Walkthrough

### Setup Identification

**Date**: January 15, 2025
**Pair**: EUR/USD
**Timeframe**: Daily

**Market Analysis**:
- Price: 1.0850
- 20 EMA: 1.0820
- 50 EMA: 1.0780
- RSI: 52
- Trend: Uptrend (price > both EMAs)

**Pullback**:
- Previous 3 days pulled back from 1.0920 to 1.0810
- Today's low touched 20 EMA at 1.0820
- Stayed above 50 EMA (trend intact)

**Signal**:
- Today closing at 1.0850 (above 20 EMA)
- Bullish candle (close > open)
- RSI in neutral zone (52)
- ✓ All criteria met → BUY SIGNAL

### Trade Execution

**Entry**:
- Signal generated: End of day Jan 15
- Execution: Next day (Jan 16) at open
- Entry Price: 1.0855 (market open + spread)

**Stop-Loss**:
- Swing low: 1.0795 (from Jan 12)
- Buffer: -10 pips = 1.0785
- SL Distance: 70 pips

**Take-Profit**:
- R:R Ratio: 2.5:1
- TP Distance: 70 × 2.5 = 175 pips
- TP Price: 1.0855 + 175 = 1.1030

**Position Size**:
- Account: $800
- Risk: 1% = $8
- SL: 70 pips
- Pip value (0.01 lot): $0.10/pip
- Position: $8 / (70 × $0.10) = 1.14 → 0.01 lots (conservative)
- Actual risk: 70 × $0.10 × 0.01 = $0.70 (well under 1%)

Note: With small capital, position size rounds down significantly.

### Trade Management

**Day 1 (Jan 16)**: Entered at 1.0855
**Day 2 (Jan 17)**: Price at 1.0890 (+35 pips)
**Day 3 (Jan 18)**: Price at 1.0920 (+65 pips)
**Day 4 (Jan 19)**: Price at 1.0960 (+105 pips, 1.5:1 R:R)
  → Move SL to break-even (1.0855)
**Day 5 (Jan 20)**: Price at 1.1025
  → TP hit at 1.1030
  → Trade closed

**Result**:
- Entry: 1.0855
- Exit: 1.1030
- Profit: 175 pips
- P&L: 175 × $0.10 × 0.01 = $1.75
- Return: 0.22% on account

### Trade Journal Entry

```
Trade #: 001
Date: 2025-01-15
Pair: EUR/USD
Direction: LONG
Timeframe: Daily

Setup:
- Uptrend confirmed (price > 20/50 EMA)
- Pullback to 20 EMA complete
- RSI at 52 (neutral)
- Bullish close above 20 EMA

Entry: 1.0855
SL: 1.0785 (70 pips)
TP: 1.1030 (175 pips)
Position: 0.01 lots
Risk: $0.70 (0.09%)

Exit: 2025-01-20 at TP
Profit: +175 pips / +$1.75

Notes:
- Clean setup, all criteria met
- Patient wait for pullback paid off
- Moved to BE at 1.5:1, reduced stress
- Hit full TP target

Lessons:
- Strategy worked as designed
- Small position size limits profit (expected with small capital)
```

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Strategy Status**: Backtesting Phase
