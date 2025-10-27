import json
import logging
import time
import os
import requests
import hmac
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class TickTraderTrader:
    """
    Handles trade execution via the FXOpen TickTrader REST API.
    """
    def __init__(self, api_id, api_key, api_secret, account_id):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id = account_id
        # The correct REST URL for the demo environment, taken from the screenshot.
        self.rest_url = os.getenv("FXOPEN_TRADE_REST_URL", "https://marginalttdemowebapi.fxopen.net/Connect/Api/v1")

    def _create_rest_hmac_signature(self, timestamp_ms, method, request_uri, content_body=""):
        """
        Creates the required HMAC-SHA256 signature for REST API authentication,
        following the specific format required by the documentation.
        """
        # Signature format: timestamp + webApiId + webApiKey + method + uri + content
        message = f"{timestamp_ms}{self.api_id}{self.api_key}{method.upper()}{request_uri}{content_body}"

        signature_bytes = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()

        return base64.b64encode(signature_bytes).decode('utf-8')

    def _send_request(self, endpoint, payload):
        """Sends a signed POST request to the specified REST endpoint."""
        url = f"{self.rest_url}/{endpoint}"
        timestamp = int(time.time() * 1000)

        # The content body must be a JSON string for the signature
        content_body_str = json.dumps(payload)

        # Create the signature using the REST-specific method
        signature = self._create_rest_hmac_signature(
            timestamp, "POST", url, content_body_str
        )

        # The Authorization header has a specific format for HMAC
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'HMAC {self.api_id}:{self.api_key}:{timestamp}:{signature}'
        }

        self.logger.info(f"POSTing to {url}")
        try:
            # Send the request with the JSON payload
            response = requests.post(url, headers=headers, data=content_body_str, timeout=10)

            if response.status_code != 200:
                self.logger.error(f"REST Error: Status {response.status_code}, Body: {response.text}")
                return {'Response': 'Error', 'Error': f"HTTP status {response.status_code}", 'Status': response.status_code}

            # If the response is empty, it's a non-JSON response.
            if not response.text:
                self.logger.info("Empty response received, assuming success.")
                return {'Response': 'Success', 'Result': 'Order executed (empty response)'}

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
                "AccountId": int(self.account_id), # Account ID should be an integer
                "Symbol": symbol,
                "Side": side.upper(),
                "Type": "Market",
                "Amount": amount,
                "StopLoss": sl_price,
                "TakeProfit": tp_price
            }
        }
        # The endpoint for creating a trade
        return self._send_request("CreateTrade", request_payload)
