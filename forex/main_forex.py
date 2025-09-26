"""
Main Application for the Forex Trading Agent.

This script connects to a data provider (FXOpen) for order book data and to
MetaTrader 5 for trade execution.

This script uses asyncio to handle the WebSocket connection for data.
"""
import os
import time
import asyncio
from dotenv import load_dotenv

from . import data_fetcher
from . import mt5_connector
from . import orderbook_analyzer
from . import strategy
from . import risk_manager

async def run_agent():
    """
    Runs the main asynchronous loop of the Forex trading agent.
    """
    load_dotenv()
    print("--- Starting Forex Trading Agent (FXOpen + MT5) ---")

    # --- Initialize Connections ---
    # The data source connection is async
    fxopen_client = await data_fetcher.initialize_data_source()
    # The MT5 connection is synchronous
    mt5_ready = mt5_connector.initialize_mt5()

    if not fxopen_client or not mt5_ready:
        print("Could not initialize all connections. Exiting.")
        if fxopen_client:
            await data_fetcher.shutdown_data_source(fxopen_client)
        if mt5_ready:
            mt5_connector.shutdown_mt5()
        return

    # --- Main Loop ---
    try:
        symbol_fxopen = os.getenv("FOREX_SYMBOL", "BTC/USD")
        symbol_mt5 = symbol_fxopen.replace('/', '')

        while True:
            # 1. Fetch L2 market data from FXOpen (async)
            order_book = await data_fetcher.get_order_book(fxopen_client, symbol_fxopen)

            if order_book:
                # 2. Analyze data and generate signal (sync)
                walls = orderbook_analyzer.find_liquidity_levels(order_book)
                imbalance = orderbook_analyzer.calculate_imbalance(order_book)
                signal = strategy.generate_signal({'order_book': order_book})

                print(f"Signal for {symbol_fxopen}: {signal} (Imbalance: {imbalance:.2f})")
                if walls['bid_walls']:
                    print(f"Found Bid Wall at: {walls['bid_walls'][0]['price']}")
                if walls['ask_walls']:
                    print(f"Found Ask Wall at: {walls['ask_walls'][0]['price']}")

                # 3. If signal is BUY or SELL, execute trade on MT5 (sync)
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
            await asyncio.sleep(30) # Use asyncio.sleep in an async function

    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    finally:
        # --- Shutdown Connections ---
        print("Shutting down agent.")
        await data_fetcher.shutdown_data_source(fxopen_client)
        mt5_connector.shutdown_mt5()

if __name__ == "__main__":
    # To run this agent:
    # 1. Fill in your details in a .env file.
    # 2. Make sure you are on a Windows machine with MT5 installed and running.
    # 3. Make sure all libraries from requirements.txt are installed.
    # 4. Run `python -m forex.main_forex` from the root directory.
    try:
        asyncio.run(run_agent())
    except (KeyboardInterrupt, SystemExit):
        print("Agent shutdown complete.")