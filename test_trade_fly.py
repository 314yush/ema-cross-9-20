"""
Test trade execution script for Fly.io.
This can be run directly on Fly.io to test trade execution.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_trade():
    """Test executing a small trade."""
    print("🧪 Testing Trade Execution on Fly.io")
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
        return False
    
    # Get price
    print()
    print("2️⃣  Getting current price...")
    try:
        price = bot.get_current_price(symbol)
        print(f"   ✅ Price: ${price:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
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
        return False
    
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
            return True
        else:
            print(f"   ❌ Trade failed: {result.get('error', 'Unknown error')}")
            if result.get("response"):
                print(f"   Response: {result.get('response')}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_trade()
    sys.exit(0 if success else 1)

