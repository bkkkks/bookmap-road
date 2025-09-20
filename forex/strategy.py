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

    # Placeholder strategy logic
    if imbalance > 0.5:
        return 'BUY'
    elif imbalance < -0.5:
        return 'SELL'
    else:
        return 'HOLD'
