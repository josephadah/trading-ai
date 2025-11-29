"""
Detailed debug to find out exactly why signals aren't generated.
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


def detailed_signal_check(symbol: str = 'EURUSD', num_bars: int = 20):
    """Check each signal criterion for recent bars."""

    logger.info(f"Detailed Signal Check for {symbol} (last {num_bars} bars)")
    logger.info("=" * 120)

    # Load data
    loader = DataLoader()
    data = loader.get_symbol_data(symbol, '1d')
    data = add_indicators_to_data(data)
    data = data.dropna(subset=['ema_20', 'ema_50', 'rsi_14'])

    generator = SignalGenerator()

    # Check last N bars
    recent_data = data.tail(num_bars)

    for i in range(len(recent_data) - 1):  # -1 because we need previous bar
        idx = len(data) - len(recent_data) + i
        current = recent_data.iloc[i + 1]  # Need previous bar, so start at i+1
        previous = recent_data.iloc[i]

        logger.info(f"\nBar {current['timestamp'].date()} (index {idx + 1}):")
        logger.info("-" * 120)

        # Check LONG conditions
        logger.info("LONG Criteria:")

        # 1. Trend
        trend_valid, trend_reason = generator.check_long_trend(
            current['close'], current['ema_20'], current['ema_50']
        )
        logger.info(f"  1. Trend: {trend_valid:5} | {trend_reason}")
        logger.info(f"      Close={current['close']:.5f}, EMA20={current['ema_20']:.5f}, EMA50={current['ema_50']:.5f}")

        if not trend_valid:
            continue

        # 2. Pullback
        pullback_valid, pullback_reason = generator.check_pullback_to_ema(
            data, idx + 1, symbol
        )
        logger.info(f"  2. Pullback: {pullback_valid:5} | {pullback_reason}")

        if not pullback_valid:
            continue

        # 3. RSI
        rsi_valid, rsi_reason = generator.check_rsi_neutral(current['rsi_14'])
        logger.info(f"  3. RSI: {rsi_valid:5} | {rsi_reason}")

        # 4. Entry trigger
        close_above_ema = current['close'] > current['ema_20']
        higher_close = current['close'] > previous['close']
        logger.info(f"  4. Entry Trigger:")
        logger.info(f"      Close > EMA20: {close_above_ema} ({current['close']:.5f} vs {current['ema_20']:.5f})")
        logger.info(f"      Close > Prev:  {higher_close} ({current['close']:.5f} vs {previous['close']:.5f})")

        if not (close_above_ema and higher_close):
            logger.info(f"      FAILED: Entry trigger not met")
            continue

        # 5. Stop-loss
        sl_price, sl_pips, sl_reason = generator.calculate_stop_loss_long(
            data, idx + 1, symbol
        )
        logger.info(f"  5. Stop-Loss: {sl_price is not None:5} | {sl_reason}")

        if sl_price is None:
            continue

        logger.info(f"\n  *** VALID LONG SIGNAL FOUND ***")
        logger.info(f"      Entry: {current['close']:.5f}")
        logger.info(f"      SL:    {sl_price:.5f} ({sl_pips:.1f} pips)")


if __name__ == '__main__':
    detailed_signal_check('EURUSD', num_bars=30)
