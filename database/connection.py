"""Database connection management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config import Config

# Create base class for declarative models
Base = declarative_base()

# Create database engine
engine = create_engine(
    Config.DATABASE_URL,
    poolclass=NullPool,  # Simpler connection handling for development
    echo=False,  # Set to True to see SQL queries (debugging)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """
    Get a database session.

    Usage:
        with get_session() as session:
            # Do database operations
            session.query(...)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database tables."""
    from database.models import (
        MarketData,
        Indicator,
        Signal,
        BacktestTrade,
        BacktestRun,
        LiveTrade,
    )

    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
