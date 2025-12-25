"""
Backtesting module for trading strategies.
Simulates trades over historical data and calculates performance metrics.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import time
from trading_bot import TradingBot
from sol_ema_momentum_strategy import SOLEMAMomentumStrategy
from technical_indicators import (
    calculate_ema,
    detect_crossover,
    calculate_rsi,
    calculate_atr,
    calculate_volume_ma,
    calculate_ema_slope,
)


class Trade:
    """Represents a single trade."""
    
    def __init__(
        self,
        entry_time: int,
        entry_price: float,
        side: str,  # "B" for long, "A" for short
        position_size: float,
        stop_loss_price: float,
        take_profit_price: float,
        risk_amount: float,
    ):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.side = side
        self.position_size = position_size
        self.stop_loss_price = stop_loss_price
        self.take_profit_price = take_profit_price
        self.risk_amount = risk_amount
        self.exit_time: Optional[int] = None
        self.exit_price: Optional[float] = None
        self.exit_reason: Optional[str] = None  # "TP", "SL", "OPPOSITE_SIGNAL", "END"
        self.pnl: Optional[float] = None
        self.pnl_percent: Optional[float] = None
    
    def close(self, exit_time: int, exit_price: float, exit_reason: str):
        """Close the trade."""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        
        # Calculate PnL
        if self.side == "B":  # Long
            self.pnl = (exit_price - self.entry_price) * self.position_size
        else:  # Short
            self.pnl = (self.entry_price - exit_price) * self.position_size
        
        # Calculate PnL percentage
        position_value = self.entry_price * self.position_size
        self.pnl_percent = (self.pnl / position_value) * 100 if position_value > 0 else 0
    
    def is_open(self) -> bool:
        """Check if trade is still open."""
        return self.exit_time is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary."""
        return {
            "entry_time": self.entry_time,
            "entry_price": self.entry_price,
            "side": self.side,
            "position_size": self.position_size,
            "stop_loss_price": self.stop_loss_price,
            "take_profit_price": self.take_profit_price,
            "risk_amount": self.risk_amount,
            "exit_time": self.exit_time,
            "exit_price": self.exit_price,
            "exit_reason": self.exit_reason,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
        }


