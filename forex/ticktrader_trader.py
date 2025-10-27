import json
import logging
import time
import os
import requests
from . import auth_utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TickTraderTrader:
    def __init__(self, api_id, api_key, api_secret, account_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id = account_id
        # Use the REST URL from environment variables, with a fallback
        self.rest_url = os.getenv("FXOPEN_TRADE_REST_URL", "https://marginalttdemowebapi.fxopen.net/Connect/Api/v1")

    def _send_request(self, endpoint, payload):
        """Sends a signed POST request to the specified REST endpoint."""
        url = f"{self.rest_url}/{endpoint}"
        timestamp = int(time.time() * 1000)

        # Use the simple signature generation from auth_utils
        signature = auth_utils.create_hmac_signature(
            self.api_id, self.api_key, self.api_secret, timestamp
        )

        headers = {
            'Content-Type': 'application/json',
            'Timestamp': str(timestamp),
            'WebApiId': self.api_id,
            'WebApiKey': self.api_key,
            'Signature': signature
        }

        self.logger.info(f"POSTing to {url}")
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code != 200:
                self.logger.error(f"REST Error: Status {response.status_code}, Body: {response.text}")
                return {'Response': 'Error', 'Error': f"HTTP status {response.status_code}", 'Status': response.status_code}

            try:
                json_response = response.json()
                self.logger.info(f"REST Response: {json_response}")
                return json_response
            except json.JSONDecodeError:
                self.logger.error(f"Non-JSON response received: {response.text}")
                return {'Response': 'Error', 'Error': 'Non-JSON response: ' + response.text, 'Status': response.status_code}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"REST Request failed: {e}")
            return {'Response': 'Error', 'Error': str(e), 'Status': None}

    def create_market_order(self, symbol, amount, side, sl_price=None, tp_price=None):
        """Creates a new market order using the REST API."""
        request_payload = {
            "Request": "CreateTrade",
            "Params": {
                "AccountId": self.account_id,
                "Symbol": symbol,
                "Side": side.upper(),
                "Type": "Market",
                "Amount": amount,
                "StopLoss": sl_price,
                "TakeProfit": tp_price
            }
        }
        return self._send_request("CreateTrade", request_payload)
