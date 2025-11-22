"""Helper functions used throughout the trading system."""

from typing import Optional
from datetime import datetime, timedelta
from utils.constants import PIP_SIZES, PIP_VALUES


def calculate_pips(symbol: str, entry_price: float, exit_price: float, direction: str) -> float:
    """
    Calculate profit/loss in pips.

    Args:
        symbol: Currency pair symbol
        entry_price: Entry price
        exit_price: Exit price
        direction: 'LONG' or 'SHORT'

    Returns:
        Profit/loss in pips (positive or negative)
    """
    pip_size = PIP_SIZES.get(symbol, 0.0001)
    price_diff = exit_price - entry_price

    if direction == 'SHORT':
        price_diff = -price_diff

    pips = price_diff / pip_size
    return round(pips, 2)


def calculate_position_size(
    account_balance: float,
    risk_pct: float,
    sl_distance_pips: float,
    symbol: str
) -> float:
    """
    Calculate position size based on risk parameters.

    Args:
        account_balance: Current account balance
        risk_pct: Risk percentage per trade (e.g., 1.0 for 1%)
        sl_distance_pips: Stop-loss distance in pips
        symbol: Currency pair symbol

    Returns:
        Position size in lots (rounded to 0.01)
    """
    risk_amount = account_balance * (risk_pct / 100)
    pip_value = PIP_VALUES.get(symbol, 0.10)

    # Position size in lots
    position_size = risk_amount / (sl_distance_pips * pip_value)

    # Round down to 0.01 (micro lot)
    position_size = round(position_size, 2)

    # Ensure minimum lot size
    if position_size < 0.01:
        position_size = 0.01

    return position_size


def calculate_profit_loss(
    entry_price: float,
    exit_price: float,
    position_size: float,
    symbol: str,
    direction: str
) -> float:
    """
    Calculate profit/loss in dollars.

    Args:
        entry_price: Entry price
        exit_price: Exit price
        position_size: Position size in lots
        symbol: Currency pair symbol
        direction: 'LONG' or 'SHORT'

    Returns:
        Profit/loss in dollars
    """
    pips = calculate_pips(symbol, entry_price, exit_price, direction)
    pip_value = PIP_VALUES.get(symbol, 0.10)

    # P&L = pips × pip_value × position_size
    pl = pips * pip_value * position_size
    return round(pl, 2)


def is_market_open(current_time: Optional[datetime] = None) -> bool:
    """
    Check if forex market is open.
    Forex is open 24/5 (Monday to Friday).

    Args:
        current_time: Time to check (defaults to now)

    Returns:
        True if market is open, False otherwise
    """
    if current_time is None:
        current_time = datetime.utcnow()

    # Check if weekend (Saturday = 5, Sunday = 6)
    if current_time.weekday() >= 5:
        return False

    # Market opens Sunday 10pm UTC and closes Friday 10pm UTC
    # For simplicity, we'll consider Monday-Friday as open
    return True


def format_price(price: float, symbol: str) -> str:
    """
    Format price according to symbol conventions.

    Args:
        price: Price value
        symbol: Currency pair symbol

    Returns:
        Formatted price string
    """
    if symbol == 'XAUUSD':
        return f"{price:.2f}"
    else:
        return f"{price:.5f}"


def validate_trade_params(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    direction: str
) -> tuple[bool, Optional[str]]:
    """
    Validate trade parameters are logical.

    Args:
        entry_price: Entry price
        stop_loss: Stop-loss price
        take_profit: Take-profit price
        direction: Trade direction ('LONG' or 'SHORT')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if direction == 'LONG':
        if stop_loss >= entry_price:
            return False, "Stop-loss must be below entry price for LONG"
        if take_profit <= entry_price:
            return False, "Take-profit must be above entry price for LONG"
    elif direction == 'SHORT':
        if stop_loss <= entry_price:
            return False, "Stop-loss must be above entry price for SHORT"
        if take_profit >= entry_price:
            return False, "Take-profit must be below entry price for SHORT"
    else:
        return False, "Direction must be 'LONG' or 'SHORT'"

    return True, None


def get_date_range(days: int) -> tuple[datetime, datetime]:
    """
    Get date range from today going back specified days.

    Args:
        days: Number of days to go back

    Returns:
        Tuple of (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date
