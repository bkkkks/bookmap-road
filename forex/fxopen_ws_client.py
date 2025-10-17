"""
FXOpen TickTrader WebSocket Client for Streaming Data.
"""
import asyncio
import websockets
import json
import uuid
import logging
import time
from . import auth_utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FXOpenWSClient:
    """
    A client for handling a persistent WebSocket connection to FXOpen's
    TickTrader Feed API and processing a continuous stream of data.
    """
    def __init__(self, api_id, api_key, api_secret, ws_urls):
        self.api_id = api_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_urls = [url.strip() for url in ws_urls.split(',')]
        self.websocket = None
        self.connected_url = None
        self.data_queue = asyncio.Queue()
        logger.info("FXOpenWSClient initialized.")

    async def connect(self):
        """
        Establishes a WebSocket connection by trying a list of URLs and logs in.
        Returns True on successful login, False otherwise.
        """
        for url in self.ws_urls:
            logger.info(f"Attempting to connect to WebSocket at: {url}")
            try:
                self.websocket = await asyncio.wait_for(websockets.connect(url), timeout=10.0)
                self.connected_url = url
                logger.info(f"WebSocket connection established at {url}. Authenticating...")

                timestamp = int(time.time() * 1000)
                signature = auth_utils.create_hmac_signature(self.api_id, self.api_key, self.api_secret, timestamp)

                login_request = {
                    "Id": str(uuid.uuid4()), "Request": "Login",
                    "Params": {
                        "AuthType": "HMAC", "WebApiId": self.api_id, "WebApiKey": self.api_key,
                        "Timestamp": timestamp, "Signature": signature, "DeviceId": "CustomPythonClient",
                        "AppSessionId": str(uuid.uuid4())
                    }
                }

                await self.websocket.send(json.dumps(login_request))
                response = json.loads(await self.websocket.recv())

                if response.get("Response") == "Login" and response.get("Result", {}).get("Info") == "ok":
                    logger.info(f"Successfully logged into FXOpen WebSocket API using {url}.")
                    return True
                else:
                    logger.warning(f"Login failed at {url}. Server response: {response}")
                    await self.close()
                    continue
            except Exception as e:
                logger.warning(f"Failed to connect to {url}: {e}. Trying next URL...")
                continue

        logger.error("Failed to connect to any of the provided WebSocket URLs.")
        return False

    async def subscribe_to_order_book(self, symbol, depth=10):
        """Subscribes to the order book feed for a given symbol."""
        if not self.websocket or not self.websocket.open:
            logger.error("Cannot subscribe, WebSocket is not connected.")
            return False

        request = {
            "Id": str(uuid.uuid4()), "Request": "FeedSubscribe",
            "Params": {"Subscribe": [{"Symbol": symbol, "BookDepth": depth}]}
        }
        await self.websocket.send(json.dumps(request))
        # The first response will be a snapshot, subsequent ones will be ticks
        logger.info(f"Subscribed to order book for {symbol}.")
        return True

    async def listen(self):
        """
        Listens for incoming messages and puts them in the queue.
        This should be run as a background task.
        """
        if not self.websocket:
            logger.error("Cannot listen, WebSocket is not connected.")
            return

        logger.info("Starting to listen for WebSocket messages...")
        try:
            while True:
                message_str = await self.websocket.recv()
                message = json.loads(message_str)
                if message.get("Response") == "FeedTick":
                    # This is a real-time order book update
                    await self.data_queue.put(message['Result'])
                # Other message types (like login responses) are ignored here
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"An error occurred in the listener loop: {e}", exc_info=True)
        finally:
            await self.close()

    async def close(self):
        """Closes the WebSocket connection gracefully."""
        if self.websocket and self.websocket.open:
            try:
                await self.websocket.close()
                logger.info("WebSocket connection closed.")
            except Exception:
                pass # Ignore errors on close
        self.websocket = None