"""
Simple basic BTC trade test (no confirmation prompt).
Opens a BTC long position immediately with improved TP/SL logic.
"""
import time
from trading_bot import TradingBot


def test_basic_btc_trade_simple():
    """Open a basic BTC long position with improved TP/SL logic."""
    print("🚀 Basic BTC Trade Test")
    print("=" * 60)
    
    bot = TradingBot()
    print(f"✅ Bot initialized")
    print(f"Wallet: {bot.get_wallet_address()}")
    print()
    
    # Configuration
    max_leverage = bot.get_max_leverage("BTC") or 40
    collateral_usd = 25.0
    stop_loss_percent = 25.0  # 25% stop loss
    take_profit_percent = 75.0  # 75% take profit
    
    print(f"📊 Configuration:")
    print(f"   Symbol: BTC")
    print(f"   Collateral: ${collateral_usd}")
    print(f"   Leverage: {max_leverage}x")
    print(f"   Stop Loss: {stop_loss_percent}%")
    print(f"   Take Profit: {take_profit_percent}%")
    print()
    
    # Get current price
    current_price = bot.get_current_price("BTC")
    if not current_price:
        print("❌ Could not get current price")
        return None
    
    print(f"💰 Current Price: ${current_price:,.2f}")
    
    # Calculate TP/SL prices for display
    tp_price = current_price * (1 + take_profit_percent / 100)
    sl_price = current_price * (1 - stop_loss_percent / 100)
    print(f"   TP Target: ${tp_price:,.2f} (+{take_profit_percent}%)")
    print(f"   SL Target: ${sl_price:,.2f} (-{stop_loss_percent}%)")
    print()
    
    # Set leverage
    print(f"📊 Setting leverage to {max_leverage}x...")
    leverage_result = bot.set_leverage("BTC", max_leverage)
    if not leverage_result.get("success") and max_leverage > 25:
        # Try 25x if 40x fails
        leverage_result = bot.set_leverage("BTC", 25)
        if leverage_result.get("success"):
            max_leverage = 25
            print(f"   ✅ Set leverage to {max_leverage}x")
    else:
        print(f"   ✅ Leverage set to {max_leverage}x")
    
    # Calculate position size (will be rounded correctly)
    position_size = bot.calculate_position_size("BTC", collateral_usd, max_leverage)
    sz_decimals = bot.get_size_decimals("BTC")
    print(f"💰 Position Size: {position_size:.{sz_decimals}f} BTC (rounded to {sz_decimals} decimals)")
    print(f"   Position Value: ${collateral_usd * max_leverage:,.2f}")
    print()
    
    # Open position
    print(f"📈 Opening BTC long position...")
    order_result = bot.create_market_order(
        symbol="BTC",
        side="B",  # Buy
        amount=str(position_size),
    )
    
    # Display result
    if not order_result.get("success"):
        error = order_result.get("error", "Unknown error")
        print(f"\n❌ Trade failed: {error}")
        return order_result
    
    print(f"\n✅ Trade executed successfully!")
    order_id = order_result.get("order_id")
    if order_id:
        print(f"   Order ID: {order_id}")
    
    # Wait for position to be confirmed
    print(f"\n⏳ Waiting 2 seconds for position confirmation...")
    time.sleep(2)
    
    # Get actual position size (may differ due to slippage)
    actual_position_size = bot.get_position_size("BTC")
    if actual_position_size:
        print(f"   ✅ Actual position size: {actual_position_size:.{sz_decimals}f} BTC")
        position_size_for_tpsl = actual_position_size
    else:
        print(f"   ⚠️  Could not get actual position size, using calculated size")
        position_size_for_tpsl = position_size
    
    # Set take profit (with retry)
    print(f"\n🎯 Setting take profit at {take_profit_percent}%...")
    tp_result = None
    for attempt in range(3):
        if attempt > 0:
            print(f"   Retry {attempt}/2...")
            time.sleep(1)
        tp_result = bot.set_take_profit(
            "BTC",
            current_price,
            position_size_for_tpsl,
            take_profit_percent,
            is_long=True
        )
        if tp_result.get("success"):
            break
    
    if not tp_result or not tp_result.get("success"):
        error_msg = tp_result.get("error", "Unknown error") if tp_result else "No response"
        response = tp_result.get("response", {}) if tp_result else {}
        if isinstance(response, dict):
            statuses = response.get("response", {}).get("data", {}).get("statuses", [])
            if statuses and "error" in statuses[0]:
                error_msg = statuses[0]["error"]
        print(f"   ❌ TP failed after retries: {error_msg}")
        if response:
            print(f"   Response: {response}")
    else:
        tp_price_actual = tp_result.get("tp_price", tp_price)
        print(f"   ✅ TP set at ${tp_price_actual:,.2f} (+{take_profit_percent}%)")
    
    # Set stop loss (with retry)
    print(f"\n🛡️  Setting stop loss at {stop_loss_percent}%...")
    sl_result = None
    for attempt in range(3):
        if attempt > 0:
            print(f"   Retry {attempt}/2...")
            time.sleep(1)
        sl_result = bot.set_stop_loss(
            "BTC",
            current_price,
            position_size_for_tpsl,
            stop_loss_percent,
            is_long=True
        )
        if sl_result.get("success"):
            break
    
    if not sl_result or not sl_result.get("success"):
        error_msg = sl_result.get("error", "Unknown error") if sl_result else "No response"
        response = sl_result.get("response", {}) if sl_result else {}
        if isinstance(response, dict):
            statuses = response.get("response", {}).get("data", {}).get("statuses", [])
            if statuses and "error" in statuses[0]:
                error_msg = statuses[0]["error"]
        print(f"   ❌ SL failed after retries: {error_msg}")
        if response:
            print(f"   Response: {response}")
    else:
        sl_price_actual = sl_result.get("sl_price", sl_price)
        print(f"   ✅ SL set at ${sl_price_actual:,.2f} (-{stop_loss_percent}%)")
    
    print(f"\n{'='*60}")
    print(f"✅ Test Complete!")
    print(f"{'='*60}")
    
    return {
        "order": order_result,
        "take_profit": tp_result,
        "stop_loss": sl_result,
    }


if __name__ == "__main__":
    test_basic_btc_trade_simple()

