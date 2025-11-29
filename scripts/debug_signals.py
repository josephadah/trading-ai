"""
Debug signal generation to understand why no signals are found.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from ingestion.data_loader import DataLoader
from analysis.indicators import add_indicators_to_data
from analysis.signal_generator import SignalGenerator
from utils.logger import setup_logger

logger = setup_logger(__name__)


def debug_signal_conditions(symbol: str = 'EURUSD'):
    """Debug why signals aren't being generated."""

    logger.info(f"=" * 80)
    logger.info(f"Debugging Signal Generation for {symbol}")
    logger.info(f"=" * 80)
    logger.info("")

    # Load data
    loader = DataLoader()
    data = loader.get_symbol_data(symbol, '1d')

    if data.empty:
        logger.error("No data found")
        return

    # Add indicators
    data = add_indicators_to_data(data)

    # Drop early rows without indicators
    data = data.dropna(subset=['ema_20', 'ema_50', 'rsi_14'])

    logger.info(f"Total bars with indicators: {len(data)}")
    logger.info("")

    # Check trend conditions
    logger.info("Checking trend conditions...")
    logger.info("-" * 80)

    # LONG trend: close > ema_20 > ema_50
    long_trend = data[
        (data['close'] > data['ema_20']) &
        (data['close'] > data['ema_50']) &
        (data['ema_20'] > data['ema_50'])
    ]

    logger.info(f"Bars in LONG trend: {len(long_trend)} ({len(long_trend)/len(data)*100:.1f}%)")

    if not long_trend.empty:
        logger.info("\nSample LONG trend bars:")
        for _, row in long_trend.tail(3).iterrows():
            logger.info(
                f"  {row['timestamp'].date()} | Close: {row['close']:.5f} | "
                f"EMA20: {row['ema_20']:.5f} | EMA50: {row['ema_50']:.5f} | "
                f"RSI: {row['rsi_14']:.2f}"
            )

    # SHORT trend: close < ema_20 < ema_50
    short_trend = data[
        (data['close'] < data['ema_20']) &
        (data['close'] < data['ema_50']) &
        (data['ema_20'] < data['ema_50'])
    ]

    logger.info(f"\nBars in SHORT trend: {len(short_trend)} ({len(short_trend)/len(data)*100:.1f}%)")

    if not short_trend.empty:
        logger.info("\nSample SHORT trend bars:")
        for _, row in short_trend.tail(3).iterrows():
            logger.info(
                f"  {row['timestamp'].date()} | Close: {row['close']:.5f} | "
                f"EMA20: {row['ema_20']:.5f} | EMA50: {row['ema_50']:.5f} | "
                f"RSI: {row['rsi_14']:.2f}"
            )

    logger.info("")

    # Check pullback conditions
    logger.info("Checking pullback conditions (close near EMA20)...")
    logger.info("-" * 80)

    # Distance from EMA20
    data['dist_to_ema20'] = abs(data['close'] - data['ema_20'])
    data['dist_to_ema20_pips'] = data['dist_to_ema20'] / 0.0001  # Convert to pips for EURUSD

    # Find bars close to EMA20 (within 20 pips)
    near_ema = data[data['dist_to_ema20_pips'] < 20]

    logger.info(f"Bars within 20 pips of EMA20: {len(near_ema)} ({len(near_ema)/len(data)*100:.1f}%)")

    if not near_ema.empty:
        logger.info("\nSample bars near EMA20:")
        for _, row in near_ema.tail(5).iterrows():
            logger.info(
                f"  {row['timestamp'].date()} | Close: {row['close']:.5f} | "
                f"EMA20: {row['ema_20']:.5f} | Distance: {row['dist_to_ema20_pips']:.1f} pips | "
                f"RSI: {row['rsi_14']:.2f}"
            )

    logger.info("")

    # Check RSI neutral zone
    logger.info("Checking RSI neutral zone (40-60)...")
    logger.info("-" * 80)

    rsi_neutral = data[(data['rsi_14'] >= 40) & (data['rsi_14'] <= 60)]

    logger.info(f"Bars with RSI in neutral zone: {len(rsi_neutral)} ({len(rsi_neutral)/len(data)*100:.1f}%)")

    if not rsi_neutral.empty:
        logger.info("\nSample bars with RSI in neutral zone:")
        for _, row in rsi_neutral.tail(5).iterrows():
            logger.info(
                f"  {row['timestamp'].date()} | Close: {row['close']:.5f} | "
                f"RSI: {row['rsi_14']:.2f} | EMA20: {row['ema_20']:.5f}"
            )

    logger.info("")

    # Check combined conditions for LONG
    logger.info("Checking combined LONG conditions...")
    logger.info("-" * 80)

    combined_long = data[
        (data['close'] > data['ema_20']) &
        (data['close'] > data['ema_50']) &
        (data['ema_20'] > data['ema_50']) &
        (data['dist_to_ema20_pips'] < 30) &  # Recently near EMA20
        (data['rsi_14'] >= 35) &  # Slightly relaxed RSI
        (data['rsi_14'] <= 65)
    ]

    logger.info(f"Bars meeting relaxed LONG criteria: {len(combined_long)}")

    if not combined_long.empty:
        logger.info("\nSample bars meeting relaxed LONG criteria:")
        for _, row in combined_long.tail(5).iterrows():
            logger.info(
                f"  {row['timestamp'].date()} | Close: {row['close']:.5f} | "
                f"EMA20: {row['ema_20']:.5f} | Dist: {row['dist_to_ema20_pips']:.1f}p | "
                f"RSI: {row['rsi_14']:.2f}"
            )

    logger.info("")

    # Market condition summary
    logger.info("Market Condition Summary:")
    logger.info("-" * 80)

    latest = data.iloc[-1]
    logger.info(f"Latest bar: {latest['timestamp'].date()}")
    logger.info(f"  Close: {latest['close']:.5f}")
    logger.info(f"  EMA20: {latest['ema_20']:.5f}")
    logger.info(f"  EMA50: {latest['ema_50']:.5f}")
    logger.info(f"  RSI:   {latest['rsi_14']:.2f}")
    logger.info(f"  ATR:   {latest['atr_14']:.5f}")

    if latest['close'] > latest['ema_20'] and latest['ema_20'] > latest['ema_50']:
        logger.info(f"  Trend: BULLISH")
    elif latest['close'] < latest['ema_20'] and latest['ema_20'] < latest['ema_50']:
        logger.info(f"  Trend: BEARISH")
    else:
        logger.info(f"  Trend: MIXED/RANGING")

    logger.info("")
    logger.info("=" * 80)


if __name__ == '__main__':
    debug_signal_conditions('EURUSD')
    print("\n")
    debug_signal_conditions('GBPUSD')
    print("\n")
    debug_signal_conditions('XAUUSD')
