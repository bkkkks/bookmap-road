"""
Data Fetcher for the Forex Agent using a custom FXOpen WebSocket client.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from .fxopen_ws_client import FXOpenWSClient

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)

async def initialize_data_source():
    """
    Initializes and connects the custom FXOpen WebSocket client.
    """
    client = FXOpenWSClient(
        api_id=os.getenv("FXOPEN_API_ID"),
        api_key=os.getenv("FXOPEN_API_KEY"),
        api_secret=os.getenv("FXOPEN_API_SECRET"),
        ws_urls=os.getenv("FXOPEN_WEBSOCKET_URLS")
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

async def get_order_book(client):
    """
    Gets the latest order book snapshot from the client's data queue.
    """
    try:
        # Get the latest item from the queue.
        # The timeout prevents the loop from blocking forever if no data arrives.
        fxopen_book = await asyncio.wait_for(client.data_queue.get(), timeout=5.0)
        client.data_queue.task_done()
        return _transform_fxopen_book(fxopen_book)
    except asyncio.TimeoutError:
        logger.warning("No new order book data in queue within timeout period.")
        return None
    except Exception as e:
        logger.error(f"Error getting data from queue: {e}", exc_info=True)
        return None

async def shutdown_data_source(client):
    """Closes the connection to the FXOpen server."""
    if client:
        await client.close()