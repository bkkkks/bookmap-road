"""
FXOpen TickTrader WebSocket Trade Client.

This module provides a client to connect to the FXOpen TickTrader
WebSocket Trade API and execute trading operations.
"""
import asyncio
import websockets
import json
import uuid
import logging
import time

from . import auth_utils

logger = logging.getLogger(__name__)

class TickTraderTrader:
    """
    A client for handling WebSocket connections to the TickTrader Trade API.
    """
    def __init__(self, api_id, api_key, api_secret, ws_trade_url):
        """Initializes the client with API credentials."""
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_trade_url = ws_trade_url
        self.websocket = None
        logger.info("TickTraderTrader initialized.")

    async def connect(self):
        """Establishes a connection to the Trade WebSocket and logs in."""
        logger.info(f"Attempting to connect to Trade WebSocket at: {self.ws_trade_url}")
        try:
            self.websocket = await asyncio.wait_for(websockets.connect(self.ws_trade_url), timeout=10.0)
            logger.info("Trade WebSocket connection established. Authenticating...")

            timestamp = int(time.time() * 1000)
            signature = auth_utils.create_hmac_signature(self.api_id, self.api_key, self.api_secret, timestamp)

            login_request = {
                "Id": str(uuid.uuid4()),
                "Request": "Login",
                "Params": {
                    "AuthType": "HMAC",
                    "WebApiId": self.api_id,
                    "WebApiKey": self.api_key,
                    "Timestamp": timestamp,
                    "Signature": signature,
                    "DeviceId": "CustomPythonClient_Trade",
                    "AppSessionId": str(uuid.uuid4())
                }
            }

            await self.websocket.send(json.dumps(login_request))
            response_str = await self.websocket.recv()
            response = json.loads(response_str)

            if response.get("Response") == "Login" and response.get("Result", {}).get("Info") == "ok":
                logger.info("Successfully logged into FXOpen Trade WebSocket API.")
                return True
            else:
                logger.error(f"Trade login failed. Server response: {response}")
                await self.close()
                return False
        except Exception as e:
            logger.error(f"Failed to connect or login to Trade API: {e}", exc_info=True)
            return False

    async def create_market_order(self, symbol, quantity, side, sl_price=None, tp_price=None):
        """Creates a new market order via the Trade WebSocket."""
        if not self.websocket or not self.websocket.open:
            logger.error("Cannot create order, Trade WebSocket is not connected.")
            return None

        request_id = str(uuid.uuid4())
        payload = {
            "Id": request_id,
            "Request": "NewOrder",
            "Params": {
                "Type": "Market",
                "Side": side.capitalize(), # e.g., 'Buy' or 'Sell'
                "Symbol": symbol,
                "Volume": quantity
            }
        }
        if sl_price:
            payload["Params"]["StopLoss"] = sl_price
        if tp_price:
            payload["Params"]["TakeProfit"] = tp_price

        logger.info(f"Sending NewOrder request: {json.dumps(payload, indent=2)}")
        try:
            await self.websocket.send(json.dumps(payload))
            # Wait for the confirmation response
            while True:
                response_str = await self.websocket.recv()
                response = json.loads(response_str)
                if response.get("Id") == request_id:
                    logger.info(f"Trade Response received: {response}")
                    return response
                else:
                    logger.info(f"Ignoring unrelated message: {response}")

        except Exception as e:
            logger.error(f"Error creating trade via WebSocket: {e}", exc_info=True)
            return None

    async def close(self):
        """Closes the WebSocket connection gracefully."""
        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Trade WebSocket connection closed.")
            except Exception as e:
                logger.warning(f"Exception while closing trade websocket: {e}")
        self.websocket = None