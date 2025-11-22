"""
Configuration management for the trading system.
Loads settings from environment variables and .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Application configuration."""

    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'trading_ai')
    DB_USER = os.getenv('DB_USER', 'trading_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    # Construct database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Data Sources
    TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')

    # Risk Management
    RISK_PER_TRADE_PCT = float(os.getenv('RISK_PER_TRADE_PCT', 1.0))
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 800))

    # Trading Parameters
    DEFAULT_SPREAD_EUR = float(os.getenv('DEFAULT_SPREAD_EUR', 0.0002))
    DEFAULT_SPREAD_GBP = float(os.getenv('DEFAULT_SPREAD_GBP', 0.0003))
    DEFAULT_SPREAD_XAU = float(os.getenv('DEFAULT_SPREAD_XAU', 0.50))

    # Strategy Parameters
    EMA_SHORT = int(os.getenv('EMA_SHORT', 20))
    EMA_LONG = int(os.getenv('EMA_LONG', 50))
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    ATR_PERIOD = int(os.getenv('ATR_PERIOD', 14))
    RISK_REWARD_RATIO = float(os.getenv('RISK_REWARD_RATIO', 2.5))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading_ai.log')

    # Environment
    ENV = os.getenv('ENV', 'development')

    # Paths
    DATA_DIR = BASE_DIR / 'data'
    RAW_DATA_DIR = DATA_DIR / 'raw'
    PROCESSED_DATA_DIR = DATA_DIR / 'processed'
    LOGS_DIR = BASE_DIR / 'logs'

    @classmethod
    def get_spread(cls, symbol: str) -> float:
        """Get default spread for a symbol."""
        spreads = {
            'EURUSD': cls.DEFAULT_SPREAD_EUR,
            'GBPUSD': cls.DEFAULT_SPREAD_GBP,
            'XAUUSD': cls.DEFAULT_SPREAD_XAU,
        }
        return spreads.get(symbol, 0.0003)  # Default 3 pips

    @classmethod
    def validate(cls):
        """Validate configuration."""
        errors = []

        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD not set")

        if cls.RISK_PER_TRADE_PCT <= 0 or cls.RISK_PER_TRADE_PCT > 5:
            errors.append("RISK_PER_TRADE_PCT must be between 0 and 5")

        if cls.INITIAL_CAPITAL <= 0:
            errors.append("INITIAL_CAPITAL must be positive")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True


# Validate configuration on import
if os.getenv('SKIP_CONFIG_VALIDATION') != 'true':
    try:
        Config.validate()
    except ValueError as e:
        print(f"Warning: {e}")
        print("Please check your .env file")
