"""
Calculate and store technical indicators in the database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy import and_
from database.connection import SessionLocal
from database.models import MarketData, Indicator
from ingestion.data_loader import DataLoader
from analysis.indicators import IndicatorCalculator
from utils.logger import setup_logger
from utils.constants import SUPPORTED_PAIRS

logger = setup_logger(__name__)


def calculate_and_store_indicators(
    symbol: str,
    timeframe: str = '1d',
    replace_existing: bool = False
) -> int:
    """
    Calculate indicators for a symbol and store in database.

    Args:
        symbol: Trading pair symbol
        timeframe: Timeframe of the data
        replace_existing: If True, delete and recalculate all indicators

    Returns:
        Number of indicator records created
    """
    logger.info(f"Calculating indicators for {symbol}...")

    # Load market data
    loader = DataLoader()
    data = loader.get_symbol_data(symbol, timeframe)

    if data.empty:
        logger.warning(f"No market data found for {symbol}")
        return 0

    # Calculate indicators
    calculator = IndicatorCalculator()
    data_with_indicators = calculator.calculate_all_indicators(data)

    # Validate indicators
    calculator.validate_indicators(data_with_indicators)

    # Store in database
    session = SessionLocal()
    inserted = 0

    try:
        # Delete existing indicators if requested
        if replace_existing:
            deleted = session.query(Indicator).filter(
                and_(
                    Indicator.symbol == symbol,
                    Indicator.timestamp.in_(data_with_indicators['timestamp'].tolist())
                )
            ).delete(synchronize_session=False)
            session.commit()
            if deleted > 0:
                logger.info(f"Deleted {deleted} existing indicator records")

        # Get existing market_data IDs
        market_data_records = session.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timeframe == timeframe
            )
        ).all()

        # Create a mapping of timestamp -> market_data_id
        timestamp_to_id = {
            record.timestamp: record.id
            for record in market_data_records
        }

        # Prepare indicator records
        records = []
        for _, row in data_with_indicators.iterrows():
            timestamp = row['timestamp']
            market_data_id = timestamp_to_id.get(timestamp)

            if market_data_id is None:
                logger.warning(f"No market_data record found for {timestamp}")
                continue

            # Skip if we don't have valid indicators yet (early in the series)
            if any(pd.isna(row[col]) for col in ['ema_20', 'ema_50', 'rsi_14', 'atr_14']):
                continue

            record = Indicator(
                market_data_id=market_data_id,
                symbol=symbol,
                timestamp=timestamp,
                ema_20=float(row['ema_20']),
                ema_50=float(row['ema_50']),
                rsi_14=float(row['rsi_14']),
                atr_14=float(row['atr_14']),
                swing_low=float(row['swing_low']) if pd.notna(row['swing_low']) else None,
                swing_high=float(row['swing_high']) if pd.notna(row['swing_high']) else None,
                created_at=datetime.utcnow()
            )
            records.append(record)

        # Bulk insert
        if records:
            session.bulk_save_objects(records)
            session.commit()
            inserted = len(records)
            logger.info(f"Inserted {inserted} indicator records for {symbol}")
        else:
            logger.warning(f"No valid indicators to insert for {symbol}")

        return inserted

    except Exception as e:
        session.rollback()
        logger.error(f"Error storing indicators for {symbol}: {e}")
        raise

    finally:
        session.close()


def get_indicator_summary():
    """Get summary of indicators in database."""
    session = SessionLocal()

    try:
        from sqlalchemy import func

        query = session.query(
            Indicator.symbol,
            func.count(Indicator.id).label('count'),
            func.min(Indicator.timestamp).label('min_date'),
            func.max(Indicator.timestamp).label('max_date')
        ).group_by(
            Indicator.symbol
        ).order_by(
            Indicator.symbol
        )

        results = query.all()

        if results:
            import pandas as pd
            df = pd.DataFrame(results, columns=['symbol', 'count', 'min_date', 'max_date'])
            return df
        else:
            import pandas as pd
            return pd.DataFrame(columns=['symbol', 'count', 'min_date', 'max_date'])

    finally:
        session.close()


def main():
    """Main function."""

    logger.info("=" * 70)
    logger.info("Indicator Calculation")
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

    # Calculate indicators for each symbol
    total_inserted = 0

    for symbol in symbols:
        try:
            inserted = calculate_and_store_indicators(
                symbol=symbol,
                timeframe=timeframe,
                replace_existing=replace_existing
            )
            total_inserted += inserted
            logger.info("")

        except Exception as e:
            logger.error(f"Failed to process {symbol}: {e}")
            logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("Calculation Complete - Summary")
    logger.info("=" * 70)

    summary = get_indicator_summary()

    if not summary.empty:
        for _, row in summary.iterrows():
            logger.info(
                f"{row['symbol']:8} | Indicators: {row['count']:4} | "
                f"Range: {row['min_date'].date()} to {row['max_date'].date()}"
            )
    else:
        logger.info("No indicators in database")

    logger.info("")
    logger.info(f"Total indicator records created: {total_inserted}")
    logger.info("")
    logger.info("=" * 70)
    logger.info("Indicator calculation completed successfully!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Verify indicators: SELECT symbol, COUNT(*) FROM indicators GROUP BY symbol;")
    logger.info("2. Continue to signal generation")
    logger.info("")


if __name__ == '__main__':
    import pandas as pd

    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nCalculation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        sys.exit(1)
