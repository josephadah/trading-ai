"""Constants used throughout the trading system."""

# Currency Pairs
EURUSD = 'EURUSD'
GBPUSD = 'GBPUSD'
XAUUSD = 'XAUUSD'

SUPPORTED_PAIRS = [EURUSD, GBPUSD, XAUUSD]

# Yahoo Finance Symbols
YAHOO_SYMBOLS = {
    EURUSD: 'EURUSD=X',
    GBPUSD: 'GBPUSD=X',
    XAUUSD: 'GC=F',  # Gold futures
}

# Pip Values (for 1 micro lot = 0.01)
PIP_VALUES = {
    EURUSD: 0.10,  # $0.10 per pip for 0.01 lot
    GBPUSD: 0.10,
    XAUUSD: 0.10,  # For gold, 1 pip = $0.10 for 0.01 lot
}

# Pip Sizes (smallest price increment)
PIP_SIZES = {
    EURUSD: 0.0001,  # 4 decimal places
    GBPUSD: 0.0001,
    XAUUSD: 0.01,    # 2 decimal places for gold
}

# Default Spreads (in price units)
DEFAULT_SPREADS = {
    EURUSD: 0.0002,  # 2 pips
    GBPUSD: 0.0003,  # 3 pips
    XAUUSD: 0.50,    # 50 cents
}

# Trading Timeframes
TIMEFRAME_1MIN = '1min'
TIMEFRAME_5MIN = '5min'
TIMEFRAME_15MIN = '15min'
TIMEFRAME_1HOUR = '1h'
TIMEFRAME_4HOUR = '4h'
TIMEFRAME_DAILY = '1d'
TIMEFRAME_WEEKLY = '1wk'

# Signal Types
SIGNAL_BUY = 'BUY'
SIGNAL_SELL = 'SELL'
SIGNAL_NONE = 'NONE'

# Trade Directions
DIRECTION_LONG = 'LONG'
DIRECTION_SHORT = 'SHORT'

# Trade Status
STATUS_PENDING = 'PENDING'
STATUS_EXECUTED = 'EXECUTED'
STATUS_SKIPPED = 'SKIPPED'
STATUS_CANCELLED = 'CANCELLED'

# Trade Outcomes
OUTCOME_WIN = 'WIN'
OUTCOME_LOSS = 'LOSS'
OUTCOME_BREAKEVEN = 'BREAKEVEN'

# Exit Reasons
EXIT_TP_HIT = 'TP_HIT'
EXIT_SL_HIT = 'SL_HIT'
EXIT_MANUAL = 'MANUAL'
EXIT_EOD = 'END_OF_DAY'

# Risk Management
MIN_SL_DISTANCE_PIPS = 30
MAX_SL_DISTANCE_PIPS = 60
DEFAULT_RISK_REWARD = 2.5

# Indicator Periods
DEFAULT_EMA_SHORT = 20
DEFAULT_EMA_LONG = 50
DEFAULT_RSI_PERIOD = 14
DEFAULT_ATR_PERIOD = 14

# RSI Thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_NEUTRAL_LOW = 40
RSI_NEUTRAL_HIGH = 60

# Position Sizing
MIN_LOT_SIZE = 0.01  # Micro lot
MAX_LOT_SIZE = 100.0  # Standard lots
