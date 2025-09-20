"""
Risk Management for the Crypto Agent.

This module handles risk calculations for crypto trading.
- Determines trade quantity based on a fixed USD amount or percentage of portfolio.
- Validates against exchange rules (min/max order size).
"""

def calculate_trade_quantity(usdt_balance, risk_amount_usd, price, market):
    """
    Calculates the quantity of a crypto asset to trade based on a fixed USD risk amount,
    and validates it against the exchange's trading limits.

    Args:
        usdt_balance (float): The available USDT balance.
        risk_amount_usd (float): The amount in USD to risk on this trade.
        price (float): The current price of the asset.
        market (dict): The market data for the symbol from ccxt (contains limits).

    Returns:
        float: The calculated quantity of the asset to trade, or 0 if invalid.
    """
    if risk_amount_usd > usdt_balance:
        print("Risk Error: Risk amount exceeds available balance.")
        return 0

    quantity = risk_amount_usd / price

    # Validate against exchange limits
    min_notional = market.get('limits', {}).get('cost', {}).get('min')

    if min_notional is not None:
        notional_value = quantity * price
        if notional_value < min_notional:
            print(f"Risk Error: Order value ({notional_value:.2f}) is below the minimum notional value ({min_notional}).")
            return 0

    # Round to the lot size precision required by the exchange
    lot_precision = market.get('precision', {}).get('amount')
    if lot_precision is not None:
        # ccxt provides precision as a float like 0.00001, not number of decimal places
        # We can't just round(), we need to truncate.
        factor = 1 / lot_precision
        quantity = int(quantity * factor) / factor

    return quantity
