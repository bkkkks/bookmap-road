"""
Trading Strategy for the Forex Agent.

This module contains the core logic that makes trading decisions.
It uses the analysis from the orderbook_analyzer to generate
trading signals (BUY, SELL, HOLD).
"""
from . import orderbook_analyzer

def generate_signal(current_market_data):
    """
    Generates a trading signal based on current market data.

    Args:
        current_market_data (dict): A dictionary containing the latest
                                    order book, time & sales, etc.

    Returns:
        str: A signal, one of 'BUY', 'SELL', or 'HOLD'.
    """
    order_book = current_market_data.get('order_book')
    if not order_book:
        return 'HOLD'

    imbalance = orderbook_analyzer.calculate_imbalance(order_book)

    # Strategy: Buy if buy-side pressure is very high, sell if sell-side is very high.
    # A value > 0.5 indicates more buy volume in the top levels.
    if imbalance > 0.7:  # e.g., 70% of volume is on the buy side
        return 'BUY'
    elif imbalance < 0.3: # e.g., 70% of volume is on the sell side (since 1.0 - 0.7 = 0.3)
        return 'SELL'
    else:
        return 'HOLD'
