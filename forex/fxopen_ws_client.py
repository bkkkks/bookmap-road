"""
FXOpen TickTrader WebSocket Client.

This module provides a low-level client to connect to the FXOpen
TickTrader WebSocket Feed API, handle authentication, and manage
the connection.
"""
import asyncio
import websockets
import json
import hmac
import hashlib
import base64
import time
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FXOpenWSClient:
    """
    A client for handling WebSocket connections to FXOpen's TickTrader API.
    """
    def __init__(self, api_id, api_key, api_secret, ws_url):
        """Initializes the client with API credentials."""
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = ws_url
        self.websocket = None
        logger.info("FXOpenWSClient initialized.")

    def _create_signature(self, timestamp_ms):
        """Creates the required HMAC-SHA256 signature for authentication."""
        message = f"{timestamp_ms}{self.api_id}{self.api_key}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')

    async def connect(self):
        """Establishes a WebSocket connection and performs login."""
        logger.info(f"Attempting to connect to WebSocket at: {self.ws_url}")
        try:
            # Add a timeout to the connection attempt
            self.websocket = await asyncio.wait_for(websockets.connect(self.ws_url), timeout=10.0)
            logger.info("WebSocket connection established. Authenticating...")

            timestamp = int(time.time() * 1000)
            signature = self._create_signature(timestamp)

            login_request = {
                "Id": str(uuid.uuid4()),
                "Request": "Login",
                "Params": {
                    "AuthType": "HMAC",
                    "WebApiId": self.api_id,
                    "WebApiKey": self.api_key,
                    "Timestamp": timestamp,
                    "Signature": signature,
                    "DeviceId": "CustomPythonClient",
                    "AppSessionId": str(uuid.uuid4())
                }
            }

            logger.info(f"Sending login request: {json.dumps(login_request, indent=2)}")
            await self.send_request(login_request)
            response = await self.receive_message()

            if response.get("Response") == "Login" and response.get("Result", {}).get("Info") == "ok":
                logger.info("Successfully logged into FXOpen WebSocket API.")
                return True
            else:
                logger.error(f"Login failed. Server response: {response}")
                await self.close()
                return False

        except asyncio.TimeoutError:
            logger.error("Connection timed out. Please check the WebSocket URL and your network connection/firewall.")
            return False
        except websockets.exceptions.InvalidURI:
            logger.error(f"Invalid WebSocket URI: '{self.ws_url}'. Please check the .env file.")
            return False
        except Exception as e:
            logger.error(f"Failed to connect or login due to an unexpected error: {e}", exc_info=True)
            if self.websocket:
                await self.close()
            return False

    async def send_request(self, request_payload):
        """Sends a JSON request to the server."""
        if not self.websocket:
            raise ConnectionError("WebSocket is not connected.")
        await self.websocket.send(json.dumps(request_payload))

    async def receive_message(self):
        """Receives and parses a single message from the server."""
        if not self.websocket:
            raise ConnectionError("WebSocket is not connected.")
        message = await self.websocket.recv()
        return json.loads(message)

    async def close(self):
        """Closes the WebSocket connection."""
        if self.websocket and self.websocket.open:
            await self.websocket.close()
            print("WebSocket connection closed.")
        self.websocket = None