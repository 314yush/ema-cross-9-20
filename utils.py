"""
Utility functions for the trading bot.
"""
import uuid


def generate_client_order_id() -> str:
    """Generate a unique client order ID."""
    return str(uuid.uuid4())
