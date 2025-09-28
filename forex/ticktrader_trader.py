"""
FXOpen TickTrader Trade Module.

This module provides a high-level interface for executing trades
using the underlying TickTraderWebClient.
"""
import os
from .tt_web_client import TickTraderWebClient

class TickTraderTrader:
    """
    A high-level client for executing trades on the TickTrader platform.
    """
    def __init__(self, api_id, api_key, api_secret, trade_url):
        """Initializes the trader and the underlying web client."""
        # The trade URL for the REST API is different from the WebSocket one.
        # It's typically the domain name without scheme or port.
        # e.g., 'ttdemowebapi.soft-fx.com'
        parsed_url = trade_url.split("://")[1].split(":")[0]

        self.client = TickTraderWebClient(
            web_api_address=parsed_url,
            web_api_id=api_id,
            web_api_key=api_key,
            web_api_secret=api_secret
        )
        print("TickTraderTrader initialized and ready to execute trades.")

    def create_market_order(self, symbol, quantity, side, sl_price=None, tp_price=None):
        """
        Creates a new market order using the TickTrader Web API.

        Args:
            symbol (str): The symbol to trade (e.g., "BTC/USD").
            quantity (float): The trade amount/volume.
            side (str): "Buy" or "Sell".
            sl_price (float, optional): Stop loss price.
            tp_price (float, optional): Take profit price.

        Returns:
            dict: The response from the trade creation request.
        """
        payload = {
            "Type": "Market",
            "Side": side,
            "Symbol": symbol,
            "Amount": quantity
        }
        if sl_price:
            payload["StopLoss"] = sl_price
        if tp_price:
            payload["TakeProfit"] = tp_price

        print(f"Sending Market Order to TickTrader: {payload}")
        try:
            response = self.client.create_trade(payload)
            print(f"Trade Response: {response}")
            return response
        except Exception as e:
            print(f"Error creating trade via TickTrader API: {e}")
            return None