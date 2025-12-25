#!/bin/bash
# Quick test trade script for Fly.io

export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

echo "🧪 Testing Trade Execution on Fly.io"
echo "======================================"
echo ""
echo "This will execute a small test trade ($5, no leverage)"
echo ""

# Check if USE_TESTNET is set
echo "Checking environment..."
fly secrets list -a ema-cross-9-20 | grep USE_TESTNET

echo ""
read -p "Continue with test trade? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Running test trade script..."
echo ""

# Create inline Python script and run it
fly ssh console -a ema-cross-9-20 << 'PYTHON_SCRIPT'
python3 << 'EOF'
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("🧪 Testing Trade Execution")
print("=" * 60)
print()

from trading_bot import TradingBot

# Check environment
use_testnet = os.getenv("USE_TESTNET", "false").lower() == "true"
symbol = os.getenv("SYMBOL", "SOL")

print(f"Environment: {'TESTNET' if use_testnet else 'MAINNET'}")
print(f"Symbol: {symbol}")
print()

# Initialize bot
print("1️⃣  Initializing bot...")
try:
    bot = TradingBot()
    print(f"   ✅ Bot initialized")
    print(f"   Wallet: {bot.get_wallet_address()}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    sys.exit(1)

# Get price
print()
print("2️⃣  Getting current price...")
try:
    price = bot.get_current_price(symbol)
    print(f"   ✅ Price: ${price:,.2f}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Calculate small test position
print()
print("3️⃣  Calculating test position...")
test_collateral = 5.0  # Very small amount
leverage = 1  # No leverage

try:
    position_size = bot.calculate_position_size(symbol, test_collateral, leverage)
    print(f"   Collateral: ${test_collateral}")
    print(f"   Position Size: {position_size:.6f} {symbol}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Set leverage
print()
print("4️⃣  Setting leverage...")
try:
    result = bot.set_leverage(symbol, leverage)
    if result.get("success"):
        print(f"   ✅ Leverage set to {leverage}x")
    else:
        print(f"   ⚠️  Leverage setting: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# Execute test trade
print()
print("5️⃣  Executing test trade...")
print(f"   Symbol: {symbol}")
print(f"   Side: BUY")
print(f"   Size: {position_size:.6f} {symbol}")
print()

try:
    result = bot.create_market_order(
        symbol=symbol,
        side="B",  # Buy
        amount=str(position_size),
    )
    
    if result.get("success"):
        print("   ✅ Trade executed successfully!")
        print(f"   Order ID: {result.get('order_id', 'N/A')}")
        print()
        print("   Check your Hyperliquid dashboard to verify the position.")
    else:
        print(f"   ❌ Trade failed: {result.get('error', 'Unknown error')}")
        if result.get("response"):
            print(f"   Response: {result.get('response')}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
PYTHON_SCRIPT

echo ""
echo "✅ Test complete!"
echo ""
echo "Check your Hyperliquid dashboard to verify the trade."