class BacktestEngine:
    """Backtesting engine for trading strategies."""
    
    def __init__(
        self,
        bot: TradingBot,
        symbol: str,
        initial_capital: float,
        strategy_params: Dict[str, Any],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 365,
    ):
        """
        Initialize backtest engine.
        
        Args:
            bot: TradingBot instance (for data fetching)
            symbol: Trading symbol
            initial_capital: Starting capital in USD
            strategy_params: Parameters for the strategy
            start_date: Start date for backtest (if None, uses days from end_date)
            end_date: End date for backtest (if None, uses current time)
            days: Number of days to backtest (if start_date is None)
        """
        self.bot = bot
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.strategy_params = strategy_params
        
        # Set date range
        if end_date is None:
            end_date = datetime.now()
        self.end_date = end_date
        
        if start_date is None:
            start_date = end_date - timedelta(days=days)
        self.start_date = start_date
        
        # Convert to timestamps (milliseconds)
        self.start_timestamp = int(start_date.timestamp() * 1000)
        self.end_timestamp = int(end_date.timestamp() * 1000)
        
        # Trading state
        self.capital = initial_capital
        self.open_trades: List[Trade] = []
        self.closed_trades: List[Trade] = []
        self.max_open_trades = 3  # Maximum concurrent trades
        
        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_capital = initial_capital
    
    def fetch_historical_data(self, timeframe: str = "15m") -> List[Dict[str, Any]]:
        """
        Fetch historical candle data for the backtest period.
        
        Args:
            timeframe: Candle timeframe
        
        Returns:
            List of candle dictionaries
        """
        try:
            candles = self.bot.info.candles_snapshot(
                self.symbol,
                timeframe,
                self.start_timestamp,
                self.end_timestamp
            )
            
            if isinstance(candles, list):
                # Sort by time (oldest first)
                return sorted(candles, key=lambda x: x.get('t', 0))
            else:
                print(f"⚠️  Unexpected candle format for {self.symbol}")
                return []
        except Exception as e:
            print(f"❌ Error fetching historical data: {e}")
            return []
    
    def check_entry_conditions(
        self,
        candles: List[Dict[str, Any]],
        idx: int,
        fast_ema: List[float],
        slow_ema: List[float],
        atr: List[float],
        prices: List[float],
        highs: List[float],
        lows: List[float],
        strategy_params: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Check if entry conditions are met at a given candle index.
        
        Returns:
            Dictionary with entry signal info if conditions met, None otherwise
        """
        if idx < 1:
            return None
        
        # Detect crossover
        if idx < len(fast_ema) - 1:
            # Check crossover between idx-1 and idx
            prev_fast = fast_ema[idx - 1]
            prev_slow = slow_ema[idx - 1]
            curr_fast = fast_ema[idx]
            curr_slow = slow_ema[idx]
            
            if None in [prev_fast, prev_slow, curr_fast, curr_slow]:
                return None
            
            crossover_signal = None
            if prev_fast <= prev_slow and curr_fast > curr_slow:
                crossover_signal = "BUY"
            elif prev_fast >= prev_slow and curr_fast < curr_slow:
                crossover_signal = "SELL"
            
            if crossover_signal is None:
                return None
            
            # Get current values (use idx+1 for current candle if available, else idx)
            current_idx = min(idx + 1, len(prices) - 1)
            
            # Need enough data for slope calculation
            slope_lookback = strategy_params.get("slope_lookback", 4)
            if current_idx < slope_lookback:
                return None
            
            current_price = prices[current_idx]
            current_atr = atr[current_idx] if current_idx < len(atr) else None
            
            if current_atr is None:
                return None
            
            # Calculate EMA slope
            slope = calculate_ema_slope(fast_ema[:current_idx + 1], slope_lookback)
            if slope is None:
                return None
            
            # Get crossover candle data
            crossover_high = highs[idx]
            crossover_low = lows[idx]
            
            slope_threshold = strategy_params.get("slope_threshold", 0.10)
            atr_stop_multiplier = strategy_params.get("atr_stop_multiplier", 0.5)
            risk_reward_ratio = strategy_params.get("risk_reward_ratio", 3.0)
            risk_per_trade_percent = strategy_params.get("risk_per_trade_percent", 1.5)
            
            # Check entry conditions
            if crossover_signal == "BUY":
                # Long entry conditions
                # 1. Momentum strength (slope > threshold)
                if slope <= slope_threshold:
                    return None
                # 2. Price action confirmation (close above crossover candle high)
                if current_price <= crossover_high:
                    return None
                
                # Calculate risk management
                entry_price = current_price
                stop_loss_price = crossover_low - (atr_stop_multiplier * current_atr)
                risk_per_unit = entry_price - stop_loss_price
                take_profit_price = entry_price + (risk_reward_ratio * risk_per_unit)
                
                return {
                    "signal": "BUY",
                    "side": "B",
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "take_profit_price": take_profit_price,
                    "entry_time": candles[current_idx]["t"],
                    "crossover_candle_idx": idx,
                }
            
            elif crossover_signal == "SELL":
                # Short entry conditions
                # 1. Momentum strength (slope < -threshold)
                if slope >= -slope_threshold:
                    return None
                # 2. Price action confirmation (close below crossover candle low)
                if current_price >= crossover_low:
                    return None
                
                # Calculate risk management
                entry_price = current_price
                stop_loss_price = crossover_high + (atr_stop_multiplier * current_atr)
                risk_per_unit = stop_loss_price - entry_price
                take_profit_price = entry_price - (risk_reward_ratio * risk_per_unit)
                
                return {
                    "signal": "SELL",
                    "side": "A",
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "take_profit_price": take_profit_price,
                    "entry_time": candles[current_idx]["t"],
                    "crossover_candle_idx": idx,
                }
        
        return None
    
    def check_exit_conditions(
        self,
        trade: Trade,
        current_candle: Dict[str, Any],
        fast_ema: List[float],
        slow_ema: List[float],
        candle_idx: int,
    ) -> Optional[str]:
        """
        Check if a trade should be closed.
        
        Returns:
            Exit reason if trade should close, None otherwise
        """
        current_price = float(current_candle["c"])
        current_high = float(current_candle["h"])
        current_low = float(current_candle["l"])
        
        # Check for opposite signal (as per strategy: exit on opposite crossover)
        if candle_idx >= 1 and candle_idx < len(fast_ema):
            prev_fast = fast_ema[candle_idx - 1]
            prev_slow = slow_ema[candle_idx - 1]
            curr_fast = fast_ema[candle_idx]
            curr_slow = slow_ema[candle_idx]
            
            if None not in [prev_fast, prev_slow, curr_fast, curr_slow]:
                # Check for opposite crossover
                if trade.side == "B":  # Long position
                    # Exit if bearish crossover occurs
                    if prev_fast >= prev_slow and curr_fast < curr_slow:
                        return "OPPOSITE_SIGNAL"
                else:  # Short position
                    # Exit if bullish crossover occurs
                    if prev_fast <= prev_slow and curr_fast > curr_slow:
                        return "OPPOSITE_SIGNAL"
        
        # Check stop loss and take profit
        if trade.side == "B":  # Long
            # Check stop loss
            if current_low <= trade.stop_loss_price:
                return "SL"
            # Check take profit
            if current_high >= trade.take_profit_price:
                return "TP"
        else:  # Short
            # Check stop loss
            if current_high >= trade.stop_loss_price:
                return "SL"
            # Check take profit
            if current_low <= trade.take_profit_price:
                return "TP"
        
        return None
    
    def run_backtest(self) -> Dict[str, Any]:
        """
        Run the backtest.
        
        Returns:
            Dictionary with backtest results and metrics
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting Backtest")
        print(f"{'='*60}")
        print(f"Symbol: {self.symbol}")
        print(f"Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Strategy: SOL EMA Momentum Crossover")
        print(f"{'='*60}\n")
        
        # Fetch historical data
        timeframe = self.strategy_params.get("timeframe", "15m")
        print(f"📊 Fetching historical data ({timeframe})...")
        candles = self.fetch_historical_data(timeframe)
        
        if len(candles) < 100:
            return {
                "success": False,
                "error": f"Insufficient historical data: {len(candles)} candles",
            }
        
        print(f"✅ Fetched {len(candles)} candles\n")
        
        # Extract price data
        prices = [float(c["c"]) for c in candles]
        highs = [float(c["h"]) for c in candles]
        lows = [float(c["l"]) for c in candles]
        
        # Calculate indicators
        print(f"📈 Calculating indicators...")
        fast_ema_period = self.strategy_params.get("fast_ema_period", 9)
        slow_ema_period = self.strategy_params.get("slow_ema_period", 15)
        atr_period = self.strategy_params.get("atr_period", 14)
        
        fast_ema = calculate_ema(prices, fast_ema_period)
        slow_ema = calculate_ema(prices, slow_ema_period)
        atr = calculate_atr(highs, lows, prices, atr_period)
        
        print(f"✅ Indicators calculated\n")
        
        # Simulate trading
        print(f"🔄 Simulating trades...")
        risk_per_trade_percent = self.strategy_params.get("risk_per_trade_percent", 1.5)
        
        # Iterate through candles
        for i in range(len(candles)):
            current_candle = candles[i]
            current_time = current_candle["t"]
            
            # Check exit conditions for open trades
            for trade in self.open_trades[:]:  # Copy list to avoid modification during iteration
                exit_reason = self.check_exit_conditions(trade, current_candle, fast_ema, slow_ema, i)
                if exit_reason:
                    # Close trade
                    exit_price = float(current_candle["c"])
                    trade.close(current_time, exit_price, exit_reason)
                    self.closed_trades.append(trade)
                    self.open_trades.remove(trade)
                    
                    # Update capital
                    self.capital += trade.pnl
                    self.total_pnl += trade.pnl
                    
                    # Update metrics
                    self.total_trades += 1
                    if trade.pnl > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
                    
                    # Update drawdown
                    if self.capital > self.peak_capital:
                        self.peak_capital = self.capital
                    drawdown = ((self.peak_capital - self.capital) / self.peak_capital) * 100
                    if drawdown > self.max_drawdown:
                        self.max_drawdown = drawdown
            
            # Check entry conditions (only if we have room for more trades)
            # Entry happens on the candle AFTER crossover (when price confirms)
            if len(self.open_trades) < self.max_open_trades and i >= 2:
                # Check for entry signal (crossover happened between i-2 and i-1, confirmation at i)
                entry_signal = self.check_entry_conditions(
                    candles, i - 1, fast_ema, slow_ema, atr,
                    prices, highs, lows, self.strategy_params
                )
                
                # Entry signal checks crossover at i-1 and confirmation at i
                # So we enter at candle i if signal is valid
                if entry_signal:
                    crossover_idx = entry_signal["crossover_candle_idx"]
                    
                    # Verify we're at the confirmation candle (i should be crossover_idx + 1)
                    if i == crossover_idx + 1:
                        # Calculate position size based on risk
                        entry_price = entry_signal["entry_price"]
                        stop_loss_price = entry_signal["stop_loss_price"]
                        
                        if entry_signal["side"] == "B":  # Long
                            risk_per_unit = entry_price - stop_loss_price
                        else:  # Short
                            risk_per_unit = stop_loss_price - entry_price
                        
                        if risk_per_unit > 0:
                            risk_amount = self.capital * (risk_per_trade_percent / 100)
                            position_size = risk_amount / risk_per_unit
                            
                            # Use current candle's timestamp and close price for entry
                            entry_time = candles[i]["t"]
                            entry_price = prices[i]  # Use actual close price of confirmation candle
                            
                            # Create trade
                            trade = Trade(
                                entry_time=entry_time,
                                entry_price=entry_price,
                                side=entry_signal["side"],
                                position_size=position_size,
                                stop_loss_price=stop_loss_price,
                                take_profit_price=entry_signal["take_profit_price"],
                                risk_amount=risk_amount,
                            )
                            
                            self.open_trades.append(trade)
            
            # Close any remaining open trades at the end
            if i == len(candles) - 1:
                for trade in self.open_trades[:]:
                    exit_price = float(current_candle["c"])
                    trade.close(current_time, exit_price, "END")
                    self.closed_trades.append(trade)
                    self.open_trades.remove(trade)
                    
                    self.capital += trade.pnl
                    self.total_pnl += trade.pnl
                    self.total_trades += 1
                    if trade.pnl > 0:
                        self.winning_trades += 1
                    else:
                        self.losing_trades += 1
        
        print(f"✅ Backtest complete\n")
        
        # Calculate final metrics
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.closed_trades:
            return {
                "success": False,
                "error": "No trades executed",
            }
        
        # Basic metrics
        total_pnl = sum(t.pnl for t in self.closed_trades)
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        # Win rate
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Average win/loss
        winning_pnls = [t.pnl for t in self.closed_trades if t.pnl > 0]
        losing_pnls = [t.pnl for t in self.closed_trades if t.pnl < 0]
        
        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0
        avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0
        
        # Profit factor
        total_wins = sum(winning_pnls) if winning_pnls else 0
        total_losses = abs(sum(losing_pnls)) if losing_pnls else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Risk-reward ratio (average)
        avg_rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Trades by exit reason
        tp_trades = len([t for t in self.closed_trades if t.exit_reason == "TP"])
        sl_trades = len([t for t in self.closed_trades if t.exit_reason == "SL"])
        
        return {
            "success": True,
            "initial_capital": self.initial_capital,
            "final_capital": self.capital,
            "total_return": total_return,
            "total_pnl": total_pnl,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "avg_risk_reward": avg_rr,
            "max_drawdown": self.max_drawdown,
            "tp_trades": tp_trades,
            "sl_trades": sl_trades,
            "trades": [t.to_dict() for t in self.closed_trades],
        }

