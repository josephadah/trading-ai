"""
Create interactive charts for visualization.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.data_loader import DataLoader
from analysis.indicators import add_indicators_to_data
from visualization.charts import create_price_chart
from utils.logger import setup_logger
from utils.constants import SUPPORTED_PAIRS

logger = setup_logger(__name__)


def main():
    """Create charts for all symbols."""

    logger.info("=" * 70)
    logger.info("Creating Charts")
    logger.info("=" * 70)
    logger.info("")

    # Create output directory
    output_dir = Path("charts")
    output_dir.mkdir(exist_ok=True)

    loader = DataLoader()

    for symbol in SUPPORTED_PAIRS:
        logger.info(f"Creating chart for {symbol}...")

        # Load data
        data = loader.get_symbol_data(symbol, '1d')

        if data.empty:
            logger.warning(f"No data for {symbol}")
            continue

        # Add indicators
        data = add_indicators_to_data(data)

        # Create chart
        output_file = output_dir / f"{symbol}_chart.html"

        fig = create_price_chart(
            data=data,
            symbol=symbol,
            show_indicators=True,
            show_signals=False,  # No signals to show yet
            output_file=str(output_file)
        )

        logger.info(f"Chart saved to {output_file}")
        logger.info("")

    logger.info("=" * 70)
    logger.info("Charts created successfully!")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"Open charts in your browser from the 'charts/' directory")
    logger.info("")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Error creating charts: {e}", exc_info=True)
        sys.exit(1)
