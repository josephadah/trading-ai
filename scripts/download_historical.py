"""
Download historical market data script.
Fetches, validates, and loads historical data for all supported pairs.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from ingestion.data_fetcher import DataFetcher
from ingestion.data_validator import DataValidator
from ingestion.data_loader import DataLoader
from utils.logger import setup_logger
from utils.constants import SUPPORTED_PAIRS
from config import Config

logger = setup_logger(__name__)


def main():
    """Main function to download and load historical data."""

    logger.info("=" * 70)
    logger.info("Historical Data Download")
    logger.info("=" * 70)
    logger.info("")

    # Configuration
    symbols = SUPPORTED_PAIRS
    months = 6  # 6 months of historical data
    interval = '1d'  # Daily data
    replace_existing = False  # Set to True to replace all existing data

    logger.info(f"Configuration:")
    logger.info(f"  Symbols: {symbols}")
    logger.info(f"  Period: {months} months")
    logger.info(f"  Interval: {interval}")
    logger.info(f"  Replace existing: {replace_existing}")
    logger.info("")

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
    logger.info("")

    # Step 1: Fetch data
    logger.info("Step 1/3: Fetching data from Yahoo Finance...")
    logger.info("-" * 70)

    fetcher = DataFetcher()
    data_dict = fetcher.fetch_multiple(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )

    if not data_dict:
        logger.error("No data was fetched. Exiting.")
        sys.exit(1)

    logger.info("")

    # Step 2: Validate data
    logger.info("Step 2/3: Validating data quality...")
    logger.info("-" * 70)

    validator = DataValidator()
    validation_results = validator.validate_multiple(data_dict, strict=False)

    # Check if any critical validation failures
    failed_symbols = [
        symbol for symbol, (is_valid, _) in validation_results.items()
        if not is_valid
    ]

    if failed_symbols:
        logger.warning(f"Validation failed for: {failed_symbols}")
        logger.warning("These symbols will be skipped")

        # Remove failed symbols from data_dict
        for symbol in failed_symbols:
            del data_dict[symbol]

    if not data_dict:
        logger.error("No valid data to load. Exiting.")
        sys.exit(1)

    logger.info("")

    # Step 3: Load data into database
    logger.info("Step 3/3: Loading data into database...")
    logger.info("-" * 70)

    loader = DataLoader()
    load_results = loader.load_multiple(
        data_dict=data_dict,
        timeframe=interval,
        replace_existing=replace_existing
    )

    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("Download Complete - Summary")
    logger.info("=" * 70)

    for symbol in symbols:
        if symbol in data_dict:
            inserted, skipped = load_results.get(symbol, (0, 0))
            is_valid, issues = validation_results[symbol]

            status = "OK" if is_valid else "FAILED"
            logger.info(
                f"{symbol:8} | Status: {status:6} | "
                f"Inserted: {inserted:4} | Skipped: {skipped:4}"
            )

            if issues:
                for issue in issues[:2]:  # Show first 2 issues
                    logger.info(f"         | Issue: {issue}")
        else:
            logger.info(f"{symbol:8} | Status: FAILED | No data fetched")

    logger.info("")

    # Database summary
    logger.info("Current database contents:")
    logger.info("-" * 70)

    summary = loader.get_data_summary()
    if not summary.empty:
        for _, row in summary.iterrows():
            logger.info(
                f"{row['symbol']:8} | {row['timeframe']:4} | "
                f"Records: {row['count']:4} | "
                f"Range: {row['min_date'].date()} to {row['max_date'].date()}"
            )
    else:
        logger.info("No data in database")

    logger.info("")
    logger.info("=" * 70)
    logger.info("Historical data download completed successfully!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Verify data: SELECT symbol, COUNT(*) FROM market_data GROUP BY symbol;")
    logger.info("2. Continue to Week 2: Build indicator calculations")
    logger.info("")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nDownload cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        sys.exit(1)
