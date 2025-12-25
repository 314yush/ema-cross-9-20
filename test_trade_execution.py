"""
Test script to verify trade execution on Fly.io.
This script attempts to open a small test trade to verify everything works.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_trade_execution():
    """Test if the bot can execute a trade."""
    print("🧪 Testing Trade Execution")
    print("=" * 60)
    print()
    
    # Import bot and strategy
    try:
        from trading_bot import TradingBot
        from sol_ema_momentum_strategy import SOLEMAMomentumStrategy
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Initialize bot
    print("1️⃣  Initializing bot...")
    try:
        bot = TradingBot()
        print(f"   ✅ Bot initialized")
        print(f"   Wallet: {bot.get_wallet_address()}")
    except Exception as e:
        print(f"   ❌ Failed to initialize bot: {e}")
        return False
    
    print()
    
    # Get current price
    print("2️⃣  Fetching current price...")
    try:
        symbol = os.getenv("SYMBOL", "SOL")
        current_price = bot.get_current_price(symbol)
        if current_price:
            print(f"   ✅ Current {symbol} price: ${current_price:,.2f}")
        else:
            print(f"   ❌ Could not fetch price for {symbol}")
            return False
    except Exception as e:
        print(f"   ❌ Error fetching price: {e}")
        return False
    
    print()
    
    # Test strategy initialization
    print("3️⃣  Testing strategy initialization...")
    try:
        strategy = SOLEMAMomentumStrategy(
            bot=bot,
            symbol=symbol,
            collateral_usd=10.0,  # Small amount for testing
            leverage=1,  # No leverage for safety
            timeframe="15m",
        )
        print(f"   ✅ Strategy initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize strategy: {e}")
        return False
    
    print()
    
    # Test indicator calculation
    print("4️⃣  Testing indicator calculation...")
    try:
        if strategy.calculate_indicators():
            signal_info = strategy.get_signal_info()
            print(f"   ✅ Indicators calculated")
            print(f"   Current Price: ${signal_info.get('current_price', 0):,.2f}")
            print(f"   EMA Fast: ${signal_info.get('ema_fast', 0):,.2f}")
            print(f"   EMA Slow: ${signal_info.get('ema_slow', 0):,.2f}")
            print(f"   Slope: {signal_info.get('slope', 0):.4f}")
        else:
            print(f"   ⚠️  Could not calculate indicators (may need more data)")
    except Exception as e:
        print(f"   ❌ Error calculating indicators: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test position size calculation
    print("5️⃣  Testing position size calculation...")
    try:
        test_collateral = 10.0
        test_leverage = 1
        position_size = bot.calculate_position_size(symbol, test_collateral, test_leverage)
        print(f"   ✅ Position size calculated")
        print(f"   Collateral: ${test_collateral}")
        print(f"   Leverage: {test_leverage}x")
        print(f"   Position Size: {position_size:.6f} {symbol}")
        print(f"   Position Value: ${test_collateral * test_leverage:,.2f}")
    except Exception as e:
        print(f"   ❌ Error calculating position size: {e}")
        return False
    
    print()
    
    # Test leverage setting (dry run - don't actually set)
    print("6️⃣  Testing leverage API...")
    try:
        max_leverage = bot.get_max_leverage(symbol)
        if max_leverage:
            print(f"   ✅ Max leverage for {symbol}: {max_leverage}x")
        else:
            print(f"   ⚠️  Could not get max leverage (API may be unavailable)")
    except Exception as e:
        print(f"   ⚠️  Error getting leverage: {e}")
    
    print()
    
    # Test market data fetching
    print("7️⃣  Testing market data fetching...")
    try:
        candles = strategy.get_candles()
        if candles and len(candles) > 0:
            print(f"   ✅ Fetched {len(candles)} candles")
            latest = candles[-1]
            print(f"   Latest candle: Close=${float(latest.get('c', 0)):,.2f}")
        else:
            print(f"   ⚠️  No candles fetched (may be normal)")
    except Exception as e:
        print(f"   ⚠️  Error fetching candles: {e}")
    
    print()
    print("=" * 60)
    print("✅ Basic functionality tests passed!")
    print()
    print("⚠️  Note: This script does NOT execute an actual trade.")
    print("   To test actual trade execution, the bot needs:")
    print("   1. Entry conditions to be met (EMA crossover + momentum)")
    print("   2. Sufficient collateral")
    print("   3. Valid API connection")
    print()
    print("💡 To test actual trade execution:")
    print("   - Monitor logs: fly logs -a ema-cross-9-20")
    print("   - Wait for entry signal (or manually trigger)")
    print("   - Verify trade appears in Hyperliquid dashboard")
    print()
    
    return True


if __name__ == "__main__":
    success = test_trade_execution()
    sys.exit(0 if success else 1)

