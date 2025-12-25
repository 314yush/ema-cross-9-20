"""
Backtest runner for SOL EMA Momentum Crossover Strategy.
Runs backtest for 365+ days with 1000 USDC initial capital.
"""
from datetime import datetime, timedelta
from trading_bot import TradingBot
from backtest import BacktestEngine
import json


def format_currency(value: float) -> str:
    """Format value as currency."""
    return f"${value:,.2f}"


def format_percent(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.2f}%"


def print_backtest_results(results: dict):
    """Print backtest results in a formatted way."""
    if not results.get("success"):
        print(f"\n❌ Backtest failed: {results.get('error', 'Unknown error')}")
        return
    
    print(f"\n{'='*60}")
    print(f"📊 BACKTEST RESULTS")
    print(f"{'='*60}\n")
    
    # Capital metrics
    print(f"💰 Capital:")
    print(f"   Initial Capital: {format_currency(results['initial_capital'])}")
    print(f"   Final Capital:   {format_currency(results['final_capital'])}")
    print(f"   Total Return:    {format_percent(results['total_return'])}")
    print(f"   Total P&L:        {format_currency(results['total_pnl'])}\n")
    
    # Trade statistics
    print(f"📈 Trade Statistics:")
    print(f"   Total Trades:    {results['total_trades']}")
    print(f"   Winning Trades:  {results['winning_trades']}")
    print(f"   Losing Trades:   {results['losing_trades']}")
    print(f"   Win Rate:        {format_percent(results['win_rate'])}\n")
    
    # Performance metrics
    print(f"📊 Performance Metrics:")
    print(f"   Average Win:     {format_currency(results['avg_win'])}")
    print(f"   Average Loss:    {format_currency(results['avg_loss'])}")
    print(f"   Profit Factor:   {results['profit_factor']:.2f}")
    print(f"   Avg Risk/Reward: {results['avg_risk_reward']:.2f}")
    print(f"   Max Drawdown:    {format_percent(results['max_drawdown'])}\n")
    
    # Exit statistics
    print(f"🎯 Exit Statistics:")
    print(f"   TP Exits:        {results['tp_trades']}")
    print(f"   SL Exits:        {results['sl_trades']}")
    print(f"   Other Exits:     {results['total_trades'] - results['tp_trades'] - results['sl_trades']}\n")
    
    # Trade breakdown
    if results['total_trades'] > 0:
        print(f"📋 Trade Breakdown:")
        print(f"   Best Trade:      {format_currency(max(t['pnl'] for t in results['trades']))}")
        print(f"   Worst Trade:     {format_currency(min(t['pnl'] for t in results['trades']))}")
        
        # Long vs Short
        long_trades = [t for t in results['trades'] if t['side'] == 'B']
        short_trades = [t for t in results['trades'] if t['side'] == 'A']
        if long_trades:
            long_win_rate = len([t for t in long_trades if t['pnl'] > 0]) / len(long_trades) * 100
            print(f"   Long Trades:     {len(long_trades)} (Win Rate: {format_percent(long_win_rate)})")
        if short_trades:
            short_win_rate = len([t for t in short_trades if t['pnl'] > 0]) / len(short_trades) * 100
            print(f"   Short Trades:    {len(short_trades)} (Win Rate: {format_percent(short_win_rate)})")
    
    print(f"\n{'='*60}\n")


def run_backtest(
    days: int = 365,
    initial_capital: float = 1000.0,
    symbol: str = "SOL",
    save_results: bool = True,
):
    """
    Run backtest for SOL EMA Momentum Crossover Strategy.
    
    Args:
        days: Number of days to backtest (default: 365)
        initial_capital: Initial capital in USD (default: 1000.0)
        symbol: Trading symbol (default: "SOL")
        save_results: Whether to save results to JSON file (default: True)
    """
    print(f"\n{'='*60}")
    print(f"🚀 SOL EMA Momentum Crossover Strategy Backtest")
    print(f"{'='*60}\n")
    
    # Initialize bot (for data fetching only)
    print("🔧 Initializing trading bot...")
    try:
        bot = TradingBot()
        print(f"✅ Bot initialized (Wallet: {bot.get_wallet_address()})\n")
    except Exception as e:
        print(f"❌ Failed to initialize bot: {e}")
        print("Note: Bot initialization is only needed for data fetching.")
        print("You can still run backtests if you have historical data.\n")
        return
    
    # Strategy parameters (matching the strategy prompt)
    strategy_params = {
        "timeframe": "15m",
        "fast_ema_period": 9,
        "slow_ema_period": 15,
        "atr_period": 14,
        "slope_lookback": 4,
        "slope_threshold": 0.10,
        "atr_stop_multiplier": 0.5,
        "risk_reward_ratio": 3.0,
        "risk_per_trade_percent": 1.5,  # 1-2% risk per trade
    }
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    print(f"📅 Backtest Period:")
    print(f"   Start: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End:   {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Days:  {days}\n")
    
    print(f"💰 Capital:")
    print(f"   Initial: {format_currency(initial_capital)}\n")
    
    print(f"⚙️  Strategy Parameters:")
    for key, value in strategy_params.items():
        print(f"   {key}: {value}")
    print()
    
    # Initialize backtest engine
    backtest = BacktestEngine(
        bot=bot,
        symbol=symbol,
        initial_capital=initial_capital,
        strategy_params=strategy_params,
        start_date=start_date,
        end_date=end_date,
        days=days,
    )
    
    # Run backtest
    results = backtest.run_backtest()
    
    # Print results
    print_backtest_results(results)
    
    # Save results to file
    if save_results and results.get("success"):
        filename = f"backtest_results_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"💾 Results saved to: {filename}\n")
        except Exception as e:
            print(f"⚠️  Could not save results to file: {e}\n")
    
    return results


if __name__ == "__main__":
    import sys
    
    # Default parameters
    days = 365
    initial_capital = 1000.0
    symbol = "SOL"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid days argument: {sys.argv[1]}, using default: {days}")
    
    if len(sys.argv) > 2:
        try:
            initial_capital = float(sys.argv[2])
        except ValueError:
            print(f"⚠️  Invalid capital argument: {sys.argv[2]}, using default: {initial_capital}")
    
    if len(sys.argv) > 3:
        symbol = sys.argv[3].upper()
    
    print(f"\n{'='*60}")
    print(f"SOL EMA Momentum Crossover Strategy Backtest")
    print(f"{'='*60}")
    print(f"Days: {days}")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Symbol: {symbol}")
    print(f"{'='*60}\n")
    
    results = run_backtest(
        days=days,
        initial_capital=initial_capital,
        symbol=symbol,
    )
    
    if results and results.get("success"):
        print(f"\n✅ Backtest completed successfully!")
        print(f"   Final Capital: {format_currency(results['final_capital'])}")
        print(f"   Total Return: {format_percent(results['total_return'])}")
        print(f"   Total Trades: {results['total_trades']}")
    else:
        print(f"\n❌ Backtest failed or produced no results.")

