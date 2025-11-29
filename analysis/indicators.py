"""
Technical indicator calculations for the trading system.
Implements EMA, RSI, ATR, and swing point detection.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
from utils.logger import setup_logger
from utils.constants import (
    DEFAULT_EMA_SHORT,
    DEFAULT_EMA_LONG,
    DEFAULT_RSI_PERIOD,
    DEFAULT_ATR_PERIOD
)

logger = setup_logger(__name__)


def calculate_ema(
    data: pd.Series,
    period: int,
    adjust: bool = False
) -> pd.Series:
    """
    Calculate Exponential Moving Average.

    Args:
        data: Price series (typically close prices)
        period: EMA period
        adjust: Use adjusted EMA calculation (pandas default=True, trading default=False)

    Returns:
        Series with EMA values
    """
    return data.ewm(span=period, adjust=adjust).mean()


def calculate_rsi(
    data: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Calculate Relative Strength Index.

    Formula:
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss

    Args:
        data: Price series (typically close prices)
        period: RSI period (default 14)

    Returns:
        Series with RSI values (0-100)
    """
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gains = delta.copy()
    losses = delta.copy()

    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)

    # Calculate average gains and losses using EMA (Wilder's smoothing)
    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()

    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14
) -> pd.Series:
    """
    Calculate Average True Range.

    True Range is the maximum of:
    1. Current High - Current Low
    2. |Current High - Previous Close|
    3. |Current Low - Previous Close|

    ATR is the EMA of True Range.

    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period (default 14)

    Returns:
        Series with ATR values
    """
    # Calculate True Range components
    high_low = high - low
    high_close = abs(high - close.shift(1))
    low_close = abs(low - close.shift(1))

    # True Range is the maximum of the three
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # ATR is the EMA of True Range
    atr = true_range.ewm(span=period, adjust=False).mean()

    return atr


def find_swing_highs(
    high: pd.Series,
    lookback: int = 10
) -> pd.Series:
    """
    Identify swing highs in the price data.

    A swing high is a peak where the high is higher than
    the highs in the surrounding bars.

    Args:
        high: High price series
        lookback: Number of bars to look back/forward

    Returns:
        Series with swing high values (NaN where not a swing high)
    """
    swing_highs = pd.Series(index=high.index, dtype=float)

    for i in range(lookback, len(high) - lookback):
        # Check if current high is the highest in the window
        window_start = i - lookback
        window_end = i + lookback + 1
        window_max = high.iloc[window_start:window_end].max()

        if high.iloc[i] == window_max:
            swing_highs.iloc[i] = high.iloc[i]

    return swing_highs


def find_swing_lows(
    low: pd.Series,
    lookback: int = 10
) -> pd.Series:
    """
    Identify swing lows in the price data.

    A swing low is a trough where the low is lower than
    the lows in the surrounding bars.

    Args:
        low: Low price series
        lookback: Number of bars to look back/forward

    Returns:
        Series with swing low values (NaN where not a swing low)
    """
    swing_lows = pd.Series(index=low.index, dtype=float)

    for i in range(lookback, len(low) - lookback):
        # Check if current low is the lowest in the window
        window_start = i - lookback
        window_end = i + lookback + 1
        window_min = low.iloc[window_start:window_end].min()

        if low.iloc[i] == window_min:
            swing_lows.iloc[i] = low.iloc[i]

    return swing_lows


def get_recent_swing_low(
    low: pd.Series,
    current_idx: int,
    lookback: int = 10,
    max_bars_back: int = 20
) -> Optional[float]:
    """
    Get the most recent swing low before current bar.

    Args:
        low: Low price series
        current_idx: Current bar index
        lookback: Lookback period for swing detection
        max_bars_back: Maximum bars to look back

    Returns:
        Most recent swing low value or None
    """
    # Find all swing lows
    swing_lows = find_swing_lows(low, lookback)

    # Get swing lows before current bar
    start_idx = max(0, current_idx - max_bars_back)
    recent_swings = swing_lows.iloc[start_idx:current_idx].dropna()

    if len(recent_swings) > 0:
        return recent_swings.iloc[-1]

    # If no swing low found, return the minimum low in the period
    return low.iloc[start_idx:current_idx].min()


