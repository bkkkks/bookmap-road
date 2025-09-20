"""
Order Book Analyzer for Crypto.

This module is responsible for analyzing L2 order book data for crypto assets.
It is similar to the forex analyzer but tailored for the data format
received from cryptocurrency exchanges like Binance.
"""

def calculate_imbalance(order_book, depth_levels=10):
    """
    Calculates the bid/ask imbalance from the crypto order book.

    Args:
        order_book (dict): A dictionary from the Binance API with 'bids' and 'asks'.
                           Each list contains sub-lists of [price, quantity].
        depth_levels (int): The number of price levels to consider.

    Returns:
        float: The imbalance ratio. > 1 means buy pressure, < 1 means sell pressure.
    """
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])

    # Kraken data includes a timestamp, so we unpack it into a throwaway variable '_'
    bid_volume = sum(float(q) for p, q, _ in bids[:depth_levels])
    ask_volume = sum(float(q) for p, q, _ in asks[:depth_levels])

    if (bid_volume + ask_volume) == 0:
        return 1.0 # Neutral

    return bid_volume / (bid_volume + ask_volume)
