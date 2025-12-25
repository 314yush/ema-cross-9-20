"""
Test script to execute a small live test trade.
WARNING: This will execute a real trade with real funds!
Use with caution and only on testnet first.
"""
import os
import sys
from dotenv import load_dotenv
from trading_bot import TradingBot

load_dotenv()

def test_live_trade():
    """Execute a small test trade."""
    print("⚠️  LIVE TRADE TEST")
    print("=" * 60)
    print("WARNING: This will execute a REAL trade!")
    print()
    
    # Check if testnet
    use_testnet = os.getenv("USE_TESTNET", "false").lower() == "true"
    if not use_testnet:
        print("❌ USE_TESTNET is not set to 'true'")
        print("   This script will execute on MAINNET with real funds!")
        response = input("   Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("   Aborted.")
            return False
    else:
        print("✅ Running on TESTNET (safe)")
    
    print()
    
    # Initialize bot
    print("1️⃣  Initializing bot...")
    try:
        bot = TradingBot()
        print(f"   ✅ Bot initialized")
        print(f"   Wallet: {bot.get_wallet_address()}")
        print(f"   Environment: {'TESTNET' if use_testnet else 'MAINNET'}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print()
    
    # Get symbol and price
    symbol = os.getenv("SYMBOL", "SOL")
    print(f"2️⃣  Getting {symbol} price...")
    try:
        price = bot.get_current_price(symbol)
        if not price:
            print(f"   ❌ Could not get price")
            return False
        print(f"   ✅ Current price: ${price:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Calculate small position
    test_collateral = float(os.getenv("TEST_COLLATERAL", "10.0"))
    leverage = 1  # No leverage for safety
    
    print(f"3️⃣  Calculating position...")
    try:
        position_size = bot.calculate_position_size(symbol, test_collateral, leverage)
        print(f"   Collateral: ${test_collateral}")
        print(f"   Leverage: {leverage}x")
        print(f"   Position Size: {position_size:.6f} {symbol}")
        print(f"   Position Value: ${test_collateral * leverage:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Confirm
    print("4️⃣  Trade Details:")
    print(f"   Symbol: {symbol}")
    print(f"   Side: BUY (Long)")
    print(f"   Size: {position_size:.6f} {symbol}")
    print(f"   Estimated Entry: ~${price:,.2f}")
    print()
    
    confirm = input("   Execute this trade? (yes/no): ")
    if confirm.lower() != "yes":
        print("   Aborted.")
        return False
    
    print()
    
    # Execute trade
    print("5️⃣  Executing trade...")
    try:
        # Set leverage first
        print("   Setting leverage...")
        leverage_result = bot.set_leverage(symbol, leverage)
        if not leverage_result.get("success"):
            print(f"   ⚠️  Leverage setting failed: {leverage_result.get('error')}")
        
        # Place order
        print("   Placing market order...")
        result = bot.create_market_order(
            symbol=symbol,
            side="B",  # Buy
            amount=str(position_size),
        )
        
        if result.get("success"):
            print("   ✅ Trade executed successfully!")
            print(f"   Order ID: {result.get('order_id', 'N/A')}")
            return True
        else:
            print(f"   ❌ Trade failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        # Skip confirmation
        pass
    
    success = test_live_trade()
    sys.exit(0 if success else 1)

