"""
Main Application for the Forex Trading Agent.

This script connects to a data provider (FXCM) for order book data and to
MetaTrader 5 for trade execution.

IMPORTANT: This script must be run on a Windows machine where the
MetaTrader 5 terminal is installed and running.
"""
import os
import time
from dotenv import load_dotenv

from . import data_fetcher
from . import mt5_connector
from . import orderbook_analyzer
from . import strategy
from . import risk_manager

def run_agent():
    """
    Runs the main loop of the Forex trading agent.
    """
    load_dotenv()
    print("--- Starting Forex Trading Agent (FXCM + MT5) ---")

    # --- Initialize Connections ---
    fxcm_client = data_fetcher.get_fxcm_client()
    mt5_ready = mt5_connector.initialize_mt5()

    if not fxcm_client or not mt5_ready:
        print("Could not initialize all connections. Exiting.")
        if fxcm_client:
            data_fetcher.close_fxcm_connection(fxcm_client)
        if mt5_ready:
            mt5_connector.shutdown_mt5()
        return

    # --- Main Loop ---
    try:
        # Get symbol from .env, default to BTC/USD for FXCM
        # and BTCUSD for MT5
        symbol_fxcm = os.getenv("FOREX_SYMBOL", "BTC/USD")
        symbol_mt5 = symbol_fxcm.replace('/', '')

        while True:
            # 1. Fetch L2 market data from FXCM
            order_book = data_fetcher.get_order_book(fxcm_client, symbol_fxcm)

            if order_book:
                # 2. Analyze data and generate signal
                walls = orderbook_analyzer.find_liquidity_levels(order_book)
                imbalance = orderbook_analyzer.calculate_imbalance(order_book)
                signal = strategy.generate_signal({'order_book': order_book})

                print(f"Signal for {symbol_fxcm}: {signal} (Imbalance: {imbalance:.2f})")
                if walls['bid_walls']:
                    print(f"Found Bid Wall at: {walls['bid_walls'][0]['price']}")
                if walls['ask_walls']:
                    print(f"Found Ask Wall at: {walls['ask_walls'][0]['price']}")

                # 3. If signal is BUY or SELL, execute trade on MT5
                if signal in ['BUY', 'SELL']:
                    entry_price = mt5_connector.mt5.symbol_info_tick(symbol_mt5).ask if signal == 'BUY' else mt5_connector.mt5.symbol_info_tick(symbol_mt5).bid

                    sl_tp = risk_manager.calculate_dynamic_sl_tp(
                        order_type=signal,
                        entry_price=entry_price,
                        bid_walls=walls['bid_walls'],
                        ask_walls=walls['ask_walls']
                    )

                    account_info = mt5_connector.mt5.account_info()
                    if not account_info:
                        print("Could not get MT5 account info. Skipping trade.")
                        continue

                    # This is the CRITICAL FIX: Calculate lot size based on the dynamic stop loss
                    lot_size = risk_manager.calculate_lot_size(
                        account_balance=account_info.balance,
                        risk_percentage=float(os.getenv("RISK_PERCENTAGE", 1.0)),
                        entry_price=entry_price,
                        stop_loss_price=sl_tp.get('sl')
                    )

                    if lot_size > 0:
                        print(f"Calculated Lot Size: {lot_size}")
                        mt5_connector.create_market_order(
                            symbol_mt5,
                            lot_size,
                            signal,
                            sl_price=sl_tp.get('sl'),
                            tp_price=sl_tp.get('tp')
                        )

            # Wait for the next cycle
            print("\nWaiting for next tick...")
            time.sleep(30) # 30-second loop

    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    finally:
        # --- Shutdown Connections ---
        print("Shutting down agent.")
        data_fetcher.close_fxcm_connection(fxcm_client)
        mt5_connector.shutdown_mt5()

if __name__ == "__main__":
    # To run this agent:
    # 1. Fill in your details in a .env file (copy from .env.example).
    # 2. Make sure you are on a Windows machine with MT5 installed and running.
    # 3. Make sure all libraries from requirements.txt are installed.
    # 4. Run `python -m forex.main_forex` from the root directory.
    run_agent()