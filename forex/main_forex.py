"""
Main Application for the Fully Independent Forex Trading Agent.

This script runs two simultaneous WebSocket connections:
1. A 'Feed' connection for live order book data.
2. A 'Trade' connection for executing orders.

It operates independently without needing any desktop trading platform.
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
    load_dotenv()
    print("--- Starting Independent Forex Trading Agent (Dual WebSocket) ---")

    data_client = None
    trade_client = None

    try:
        # --- Initialize Connections ---
        # Initialize the data connection
        data_client = await data_fetcher.initialize_data_source()

        # Initialize the trade connection
        trade_client = TickTraderTrader(
            api_id=os.getenv("FXOPEN_API_ID"),
            api_key=os.getenv("FXOPEN_API_KEY"),
            api_secret=os.getenv("FXOPEN_API_SECRET"),
            ws_trade_url=os.getenv("FXOPEN_WEBSOCKET_TRADE_URL")
        )
        trade_connected = await trade_client.connect()

        if not data_client or not trade_connected:
            print("Could not initialize all connections. Exiting.")
            return

        # --- Main Loop ---
        symbol = os.getenv("FOREX_SYMBOL", "BTC/USD")

        # In this version, we use a static balance for risk calculation.
        # A future enhancement would be to fetch this dynamically.
        account_balance = 10000.0
        print(f"Using static account balance for risk calculation: {account_balance}")

        while True:
            # 1. Fetch L2 market data
            order_book = await data_fetcher.get_order_book(data_client, symbol)

            if order_book:
                # 2. Analyze data and generate signal
                walls = orderbook_analyzer.find_liquidity_levels(order_book)
                imbalance = orderbook_analyzer.calculate_imbalance(order_book)
                signal = strategy.generate_signal({'order_book': order_book})

                print(f"Signal for {symbol}: {signal} (Imbalance: {imbalance:.2f})")

                # 3. If signal is BUY or SELL, execute trade
                if signal in ['BUY', 'SELL']:
                    entry_price = float(order_book['asks'][0][0]) if signal == 'BUY' else float(order_book['bids'][0][0])

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
                        # FXOpen uses integer amounts, not lots. We need to convert.
                        # Assuming 1 lot = 1 unit for BTC/USD on TickTrader.
                        trade_amount = lot_size
                        await trade_client.create_market_order(
                            symbol,
                            trade_amount,
                            signal,
                            sl_price=sl_tp.get('sl'),
                            tp_price=sl_tp.get('tp')
                        )

            # Wait for the next cycle
            print("\nWaiting for next tick...")
            await asyncio.sleep(30)

    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
    finally:
        # --- Shutdown Connections ---
        print("Shutting down agent.")
        if data_client:
            await data_fetcher.shutdown_data_source(data_client)
        if trade_client:
            await trade_client.close()

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except (KeyboardInterrupt, SystemExit):
        print("Agent shutdown complete.")