"""
Data Fetcher for the Forex Agent using FXCM.

This module is responsible for connecting to FXCM via its API
and fetching live market data.

- Fetches L2 order book data (Market Depth).
"""
import os
import time
import fxcmpy
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

def get_fxcm_client():
    """
    Initializes and returns the FXCM API client.
    Reads credentials from environment variables.
    """
    api_token = os.getenv("FXCM_API_TOKEN")
    server_mode = os.getenv("FXCM_SERVER_MODE", "demo")

    if not api_token:
        print("Error: FXCM_API_TOKEN must be set in .env file.")
        return None

    try:
        # set log_level='error' to hide verbose informational messages
        client = fxcmpy.fxcmpy(access_token=api_token, server=server_mode, log_level='error')
        client.connect()
        print("Successfully connected to FXCM.")
        return client
    except Exception as e:
        print(f"Error initializing FXCM client: {e}")
        return None


def get_order_book(client, symbol="BTC/USD"):
    """
    Fetches the current order book for a given instrument from FXCM.

    This function subscribes to market data, gets a snapshot of the
    order book as a DataFrame, processes it, and then unsubscribes.
    """
    if not client or not client.is_connected():
        print("FXCM client not connected.")
        return None

    try:
        print(f"Fetching order book for {symbol} from FXCM...")

        client.subscribe_market_data(symbol)
        # Give the server a moment to stream the data
        time.sleep(1)

        # This is the correct method to get the order book DataFrame
        df = client.get_market_depth_df(symbol)

        client.unsubscribe_market_data(symbol)

        # Transform the DataFrame into our standard dict format
        bids = df[['Bid', 'BidQty']].values.tolist()
        asks = df[['Ask', 'AskQty']].values.tolist()

        order_book = {
            "bids": bids,
            "asks": asks
        }

        return order_book

    except Exception as e:
        print(f"An unexpected error occurred while fetching from FXCM: {e}")
        return None

def close_fxcm_connection(client):
    """Closes the connection to the FXCM server."""
    if client and client.is_connected():
        print("Closing FXCM connection.")
        client.close()