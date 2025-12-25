"""
Main entry point for the trading bot.
EMA 9/20 Crossover Strategy - 15 Minute Timeframe
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from trading_bot import TradingBot
from ema_strategy import EMA9_20Strategy
from health_server import HealthServer
from technical_indicators import detect_crossover

# Load environment variables
load_dotenv()

def main():
    """Main entry point."""
    print("🚀 EMA 9/20 Strategy - 15 Minute Timeframe")
    print("=" * 60)
    print(f"Environment: {'TESTNET' if os.getenv('USE_TESTNET', 'false').lower() == 'true' else 'MAINNET'}")
    print()
    
    # Initialize bot
    bot = TradingBot()
    print(f"✅ Bot initialized")
    print(f"Wallet: {bot.get_wallet_address()}")
    print()
    
    # Strategy parameters from environment variables
    symbols_str = os.getenv("SYMBOLS", "ETH,SOL,BTC")
    symbols = [s.strip() for s in symbols_str.split(",")]
    
    # Parse numeric values, stripping quotes if present
    def parse_float(env_var, default):
        value = os.getenv(env_var, str(default))
        # Remove quotes if present
        value = value.strip('"\'')
        return float(value)
    
    collateral_usd = parse_float("COLLATERAL_USD", 25.0)
    sl_percent = parse_float("STOP_LOSS_PERCENT", 30.0)
    tp_percent = parse_float("TAKE_PROFIT_PERCENT", 100.0)
    timeframe = os.getenv("TIMEFRAME", "15m").strip('"\'')
    
    # Get maximum leverage for each asset
    print(f"📊 Getting maximum leverage for each asset...")
    asset_leverages = {}
    for symbol in symbols:
        max_lev = bot.get_max_leverage(symbol)
        if max_lev:
            asset_leverages[symbol] = max_lev
            print(f"   {symbol}: {max_lev}x")
        else:
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
    
    # Start health check server
    health_port = int(os.getenv("HEALTH_CHECK_PORT", os.getenv("PORT", "8080")))
    bot_status = {}
    health_server = HealthServer(port=health_port, bot_status=bot_status)
    health_server.start()
    
    print(f"🔄 Running in continuous mode - checking every {timeframe}")
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
            
            # Update health check status
            health_server.update_status(
                checks=check_count,
                last_check=current_time,
                status="running"
            )
            
            # Check each symbol
            for symbol in symbols:
                try:
                    leverage = asset_leverages.get(symbol, 20)
                    
                    # Create EMA strategy
                    strategy = EMA9_20Strategy(
                        bot=bot,
                        symbol=symbol,
                        collateral_usd=collateral_usd,
                        leverage=leverage,
                        take_profit_percent=tp_percent,
                        stop_loss_percent=sl_percent,
                        timeframe=timeframe,
                    )
                    
                    # Calculate EMAs
                    if strategy.calculate_emas():
                        signal_info = strategy.get_signal_info()
                        trend = signal_info.get("trend", "N/A")
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
                            crossover = detect_crossover(strategy.ema9, strategy.ema20)
                            print(f"   Crossover Signal: {crossover if crossover else 'None'}")
                        else:
                            crossover = None
                            print(f"   Crossover Signal: None (insufficient data)")
                    else:
                        print(f"\n📊 {symbol}:")
                        print(f"   ⚠️  Could not calculate EMAs - insufficient data")
                        crossover = None
                    
                    # Execute if crossover detected
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
            
            # Wait for next check
            timeframe_seconds = {
                "15m": 900,
                "30m": 1800,
                "1h": 3600,
                "4h": 14400,
                "1d": 86400,
            }.get(timeframe, 900)
            
            print(f"\n⏳ Waiting {timeframe} until next check...")
            time.sleep(timeframe_seconds)
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped by user")
        print(f"   Total checks performed: {check_count}")
        health_server.update_status(status="stopped")
        health_server.stop()
        print(f"   Bot stopped")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        health_server.update_status(status="error")
        health_server.stop()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

