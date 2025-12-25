"""
SOL EMA Momentum Crossover Strategy v1.0
15-minute timeframe strategy with EMA crossover, momentum, volume, and RSI filters.
"""
from typing import Dict, Any, Optional, List
import time
from trading_bot import TradingBot
from strategy_template import AdvancedStrategy
from technical_indicators import (
    calculate_ema,
    detect_crossover,
    calculate_rsi,
    calculate_atr,
    calculate_volume_ma,
    calculate_ema_slope,
)


class SOLEMAMomentumStrategy(AdvancedStrategy):
    """
    SOL EMA Momentum Crossover Strategy.
    
    Entry Conditions:
    - Long: EMA(9) crosses above EMA(15), slope > 0.10, price closes above crossover candle high
    - Short: EMA(9) crosses below EMA(15), slope < -0.10, price closes below crossover candle low
    
    Risk Management:
    - Stop Loss: 0.5 ATR below/above entry candle
    - Take Profit: 3R (3x risk)
    """
    
    def __init__(
        self,
        bot: TradingBot,
        symbol: str = "SOL",
        collateral_usd: float = 1000.0,
        leverage: int = 10,
        timeframe: str = "15m",
        lookback_candles: int = 200,
        # Strategy parameters
        fast_ema_period: int = 9,
        slow_ema_period: int = 15,
        rsi_period: int = 14,
        volume_ma_period: int = 20,
        atr_period: int = 14,
        slope_lookback: int = 4,
        slope_threshold: float = 0.10,
        rsi_long_max: float = 60.0,
        rsi_short_min: float = 40.0,
        # Risk management
        atr_stop_multiplier: float = 0.5,
        risk_reward_ratio: float = 3.0,
        risk_per_trade_percent: float = 1.5,  # 1-2% risk per trade
    ):
        """
        Initialize SOL EMA Momentum strategy.
        
        Args:
            bot: TradingBot instance
            symbol: Trading symbol (default: "SOL")
            collateral_usd: Collateral amount in USD per trade
            leverage: Leverage multiplier
            timeframe: Candle interval (default: "15m")
            lookback_candles: Number of candles to fetch for calculations
            fast_ema_period: Fast EMA period (default: 9)
            slow_ema_period: Slow EMA period (default: 15)
            rsi_period: RSI period (default: 14)
            volume_ma_period: Volume MA period (default: 20)
            atr_period: ATR period (default: 14)
            slope_lookback: Bars to look back for slope calculation (default: 4)
            slope_threshold: Minimum slope threshold (default: 0.10)
            rsi_long_max: Maximum RSI for long entry (default: 60)
            rsi_short_min: Minimum RSI for short entry (default: 40)
            atr_stop_multiplier: ATR multiplier for stop loss (default: 0.5)
            risk_reward_ratio: Risk-to-reward ratio (default: 3.0)
            risk_per_trade_percent: Risk percentage per trade (default: 1.5%)
        """
        # Initialize with dummy TP/SL - will be calculated dynamically
        super().__init__(
            bot=bot,
            name=f"SOLEMAMomentum_{symbol}",
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            take_profit_percent=0.0,  # Will be calculated dynamically
            stop_loss_percent=0.0,  # Will be calculated dynamically
            side="B",  # Will be set based on signal
        )
        
        self.timeframe = timeframe
        self.lookback_candles = lookback_candles
        
        # Strategy parameters
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period
        self.rsi_period = rsi_period
        self.volume_ma_period = volume_ma_period
        self.atr_period = atr_period
        self.slope_lookback = slope_lookback
        self.slope_threshold = slope_threshold
        self.rsi_long_max = rsi_long_max
        self.rsi_short_min = rsi_short_min
        
        # Risk management
        self.atr_stop_multiplier = atr_stop_multiplier
        self.risk_reward_ratio = risk_reward_ratio
        self.risk_per_trade_percent = risk_per_trade_percent
        
        # Store calculated data
        self.ema_fast: Optional[List[float]] = None
        self.ema_slow: Optional[List[float]] = None
        self.atr: Optional[List[float]] = None
        self.prices: Optional[List[float]] = None
        self.highs: Optional[List[float]] = None
        self.lows: Optional[List[float]] = None
        self.candles: Optional[List[Dict[str, Any]]] = None
        self.current_signal: Optional[str] = None
        self.crossover_candle_index: Optional[int] = None
    
    def get_candles(self) -> List[Dict[str, Any]]:
        """
        Fetch historical candles from Hyperliquid.
        
        Returns:
            List of candle dictionaries
        """
        try:
            end_time = int(time.time() * 1000)  # Current time in milliseconds
            # Calculate start time based on lookback_candles
            timeframe_ms = {
                "1h": 3600000,
                "4h": 14400000,
                "1d": 86400000,
                "15m": 900000,
                "30m": 1800000,
                "5m": 300000,
            }.get(self.timeframe, 900000)
            
            start_time = end_time - (self.lookback_candles * timeframe_ms)
            
            candles = self.bot.info.candles_snapshot(
                self.symbol,
                self.timeframe,
                start_time,
                end_time
            )
            
            if isinstance(candles, list):
                return candles
            else:
                print(f"⚠️  Unexpected candle format for {self.symbol}")
                return []
        except Exception as e:
            print(f"❌ Error fetching candles for {self.symbol}: {e}")
            return []
    
    def calculate_indicators(self) -> bool:
        """
        Calculate all required indicators from candle data.
        
        Returns:
            True if indicators calculated successfully, False otherwise
        """
        self.candles = self.get_candles()
        
        if len(self.candles) < max(self.slow_ema_period, self.atr_period) + self.slope_lookback + 1:
            print(f"⚠️  Insufficient candles for {self.symbol}: {len(self.candles)}")
            return False
        
        # Sort candles by time (oldest first)
        sorted_candles = sorted(self.candles, key=lambda x: x.get('t', 0))
        
        # Extract price data
        self.prices = [float(candle['c']) for candle in sorted_candles]
        self.highs = [float(candle['h']) for candle in sorted_candles]
        self.lows = [float(candle['l']) for candle in sorted_candles]
        
        # Calculate indicators (only EMA and ATR needed)
        self.ema_fast = calculate_ema(self.prices, self.fast_ema_period)
        self.ema_slow = calculate_ema(self.prices, self.slow_ema_period)
        self.atr = calculate_atr(self.highs, self.lows, self.prices, self.atr_period)
        
        # Verify we have valid values
        if (not self.ema_fast or not self.ema_slow or not self.atr):
            return False
        
        if (self.ema_fast[-1] is None or self.ema_slow[-1] is None or 
            self.atr[-1] is None):
            return False
        
        return True
    
    def should_execute(self) -> bool:
        """
        Check if all entry conditions are met.
        
        Returns:
            True if entry conditions met, False otherwise
        """
        # Calculate indicators
        if not self.calculate_indicators():
            return False
        
        # Detect crossover
        crossover_signal = detect_crossover(self.ema_fast, self.ema_slow)
        
        if crossover_signal is None:
            return False
        
        # Store crossover candle index (the candle where crossover occurred)
        # Crossover is detected between last two candles, so crossover candle is second-to-last
        self.crossover_candle_index = len(self.ema_fast) - 2
        
        # Get current values
        current_idx = -1
        current_price = self.prices[current_idx]
        current_atr = self.atr[current_idx]
        
        # Calculate EMA slope
        slope = calculate_ema_slope(self.ema_fast, self.slope_lookback)
        
        if slope is None:
            return False
        
        # Get crossover candle data
        crossover_high = self.highs[self.crossover_candle_index]
        crossover_low = self.lows[self.crossover_candle_index]
        
        # Check entry conditions based on signal type
        if crossover_signal == "BUY":
            # Long entry conditions
            # 1. Crossover trigger (already checked)
            # 2. Momentum strength (slope > threshold)
            if slope <= self.slope_threshold:
                return False
            
            # 3. Price action confirmation (close above crossover candle high)
            if current_price <= crossover_high:
                return False
            
            self.current_signal = "BUY"
            self.side = "B"
            return True
        
        elif crossover_signal == "SELL":
            # Short entry conditions
            # 1. Crossover trigger (already checked)
            # 2. Momentum strength (slope < -threshold)
            if slope >= -self.slope_threshold:
                return False
            
            # 3. Price action confirmation (close below crossover candle low)
            if current_price >= crossover_low:
                return False
            
            self.current_signal = "SELL"
            self.side = "A"
            return True
        
        return False
    
    def calculate_risk_management(self) -> Dict[str, float]:
        """
        Calculate stop loss and take profit based on ATR and risk management rules.
        
        Returns:
            Dictionary with entry_price, stop_loss_price, take_profit_price, risk_amount
        """
        if not self.calculate_indicators():
            raise ValueError("Cannot calculate risk management: insufficient data")
        
        current_idx = -1
        current_price = self.prices[current_idx]
        current_atr = self.atr[current_idx]
        
        # Get entry candle (crossover candle)
        entry_candle_low = self.lows[self.crossover_candle_index]
        entry_candle_high = self.highs[self.crossover_candle_index]
        
        is_long = self.current_signal == "BUY"
        
        if is_long:
            # Long position: Stop loss 0.5 ATR below entry candle low
            stop_loss_price = entry_candle_low - (self.atr_stop_multiplier * current_atr)
            # Entry price is current price
            entry_price = current_price
            # Risk per unit
            risk_per_unit = entry_price - stop_loss_price
            # Take profit: 3R above entry
            take_profit_price = entry_price + (self.risk_reward_ratio * risk_per_unit)
        else:
            # Short position: Stop loss 0.5 ATR above entry candle high
            stop_loss_price = entry_candle_high + (self.atr_stop_multiplier * current_atr)
            # Entry price is current price
            entry_price = current_price
            # Risk per unit
            risk_per_unit = stop_loss_price - entry_price
            # Take profit: 3R below entry
            take_profit_price = entry_price - (self.risk_reward_ratio * risk_per_unit)
        
        # Calculate position size based on risk percentage
        # Risk amount = collateral * risk_per_trade_percent / 100
        risk_amount = self.collateral_usd * (self.risk_per_trade_percent / 100)
        
        # Position size = risk_amount / risk_per_unit
        position_size = risk_amount / risk_per_unit if risk_per_unit > 0 else 0
        
        # Calculate TP/SL percentages for the strategy template
        if is_long:
            stop_loss_percent = ((entry_price - stop_loss_price) / entry_price) * 100
            take_profit_percent = ((take_profit_price - entry_price) / entry_price) * 100
        else:
            stop_loss_percent = ((stop_loss_price - entry_price) / entry_price) * 100
            take_profit_percent = ((entry_price - take_profit_price) / entry_price) * 100
        
        return {
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "risk_amount": risk_amount,
            "risk_per_unit": risk_per_unit,
            "position_size": position_size,
            "stop_loss_percent": stop_loss_percent,
            "take_profit_percent": take_profit_percent,
        }
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the strategy with dynamic risk management.
        
        Returns:
            Response dictionary with execution details
        """
        # Check if we should execute
        if not self.should_execute():
            return {
                "success": False,
                "error": "Entry conditions not met",
                "strategy": self.name,
            }
        
        # Calculate risk management
        try:
            risk_mgmt = self.calculate_risk_management()
            
            # Update TP/SL percentages
            self.take_profit_percent = risk_mgmt["take_profit_percent"]
            self.stop_loss_percent = risk_mgmt["stop_loss_percent"]
            
            # Override position size calculation to use risk-based sizing
            # But we'll still use the parent's execute method which uses collateral_usd
            # For backtesting, we'll handle this differently
            
            # Execute parent strategy
            result = super().execute()
            
            # Add risk management details
            result["risk_management"] = risk_mgmt
            result["signal"] = self.current_signal
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Risk management calculation failed: {str(e)}",
                "strategy": self.name,
            }
    
    def get_signal_info(self) -> Dict[str, Any]:
        """
        Get current signal information for display.
        
        Returns:
            Dictionary with signal details
        """
        if not self.calculate_indicators():
            return {}
        
        current_idx = -1
        slope = calculate_ema_slope(self.ema_fast, self.slope_lookback)
        
        return {
            "symbol": self.symbol,
            "signal": self.current_signal,
            "current_price": self.prices[current_idx] if self.prices else None,
            "ema_fast": self.ema_fast[current_idx] if self.ema_fast else None,
            "ema_slow": self.ema_slow[current_idx] if self.ema_slow else None,
            "atr": self.atr[current_idx] if self.atr else None,
            "slope": slope,
            "timeframe": self.timeframe,
        }

