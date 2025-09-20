"""
Main Application for the Forex Trading Agent.

This script is the entry point for running the Forex agent.
It simulates a live trading loop:
1. Fetches (or simulates) market data.
2. Calls the strategy module to get a trading signal.
3. Calculates risk for the potential trade.
4. Calls the mock executor to log the trade.
"""
import time
from . import strategy
from . import risk_manager
from . import mock_executor

def run_agent():
    """
    Runs the main loop of the Forex trading agent.
    """
    print("Starting Forex Trading Agent (Simulation Mode)...")
    account_balance = 10000  # Example balance

    while True:
        # 1. Simulate fetching market data
        mock_market_data = {
            'order_book': {
                'bids': [(1.0500, 10), (1.0499, 15)],
                'asks': [(1.0501, 12), (1.0502, 18)]
            }
        }

        # 2. Get signal from strategy
        signal = strategy.generate_signal(mock_market_data)
        print(f"Generated Signal: {signal}")

        if signal in ['BUY', 'SELL']:
            # 3. Calculate risk
            lot_size = risk_manager.calculate_lot_size(
                account_balance=account_balance,
                risk_percentage=1.0,
                stop_loss_pips=20
            )

            # 4. Execute mock trade
            trade = {
                'symbol': 'EURUSD',
                'action': signal,
                'lots': lot_size,
                'price': mock_market_data['order_book']['asks'][0][0] if signal == 'BUY' else mock_market_data['order_book']['bids'][0][0]
            }
            mock_executor.execute_trade(trade)

        # Wait for the next cycle
        time.sleep(10)

if __name__ == "__main__":
    # To run this, you would execute `python -m forex.main_forex` from the root directory.
    # run_agent()
    print("Forex agent main file created. Run disabled by default.")
