"""
FXOpen TickTrader REST Trade Client
-----------------------------------
This module handles authenticated REST trading operations for FXOpen TickTrader API.
WebSocket is used only for login/session (optional), not for trade execution.
"""

import os
import aiohttp
import json
import uuid
import logging
import time
from . import auth_utils

logger = logging.getLogger(__name__)

class TickTraderTrader:
    """
    A lightweight REST-based FXOpen trader client.
    Executes trades using the FXOpen TickTrader REST API.
    """

    def __init__(self, api_id, api_key, api_secret, ws_trade_url=None, rest_trade_url=None):
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.rest_trade_url = rest_trade_url or os.getenv("FXOPEN_TRADE_REST_URL")
        self.account_id = None
        logger.info("TickTraderTrader initialized (REST mode).")

    async def _rest_call(self, endpoint, body):
        """Helper: Send REST POST request with authentication."""
        if not self.rest_trade_url:
            logger.error("REST trade URL not configured.")
            return {"Response": "Error", "Error": "REST URL not configured"}

        url = f"{self.rest_trade_url.rstrip('/')}/CreateTrade"
        timestamp = int(time.time() * 1000)
        signature = auth_utils.create_hmac_signature(self.api_id, self.api_key, self.api_secret, timestamp)

        body["Params"].update({
            "AuthType": "HMAC",
            "WebApiId": self.api_id,
            "WebApiKey": self.api_key,
            "Timestamp": timestamp,
            "Signature": signature,
            "DeviceId": "PythonRESTClient"
        })

        logger.info(f"POSTing to {url}")
        logger.debug("Payload:\n%s", json.dumps(body, indent=2))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body, timeout=50) as resp:
                    text = await resp.text()
                    try:
                        result = json.loads(text)
                    except Exception:
                        result = {"Response": "Error", "Error": f"Non-JSON response: {text}", "Status": resp.status}
                    logger.info("REST Response: %s", result)
                    return result
        except Exception as e:
            logger.error(f"REST request failed: {e}", exc_info=True)
            return {"Response": "Error", "Error": str(e)}

    async def create_market_order(self, symbol, quantity, side, sl_price=None, tp_price=None):
        """Create a market order using REST API."""
        request_id = str(uuid.uuid4())

        params = {
            "Symbol": symbol,
            "Side": side.capitalize(),
            "Volume": quantity,
            "Type": "Market",
            "AccountId": os.getenv("FXOPEN_ACCOUNT_ID")

        }

        if self.account_id:
            params["AccountId"] = self.account_id
        if sl_price is not None:
            params["StopLoss"] = sl_price
        if tp_price is not None:
            params["TakeProfit"] = tp_price

        body = {
            "Id": request_id,
            "Request": "CreateTrade",
            "Params": params
        }

        return await self._rest_call("api/v1/CreateTrade", body)

    async def close(self):
        """No-op for REST mode (kept for compatibility)."""
        logger.info("TickTraderTrader REST client closed (no persistent connection).")