def get_recent_swing_high(
    high: pd.Series,
    current_idx: int,
    lookback: int = 10,
    max_bars_back: int = 20
) -> Optional[float]:
    """
    Get the most recent swing high before current bar.

    Args:
        high: High price series
        current_idx: Current bar index
        lookback: Lookback period for swing detection
        max_bars_back: Maximum bars to look back

    Returns:
        Most recent swing high value or None
    """
    # Find all swing highs
    swing_highs = find_swing_highs(high, lookback)

    # Get swing highs before current bar
    start_idx = max(0, current_idx - max_bars_back)
    recent_swings = swing_highs.iloc[start_idx:current_idx].dropna()

    if len(recent_swings) > 0:
        return recent_swings.iloc[-1]

    # If no swing high found, return the maximum high in the period
    return high.iloc[start_idx:current_idx].max()


class IndicatorCalculator:
    """Calculate and manage technical indicators for market data."""

    def __init__(
        self,
        ema_short: int = DEFAULT_EMA_SHORT,
        ema_long: int = DEFAULT_EMA_LONG,
        rsi_period: int = DEFAULT_RSI_PERIOD,
        atr_period: int = DEFAULT_ATR_PERIOD
    ):
        """
        Initialize the indicator calculator.

        Args:
            ema_short: Short EMA period (default 20)
            ema_long: Long EMA period (default 50)
            rsi_period: RSI period (default 14)
            atr_period: ATR period (default 14)
        """
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.rsi_period = rsi_period
        self.atr_period = atr_period

    def calculate_all_indicators(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate all indicators for a dataset.

        Args:
            data: DataFrame with OHLC data (columns: open, high, low, close)

        Returns:
            DataFrame with added indicator columns
        """
        if data.empty:
            logger.warning("Empty data provided for indicator calculation")
            return data

        # Make a copy to avoid modifying original
        df = data.copy()

        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Calculate EMAs
        df['ema_20'] = calculate_ema(df['close'], self.ema_short)
        df['ema_50'] = calculate_ema(df['close'], self.ema_long)

        # Calculate RSI
        df['rsi_14'] = calculate_rsi(df['close'], self.rsi_period)

        # Calculate ATR
        df['atr_14'] = calculate_atr(df['high'], df['low'], df['close'], self.atr_period)

        # Find swing points
        df['swing_high'] = find_swing_highs(df['high'], lookback=5)
        df['swing_low'] = find_swing_lows(df['low'], lookback=5)

        logger.info(f"Calculated indicators for {len(df)} rows")

        return df

    def validate_indicators(
        self,
        data: pd.DataFrame,
        sample_size: int = 5
    ) -> bool:
        """
        Validate calculated indicators.

        Args:
            data: DataFrame with calculated indicators
            sample_size: Number of recent rows to display for validation

        Returns:
            True if validation passes
        """
        required_indicators = ['ema_20', 'ema_50', 'rsi_14', 'atr_14']
        missing = [ind for ind in required_indicators if ind not in data.columns]

        if missing:
            logger.error(f"Missing indicators: {missing}")
            return False

        # Check for null values in recent data (expect nulls at beginning)
        recent_data = data.tail(sample_size)
        null_counts = recent_data[required_indicators].isnull().sum()

        if null_counts.any():
            logger.warning(f"Null values in recent indicators: {null_counts[null_counts > 0]}")

        # Display sample data for manual verification
        logger.info("\nSample indicator values (most recent):")
        logger.info("-" * 80)

        for idx, row in recent_data.iterrows():
            if 'timestamp' in row:
                date_str = row['timestamp'].strftime('%Y-%m-%d')
            else:
                date_str = str(idx)

            logger.info(
                f"{date_str} | Close: {row['close']:.5f} | "
                f"EMA20: {row['ema_20']:.5f} | EMA50: {row['ema_50']:.5f} | "
                f"RSI: {row['rsi_14']:.2f} | ATR: {row['atr_14']:.5f}"
            )

        logger.info("-" * 80)

        return True


def add_indicators_to_data(
    data: pd.DataFrame,
    ema_short: int = DEFAULT_EMA_SHORT,
    ema_long: int = DEFAULT_EMA_LONG,
    rsi_period: int = DEFAULT_RSI_PERIOD,
    atr_period: int = DEFAULT_ATR_PERIOD
) -> pd.DataFrame:
    """
    Convenience function to add all indicators to a DataFrame.

    Args:
        data: DataFrame with OHLC data
        ema_short: Short EMA period
        ema_long: Long EMA period
        rsi_period: RSI period
        atr_period: ATR period

    Returns:
        DataFrame with added indicators
    """
    calculator = IndicatorCalculator(ema_short, ema_long, rsi_period, atr_period)
    return calculator.calculate_all_indicators(data)
