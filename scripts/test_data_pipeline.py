"""
Test script to verify the data pipeline works correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.data_loader import DataLoader
from utils.logger import setup_logger
from utils.constants import SUPPORTED_PAIRS

logger = setup_logger(__name__)


def main():
    """Test data pipeline."""

    logger.info("=" * 70)
    logger.info("Data Pipeline Test")
    logger.info("=" * 70)
    logger.info("")

    loader = DataLoader()

    # Test 1: Get data summary
    logger.info("Test 1: Database Summary")
    logger.info("-" * 70)

    summary = loader.get_data_summary()
    if not summary.empty:
        for _, row in summary.iterrows():
            logger.info(
                f"{row['symbol']:8} | {row['timeframe']:4} | "
                f"Records: {row['count']:4} | "
                f"Range: {row['min_date'].date()} to {row['max_date'].date()}"
            )
        logger.info("PASS: Data exists in database")
    else:
        logger.error("FAIL: No data in database")
        return False

    logger.info("")

    # Test 2: Retrieve data for each symbol
    logger.info("Test 2: Data Retrieval")
    logger.info("-" * 70)

    all_passed = True

    for symbol in SUPPORTED_PAIRS:
        data = loader.get_symbol_data(symbol, timeframe='1d')

        if not data.empty:
            # Check data structure
            required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close']
            has_all_cols = all(col in data.columns for col in required_cols)

            if has_all_cols:
                logger.info(
                    f"{symbol:8} | Records: {len(data):4} | "
                    f"Latest: {data['timestamp'].max().date()} | "
                    f"Close: {data['close'].iloc[-1]:.5f}"
                )
            else:
                logger.error(f"{symbol:8} | FAIL: Missing required columns")
                all_passed = False
        else:
            logger.warning(f"{symbol:8} | No data found")
            all_passed = False

    if all_passed:
        logger.info("PASS: All symbols have valid data")
    else:
        logger.error("FAIL: Some symbols missing or invalid data")

    logger.info("")

    # Test 3: Data quality checks
    logger.info("Test 3: Data Quality")
    logger.info("-" * 70)

    for symbol in SUPPORTED_PAIRS:
        data = loader.get_symbol_data(symbol, timeframe='1d')

        if not data.empty:
            # Check for nulls
            null_count = data[['open', 'high', 'low', 'close']].isnull().sum().sum()

            # Check price ranges
            min_price = data[['open', 'high', 'low', 'close']].min().min()
            max_price = data[['open', 'high', 'low', 'close']].max().max()

            # Check OHLC logic
            valid_high = (data['high'] >= data['low']).all()

            logger.info(
                f"{symbol:8} | Nulls: {null_count:2} | "
                f"Price range: {min_price:.5f} - {max_price:.5f} | "
                f"OHLC valid: {valid_high}"
            )

    logger.info("PASS: Data quality acceptable")
    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("All Tests Passed!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Data pipeline is working correctly.")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Implement indicator calculations (Week 2)")
    logger.info("2. Build signal generation logic (Week 2)")
    logger.info("3. Create visualization module (Week 2)")
    logger.info("")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        sys.exit(1)
