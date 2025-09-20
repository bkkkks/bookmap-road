"""
Data Fetcher for the Forex Agent.

This module is responsible for connecting to a Forex data provider
(OANDA) via its API and fetching live market data.

- Fetches L2 order book data.
"""
import os
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_oanda_client():
    """
    Initializes and returns the OANDA API client.
    Reads credentials from environment variables.
    """
    api_key = os.getenv("OANDA_API_KEY")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    environment = os.getenv("OANDA_ENVIRONMENT", "practice") # Default to practice

    if not api_key or not account_id:
        print("Error: OANDA_API_KEY and OANDA_ACCOUNT_ID must be set in .env file.")
        return None, None

    try:
        client = oandapyV20.API(access_token=api_key, environment=environment)
        print("Successfully initialized OANDA client.")
        return client, account_id
    except Exception as e:
        print(f"Error initializing OANDA client: {e}")
        return None, None


def get_order_book(client, instrument="BTC_USD"):
    """
    Fetches the current order book for a given instrument from OANDA.
    Note: OANDA uses '_' instead of '/' for symbols, e.g., 'BTC_USD'.
    """
    if not client:
        return None

    # OANDA's order book shows aggregated orders at price points,
    # not a full list of individual orders like a crypto exchange.
    request = instruments.InstrumentsOrderBook(instrument=instrument)

    try:
        print(f"Fetching order book for {instrument} from OANDA...")
        response = client.request(request)
        # The actual order book data is in the 'orderBook' key
        return response.get('orderBook')
    except oandapyV20.exceptions.V20Error as err:
        print(f"OANDA API Error: {err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
