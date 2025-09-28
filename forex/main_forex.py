"""
Main Application for the Fully Independent Forex Trading Agent.

This script connects to the FXOpen TickTrader API for both live
order book data (via WebSocket) and trade execution (via WebREST).

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
    print("--- Starting Independent Forex Trading Agent (FXOpen TickTrader) ---")

    # --- Initialize Connections ---
    # Data connection (WebSocket)
    data_client = await data_fetcher.initialize_data_source()

    # Trade execution connection (REST)
    # Note: The trade URL is different from the WebSocket URL.
    # The user must add FXOPEN_TRADE_URL to their .env file.
    trade_client = TickTraderTrader(
        api_id=os.getenv("FXOPEN_API_ID"),
        api_key=os.getenv("FXOPEN_API_KEY"),
        api_secret=os.getenv("FXOPEN_API_SECRET"),
        trade_url=os.getenv("FXOPEN_TRADE_URL", "ttdemowebapi.soft-fx.com") # Default to demo
    )

    if not data_client or not trade_client:
        print("Could not initialize all connections. Exiting.")
        if data_client:
            await data_fetcher.shutdown_data_source(data_client)
        return

    # --- Main Loop ---
    try:
        symbol = os.getenv("FOREX_SYMBOL", "BTC/USD")

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
                    # Get the current price from the live order book
                    entry_price = float(order_book['asks'][0][0]) if signal == 'BUY' else float(order_book['bids'][0][0])

                    sl_tp = risk_manager.calculate_dynamic_sl_tp(
                        order_type=signal,
                        entry_price=entry_price,
                        bid_walls=walls['bid_walls'],
                        ask_walls=walls['ask_walls']
                    )

                    # Get account info via REST API for risk management
                    account_info = trade_client.client.get_account()
                    if not account_info:
                        print("Could not get account info. Skipping trade.")
                        continue

                    lot_size = risk_manager.calculate_lot_size(
                        account_balance=float(account_info.get("Balance", 0)),
                        risk_percentage=float(os.getenv("RISK_PERCENTAGE", 1.0)),
                        entry_price=entry_price,
                        stop_loss_price=sl_tp.get('sl')
                    )

                    if lot_size > 0:
                        print(f"Calculated Lot Size: {lot_size}")
                        # FXOpen uses integer amounts, not lots. We need to convert.
                        # Assuming 1 lot = 1 unit for BTC/USD on TickTrader. This may need adjustment.
                        trade_amount = lot_size
                        trade_client.create_market_order(
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
        await data_fetcher.shutdown_data_source(data_client)

if __name__ == "__main__":
    try:
        asyncio.run(run_agent())
    except (KeyboardInterrupt, SystemExit):
        print("Agent shutdown complete.")