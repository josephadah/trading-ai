"""
Signal generation module for identifying trading setups.
Implements the Daily EMA Pullback Strategy rules.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from utils.logger import setup_logger
from utils.constants import (
    SIGNAL_BUY,
    SIGNAL_SELL,
    SIGNAL_NONE,
    PIP_SIZES,
    MIN_SL_DISTANCE_PIPS,
    MAX_SL_DISTANCE_PIPS,
    DEFAULT_RISK_REWARD,
    RSI_NEUTRAL_LOW,
    RSI_NEUTRAL_HIGH
)
from utils.helpers import calculate_pips
from analysis.indicators import get_recent_swing_low, get_recent_swing_high

logger = setup_logger(__name__)


class SignalGenerator:
    """Generate trading signals based on strategy rules."""

    def __init__(
        self,
        risk_reward_ratio: float = DEFAULT_RISK_REWARD,
        min_sl_pips: float = MIN_SL_DISTANCE_PIPS,
        max_sl_pips: float = MAX_SL_DISTANCE_PIPS,
        ema_tolerance_pips: float = 10.0,
        rsi_low: float = RSI_NEUTRAL_LOW,
        rsi_high: float = RSI_NEUTRAL_HIGH
    ):
        """
        Initialize signal generator.

        Args:
            risk_reward_ratio: Minimum risk/reward ratio (default 2.5)
            min_sl_pips: Minimum stop-loss distance in pips
            max_sl_pips: Maximum stop-loss distance in pips
            ema_tolerance_pips: Tolerance for price touching EMA (±pips)
            rsi_low: RSI lower bound for neutral zone
            rsi_high: RSI upper bound for neutral zone
        """
        self.risk_reward_ratio = risk_reward_ratio
        self.min_sl_pips = min_sl_pips
        self.max_sl_pips = max_sl_pips
        self.ema_tolerance_pips = ema_tolerance_pips
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high

    def check_long_trend(
        self,
        close: float,
        ema_20: float,
        ema_50: float
    ) -> Tuple[bool, str]:
        """
        Check if long trend conditions are met.

        Criteria:
        - Price > 20 EMA
        - Price > 50 EMA
        - 20 EMA > 50 EMA

        Args:
            close: Current close price
            ema_20: 20 EMA value
            ema_50: 50 EMA value

        Returns:
            Tuple of (is_valid, reason)
        """
        if close <= ema_20:
            return False, "Price not above 20 EMA"

        if close <= ema_50:
            return False, "Price not above 50 EMA"

        if ema_20 <= ema_50:
            return False, "20 EMA not above 50 EMA"

        return True, "Long trend confirmed"

    def check_short_trend(
        self,
        close: float,
        ema_20: float,
        ema_50: float
    ) -> Tuple[bool, str]:
        """
        Check if short trend conditions are met.

        Criteria:
        - Price < 20 EMA
        - Price < 50 EMA
        - 20 EMA < 50 EMA

        Args:
            close: Current close price
            ema_20: 20 EMA value
            ema_50: 50 EMA value

        Returns:
            Tuple of (is_valid, reason)
        """
        if close >= ema_20:
            return False, "Price not below 20 EMA"

        if close >= ema_50:
            return False, "Price not below 50 EMA"

        if ema_20 >= ema_50:
            return False, "20 EMA not below 50 EMA"

        return True, "Short trend confirmed"

    def check_pullback_to_ema(
        self,
        data: pd.DataFrame,
        current_idx: int,
        symbol: str,
        lookback: int = 5
    ) -> Tuple[bool, str]:
        """
        Check if price pulled back to 20 EMA in recent bars.

        Args:
            data: DataFrame with price and indicator data
            current_idx: Index of current bar
            symbol: Symbol being analyzed
            lookback: Number of bars to look back

        Returns:
            Tuple of (touched_ema, reason)
        """
        if current_idx < lookback:
            return False, "Not enough data"

        pip_size = PIP_SIZES.get(symbol, 0.0001)
        tolerance = self.ema_tolerance_pips * pip_size

        current_row = data.iloc[current_idx]
        current_close = current_row['close']
        current_ema = current_row['ema_20']

        # Check if currently close to EMA (within 30 pips as a more relaxed criterion)
        distance = abs(current_close - current_ema)
        distance_pips = distance / pip_size

        if distance_pips <= 30:
            return True, f"Currently near 20 EMA ({distance_pips:.1f} pips)"

        # Check if price touched 20 EMA in recent bars
        for i in range(max(0, current_idx - lookback), current_idx):
            row = data.iloc[i]
            low = row['low']
            high = row['high']
            ema_20 = row['ema_20']

            # Check if price touched EMA within tolerance
            if low - tolerance <= ema_20 <= high + tolerance:
                return True, f"Touched 20 EMA {current_idx - i} bars ago"

        return False, "No pullback to 20 EMA detected"

    def check_rsi_neutral(
        self,
        rsi: float
    ) -> Tuple[bool, str]:
        """
        Check if RSI is in neutral zone.

        Args:
            rsi: RSI value

        Returns:
            Tuple of (is_neutral, reason)
        """
        if pd.isna(rsi):
            return False, "RSI not available"

        if self.rsi_low <= rsi <= self.rsi_high:
            return True, f"RSI in neutral zone ({rsi:.2f})"

        return False, f"RSI outside neutral zone ({rsi:.2f})"

    def calculate_stop_loss_long(
        self,
        data: pd.DataFrame,
        current_idx: int,
        symbol: str
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Calculate stop-loss for LONG position.

        Args:
            data: DataFrame with price data
            current_idx: Index of current bar
            symbol: Symbol being analyzed

        Returns:
            Tuple of (stop_loss_price, sl_distance_pips, reason)
        """
        # Find recent swing low
        swing_low = get_recent_swing_low(
            data['low'],
            current_idx,
            lookback=5,
            max_bars_back=10
        )

        if swing_low is None:
            return None, None, "No swing low found"

        # Add buffer
        pip_size = PIP_SIZES.get(symbol, 0.0001)
        buffer = 10 * pip_size  # 10 pips buffer
        sl_price = swing_low - buffer

        # Calculate distance in pips
        entry_price = data.iloc[current_idx]['close']
        sl_distance = calculate_pips(symbol, entry_price, sl_price, 'LONG')

        # Validate SL distance
        if sl_distance < self.min_sl_pips:
            return None, None, f"SL too tight ({sl_distance:.1f} pips < {self.min_sl_pips})"

        if sl_distance > self.max_sl_pips:
            return None, None, f"SL too wide ({sl_distance:.1f} pips > {self.max_sl_pips})"

        return sl_price, sl_distance, f"SL at {sl_price:.5f} ({sl_distance:.1f} pips)"

    def calculate_stop_loss_short(
        self,
        data: pd.DataFrame,
        current_idx: int,
        symbol: str
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Calculate stop-loss for SHORT position.

        Args:
            data: DataFrame with price data
            current_idx: Index of current bar
            symbol: Symbol being analyzed

        Returns:
            Tuple of (stop_loss_price, sl_distance_pips, reason)
        """
        # Find recent swing high
        swing_high = get_recent_swing_high(
            data['high'],
            current_idx,
            lookback=5,
            max_bars_back=10
        )

        if swing_high is None:
            return None, None, "No swing high found"

        # Add buffer
        pip_size = PIP_SIZES.get(symbol, 0.0001)
        buffer = 10 * pip_size  # 10 pips buffer
        sl_price = swing_high + buffer

        # Calculate distance in pips
        entry_price = data.iloc[current_idx]['close']
        sl_distance = calculate_pips(symbol, sl_price, entry_price, 'SHORT')

        # Validate SL distance
        if sl_distance < self.min_sl_pips:
            return None, None, f"SL too tight ({sl_distance:.1f} pips < {self.min_sl_pips})"

        if sl_distance > self.max_sl_pips:
            return None, None, f"SL too wide ({sl_distance:.1f} pips > {self.max_sl_pips})"

        return sl_price, sl_distance, f"SL at {sl_price:.5f} ({sl_distance:.1f} pips)"

    def calculate_take_profit(
        self,
        entry_price: float,
        sl_price: float,
        signal_type: str
    ) -> float:
        """
        Calculate take-profit based on risk/reward ratio.

        Args:
            entry_price: Entry price
            sl_price: Stop-loss price
            signal_type: 'BUY' or 'SELL'

        Returns:
            Take-profit price
        """
        sl_distance = abs(entry_price - sl_price)
        tp_distance = sl_distance * self.risk_reward_ratio

        if signal_type == SIGNAL_BUY:
            tp_price = entry_price + tp_distance
        else:
            tp_price = entry_price - tp_distance

        return tp_price

    def generate_long_signal(
        self,
        data: pd.DataFrame,
        current_idx: int,
        symbol: str
    ) -> Optional[Dict]:
        """
        Check for LONG signal setup.

        Args:
            data: DataFrame with OHLC and indicator data
            current_idx: Index of current bar
            symbol: Symbol being analyzed

        Returns:
            Signal dictionary or None if no valid signal
        """
        if current_idx < 1:
            return None

        current = data.iloc[current_idx]
        previous = data.iloc[current_idx - 1]

        reasons = []

        # Required indicators
        if any(pd.isna(current[col]) for col in ['ema_20', 'ema_50', 'rsi_14']):
            return None

        # 1. Check trend
        trend_valid, trend_reason = self.check_long_trend(
            current['close'],
            current['ema_20'],
            current['ema_50']
        )
        reasons.append(trend_reason)

        if not trend_valid:
            return None

        # 2. Check pullback to EMA
        pullback_valid, pullback_reason = self.check_pullback_to_ema(
            data, current_idx, symbol
        )
        reasons.append(pullback_reason)

        if not pullback_valid:
            return None

        # 3. Check RSI
        rsi_valid, rsi_reason = self.check_rsi_neutral(current['rsi_14'])
        reasons.append(rsi_reason)

        # RSI is a filter, not a requirement (allow some flexibility)
        # if not rsi_valid:
        #     return None

        # 4. Check entry trigger: current close > 20 EMA and higher than previous
        if current['close'] <= current['ema_20']:
            reasons.append("Not closed above 20 EMA")
            return None

        if current['close'] <= previous['close']:
            reasons.append("Not higher close than previous")
            return None

        reasons.append("Entry trigger confirmed")

        # 5. Calculate stop-loss
        sl_price, sl_pips, sl_reason = self.calculate_stop_loss_long(
            data, current_idx, symbol
        )
        reasons.append(sl_reason)

        if sl_price is None:
            return None

        # 6. Calculate take-profit
        tp_price = self.calculate_take_profit(current['close'], sl_price, SIGNAL_BUY)
        tp_pips = calculate_pips(symbol, current['close'], tp_price, 'LONG')

        # Calculate risk/reward
        rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 0

        # Create signal
        signal = {
            'symbol': symbol,
            'signal_date': current['timestamp'],
            'signal_type': SIGNAL_BUY,
            'entry_price': current['close'],
            'stop_loss': sl_price,
            'take_profit': tp_price,
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'risk_reward_ratio': rr_ratio,
            'reasoning': ' | '.join(reasons),
            'ema_20': current['ema_20'],
            'ema_50': current['ema_50'],
            'rsi_14': current['rsi_14'],
            'atr_14': current['atr_14']
        }

        return signal

    def generate_short_signal(
        self,
        data: pd.DataFrame,
        current_idx: int,
        symbol: str
    ) -> Optional[Dict]:
        """
        Check for SHORT signal setup.

        Args:
            data: DataFrame with OHLC and indicator data
            current_idx: Index of current bar
            symbol: Symbol being analyzed

        Returns:
            Signal dictionary or None if no valid signal
        """
        if current_idx < 1:
            return None

        current = data.iloc[current_idx]
        previous = data.iloc[current_idx - 1]

        reasons = []

        # Required indicators
        if any(pd.isna(current[col]) for col in ['ema_20', 'ema_50', 'rsi_14']):
            return None

        # 1. Check trend
        trend_valid, trend_reason = self.check_short_trend(
            current['close'],
            current['ema_20'],
            current['ema_50']
        )
        reasons.append(trend_reason)

        if not trend_valid:
            return None

        # 2. Check pullback to EMA
        pullback_valid, pullback_reason = self.check_pullback_to_ema(
            data, current_idx, symbol
        )
        reasons.append(pullback_reason)

        if not pullback_valid:
            return None

        # 3. Check RSI
        rsi_valid, rsi_reason = self.check_rsi_neutral(current['rsi_14'])
        reasons.append(rsi_reason)

        # 4. Check entry trigger: current close < 20 EMA and lower than previous
        if current['close'] >= current['ema_20']:
            reasons.append("Not closed below 20 EMA")
            return None

        if current['close'] >= previous['close']:
            reasons.append("Not lower close than previous")
            return None

        reasons.append("Entry trigger confirmed")

        # 5. Calculate stop-loss
        sl_price, sl_pips, sl_reason = self.calculate_stop_loss_short(
            data, current_idx, symbol
        )
        reasons.append(sl_reason)

        if sl_price is None:
            return None

        # 6. Calculate take-profit
        tp_price = self.calculate_take_profit(current['close'], sl_price, SIGNAL_SELL)
        tp_pips = calculate_pips(symbol, tp_price, current['close'], 'SHORT')

        # Calculate risk/reward
        rr_ratio = tp_pips / sl_pips if sl_pips > 0 else 0

        # Create signal
        signal = {
            'symbol': symbol,
            'signal_date': current['timestamp'],
            'signal_type': SIGNAL_SELL,
            'entry_price': current['close'],
            'stop_loss': sl_price,
            'take_profit': tp_price,
            'sl_pips': sl_pips,
            'tp_pips': tp_pips,
            'risk_reward_ratio': rr_ratio,
            'reasoning': ' | '.join(reasons),
            'ema_20': current['ema_20'],
            'ema_50': current['ema_50'],
            'rsi_14': current['rsi_14'],
            'atr_14': current['atr_14']
        }

        return signal

    def scan_for_signals(
        self,
        data: pd.DataFrame,
        symbol: str
    ) -> List[Dict]:
        """
        Scan historical data for signals.

        Args:
            data: DataFrame with OHLC and indicator data
            symbol: Symbol being analyzed

        Returns:
            List of signal dictionaries
        """
        signals = []

        logger.info(f"Scanning {len(data)} bars for {symbol} signals...")

        for i in range(1, len(data)):
            # Check for LONG signal
            long_signal = self.generate_long_signal(data, i, symbol)
            if long_signal:
                signals.append(long_signal)
                logger.debug(
                    f"LONG signal on {long_signal['signal_date']}: "
                    f"Entry {long_signal['entry_price']:.5f}, "
                    f"SL {long_signal['sl_pips']:.1f} pips, "
                    f"TP {long_signal['tp_pips']:.1f} pips"
                )

            # Check for SHORT signal
            short_signal = self.generate_short_signal(data, i, symbol)
            if short_signal:
                signals.append(short_signal)
                logger.debug(
                    f"SHORT signal on {short_signal['signal_date']}: "
                    f"Entry {short_signal['entry_price']:.5f}, "
                    f"SL {short_signal['sl_pips']:.1f} pips, "
                    f"TP {short_signal['tp_pips']:.1f} pips"
                )

        logger.info(f"Found {len(signals)} signals for {symbol}")

        return signals
