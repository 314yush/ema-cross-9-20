"""
Configuration file for the trading bot.
Set your private key and other settings here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Hyperliquid API Configuration
API_URL = os.getenv("API_URL", "https://api.hyperliquid.xyz")  # Use testnet: https://api.hyperliquid-testnet.xyz
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")  # Your Ethereum-style private key (hex format, 0x prefix optional)

# Trading Configuration
USE_TESTNET = os.getenv("USE_TESTNET", "false").lower() == "true"

