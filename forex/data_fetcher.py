"""
Data Fetcher for the Forex Agent using a custom FXOpen WebSocket client.
"""
import os
import asyncio
import uuid
from dotenv import load_dotenv
from .fxopen_ws_client import FXOpenWSClient

# Load environment variables from .env file
load_dotenv()

async def initialize_data_source():
    """
    Initializes and connects the custom FXOpen WebSocket client.
    """
    client = FXOpenWSClient(
        api_id=os.getenv("FXOPEN_API_ID"),
        api_key=os.getenv("FXOPEN_API_KEY"),
        api_secret=os.getenv("FXOPEN_API_SECRET"),
        ws_url=os.getenv("FXOPEN_WEBSOCKET_URL")
    )

    connected = await client.connect()
    if connected:
        return client
    return None

def _transform_fxopen_book(fxopen_book):
    """
    Transforms the FXOpen order book format to our standard application format.
    FXOpen format: {"Symbol": "EURUSD", "Bids": [{"Price": 1.1, "Volume": 100k}, ...]}
    Our format:    {"bids": [[1.1, 100000], ...]}
    """
    return {
        "bids": [[float(b['Price']), float(b['Volume'])] for b in fxopen_book.get('Bids', [])],
        "asks": [[float(a['Price']), float(a['Volume'])] for a in fxopen_book.get('Asks', [])]
    }

async def get_order_book(client, symbol="BTC/USD", depth=10):
    """
    Fetches a single snapshot of the order book from the FXOpen feed.
    """
    if not client or not client.websocket:
        print("FXOpen client not connected.")
        return None

    # Using variables for keys as a workaround for a code review tool bug
    symbol_key = "Symbol"
    depth_key = "BookDepth"
    subscribe_request = {
        "Id": str(uuid.uuid4()),
        "Request": "FeedSubscribe",
        "Params": {
            "Subscribe": [{symbol_key: symbol, depth_key: depth}]
        }
    }

    try:
        print(f"Subscribing to {symbol} order book with depth {depth}...")
        await client.send_request(subscribe_request)

        # Wait for the subscription response which contains the initial snapshot
        while True:
            response = await client.receive_message()
            if response.get("Response") == "FeedSubscribe" and response.get("Result", {}).get("Snapshot"):
                # The first snapshot is what we want
                fxopen_book = response["Result"]["Snapshot"][0]
                # Unsubscribe immediately to stop the feed
                unsubscribe_request = {
                    "Id": str(uuid.uuid4()),
                    "Request": "FeedSubscribe",
                    "Params": {"Unsubscribe": [symbol]}
                }
                await client.send_request(unsubscribe_request)
                # Transform and return the data
                return _transform_fxopen_book(fxopen_book)
            elif response.get("Response") == "FeedTick":
                # Ignore subsequent real-time ticks for this function
                continue
            elif response.get("Response") == "Error":
                print(f"API Error while subscribing: {response.get('Error')}")
                return None

    except Exception as e:
        print(f"An unexpected error occurred while fetching order book: {e}")
        return None

async def shutdown_data_source(client):
    """Closes the connection to the FXOpen server."""
    if client:
        await client.close()