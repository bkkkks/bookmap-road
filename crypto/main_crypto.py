"""
Main Application for the Crypto Trading Agent.

This script is the entry point for running the crypto agent.
It connects to the exchange and runs a live trading loop:
1. Fetches live market data (order book).
2. Calls the strategy module to get a trading signal.
3. Calculates risk and trade quantity.
4. Calls the exchange trader to execute the trade (in test mode).
"""
import time
from . import data_fetcher
from . import strategy
from . import risk_manager
from . import exchange_trader

import json
import time

def save_historical_data(num_snapshots=5, delay_seconds=2):
    """
    Fetches a few snapshots of order book data and saves them to a file.
    """
    print(f"Fetching {num_snapshots} snapshots of order book data...")
    client = data_fetcher.get_exchange_client('kraken')
    symbol = 'BTC/USD'
    if not client:
        print("Could not initialize exchange client. Aborting.")
        return

    historical_data = []
    for i in range(num_snapshots):
        print(f"Fetching snapshot {i+1}/{num_snapshots}...")
        order_book = data_fetcher.get_order_book(client, symbol)
        # Add a timestamp to the snapshot
        order_book['timestamp_utc'] = int(time.time())
        historical_data.append(order_book)
        if i < num_snapshots - 1:
            time.sleep(delay_seconds)

    filepath = 'crypto/historical_data.json'
    with open(filepath, 'w') as f:
        json.dump(historical_data, f, indent=2)
    print(f"Successfully saved data to {filepath}")


if __name__ == "__main__":
    # This will now save data for the backtester instead of running a test.
    save_historical_data()
