"""
Data fetcher module for downloading market data from Yahoo Finance.
Handles downloading OHLC data for supported currency pairs.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
from utils.logger import setup_logger
from utils.constants import YAHOO_SYMBOLS, SUPPORTED_PAIRS

logger = setup_logger(__name__)


class DataFetcher:
    """Fetches market data from Yahoo Finance."""

    def __init__(self):
        """Initialize the data fetcher."""
        self.yahoo_symbols = YAHOO_SYMBOLS

    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = '6mo',
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data for a symbol from Yahoo Finance.

        Args:
            symbol: Trading pair symbol (e.g., 'EURUSD', 'GBPUSD')
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            period: Period to download (if start_date not provided)
                    Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval: Data interval
                     Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume, Date
            None if download fails
        """
        if symbol not in SUPPORTED_PAIRS:
            logger.error(f"Unsupported symbol: {symbol}. Supported: {SUPPORTED_PAIRS}")
            return None

        yahoo_symbol = self.yahoo_symbols.get(symbol)
        if not yahoo_symbol:
            logger.error(f"No Yahoo Finance mapping for symbol: {symbol}")
            return None

        try:
            logger.info(f"Fetching data for {symbol} ({yahoo_symbol})...")

            # Download data
            if start_date and end_date:
                data = yf.download(
                    yahoo_symbol,
                    start=start_date,
                    end=end_date,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )
            else:
                data = yf.download(
                    yahoo_symbol,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )

            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            # Clean up the data
            data = self._clean_data(data, symbol)

            logger.info(f"Successfully fetched {len(data)} rows for {symbol}")
            logger.info(f"Date range: {data.index[0]} to {data.index[-1]}")

            return data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def _clean_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """
        Clean and standardize the downloaded data.

        Args:
            data: Raw DataFrame from yfinance
            symbol: Symbol being processed

        Returns:
            Cleaned DataFrame
        """
        # Reset index to make Date a column
        data = data.reset_index()

        # Handle MultiIndex columns from yfinance (when downloading single symbol)
        if isinstance(data.columns, pd.MultiIndex):
            # Flatten MultiIndex by taking the first level (column name)
            data.columns = data.columns.get_level_values(0)

        # Rename columns to standard format
        column_mapping = {
            'Date': 'timestamp',
            'Datetime': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Price': 'close'  # Sometimes yfinance uses 'Price' instead of 'Close'
        }

        # Only rename columns that exist
        existing_cols = {k: v for k, v in column_mapping.items() if k in data.columns}
        data = data.rename(columns=existing_cols)

        # Add symbol column
        data['symbol'] = symbol

        # Select required columns
        required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close']
        optional_cols = ['volume']

        # Include volume if it exists
        final_cols = required_cols.copy()
        if 'volume' in data.columns:
            final_cols.append('volume')

        data = data[final_cols]

        # Remove any rows with NaN in OHLC data
        data = data.dropna(subset=['open', 'high', 'low', 'close'])

        # Sort by timestamp
        data = data.sort_values('timestamp')

        # Reset index
        data = data.reset_index(drop=True)

        return data

    def fetch_multiple(
        self,
        symbols: list,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = '6mo',
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.

        Args:
            symbols: List of symbol strings
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            period: Period to download (if dates not provided)
            interval: Data interval

        Returns:
            Dictionary mapping symbol -> DataFrame
        """
        results = {}

        logger.info(f"Fetching data for {len(symbols)} symbols...")

        for symbol in symbols:
            data = self.fetch_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                period=period,
                interval=interval
            )

            if data is not None:
                results[symbol] = data
            else:
                logger.warning(f"Failed to fetch data for {symbol}")

        logger.info(f"Successfully fetched data for {len(results)}/{len(symbols)} symbols")

        return results

    def get_latest_data(
        self,
        symbol: str,
        days: int = 5
    ) -> Optional[pd.DataFrame]:
        """
        Get the most recent data for a symbol.

        Args:
            symbol: Trading pair symbol
            days: Number of days to fetch

        Returns:
            DataFrame with latest data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.fetch_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )


def fetch_historical_data(
    symbols: list = None,
    months: int = 6,
    interval: str = '1d'
) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to fetch historical data for multiple symbols.

    Args:
        symbols: List of symbols (defaults to all supported pairs)
        months: Number of months of historical data
        interval: Data interval

    Returns:
        Dictionary of symbol -> DataFrame
    """
    if symbols is None:
        symbols = SUPPORTED_PAIRS

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    fetcher = DataFetcher()
    return fetcher.fetch_multiple(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )
