"""
Order Book Analyzer for Forex.

This module is responsible for analyzing L2 order book data for Forex pairs.
It will contain functions to calculate:
- Order book imbalance.
- Liquidity clusters (support/resistance).
- Order flow pressure (by analyzing time & sales data).

Note: This module assumes a data source providing detailed L2 data,
which needs to be sourced from a specialized Forex data provider.
"""

def find_liquidity_levels(order_book, threshold_multiplier=3.0):
    """
    Finds significant liquidity levels (walls) in the order book.

    Args:
        order_book (dict): The 'orderBook' object from OANDA.
        threshold_multiplier (float): How many times larger than the average
                                      a bucket's liquidity must be to be
                                      considered a "wall".

    Returns:
        dict: A dictionary with 'bid_walls' and 'ask_walls'. Each is a list
              of {'price': float, 'liquidity': float}.
    """
    if not order_book or 'buckets' not in order_book:
        return {'bid_walls': [], 'ask_walls': []}

    price_buckets = order_book.get('buckets', [])
    if not price_buckets:
        return {'bid_walls': [], 'ask_walls': []}

    # Calculate average liquidity
    total_liquidity = sum(float(b['liquidity']) for b in price_buckets)
    average_liquidity = total_liquidity / len(price_buckets)
    liquidity_threshold = average_liquidity * threshold_multiplier

    current_price = float(order_book.get('price', 0))
    if current_price == 0:
        return {'bid_walls': [], 'ask_walls': []}

    bid_walls = []
    ask_walls = []

    for bucket in price_buckets:
        price = float(bucket['price'])
        liquidity = float(bucket['liquidity'])
        if liquidity > liquidity_threshold:
            wall_info = {'price': price, 'liquidity': liquidity}
            if price < current_price:
                bid_walls.append(wall_info)
            else:
                ask_walls.append(wall_info)

    # Sort walls: bids from highest to lowest, asks from lowest to highest
    bid_walls.sort(key=lambda x: x['price'], reverse=True)
    ask_walls.sort(key=lambda x: x['price'])

    return {'bid_walls': bid_walls, 'ask_walls': ask_walls}


def calculate_imbalance(order_book, depth_levels=5):
    """
    Calculates the bid/ask imbalance from the OANDA order book.
    OANDA provides buckets of liquidity at different prices.

    Args:
        order_book (dict): The 'orderBook' object from OANDA.
        depth_levels (int): The number of price buckets to consider.

    Returns:
        float: The imbalance ratio. > 0.5 means buy pressure.
    """
    if not order_book or 'buckets' not in order_book:
        return 0.5 # Neutral

    # OANDA's order book is a list of price buckets
    price_buckets = order_book.get('buckets', [])

    # We need to find the current price to separate bids from asks
    # OANDA provides this in the main object
    current_price = float(order_book.get('price', 0))
    if current_price == 0:
        return 0.5 # Cannot determine bids/asks

    bids_volume = sum(float(b['liquidity']) for b in price_buckets if float(b['price']) < current_price)
    asks_volume = sum(float(b['liquidity']) for b in price_buckets if float(b['price']) > current_price)

    total_volume = bids_volume + asks_volume
    if total_volume == 0:
        return 0.5 # Neutral

    return bids_volume / total_volume
