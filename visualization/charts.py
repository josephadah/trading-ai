"""
Chart visualization module for displaying price data with indicators and signals.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ChartVisualizer:
    """Create interactive charts for price analysis."""

    def __init__(self):
        """Initialize chart visualizer."""
        pass

    def create_candlestick_chart(
        self,
        data: pd.DataFrame,
        symbol: str,
        show_volume: bool = True,
        show_indicators: bool = True,
        show_signals: bool = False,
        signals: Optional[List[Dict]] = None,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create an interactive candlestick chart with indicators.

        Args:
            data: DataFrame with OHLC data and indicators
            symbol: Trading pair symbol
            show_volume: If True, show volume subplot
            show_indicators: If True, show EMA and RSI indicators
            show_signals: If True, mark entry signals
            signals: List of signal dictionaries
            title: Custom chart title

        Returns:
            Plotly Figure object
        """
        # Determine number of subplots
        rows = 1
        row_heights = [0.7]

        if show_indicators:
            rows += 1
            row_heights.append(0.3)

        if show_volume:
            rows += 1
            row_heights = [0.6, 0.2, 0.2] if show_indicators else [0.8, 0.2]

        # Create subplots
        subplot_titles = []
        if title:
            subplot_titles.append(title)
        else:
            subplot_titles.append(f'{symbol} Daily Chart')

        if show_indicators:
            subplot_titles.append('RSI')

        if show_volume:
            subplot_titles.append('Volume')

        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=row_heights
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data['timestamp'],
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )

        # Add EMAs if available
        if show_indicators and 'ema_20' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=data['ema_20'],
                    name='EMA 20',
                    line=dict(color='blue', width=1.5),
                    opacity=0.7
                ),
                row=1, col=1
            )

        if show_indicators and 'ema_50' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=data['ema_50'],
                    name='EMA 50',
                    line=dict(color='orange', width=1.5),
                    opacity=0.7
                ),
                row=1, col=1
            )

        # Add signals if provided
        if show_signals and signals:
            buy_signals = [s for s in signals if s['signal_type'] == 'BUY']
            sell_signals = [s for s in signals if s['signal_type'] == 'SELL']

            if buy_signals:
                buy_dates = [s['signal_date'] for s in buy_signals]
                buy_prices = [s['entry_price'] for s in buy_signals]

                fig.add_trace(
                    go.Scatter(
                        x=buy_dates,
                        y=buy_prices,
                        mode='markers',
                        name='BUY Signal',
                        marker=dict(
                            symbol='triangle-up',
                            size=12,
                            color='lime',
                            line=dict(color='darkgreen', width=2)
                        )
                    ),
                    row=1, col=1
                )

            if sell_signals:
                sell_dates = [s['signal_date'] for s in sell_signals]
                sell_prices = [s['entry_price'] for s in sell_signals]

                fig.add_trace(
                    go.Scatter(
                        x=sell_dates,
                        y=sell_prices,
                        mode='markers',
                        name='SELL Signal',
                        marker=dict(
                            symbol='triangle-down',
                            size=12,
                            color='red',
                            line=dict(color='darkred', width=2)
                        )
                    ),
                    row=1, col=1
                )

        # RSI subplot
        current_row = 2 if show_indicators else None

        if show_indicators and 'rsi_14' in data.columns and current_row:
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=data['rsi_14'],
                    name='RSI(14)',
                    line=dict(color='purple', width=1.5)
                ),
                row=current_row, col=1
            )

            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red",
                         opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green",
                         opacity=0.5, row=current_row, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray",
                         opacity=0.3, row=current_row, col=1)

            # Update RSI y-axis
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)

        # Volume subplot
        if show_volume and 'volume' in data.columns:
            volume_row = rows

            colors = ['red' if row['close'] < row['open'] else 'green'
                     for _, row in data.iterrows()]

            fig.add_trace(
                go.Bar(
                    x=data['timestamp'],
                    y=data['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=volume_row, col=1
            )

            fig.update_yaxes(title_text="Volume", row=volume_row, col=1)

        # Update layout
        fig.update_layout(
            height=800 if show_indicators else 600,
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update x-axis
        fig.update_xaxes(title_text="Date", row=rows, col=1)

        # Update y-axis for price
        fig.update_yaxes(title_text="Price", row=1, col=1)

        return fig

    def save_chart(
        self,
        fig: go.Figure,
        filename: str,
        format: str = 'html'
    ):
        """
        Save chart to file.

        Args:
            fig: Plotly figure
            filename: Output filename
            format: Output format ('html', 'png', 'svg')
        """
        if format == 'html':
            fig.write_html(filename)
            logger.info(f"Chart saved to {filename}")
        elif format == 'png':
            fig.write_image(filename, format='png')
            logger.info(f"Chart saved to {filename}")
        elif format == 'svg':
            fig.write_image(filename, format='svg')
            logger.info(f"Chart saved to {filename}")
        else:
            raise ValueError(f"Unsupported format: {format}")

    def show_chart(self, fig: go.Figure):
        """
        Display chart in browser.

        Args:
            fig: Plotly figure
        """
        fig.show()


def create_price_chart(
    data: pd.DataFrame,
    symbol: str,
    show_indicators: bool = True,
    show_signals: bool = False,
    signals: Optional[List[Dict]] = None,
    output_file: Optional[str] = None
) -> go.Figure:
    """
    Convenience function to create a price chart.

    Args:
        data: DataFrame with OHLC and indicator data
        symbol: Trading pair symbol
        show_indicators: If True, show indicators
        show_signals: If True, mark signals
        signals: List of signal dictionaries
        output_file: Optional file to save chart (HTML)

    Returns:
        Plotly Figure object
    """
    visualizer = ChartVisualizer()

    fig = visualizer.create_candlestick_chart(
        data=data,
        symbol=symbol,
        show_indicators=show_indicators,
        show_signals=show_signals,
        signals=signals
    )

    if output_file:
        visualizer.save_chart(fig, output_file, format='html')

    return fig
