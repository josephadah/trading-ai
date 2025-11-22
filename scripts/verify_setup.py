"""
Setup verification script.
Checks that all components are properly configured.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from database.connection import engine
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        logger.info(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"✗ Python version {version.major}.{version.minor} (need 3.11+)")
        return False


def check_virtual_environment():
    """Check if running in virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("✓ Virtual environment: Active")
        return True
    else:
        logger.warning("⚠ Virtual environment: Not detected (recommended to use venv)")
        return True  # Not critical


def check_packages():
    """Check if required packages are installed."""
    required_packages = [
        'pandas',
        'numpy',
        'sqlalchemy',
        'psycopg2',
        'yfinance',
        'pandas_ta',
        'plotly',
        'dotenv',
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ Package installed: {package}")
        except ImportError:
            logger.error(f"✗ Package missing: {package}")
            all_installed = False

    return all_installed


def check_database_connection():
    """Check database connection."""
    try:
        with engine.connect() as conn:
            logger.info("✓ Database connection: Success")
            logger.info(f"  Database: {Config.DB_NAME}")
            logger.info(f"  Host: {Config.DB_HOST}:{Config.DB_PORT}")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection: Failed")
        logger.error(f"  Error: {e}")
        return False


def check_database_tables():
    """Check if database tables exist."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'market_data',
            'indicators',
            'signals',
            'backtest_trades',
            'backtest_runs',
            'live_trades'
        ]

        all_exist = True
        for table in expected_tables:
            if table in tables:
                logger.info(f"✓ Table exists: {table}")
            else:
                logger.error(f"✗ Table missing: {table}")
                all_exist = False

        return all_exist
    except Exception as e:
        logger.error(f"✗ Could not check tables: {e}")
        return False


def check_project_structure():
    """Check if project directories exist."""
    project_root = Path(__file__).parent.parent
    required_dirs = [
        'data/raw',
        'data/processed',
        'database',
        'ingestion',
        'analysis',
        'strategy',
        'backtesting',
        'visualization',
        'utils',
        'scripts',
        'tests',
        'logs',
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            logger.info(f"✓ Directory exists: {dir_path}")
        else:
            logger.error(f"✗ Directory missing: {dir_path}")
            all_exist = False

    return all_exist


def check_environment_variables():
    """Check if environment variables are loaded."""
    required_vars = [
        'DB_HOST',
        'DB_PORT',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
    ]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"✓ Environment variable set: {var}")
        else:
            logger.error(f"✗ Environment variable missing: {var}")
            all_set = False

    return all_set


def main():
    """Run all verification checks."""
    logger.info("=" * 60)
    logger.info("Trading System Setup Verification")
    logger.info("=" * 60)
    logger.info("")

    checks = []

    # Python version
    logger.info("1. Checking Python version...")
    checks.append(check_python_version())
    logger.info("")

    # Virtual environment
    logger.info("2. Checking virtual environment...")
    checks.append(check_virtual_environment())
    logger.info("")

    # Environment variables
    logger.info("3. Checking environment variables...")
    checks.append(check_environment_variables())
    logger.info("")

    # Required packages
    logger.info("4. Checking required packages...")
    checks.append(check_packages())
    logger.info("")

    # Project structure
    logger.info("5. Checking project structure...")
    checks.append(check_project_structure())
    logger.info("")

    # Database connection
    logger.info("6. Checking database connection...")
    checks.append(check_database_connection())
    logger.info("")

    # Database tables
    logger.info("7. Checking database tables...")
    checks.append(check_database_tables())
    logger.info("")

    # Summary
    logger.info("=" * 60)
    passed = sum(checks)
    total = len(checks)

    if all(checks):
        logger.info(f"✓ All checks passed ({passed}/{total})")
        logger.info("\nSetup verification complete!")
        logger.info("\nYour system is ready for development.")
        logger.info("\nNext step: Download historical data")
        logger.info("  python scripts/download_historical.py")
    else:
        logger.error(f"✗ Some checks failed ({passed}/{total} passed)")
        logger.error("\nPlease fix the issues above before continuing.")
        sys.exit(1)

    logger.info("=" * 60)


if __name__ == '__main__':
    main()
