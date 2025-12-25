"""
Simple basic BTC trade test (no confirmation prompt).
Opens a BTC long position immediately.
"""
from trading_bot import TradingBot


def test_basic_btc_trade_simple():
    """Open a basic BTC long position - simple version."""
    print("🚀 Basic BTC Trade Test")
    print("=" * 60)
    
    bot = TradingBot()
    print(f"✅ Bot initialized")
    print(f"Wallet: {bot.get_wallet_address()}")
    print()
    
    # Get max leverage
    max_leverage = bot.get_max_leverage("BTC") or 40
    collateral_usd = 25.0
    
    print(f"📊 Configuration:")
    print(f"   Symbol: BTC")
    print(f"   Collateral: ${collateral_usd}")
    print(f"   Leverage: {max_leverage}x")
    print(f"   Stop Loss: 30%")
    print(f"   Take Profit: 100%")
    print()
    
    # Get current price
    current_price = bot.get_current_price("BTC")
    if not current_price:
        print("❌ Could not get current price")
        return None
    
    print(f"💰 Current Price: ${current_price:,.2f}")
    
    # Set leverage
    print(f"\n📊 Setting leverage to {max_leverage}x...")
    leverage_result = bot.set_leverage("BTC", max_leverage)
    if not leverage_result.get("success") and max_leverage > 25:
        # Try 25x if 40x fails
        leverage_result = bot.set_leverage("BTC", 25)
        if leverage_result.get("success"):
            max_leverage = 25
    
    # Calculate position size (will be rounded correctly)
    position_size = bot.calculate_position_size("BTC", collateral_usd, max_leverage)
    sz_decimals = bot.get_size_decimals("BTC")
    print(f"💰 Position Size: {position_size:.{sz_decimals}f} BTC (rounded to {sz_decimals} decimals)")
    
    # Open position
    print(f"\n📈 Opening BTC long position...")
    order_result = bot.create_market_order(
        symbol="BTC",
        side="B",  # Buy
        amount=str(position_size),
    )
    
    # Display result
    if order_result.get("success"):
        print(f"\n✅ Trade executed successfully!")
        order_id = order_result.get("order_id")
        if order_id:
            print(f"Order ID: {order_id}")
        
        # Set TP/SL
        print(f"\n🎯 Setting TP/SL...")
        
        tp_result = bot.set_take_profit("BTC", current_price, position_size, 100.0, is_long=True)
        if tp_result.get("success"):
            print(f"✅ TP set: 100%")
        
        sl_result = bot.set_stop_loss("BTC", current_price, position_size, 30.0, is_long=True)
        if sl_result.get("success"):
            print(f"✅ SL set: 30%")
    else:
        print(f"\n❌ Trade failed: {order_result.get('error')}")
    
    return order_result


if __name__ == "__main__":
    test_basic_btc_trade_simple()

