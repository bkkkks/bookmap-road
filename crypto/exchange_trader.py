"""
Exchange Trader for Crypto.

This module handles the execution of trades on the cryptocurrency exchange using ccxt.
It can create new market or limit orders.
"""
import ccxt

def create_market_order(client, symbol, side, quantity):
    """
    Creates a market order on the exchange using ccxt.

    Args:
        client (ccxt.Exchange): The ccxt exchange client.
        symbol (str): The symbol to trade (e.g., 'BTC/USD').
        side (str): 'buy' or 'sell' (lowercase for ccxt).
        quantity (float): The amount of the asset to trade.

    Returns:
        dict: The response from the exchange.
    """
    if not client:
        print("Error: Exchange client is not initialized.")
        return None

    print(f"Creating market {side} order for {quantity} {symbol} on {client.id}...")
    try:
        # ccxt uses lowercase for side
        order_side = side.lower()

        # Some exchanges support test orders via params
        params = {'test': True}

        order = client.create_order(symbol, 'market', order_side, quantity, params=params)
        print("Test order created successfully.")
        return order
    except Exception as e:
        print(f"An error occurred while creating order: {e}")
        return None
