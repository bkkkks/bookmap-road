"""
Order Book Analyzer for Forex.

This module is responsible for analyzing L2 order book data.
It contains functions to calculate:
- Order book imbalance.
- Liquidity clusters (support/resistance walls).
"""

def find_liquidity_levels(order_book, threshold_multiplier=3.0):
    """
    Finds significant liquidity levels (walls) in the order book.
    The data format is expected to be a list of [price, quantity] lists.

    Args:
        order_book (dict): A dictionary with 'bids' and 'asks' lists.
        threshold_multiplier (float): How many times larger than the average
                                      a bucket's liquidity must be to be
                                      considered a "wall".

    Returns:
        dict: A dictionary with 'bid_walls' and 'ask_walls'.
    """
    if not order_book:
        return {'bid_walls': [], 'ask_walls': []}

    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])

    all_liquidity = [float(q) for p, q in bids] + [float(q) for p, q in asks]
    if not all_liquidity:
        return {'bid_walls': [], 'ask_walls': []}

    average_liquidity = sum(all_liquidity) / len(all_liquidity)
    liquidity_threshold = average_liquidity * threshold_multiplier

    bid_walls = [{'price': float(p), 'liquidity': float(q)} for p, q in bids if float(q) > liquidity_threshold]
    ask_walls = [{'price': float(p), 'liquidity': float(q)} for p, q in asks if float(q) > liquidity_threshold]

    # Sort walls: bids from highest to lowest, asks from lowest to highest
    bid_walls.sort(key=lambda x: x['price'], reverse=True)
    ask_walls.sort(key=lambda x: x['price'])

    return {'bid_walls': bid_walls, 'ask_walls': ask_walls}


def calculate_imbalance(order_book, depth_levels=10):
    """
    Calculates the bid/ask imbalance from the order book.
    The data format is expected to be a list of [price, quantity] lists.
    """
    if not order_book:
        return 0.5 # Neutral

    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])

    bid_volume = sum(float(q) for p, q in bids[:depth_levels])
    ask_volume = sum(float(q) for p, q in asks[:depth_levels])

    total_volume = bid_volume + ask_volume
    if total_volume == 0:
        return 0.5 # Neutral

    return bid_volume / total_volume