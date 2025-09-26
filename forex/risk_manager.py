"""
Risk Management for the Forex Agent.

This module handles all risk-related calculations, including:
- Dynamic lot sizing based on account balance and risk percentage.
- Stop-loss and take-profit calculations.
- Trailing stop logic based on market liquidity.
"""

def calculate_lot_size(account_balance, risk_percentage, entry_price, stop_loss_price):
    """
    Calculates the appropriate lot size for a trade based on a precise
    stop loss level.

    Args:
        account_balance (float): The current account balance.
        risk_percentage (float): The percentage of the account to risk (e.g., 1.0 for 1%).
        entry_price (float): The expected entry price of the trade.
        stop_loss_price (float): The price at which the stop loss will be set.

    Returns:
        float: The calculated lot size, or 0 if inputs are invalid.
    """
    if stop_loss_price is None or entry_price is None:
        print("Risk Error: Cannot calculate lot size without a valid stop loss price.")
        return 0

    # 1. Determine the total amount to risk in account currency (e.g., USD)
    risk_amount_in_currency = account_balance * (risk_percentage / 100.0)

    # 2. Determine the risk per lot in account currency
    price_difference = abs(entry_price - stop_loss_price)

    # For BTC/USD, the contract size is 1, so the value of a price move is direct.
    # For other pairs like EUR/USD, contract_size would be 100,000.
    contract_size = 1
    risk_per_lot = price_difference * contract_size

    if risk_per_lot == 0:
        return 0

    # 3. Calculate the lot size
    lot_size = risk_amount_in_currency / risk_per_lot

    # Return a rounded lot size, typically to 2 decimal places for forex.
    return round(lot_size, 2)

def calculate_dynamic_sl_tp(order_type, entry_price, bid_walls, ask_walls, pips_buffer=5):
    """
    Calculates dynamic Stop Loss and Take Profit levels based on liquidity walls.

    Args:
        order_type (str): 'BUY' or 'SELL'.
        entry_price (float): The price at which the trade is entered.
        bid_walls (list): A sorted list of significant bid liquidity levels.
        ask_walls (list): A sorted list of significant ask liquidity levels.
        pips_buffer (int): A buffer in pips to place SL/TP away from the wall.

    Returns:
        dict: A dictionary with 'sl' and 'tp' prices. Can be None if no walls found.
    """
    # Pip value assumes a standard 5-decimal price quote for most pairs
    # For BTCUSD, a "pip" is more ambiguous, let's treat it as the smallest price change (e.g. 0.1)
    # This should be configured based on the specific broker's instrument details.
    pip_size = 0.1
    buffer_amount = pips_buffer * pip_size

    sl_price = None
    tp_price = None

    if order_type.upper() == 'BUY':
        # SL for a BUY is below a support wall (highest bid wall)
        if bid_walls:
            support_price = bid_walls[0]['price']
            sl_price = support_price - buffer_amount
        # TP for a BUY is before a resistance wall (lowest ask wall)
        if ask_walls:
            resistance_price = ask_walls[0]['price']
            tp_price = resistance_price - buffer_amount

    elif order_type.upper() == 'SELL':
        # SL for a SELL is above a resistance wall (lowest ask wall)
        if ask_walls:
            resistance_price = ask_walls[0]['price']
            sl_price = resistance_price + buffer_amount
        # TP for a SELL is after a support wall (highest bid wall)
        if bid_walls:
            support_price = bid_walls[0]['price']
            tp_price = support_price + buffer_amount

    # Basic validation to ensure SL/TP are logical relative to entry price
    if sl_price and tp_price:
        if order_type.upper() == 'BUY' and (sl_price >= entry_price or tp_price <= entry_price):
            return {'sl': None, 'tp': None}
        if order_type.upper() == 'SELL' and (sl_price <= entry_price or tp_price >= entry_price):
            return {'sl': None, 'tp': None}

    return {'sl': sl_price, 'tp': tp_price}
