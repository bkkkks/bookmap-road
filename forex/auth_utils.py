"""
Authentication Utilities for FXOpen TickTrader API.

This module provides shared functions for creating authentication signatures.
"""
import hmac
import hashlib
import base64

def create_hmac_signature(api_id, api_key, api_secret, timestamp_ms):
    """
    Creates the required HMAC-SHA256 signature for authentication.

    Args:
        api_id (str): The Web API ID.
        api_key (str): The Web API Key.
        api_secret (str): The Web API Secret.
        timestamp_ms (int): The current timestamp in milliseconds.

    Returns:
        str: The Base64 encoded HMAC-SHA256 signature.
    """
    message = f"{timestamp_ms}{api_id}{api_key}"
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')
