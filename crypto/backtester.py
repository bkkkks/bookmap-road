"""
Backtester for the Crypto Trading Agent.

This module simulates the trading strategy against historical data.
"""
import json
from . import strategy
from . import risk_manager
from . import orderbook_analyzer

def load_historical_data(filepath='crypto/historical_data.json'):
    """Loads historical data from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def run_backtest():
    """
    Runs a backtest simulation using the saved historical data.
    """
    print("--- Starting Backtest Simulation ---")

    # Load data
    historical_data = load_historical_data()
    if not historical_data:
        print("No historical data found.")
        return

    # Initial simulation state
    account_balance = 1000.0
    risk_per_trade_usd = 20.0 # Risk $20 per trade
    trades = []
    position = None # To track if we are in a trade ('BUY' or 'SELL')

    # Mock market data for risk manager (assuming BTC/USD on Kraken)
    # In a real backtester, this should be loaded dynamically
    mock_market = {
        'limits': {'cost': {'min': 0.5}},
        'precision': {'amount': 1e-08}
    }

    # Loop through each historical data point
    for i, data_point in enumerate(historical_data):
        print(f"\n--- Tick {i+1} ---")

        # The strategy only needs the order book
        market_data = {'order_book': data_point}
        signal = strategy.generate_signal(market_data)
        print(f"Signal: {signal}")

        current_ask = float(data_point['asks'][0][0])
        current_bid = float(data_point['bids'][0][0])

        # Position closing logic
        if position == 'BUY' and signal == 'SELL':
            profit = current_bid - trades[-1]['entry_price']
            account_balance += profit * trades[-1]['quantity']
            print(f"Closed BUY position at {current_bid}. P/L: {profit * trades[-1]['quantity']:.2f}")
            position = None
        elif position == 'SELL' and signal == 'BUY':
            profit = trades[-1]['entry_price'] - current_ask
            account_balance += profit * trades[-1]['quantity']
            print(f"Closed SELL position at {current_ask}. P/L: {profit * trades[-1]['quantity']:.2f}")
            position = None

        # Position opening logic
        if not position and signal in ['BUY', 'SELL']:
            price = current_ask if signal == 'BUY' else current_bid
            quantity = risk_manager.calculate_trade_quantity(
                usdt_balance=account_balance,
                risk_amount_usd=risk_per_trade_usd,
                price=price,
                market=mock_market
            )
            if quantity > 0:
                trade_info = {'tick': i, 'action': signal, 'entry_price': price, 'quantity': quantity}
                trades.append(trade_info)
                position = signal
                print(f"Opened {signal} position for {quantity} at {price}")

    # Print final results
    print("\n--- Backtest Complete ---")
    print(f"Final Account Balance: {account_balance:.2f}")
    print(f"Total Trades: {len(trades)}")
    print("Trade Log:", trades)

if __name__ == '__main__':
    run_backtest()
