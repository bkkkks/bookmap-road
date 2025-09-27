"""
MT5 Connector for the Forex Agent.

This module handles the connection to the MetaTrader 5 terminal
and the execution of trades.

IMPORTANT: This script requires the 'MetaTrader5' library and MUST be run
on a Windows machine with the MetaTrader 5 terminal installed.
"""
import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_mt5():
    """
    Initializes the connection to an already running MetaTrader 5 terminal.
    The user must be logged into their account in the terminal beforehand.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    path = os.getenv("MT5_PATH")
    if not path:
        print("Error: MT5_PATH is not set in the .env file.")
        return False

    # Establish connection to the MetaTrader 5 terminal
    if not mt5.initialize(path=path):
        print(f"MT5 initialize() failed, error code = {mt5.last_error()}")
        return False

    # Check the connection status without logging in again
    account_info = mt5.account_info()
    if account_info is None:
        print("Failed to connect to MT5 account. Make sure the terminal is running and you are logged in.")
        print(f"Last error: {mt5.last_error()}")
        mt5.shutdown()
        return False

    print("Successfully connected to MetaTrader 5.")
    print(f"Account: {account_info.login}, Server: {account_info.server}")
    print(f"Balance: {account_info.balance} {account_info.currency}")

    return True

def shutdown_mt5():
    """Shuts down the connection to the MT5 terminal."""
    print("Shutting down MT5 connection.")
    mt5.shutdown()

def create_market_order(symbol, lot, order_type, sl_price=None, tp_price=None):
    """
    Sends a market order to the MT5 terminal, with optional SL and TP.

    Args:
        symbol (str): The symbol to trade (e.g., "BTCUSD").
        lot (float): The volume of the trade in lots.
        order_type (str): "BUY" or "SELL".
        sl_price (float, optional): Stop Loss price. Defaults to None.
        tp_price (float, optional): Take Profit price. Defaults to None.

    Returns:
        dict: The result of the trade execution, or None if failed.
    """
    if order_type.upper() == "BUY":
        mt5_order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif order_type.upper() == "SELL":
        mt5_order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        print(f"Error: Invalid order type '{order_type}'")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5_order_type,
        "price": price,
        "deviation": 20, # Slippage
        "magic": 123456, # A magic number for this EA
        "comment": "Sent by Python Agent",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Add SL and TP to the request if they are provided
    if sl_price is not None:
        request['sl'] = sl_price
        print(f"Setting Stop Loss at: {sl_price}")
    if tp_price is not None:
        request['tp'] = tp_price
        print(f"Setting Take Profit at: {tp_price}")

    try:
        print(f"Sending {order_type} order for {lot} lots of {symbol}...")
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"order_send failed, retcode={result.retcode}")
            # log result
            print(result)
        else:
            print(f"Order executed successfully, ticket {result.order}")
        return result

    except Exception as e:
        print(f"An unexpected error occurred during order send: {e}")
        return None
