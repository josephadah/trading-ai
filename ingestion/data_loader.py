"""
Data loader module for loading market data into the database.
Handles bulk inserts and duplicate detection.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_

from database.connection import SessionLocal, engine
from database.models import MarketData
from utils.logger import setup_logger
from utils.constants import TIMEFRAME_DAILY

logger = setup_logger(__name__)


class DataLoader:
    """Loads market data into the database."""

    def __init__(self):
        """Initialize the data loader."""
        pass

    def load_data(
        self,
        data: pd.DataFrame,
        symbol: str,
        timeframe: str = TIMEFRAME_DAILY,
        replace_existing: bool = False
    ) -> Tuple[int, int]:
        """
        Load market data into the database.

        Args:
            data: DataFrame with market data (columns: timestamp, open, high, low, close, volume)
            symbol: Trading pair symbol
            timeframe: Timeframe of the data (e.g., '1d')
            replace_existing: If True, delete existing data for this symbol/timeframe first

        Returns:
            Tuple of (inserted_count, skipped_count)
        """
        if data.empty:
            logger.warning(f"No data to load for {symbol}")
            return 0, 0

        session = SessionLocal()
        inserted = 0
        skipped = 0

        try:
            # Delete existing data if requested
            if replace_existing:
                deleted = session.query(MarketData).filter(
                    and_(
                        MarketData.symbol == symbol,
                        MarketData.timeframe == timeframe
                    )
                ).delete()
                session.commit()
                if deleted > 0:
                    logger.info(f"Deleted {deleted} existing records for {symbol}")

            # Get existing timestamps to avoid duplicates
            existing_timestamps = set()
            if not replace_existing:
                existing = session.query(MarketData.timestamp).filter(
                    and_(
                        MarketData.symbol == symbol,
                        MarketData.timeframe == timeframe
                    )
                ).all()
                existing_timestamps = {ts[0] for ts in existing}

            # Prepare records for insertion
            records = []
            for _, row in data.iterrows():
                timestamp = pd.to_datetime(row['timestamp'])

                # Skip if already exists
                if timestamp in existing_timestamps:
                    skipped += 1
                    continue

                record = MarketData(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row.get('volume', 0)) if pd.notna(row.get('volume')) else None,
                    created_at=datetime.utcnow()
                )
                records.append(record)

            # Bulk insert
            if records:
                session.bulk_save_objects(records)
                session.commit()
                inserted = len(records)
                logger.info(
                    f"Loaded {inserted} records for {symbol} "
                    f"(skipped {skipped} duplicates)"
                )
            else:
                logger.info(f"No new records to load for {symbol} (all duplicates)")

            return inserted, skipped

        except Exception as e:
            session.rollback()
            logger.error(f"Error loading data for {symbol}: {e}")
            raise

        finally:
            session.close()

    def load_multiple(
        self,
        data_dict: Dict[str, pd.DataFrame],
        timeframe: str = TIMEFRAME_DAILY,
        replace_existing: bool = False
    ) -> Dict[str, Tuple[int, int]]:
        """
        Load data for multiple symbols.

        Args:
            data_dict: Dictionary mapping symbol -> DataFrame
            timeframe: Timeframe of the data
            replace_existing: If True, delete existing data first

        Returns:
            Dictionary mapping symbol -> (inserted_count, skipped_count)
        """
        results = {}

        logger.info(f"Loading data for {len(data_dict)} symbols...")

        for symbol, data in data_dict.items():
            try:
                inserted, skipped = self.load_data(
                    data=data,
                    symbol=symbol,
                    timeframe=timeframe,
                    replace_existing=replace_existing
                )
                results[symbol] = (inserted, skipped)
            except Exception as e:
                logger.error(f"Failed to load data for {symbol}: {e}")
                results[symbol] = (0, 0)

        # Summary
        total_inserted = sum(inserted for inserted, _ in results.values())
        total_skipped = sum(skipped for _, skipped in results.values())

        logger.info(
            f"Loading complete: {total_inserted} records inserted, "
            f"{total_skipped} duplicates skipped"
        )

        return results

    def get_data_summary(self) -> pd.DataFrame:
        """
        Get a summary of data in the database.

        Returns:
            DataFrame with columns: symbol, timeframe, count, min_date, max_date
        """
        session = SessionLocal()

        try:
            # Query for summary stats
            from sqlalchemy import func

            query = session.query(
                MarketData.symbol,
                MarketData.timeframe,
                func.count(MarketData.id).label('count'),
                func.min(MarketData.timestamp).label('min_date'),
                func.max(MarketData.timestamp).label('max_date')
            ).group_by(
                MarketData.symbol,
                MarketData.timeframe
            ).order_by(
                MarketData.symbol,
                MarketData.timeframe
            )

            results = query.all()

            # Convert to DataFrame
            if results:
                df = pd.DataFrame(results, columns=[
                    'symbol', 'timeframe', 'count', 'min_date', 'max_date'
                ])
                return df
            else:
                return pd.DataFrame(columns=[
                    'symbol', 'timeframe', 'count', 'min_date', 'max_date'
                ])

        finally:
            session.close()

    def get_symbol_data(
        self,
        symbol: str,
        timeframe: str = TIMEFRAME_DAILY,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        """
        Retrieve market data from the database.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe of the data
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            DataFrame with market data
        """
        session = SessionLocal()

        try:
            query = session.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                )
            )

            # Apply date filters
            if start_date:
                query = query.filter(MarketData.timestamp >= start_date)
            if end_date:
                query = query.filter(MarketData.timestamp <= end_date)

            # Order by timestamp
            query = query.order_by(MarketData.timestamp)

            # Execute and convert to DataFrame
            results = query.all()

            if not results:
                logger.warning(f"No data found for {symbol} ({timeframe})")
                return pd.DataFrame()

            # Convert to DataFrame
            data = pd.DataFrame([
                {
                    'timestamp': r.timestamp,
                    'symbol': r.symbol,
                    'open': r.open,
                    'high': r.high,
                    'low': r.low,
                    'close': r.close,
                    'volume': r.volume
                }
                for r in results
            ])

            logger.info(f"Retrieved {len(data)} records for {symbol}")
            return data

        finally:
            session.close()

    def delete_symbol_data(
        self,
        symbol: str,
        timeframe: str = TIMEFRAME_DAILY
    ) -> int:
        """
        Delete all data for a symbol and timeframe.

        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe of the data

        Returns:
            Number of records deleted
        """
        session = SessionLocal()

        try:
            deleted = session.query(MarketData).filter(
                and_(
                    MarketData.symbol == symbol,
                    MarketData.timeframe == timeframe
                )
            ).delete()

            session.commit()
            logger.info(f"Deleted {deleted} records for {symbol} ({timeframe})")

            return deleted

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting data for {symbol}: {e}")
            raise

        finally:
            session.close()


def load_data_to_db(
    data: pd.DataFrame,
    symbol: str,
    timeframe: str = TIMEFRAME_DAILY,
    replace_existing: bool = False
) -> Tuple[int, int]:
    """
    Convenience function to load data to database.

    Args:
        data: DataFrame with market data
        symbol: Trading pair symbol
        timeframe: Timeframe of the data
        replace_existing: If True, delete existing data first

    Returns:
        Tuple of (inserted_count, skipped_count)
    """
    loader = DataLoader()
    return loader.load_data(data, symbol, timeframe, replace_existing)
