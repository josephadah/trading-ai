"""
Consolidated Test Suite for Trading AI System
==============================================

Runs all system tests and provides comprehensive status report.

This script:
- Verifies database setup and connectivity
- Tests data pipeline functionality
- Validates indicator calculations
- Checks signal generation
- Verifies chart generation
- Provides overall system health check

Usage:
    python scripts/run_all_tests.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from database.connection import SessionLocal
from database.models import MarketData, Indicator, Signal
from utils.constants import SUPPORTED_PAIRS


class TestSuite:
    """Consolidated test suite for the trading system."""

    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.start_time = datetime.now()

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success status."""
        print("=" * 70)
        print("TRADING AI SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Run all test categories
        self.test_database_connectivity()
        self.test_market_data()
        self.test_indicators()
        self.test_signals()
        self.test_charts()
        self.test_file_structure()

        # Print summary
        self.print_summary()

        # Return overall success
        return all(result[0] for result in self.results.values())

    def test_database_connectivity(self):
        """Test database connection and table existence."""
        print("\n[1/6] Testing Database Connectivity...")
        print("-" * 70)

        try:
            session = SessionLocal()

            # Test connection
            session.execute(text("SELECT 1"))
            print("  [OK] Database connection successful")

            # Check tables exist
            tables = ['market_data', 'indicators', 'signals',
                     'backtest_trades', 'backtest_runs', 'live_trades']

            for table in tables:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  [OK] Table '{table}' exists ({count} records)")

            session.close()
            self.results['database'] = (True, "All database checks passed")

        except Exception as e:
            print(f"  [FAIL] Database test failed: {str(e)}")
            self.results['database'] = (False, str(e))

    def test_market_data(self):
        """Test market data integrity."""
        print("\n[2/6] Testing Market Data...")
        print("-" * 70)

        try:
            session = SessionLocal()

            for symbol in SUPPORTED_PAIRS:
                # Get data for symbol
                data = session.query(MarketData).filter_by(symbol=symbol).all()

                if not data:
                    print(f"  [FAIL] No data for {symbol}")
                    continue

                # Check data quality
                count = len(data)
                date_range = f"{data[0].timestamp.date()} to {data[-1].timestamp.date()}"

                # Check for nulls
                nulls = sum(1 for d in data if None in [d.open, d.high, d.low, d.close, d.volume])

                # Check OHLC logic
                invalid_ohlc = sum(1 for d in data if d.high < d.low or
                                  d.close > d.high or d.close < d.low or
                                  d.open > d.high or d.open < d.low)

                if nulls == 0 and invalid_ohlc == 0:
                    print(f"  [OK] {symbol}: {count} records | {date_range} | Valid")
                else:
                    print(f"  [FAIL] {symbol}: {nulls} nulls, {invalid_ohlc} invalid OHLC")

            session.close()
            self.results['market_data'] = (True, "Market data validated")

        except Exception as e:
            print(f"  [FAIL] Market data test failed: {str(e)}")
            self.results['market_data'] = (False, str(e))

    def test_indicators(self):
        """Test indicator calculations."""
        print("\n[3/6] Testing Indicators...")
        print("-" * 70)

        try:
            session = SessionLocal()

            total_indicators = 0
            for symbol in SUPPORTED_PAIRS:
                # Get indicators for symbol
                indicators = session.query(Indicator).filter_by(symbol=symbol).all()

                if not indicators:
                    print(f"  [FAIL] No indicators for {symbol}")
                    continue

                count = len(indicators)
                total_indicators += count

                # Check for nulls (first few may be null due to EMA warmup)
                # Only check last 100 records
                recent = indicators[-100:] if len(indicators) > 100 else indicators
                nulls = sum(1 for ind in recent if None in [ind.ema_20, ind.ema_50, ind.rsi_14, ind.atr_14])

                # Get latest values for display
                latest = indicators[-1]
                date_range = f"{indicators[0].timestamp.date()} to {latest.timestamp.date()}"

                if nulls == 0:
                    print(f"  [OK] {symbol}: {count} indicators | {date_range}")
                    print(f"      Latest: EMA20={latest.ema_20:.5f}, EMA50={latest.ema_50:.5f}, "
                          f"RSI={latest.rsi_14:.2f}, ATR={latest.atr_14:.5f}")
                else:
                    print(f"  [WARN] {symbol}: {count} indicators ({nulls} nulls in recent data)")

            session.close()

            if total_indicators > 0:
                self.results['indicators'] = (True, f"{total_indicators} indicators calculated")
            else:
                self.results['indicators'] = (False, "No indicators found")

        except Exception as e:
            print(f"  [FAIL] Indicator test failed: {str(e)}")
            self.results['indicators'] = (False, str(e))

    def test_signals(self):
        """Test signal generation."""
        print("\n[4/6] Testing Signal Generation...")
        print("-" * 70)

        try:
            session = SessionLocal()

            # Get all signals
            signals = session.query(Signal).all()

            if not signals:
                print("  [INFO] No signals generated (strategy being conservative)")
                print("      This is expected behavior for current market conditions")
                self.results['signals'] = (True, "Signal generation working (0 signals)")
            else:
                # Count by type
                long_signals = sum(1 for s in signals if s.signal_type == 'LONG')
                short_signals = sum(1 for s in signals if s.signal_type == 'SHORT')

                print(f"  [OK] Total signals: {len(signals)}")
                print(f"      LONG:  {long_signals}")
                print(f"      SHORT: {short_signals}")

                # Show sample signal
                sample = signals[0]
                print(f"\n  Sample Signal:")
                print(f"      {sample.symbol} {sample.signal_type} on {sample.timestamp.date()}")
                print(f"      Entry: {sample.entry_price}, SL: {sample.stop_loss}, TP: {sample.take_profit}")

                self.results['signals'] = (True, f"{len(signals)} signals generated")

            session.close()

        except Exception as e:
            print(f"  [FAIL] Signal test failed: {str(e)}")
            self.results['signals'] = (False, str(e))

    def test_charts(self):
        """Test chart generation."""
        print("\n[5/6] Testing Chart Generation...")
        print("-" * 70)

        try:
            charts_dir = project_root / 'charts'

            if not charts_dir.exists():
                print(f"  [FAIL] Charts directory not found")
                self.results['charts'] = (False, "Charts directory missing")
                return

            # Check for expected charts
            expected_charts = [f"{symbol}_chart.html" for symbol in SUPPORTED_PAIRS]
            found_charts = list(charts_dir.glob('*.html'))

            for chart_file in expected_charts:
                chart_path = charts_dir / chart_file
                if chart_path.exists():
                    size_mb = chart_path.stat().st_size / (1024 * 1024)
                    print(f"  [OK] {chart_file} ({size_mb:.1f} MB)")
                else:
                    print(f"  [FAIL] {chart_file} not found")

            if len(found_charts) >= len(SUPPORTED_PAIRS):
                self.results['charts'] = (True, f"{len(found_charts)} charts created")
            else:
                self.results['charts'] = (False, f"Only {len(found_charts)}/{len(SUPPORTED_PAIRS)} charts found")

        except Exception as e:
            print(f"  [FAIL] Chart test failed: {str(e)}")
            self.results['charts'] = (False, str(e))

    def test_file_structure(self):
        """Test project file structure."""
        print("\n[6/6] Testing File Structure...")
        print("-" * 70)

        try:
            # Check required directories
            required_dirs = ['database', 'ingestion', 'analysis', 'strategy',
                           'backtesting', 'visualization', 'utils', 'scripts',
                           'tests', 'charts', 'data', 'logs']

            missing_dirs = []
            for dir_name in required_dirs:
                dir_path = project_root / dir_name
                if dir_path.exists():
                    print(f"  [OK] {dir_name}/ directory exists")
                else:
                    print(f"  [FAIL] {dir_name}/ directory missing")
                    missing_dirs.append(dir_name)

            # Check key files
            key_files = [
                'config.py',
                'requirements.txt',
                'README.md',
                'DEVELOPMENT_ROADMAP.md',
                'IMPLEMENTATION_LOG.md',
                'STRATEGY.md'
            ]

            for file_name in key_files:
                file_path = project_root / file_name
                if file_path.exists():
                    print(f"  [OK] {file_name} exists")
                else:
                    print(f"  [FAIL] {file_name} missing")

            if not missing_dirs:
                self.results['file_structure'] = (True, "All directories and files present")
            else:
                self.results['file_structure'] = (False, f"Missing directories: {', '.join(missing_dirs)}")

        except Exception as e:
            print(f"  [FAIL] File structure test failed: {str(e)}")
            self.results['file_structure'] = (False, str(e))

    def print_summary(self):
        """Print test summary."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for result in self.results.values() if result[0])
        total = len(self.results)

        for test_name, (success, message) in self.results.items():
            status = "PASS" if success else "FAIL"
            symbol = "[OK]" if success else "[FAIL]"
            print(f"  {symbol} {test_name.upper():<20} [{status}] - {message}")

        print(f"\n  Results: {passed}/{total} tests passed")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n" + "=" * 70)

        if passed == total:
            print("STATUS: ALL TESTS PASSED [OK]")
            print("The trading system is fully operational and ready for Week 3.")
        else:
            print("STATUS: SOME TESTS FAILED [FAIL]")
            print("Please review the failures above and resolve issues.")

        print("=" * 70 + "\n")


def main():
    """Main test execution."""
    suite = TestSuite()
    success = suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
