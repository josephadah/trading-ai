"""
Generate trading signals and store in database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy import and_
from database.connection import SessionLocal
from database.models import Signal
from ingestion.data_loader import DataLoader
from analysis.indicators import add_indicators_to_data
from analysis.signal_generator import SignalGenerator
from utils.logger import setup_logger
from utils.constants import SUPPORTED_PAIRS, STATUS_PENDING

logger = setup_logger(__name__)


def generate_and_store_signals(
    symbol: str,
    timeframe: str = '1d',
    replace_existing: bool = False
) -> int:
    """
    Generate signals for a symbol and store in database.

    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe of the data
        replace_existing: If True, delete and regenerate all signals

    Returns:
        Number of signals generated
    """
    logger.info(f"Generating signals for {symbol}...")

    # Load market data
    loader = DataLoader()
    data = loader.get_symbol_data(symbol, timeframe)

    if data.empty:
        logger.warning(f"No market data found for {symbol}")
        return 0

    # Add indicators
    logger.info(f"Calculating indicators for {symbol}...")
    data_with_indicators = add_indicators_to_data(data)

    # Generate signals
    generator = SignalGenerator()
    signals = generator.scan_for_signals(data_with_indicators, symbol)

    if not signals:
        logger.info(f"No signals found for {symbol}")
        return 0

    # Store in database
    session = SessionLocal()
    inserted = 0

    try:
        # Delete existing signals if requested
        if replace_existing:
            deleted = session.query(Signal).filter(
                Signal.symbol == symbol
            ).delete()
            session.commit()
            if deleted > 0:
                logger.info(f"Deleted {deleted} existing signals")

        # Prepare signal records
        records = []
        for signal_data in signals:
            record = Signal(
                symbol=signal_data['symbol'],
                signal_date=signal_data['signal_date'],
                signal_type=signal_data['signal_type'],
                entry_price=float(signal_data['entry_price']),
                stop_loss=float(signal_data['stop_loss']),
                take_profit=float(signal_data['take_profit']),
                sl_pips=float(signal_data['sl_pips']),
                tp_pips=float(signal_data['tp_pips']),
                risk_reward_ratio=float(signal_data['risk_reward_ratio']),
                reasoning=signal_data['reasoning'],
                status=STATUS_PENDING,
                created_at=datetime.utcnow()
            )
            records.append(record)

        # Bulk insert
        if records:
            session.bulk_save_objects(records)
            session.commit()
            inserted = len(records)
            logger.info(f"Inserted {inserted} signals for {symbol}")

        return inserted

    except Exception as e:
        session.rollback()
        logger.error(f"Error storing signals for {symbol}: {e}")
        raise

    finally:
        session.close()


def get_signal_summary():
    """Get summary of signals in database."""
    session = SessionLocal()

    try:
        from sqlalchemy import func

        query = session.query(
            Signal.symbol,
            Signal.signal_type,
            func.count(Signal.id).label('count')
        ).group_by(
            Signal.symbol,
            Signal.signal_type
        ).order_by(
            Signal.symbol,
            Signal.signal_type
        )

        results = query.all()

        if results:
            import pandas as pd
            df = pd.DataFrame(results, columns=['symbol', 'signal_type', 'count'])
            return df
        else:
            import pandas as pd
            return pd.DataFrame(columns=['symbol', 'signal_type', 'count'])

    finally:
        session.close()


def display_recent_signals(limit: int = 10):
    """Display recent signals."""
    session = SessionLocal()

    try:
        signals = session.query(Signal).order_by(
            Signal.signal_date.desc()
        ).limit(limit).all()

        if signals:
            logger.info(f"\nMost recent {len(signals)} signals:")
            logger.info("-" * 100)

            for signal in signals:
                logger.info(
                    f"{signal.signal_date.date()} | {signal.symbol:8} | "
                    f"{signal.signal_type:4} | Entry: {signal.entry_price:.5f} | "
                    f"SL: {signal.sl_pips:5.1f}p | TP: {signal.tp_pips:6.1f}p | "
                    f"R:R {signal.risk_reward_ratio:.2f}"
                )

            logger.info("-" * 100)
        else:
            logger.info("No signals in database")

    finally:
        session.close()


def main():
    """Main function."""

    logger.info("=" * 70)
    logger.info("Signal Generation")
    logger.info("=" * 70)
    logger.info("")

    symbols = SUPPORTED_PAIRS
    timeframe = '1d'
    replace_existing = False

    logger.info(f"Configuration:")
    logger.info(f"  Symbols: {symbols}")
    logger.info(f"  Timeframe: {timeframe}")
    logger.info(f"  Replace existing: {replace_existing}")
    logger.info("")

    # Generate signals for each symbol
    total_generated = 0

    for symbol in symbols:
        try:
            generated = generate_and_store_signals(
                symbol=symbol,
                timeframe=timeframe,
                replace_existing=replace_existing
            )
            total_generated += generated
            logger.info("")

        except Exception as e:
            logger.error(f"Failed to process {symbol}: {e}")
            logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("Signal Generation Complete - Summary")
    logger.info("=" * 70)

    summary = get_signal_summary()

    if not summary.empty:
        logger.info("\nSignals by symbol and type:")
        for _, row in summary.iterrows():
            logger.info(
                f"{row['symbol']:8} | {row['signal_type']:4} | Count: {row['count']:3}"
            )

        total_signals = summary['count'].sum()
        logger.info(f"\nTotal signals generated: {total_signals}")
    else:
        logger.info("\nNo signals generated")

    logger.info("")

    # Display recent signals
    display_recent_signals(limit=10)

    logger.info("")
    logger.info("=" * 70)
    logger.info("Signal generation completed successfully!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Review signals: SELECT * FROM signals ORDER BY signal_date DESC;")
    logger.info("2. Build backtesting engine (Week 3)")
    logger.info("")


if __name__ == '__main__':
    import pandas as pd

    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nSignal generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        sys.exit(1)
