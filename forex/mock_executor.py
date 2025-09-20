"""
Mock Executor for Forex Trading.

This module simulates trade execution for the Forex trading agent.
Instead of sending real orders to a broker, it logs the intended trades
to a file or the console. This allows for testing the strategy logic
without any financial risk or dependency on a live broker connection.
"""

def execute_trade(trade_details):
    """
    Simulates the execution of a trade by logging its details.

    Args:
        trade_details (dict): A dictionary containing trade information,
                              e.g., {'symbol': 'EURUSD', 'action': 'BUY',
                                    'lots': 0.1, 'price': 1.0500}.
    """
    print(f"[MOCK EXECUTION]: {trade_details}")
    # In a real scenario, you might append this to a CSV log file.
