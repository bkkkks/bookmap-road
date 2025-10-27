"""
Main Application for the Fully Independent Forex Trading Agent.
This agent uses a persistent WebSocket connection for a real-time data feed.
"""
import os
import time
import asyncio
from dotenv import load_dotenv

from . import data_fetcher
from .ticktrader_trader import TickTraderTrader
from . import orderbook_analyzer
from . import strategy
from . import risk_manager

async def run_agent():
    """
    Runs the main asynchronous loop of the Forex trading agent.
    """
    # Load environment variables from the forex directory
    load_dotenv(dotenv_path='forex/.env')
    print("--- Starting Independent Forex Trading Agent (Persistent Stream) ---")

    data_client = None
    trade_client = None
    listener_task = None

    try:
        # --- Define Symbols ---
        # The WebSocket feed requires the symbol without a slash (e.g., "BTCUSD")
        feed_symbol = os.getenv("FOREX_SYMBOL", "BTCUSD").replace('/', '')
        # The REST API for trading requires the symbol with a slash (e.g., "BTC/USD")
        trade_symbol = f"{feed_symbol[:3]}/{feed_symbol[3:]}"

        print(f"Using Feed Symbol: {feed_symbol}")
        print(f"Using Trade Symbol: {trade_symbol}")

        # --- Initialize Connections ---
        data_client = await data_fetcher.initialize_data_source()
        trade_client = TickTraderTrader(
            api_id=os.getenv("FXOPEN_API_ID"),
            api_key=os.getenv("FXOPEN_API_KEY"),
            api_secret=os.getenv("FXOPEN_API_SECRET"),
            account_id=os.getenv("FXOPEN_ACCOUNT_ID")
        )

        if not data_client:
            print("Could not initialize data connection. Exiting.")
            return

        # --- Subscribe to Data and Start Listening in the Background ---
        await data_client.subscribe_to_order_book(feed_symbol)
        listener_task = asyncio.create_task(data_client.listen())
        print(f"Listener task for {feed_symbol} started in the background.")

        # --- Main Trading Loop ---
        account_balance = 10000.0
        print(f"Using static account balance for risk calculation: {account_balance}")

        while True:
            order_book = await data_fetcher.get_order_book(data_client)

            if order_book:
                imbalance = orderbook_analyzer.calculate_imbalance(order_book)
                signal = strategy.generate_signal({'order_book': order_book})

                print(f"Signal for {feed_symbol}: {signal} (Imbalance: {imbalance:.2f})")

                if signal in ['BUY', 'SELL']:
                    entry_price = float(order_book['asks'][0][0]) if signal == 'BUY' else float(order_book['bids'][0][0])
                    walls = orderbook_analyzer.find_liquidity_levels(order_book)
                    sl_tp = risk_manager.calculate_dynamic_sl_tp(
                        order_type=signal,
                        entry_price=entry_price,
                        bid_walls=walls['bid_walls'],
                        ask_walls=walls['ask_walls']
                    )

                    lot_size = risk_manager.calculate_lot_size(
                        account_balance=account_balance,
                        risk_percentage=float(os.getenv("RISK_PERCENTAGE", 1.0)),
                        entry_price=entry_price,
                        stop_loss_price=sl_tp.get('sl')
                    )

                    if lot_size > 0:
                        print(f"Calculated Lot Size: {lot_size}")
                        trade_client.create_market_order(
                            trade_symbol, # Use the correct symbol for trading
                            lot_size,
                            signal,
                            sl_price=sl_tp.get('sl'),
                            tp_price=sl_tp.get('tp')
                        )

            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    finally:
        print("Shutting down agent.")
        if listener_task:
            listener_task.cancel()
        if data_client:
            await data_fetcher.shutdown_data_source(data_client)
        # No explicit close needed for the REST-based trade client

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except (KeyboardInterrupt, SystemExit):
        print("Agent shutdown complete.")
