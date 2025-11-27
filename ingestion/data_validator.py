"""
Data validation module for ensuring data quality.
Checks for gaps, anomalies, and data integrity issues.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple, List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    """Validates market data quality."""

    def __init__(self):
        """Initialize the data validator."""
        pass

    def validate(
        self,
        data: pd.DataFrame,
        symbol: str,
        strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a DataFrame of market data.

        Args:
            data: DataFrame with market data
            symbol: Symbol being validated
            strict: If True, fail on any issues; if False, only fail on critical issues

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check if data is empty
        if data.empty:
            issues.append("Data is empty")
            return False, issues

        # Check required columns
        required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
            return False, issues

        # Check for null values in OHLC data
        null_check = data[['open', 'high', 'low', 'close']].isnull().any()
        if null_check.any():
            null_cols = null_check[null_check].index.tolist()
            issues.append(f"Null values found in columns: {null_cols}")
            if strict:
                return False, issues

        # Check OHLC logic (high >= low, etc.)
        ohlc_issues = self._validate_ohlc_logic(data)
        if ohlc_issues:
            issues.extend(ohlc_issues)
            if strict:
                return False, issues

        # Check for price anomalies
        anomalies = self._check_price_anomalies(data, symbol)
        if anomalies:
            issues.extend(anomalies)
            # Anomalies are warnings, not critical errors

        # Check for data gaps
        gaps = self._check_data_gaps(data)
        if gaps:
            issues.append(f"Found {len(gaps)} date gaps: {gaps[:5]}")  # Show first 5
            # Gaps are expected on weekends, so not critical

        # Check data range
        date_range = self._check_date_range(data)
        if date_range:
            issues.append(date_range)

        # Determine if data is valid
        critical_issues = [
            issue for issue in issues
            if any(word in issue.lower() for word in ['missing', 'empty', 'null'])
        ]

        is_valid = len(critical_issues) == 0

        if is_valid:
            logger.info(f"Validation passed for {symbol} ({len(data)} rows)")
            if issues:
                logger.warning(f"Non-critical issues found: {issues}")
        else:
            logger.error(f"Validation failed for {symbol}: {critical_issues}")

        return is_valid, issues

    def _validate_ohlc_logic(self, data: pd.DataFrame) -> List[str]:
        """
        Validate OHLC price logic.

        Args:
            data: Market data DataFrame

        Returns:
            List of validation issues
        """
        issues = []

        # High should be >= Low
        invalid_high_low = data[data['high'] < data['low']]
        if not invalid_high_low.empty:
            issues.append(f"Found {len(invalid_high_low)} rows where high < low")

        # High should be >= Open and Close
        invalid_high = data[(data['high'] < data['open']) | (data['high'] < data['close'])]
        if not invalid_high.empty:
            issues.append(f"Found {len(invalid_high)} rows where high < open or close")

        # Low should be <= Open and Close
        invalid_low = data[(data['low'] > data['open']) | (data['low'] > data['close'])]
        if not invalid_low.empty:
            issues.append(f"Found {len(invalid_low)} rows where low > open or close")

        # Prices should be positive
        invalid_prices = data[
            (data['open'] <= 0) |
            (data['high'] <= 0) |
            (data['low'] <= 0) |
            (data['close'] <= 0)
        ]
        if not invalid_prices.empty:
            issues.append(f"Found {len(invalid_prices)} rows with non-positive prices")

        return issues

    def _check_price_anomalies(
        self,
        data: pd.DataFrame,
        symbol: str,
        threshold: float = 0.10
    ) -> List[str]:
        """
        Check for unusual price movements that might indicate data errors.

        Args:
            data: Market data DataFrame
            symbol: Symbol being checked
            threshold: Maximum allowed daily price change (default 10%)

        Returns:
            List of anomaly warnings
        """
        issues = []

        # Calculate daily returns
        data = data.copy()
        data['return'] = data['close'].pct_change()

        # Find extreme movements
        extreme_moves = data[abs(data['return']) > threshold]

        if not extreme_moves.empty:
            issues.append(
                f"Found {len(extreme_moves)} days with >{threshold*100}% price change "
                f"(may be normal for {symbol})"
            )
            # Log details for investigation
            for idx, row in extreme_moves.head(3).iterrows():
                logger.debug(
                    f"Large move on {row['timestamp']}: "
                    f"{row['return']*100:.2f}% (close: {row['close']})"
                )

        return issues

    def _check_data_gaps(self, data: pd.DataFrame) -> List[str]:
        """
        Check for gaps in the date sequence.

        Args:
            data: Market data DataFrame

        Returns:
            List of date gap descriptions
        """
        gaps = []

        # Sort by timestamp
        data = data.sort_values('timestamp')

        # Convert timestamp to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            data['timestamp'] = pd.to_datetime(data['timestamp'])

        # Check for gaps > 3 days (accounting for weekends)
        for i in range(1, len(data)):
            time_diff = (data.iloc[i]['timestamp'] - data.iloc[i-1]['timestamp']).days

            # More than 3 days is suspicious (accounts for weekends)
            if time_diff > 3:
                gap_str = (
                    f"{data.iloc[i-1]['timestamp'].date()} -> "
                    f"{data.iloc[i]['timestamp'].date()} ({time_diff} days)"
                )
                gaps.append(gap_str)

        return gaps

    def _check_date_range(self, data: pd.DataFrame) -> str:
        """
        Check and report the date range of the data.

        Args:
            data: Market data DataFrame

        Returns:
            Date range information string
        """
        if data.empty:
            return "No data"

        min_date = data['timestamp'].min()
        max_date = data['timestamp'].max()
        num_days = (max_date - min_date).days

        return f"Date range: {min_date} to {max_date} ({num_days} days, {len(data)} records)"

    def validate_multiple(
        self,
        data_dict: Dict[str, pd.DataFrame],
        strict: bool = False
    ) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate multiple symbol datasets.

        Args:
            data_dict: Dictionary mapping symbol -> DataFrame
            strict: If True, fail on any issues

        Returns:
            Dictionary mapping symbol -> (is_valid, issues)
        """
        results = {}

        logger.info(f"Validating {len(data_dict)} datasets...")

        for symbol, data in data_dict.items():
            is_valid, issues = self.validate(data, symbol, strict)
            results[symbol] = (is_valid, issues)

        # Summary
        valid_count = sum(1 for is_valid, _ in results.values() if is_valid)
        logger.info(f"Validation complete: {valid_count}/{len(results)} datasets valid")

        return results


def validate_data(
    data: pd.DataFrame,
    symbol: str,
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a single dataset.

    Args:
        data: DataFrame with market data
        symbol: Symbol being validated
        strict: If True, fail on any issues

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    validator = DataValidator()
    return validator.validate(data, symbol, strict)
