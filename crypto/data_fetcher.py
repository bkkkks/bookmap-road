"""
Data Fetcher for Crypto Trading.

This module is responsible for connecting to a cryptocurrency exchange
using the ccxt library and fetching live market data.

- Fetches full L2 order book depth.
- Fetches real-time trades (Time & Sales).
"""
import ccxt
import os

def get_exchange_client(exchange_name='kraken'):
    """
    Initializes and returns a ccxt exchange client.
    API keys can be set as environment variables for private endpoints.
    """
    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            'apiKey': os.environ.get(f'{exchange_name.upper()}_API_KEY'),
            'secret': os.environ.get(f'{exchange_name.upper()}_API_SECRET'),
        })
        print(f"Successfully initialized ccxt client for {exchange_name}.")
        # Test connection to public endpoint
        exchange.fetch_ticker('BTC/USD')
        return exchange
    except AttributeError:
        print(f"Error: Exchange '{exchange_name}' not found in ccxt.")
        return None
    except Exception as e:
        print(f"Error connecting to {exchange_name}: {e}")
        return None


def get_order_book(client, symbol='BTC/USD'):
    """
    Fetches the current order book for a given symbol using ccxt.
    """
    if not client:
        return None
    print(f"Fetching order book for {symbol} from {client.id}...")
    return client.fetch_order_book(symbol)

def get_recent_trades(client, symbol='BTC/USD'):
    """
    Fetches the most recent trades for a given symbol using ccxt.
    """
    if not client:
        return None
    print(f"Fetching recent trades for {symbol} from {client.id}...")
    return client.fetch_trades(symbol)

def load_markets(client):
    """
    Loads all market data from the exchange, including trading rules and limits.
    """
    if not client:
        return None
    print(f"Loading markets from {client.id}...")
    return client.load_markets()
