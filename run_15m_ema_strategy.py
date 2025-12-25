"""
EMA 9/20 Crossover Strategy - 15 Minute Timeframe
Checks for crossovers every 15 minutes and executes trades automatically.
"""
from trading_bot import TradingBot
from ema_strategy import EMA9_20Strategy
import time
from datetime import datetime


def run_15m_ema_strategy(continuous: bool = True):
    """
    Run EMA strategy on 15-minute timeframe.
    
    Args:
        continuous: If True, runs continuously checking every 15 minutes
    """
    print("🚀 EMA 9/20 Strategy - 15 Minute Timeframe")
    print("=" * 60)
    
    # Initialize bot
    bot = TradingBot()
    print(f"✅ Bot initialized")
    print(f"Wallet: {bot.get_wallet_address()}")
    print()
    
    # Strategy parameters
    symbols = ["ETH", "SOL", "BTC"]
    collateral_usd = 25.0
    sl_percent = 30.0
    tp_percent = 100.0
    timeframe = "15m"  # 15-minute timeframe
    
    # Get maximum leverage for each asset
    print(f"📊 Getting maximum leverage for each asset...")
    asset_leverages = {}
    for symbol in symbols:
        max_lev = bot.get_max_leverage(symbol)
        if max_lev:
            asset_leverages[symbol] = max_lev
            print(f"   {symbol}: {max_lev}x")
        else:
            # Fallback to 20x if not found
            asset_leverages[symbol] = 20
            print(f"   {symbol}: 20x (fallback)")
    
    print()
    print(f"📊 Strategy Configuration:")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Timeframe: {timeframe}")
    print(f"   Collateral per asset: ${collateral_usd}")
    print(f"   Leverage: Using maximum per asset (see above)")
    print(f"   Stop Loss: {sl_percent}%")
    print(f"   Take Profit: {tp_percent}%")
    print()
    print(f"⚠️  Risk Summary:")
    for symbol in symbols:
        lev = asset_leverages[symbol]
        max_loss = collateral_usd * (sl_percent / 100)
        max_profit = collateral_usd * lev * (tp_percent / 100)
        print(f"   {symbol} ({lev}x): Max Loss ${max_loss:.2f}, Max Profit ${max_profit:.2f}")
    print()
    
    if continuous:
        print(f"🔄 Running in continuous mode - checking every 15 minutes")
        print(f"   Press Ctrl+C to stop")
        print()
    
    check_count = 0
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n{'='*60}")
            print(f"⏰ Check #{check_count} - {current_time}")
            print(f"{'='*60}")
            
            # Create strategies and check for signals
            for symbol in symbols:
                try:
                    # Get maximum leverage for this asset
                    leverage = asset_leverages.get(symbol, 20)
                    
                    # Create EMA strategy with 15m timeframe and asset-specific leverage
                    strategy = EMA9_20Strategy(
                        bot=bot,
                        symbol=symbol,
                        collateral_usd=collateral_usd,
                        leverage=leverage,  # Use maximum leverage for this asset
                        take_profit_percent=tp_percent,
                        stop_loss_percent=sl_percent,
                        timeframe=timeframe,  # 15-minute timeframe
                    )
                    
                    # Calculate EMAs first to get signal info
                    if strategy.calculate_emas():
                        signal_info = strategy.get_signal_info()
                        trend = signal_info.get("trend", "N/A")
                        crossover = signal_info.get("crossover_signal")
                        ema9 = signal_info.get("ema9", 0)
                        ema20 = signal_info.get("ema20", 0)
                        current_price = signal_info.get("current_price", 0)
                        
                        print(f"\n📊 {symbol}:")
                        print(f"   Price: ${current_price:,.2f}")
                        print(f"   EMA 9: ${ema9:,.2f}")
                        print(f"   EMA 20: ${ema20:,.2f}")
                        print(f"   Trend: {trend}")
                        
                        # Detect crossover
                        if strategy.ema9 and strategy.ema20:
                            from technical_indicators import detect_crossover
                            crossover = detect_crossover(strategy.ema9, strategy.ema20)
                            print(f"   Crossover Signal: {crossover if crossover else 'None'}")
                        else:
                            crossover = None
                            print(f"   Crossover Signal: None (insufficient data)")
                    else:
                        print(f"\n📊 {symbol}:")
                        print(f"   ⚠️  Could not calculate EMAs - insufficient data")
                        crossover = None
                    
                    # Check if we should execute
                    if crossover and strategy.should_execute():
                        print(f"   ✅ CROSSOVER DETECTED! Executing trade...")
                        
                        result = strategy.execute()
                        
                        if result.get("success"):
                            print(f"   ✅ Trade executed successfully!")
                            
                            pos = result.get("position", {})
                            order = result.get("order", {})
                            
                            print(f"   Entry Price: ${pos.get('entry_price', 0):,.2f}")
                            print(f"   Position Size: {pos.get('position_size', 0):.6f} {symbol}")
                            
                            if order.get("order_id"):
                                print(f"   Order ID: {order.get('order_id')}")
                            
                            tp = result.get("take_profit", {})
                            sl = result.get("stop_loss", {})
                            
                            if tp.get("success"):
                                print(f"   ✅ TP Set: {tp.get('tp_percent')}%")
                            if sl.get("success"):
                                print(f"   ✅ SL Set: {sl.get('sl_percent')}%")
                        else:
                            error = result.get("error", "Unknown error")
                            print(f"   ❌ Execution failed: {error}")
                    else:
                        print(f"   ℹ️  No crossover - waiting for signal")
                
                except Exception as e:
                    print(f"   ❌ Error processing {symbol}: {e}")
                    import traceback
                    traceback.print_exc()
            
            if not continuous:
                break
            
            # Wait 15 minutes (900 seconds) before next check
            print(f"\n⏳ Waiting 15 minutes until next check...")
            print(f"   Next check at: {(datetime.now().timestamp() + 900):.0f}")
            
            # Sleep for 15 minutes
            time.sleep(900)  # 15 minutes = 900 seconds
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped by user")
        print(f"   Total checks performed: {check_count}")
        print(f"   Strategy monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def run_single_check():
    """Run a single check (for testing)."""
    run_15m_ema_strategy(continuous=False)


if __name__ == "__main__":
    import sys
    
    # Check if running in single-check mode
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("Running single check mode...")
        run_single_check()
    else:
        print("Running continuous mode (checks every 15 minutes)...")
        print("Use --once flag for single check")
        print()
        run_15m_ema_strategy(continuous=True)

