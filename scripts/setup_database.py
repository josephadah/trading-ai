"""
Database setup script.
Creates all necessary tables in the PostgreSQL database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import engine, init_db, Base
from database.models import MarketData, Indicator, Signal, BacktestTrade, BacktestRun, LiveTrade
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)


def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("Trading System Database Setup")
    logger.info("=" * 60)

    # Display configuration
    logger.info(f"Database: {Config.DB_NAME}")
    logger.info(f"Host: {Config.DB_HOST}:{Config.DB_PORT}")
    logger.info(f"User: {Config.DB_USER}")
    logger.info("")

    try:
        # Test connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            logger.info("✓ Database connection successful")

        # Create tables
        logger.info("\nCreating database tables...")
        init_db()

        # Verify tables created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        logger.info(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table}")

        logger.info("\n" + "=" * 60)
        logger.info("Database setup completed successfully!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Download historical data: python scripts/download_historical.py")
        logger.info("2. Verify setup: python scripts/verify_setup.py")

    except Exception as e:
        logger.error(f"\n✗ Database setup failed: {e}")
        logger.error("\nPlease check:")
        logger.error("1. PostgreSQL is running")
        logger.error("2. Database 'trading_ai' exists")
        logger.error("3. Credentials in .env file are correct")
        logger.error("4. User has necessary permissions")
        sys.exit(1)


if __name__ == '__main__':
    main()
