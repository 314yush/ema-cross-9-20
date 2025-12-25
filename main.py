"""
Main entry point for the trading bot.
Supports running different strategies based on environment variables.
"""
import os
import sys
from dotenv import load_dotenv
from health_server import HealthServer

# Load environment variables
load_dotenv()

def main():
    """Main entry point."""
    # Get strategy from environment variable
    strategy = os.getenv("STRATEGY", "sol_momentum").lower()
    
    print(f"🚀 Starting Trading Bot")
    print(f"   Strategy: {strategy}")
    print(f"   Environment: {'TESTNET' if os.getenv('USE_TESTNET', 'false').lower() == 'true' else 'MAINNET'}")
    print()
    
    if strategy == "sol_momentum" or strategy == "sol_ema_momentum":
        # Run SOL EMA Momentum Strategy
        from sol_ema_momentum_strategy import SOLEMAMomentumStrategy
        from trading_bot import TradingBot
        import time
        from datetime import datetime
        
        print("📊 SOL EMA Momentum Crossover Strategy")
        print("=" * 60)
        
        # Initialize bot
        bot = TradingBot()
        print(f"✅ Bot initialized")
        print(f"Wallet: {bot.get_wallet_address()}")
        print()
        
        # Strategy parameters from environment variables
        symbol = os.getenv("SYMBOL", "SOL")
        collateral_usd = float(os.getenv("COLLATERAL_USD", "1000.0"))
        leverage = int(os.getenv("LEVERAGE", "10"))
        timeframe = os.getenv("TIMEFRAME", "15m")
        
        # Risk management parameters
        risk_per_trade_percent = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.5"))
        atr_stop_multiplier = float(os.getenv("ATR_STOP_MULTIPLIER", "0.5"))
        risk_reward_ratio = float(os.getenv("RISK_REWARD_RATIO", "3.0"))
        slope_threshold = float(os.getenv("SLOPE_THRESHOLD", "0.10"))
        
        print(f"📊 Strategy Configuration:")
        print(f"   Symbol: {symbol}")
        print(f"   Timeframe: {timeframe}")
        print(f"   Collateral: ${collateral_usd:,.2f}")
        print(f"   Leverage: {leverage}x")
        print(f"   Risk per Trade: {risk_per_trade_percent}%")
        print(f"   Risk/Reward: 1:{risk_reward_ratio}")
        print()
        
        # Create strategy instance
        strategy_instance = SOLEMAMomentumStrategy(
            bot=bot,
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            timeframe=timeframe,
            risk_per_trade_percent=risk_per_trade_percent,
            atr_stop_multiplier=atr_stop_multiplier,
            risk_reward_ratio=risk_reward_ratio,
            slope_threshold=slope_threshold,
        )
        
        # Calculate timeframe in seconds
        timeframe_seconds = {
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400,
        }.get(timeframe, 900)
        
        print(f"🔄 Running in continuous mode - checking every {timeframe}")
        print(f"   Press Ctrl+C to stop")
        print()
        
        # Start health check server to prevent Railway from sleeping
        health_port = int(os.getenv("HEALTH_CHECK_PORT", "8080"))
        bot_status = {}
        health_server = HealthServer(port=health_port, bot_status=bot_status)
        health_server.start()
        
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
                
                try:
                    # Check if we should execute
                    if strategy_instance.should_execute():
                        print(f"✅ Entry conditions met! Executing trade...")
                        
                        result = strategy_instance.execute()
                        
                        if result.get("success"):
                            print(f"✅ Trade executed successfully!")
                            
                            pos = result.get("position", {})
                            print(f"   Entry Price: ${pos.get('entry_price', 0):,.2f}")
                            print(f"   Position Size: {pos.get('position_size', 0):.6f} {symbol}")
                            
                            rm = result.get("risk_management", {})
                            if rm:
                                print(f"   Stop Loss: ${rm.get('stop_loss_price', 0):,.2f}")
                                print(f"   Take Profit: ${rm.get('take_profit_price', 0):,.2f}")
                        else:
                            error = result.get("error", "Unknown error")
                            print(f"   ❌ Execution failed: {error}")
                    else:
                        signal_info = strategy_instance.get_signal_info()
                        print(f"ℹ️  No entry signal")
                        if signal_info.get("current_price"):
                            print(f"   Current Price: ${signal_info.get('current_price'):,.2f}")
                            print(f"   EMA Fast: ${signal_info.get('ema_fast', 0):,.2f}")
                            print(f"   EMA Slow: ${signal_info.get('ema_slow', 0):,.2f}")
                            print(f"   Slope: {signal_info.get('slope', 0):.4f}")
                
                except Exception as e:
                    print(f"❌ Error during check: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Wait for next check
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
    
    elif strategy == "ema_9_20":
        # Run EMA 9/20 Strategy
        # Start health check server to prevent Railway from sleeping
        health_port = int(os.getenv("HEALTH_CHECK_PORT", "8080"))
        bot_status = {}
        health_server = HealthServer(port=health_port, bot_status=bot_status)
        health_server.start()
        
        try:
            from run_15m_ema_strategy import run_15m_ema_strategy
            run_15m_ema_strategy(continuous=True)
        except KeyboardInterrupt:
            health_server.update_status(status="stopped")
            health_server.stop()
        except Exception as e:
            health_server.update_status(status="error")
            health_server.stop()
            raise
    
    else:
        print(f"❌ Unknown strategy: {strategy}")
        print(f"   Available strategies: sol_momentum, ema_9_20")
        sys.exit(1)


if __name__ == "__main__":
    main()

