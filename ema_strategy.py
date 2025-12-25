"""
EMA 9/20 Crossover Strategy for multiple assets (ETH, SOL, BTC, XRP).
"""
from typing import Dict, Any, Optional, List
import time
from trading_bot import TradingBot
from strategy_template import AdvancedStrategy
from technical_indicators import calculate_ema, detect_crossover, get_current_ema_values, get_ema_trend


class EMA9_20Strategy(AdvancedStrategy):
    """
    EMA 9/20 Crossover Strategy.
    
    Signals:
    - BUY: EMA 9 crosses above EMA 20 (bullish crossover)
    - SELL: EMA 9 crosses below EMA 20 (bearish crossover)
    """
    
    def __init__(
        self,
        bot: TradingBot,
        symbol: str,
        collateral_usd: float,
        leverage: int,
        take_profit_percent: float,
        stop_loss_percent: float,
        timeframe: str = "1h",
        lookback_candles: int = 100,
        require_confirmation: bool = False,
    ):
        """
        Initialize EMA 9/20 strategy.
        
        Args:
            bot: TradingBot instance
            symbol: Trading symbol (e.g., "BTC", "ETH", "SOL", "XRP")
            collateral_usd: Collateral amount in USD per trade
            leverage: Leverage multiplier
            take_profit_percent: Take profit percentage
            stop_loss_percent: Stop loss percentage
            timeframe: Candle interval (e.g., "1h", "4h", "1d")
            lookback_candles: Number of candles to fetch for EMA calculation
            require_confirmation: If True, wait for 1 candle confirmation before trading
        """
        # Determine side based on signal (will be set in should_execute)
        super().__init__(
            bot=bot,
            name=f"EMA9_20_{symbol}",
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            side="B",  # Will be overridden based on signal
        )
        
        self.timeframe = timeframe
        self.lookback_candles = lookback_candles
        self.require_confirmation = require_confirmation
        
        # Store EMA data
        self.ema9: Optional[List[float]] = None
        self.ema20: Optional[List[float]] = None
        self.current_signal: Optional[str] = None
        self.prices: Optional[List[float]] = None
    
    def get_candles(self) -> List[Dict[str, Any]]:
        """
        Fetch historical candles from Hyperliquid.
        
        Returns:
            List of candle dictionaries
        """
        try:
            end_time = int(time.time() * 1000)  # Current time in milliseconds
            # Calculate start time based on lookback_candles
            # Approximate: 1h = 3600000 ms, 4h = 14400000 ms, 1d = 86400000 ms
            timeframe_ms = {
                "1h": 3600000,
                "4h": 14400000,
                "1d": 86400000,
                "15m": 900000,
                "30m": 1800000,
            }.get(self.timeframe, 3600000)
            
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
    
    def calculate_emas(self) -> bool:
        """
        Calculate EMA 9 and EMA 20 from candle data.
        
        Returns:
            True if EMAs calculated successfully, False otherwise
        """
        candles = self.get_candles()
        
        if len(candles) < 50:  # Need at least 50 candles for EMA 20
            print(f"⚠️  Insufficient candles for {self.symbol}: {len(candles)}")
            return False
        
        # Extract close prices (sorted by time, oldest first)
        # Candles should already be sorted, but ensure they are
        sorted_candles = sorted(candles, key=lambda x: x.get('t', 0))
        self.prices = [float(candle['c']) for candle in sorted_candles]
        
        # Calculate EMAs
        self.ema9 = calculate_ema(self.prices, 9)
        self.ema20 = calculate_ema(self.prices, 20)
        
        # Verify we have valid EMA values
        if not self.ema9 or not self.ema20:
            return False
        
        if self.ema9[-1] is None or self.ema20[-1] is None:
            return False
        
        return True
    
    def should_execute(self) -> bool:
        """
        Check if EMA crossover signal exists and strategy should execute.
        
        Returns:
            True if crossover signal detected, False otherwise
        """
        # Calculate EMAs
        if not self.calculate_emas():
            return False
        
        # Detect crossover
        signal = detect_crossover(self.ema9, self.ema20)
        
        if signal is None:
            return False
        
        # Store signal for use in execution
        self.current_signal = signal
        
        # Set side based on signal
        if signal == "BUY":
            self.side = "B"  # Long position
        elif signal == "SELL":
            self.side = "A"  # Short position
        
        # If confirmation required, check previous signal
        if self.require_confirmation:
            # Check if we had the same signal in previous candle
            if len(self.ema9) >= 3 and len(self.ema20) >= 3:
                prev_signal = detect_crossover(
                    self.ema9[:-1],  # Previous candles
                    self.ema20[:-1]
                )
                # Only execute if signal persists for 2 candles
                if prev_signal != signal:
                    return False
        
        return True
    
    def get_signal_info(self) -> Dict[str, Any]:
        """
        Get current signal information for display.
        
        Returns:
            Dictionary with signal details
        """
        if not self.ema9 or not self.ema20:
            return {}
        
        current_fast, current_slow = get_current_ema_values(self.ema9, self.ema20)
        trend = get_ema_trend(self.ema9, self.ema20)
        current_price = self.prices[-1] if self.prices else None
        
        return {
            "symbol": self.symbol,
            "signal": self.current_signal,
            "current_price": current_price,
            "ema9": current_fast,
            "ema20": current_slow,
            "trend": trend,
            "timeframe": self.timeframe,
        }
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the EMA strategy with full setup.
        
        Returns:
            Response dictionary with execution details
        """
        # Check if we should execute
        if not self.should_execute():
            signal_info = self.get_signal_info()
            return {
                "success": False,
                "error": "No crossover signal detected",
                "strategy": self.name,
                "signal_info": signal_info,
            }
        
        # Get signal info for logging
        signal_info = self.get_signal_info()
        print(f"\n📊 EMA Signal for {self.symbol}:")
        print(f"   Signal: {self.current_signal}")
        print(f"   Current Price: ${signal_info.get('current_price'):,.2f}")
        print(f"   EMA 9: ${signal_info.get('ema9'):,.2f}")
        print(f"   EMA 20: ${signal_info.get('ema20'):,.2f}")
        print(f"   Trend: {signal_info.get('trend')}")
        
        # Execute parent strategy (sets leverage, opens position, sets TP/SL)
        result = super().execute()
        
        # Add signal info to result
        result["signal_info"] = signal_info
        
        return result


class MultiAssetEMAStrategy:
    """
    Manages EMA 9/20 strategy across multiple assets.
    """
    
    def __init__(
        self,
        bot: TradingBot,
        symbols: List[str],
        collateral_usd: float,
        leverage: int,
        take_profit_percent: float,
        stop_loss_percent: float,
        timeframe: str = "1h",
        lookback_candles: int = 100,
    ):
        """
        Initialize multi-asset EMA strategy.
        
        Args:
            bot: TradingBot instance
            symbols: List of symbols to trade (e.g., ["BTC", "ETH", "SOL", "XRP"])
            collateral_usd: Collateral amount per trade per asset
            leverage: Leverage multiplier
            take_profit_percent: Take profit percentage
            stop_loss_percent: Stop loss percentage
            timeframe: Candle interval
            lookback_candles: Number of candles to fetch
        """
        self.bot = bot
        self.symbols = symbols
        self.strategies = {}
        
        # Create strategy instance for each symbol
        for symbol in symbols:
            self.strategies[symbol] = EMA9_20Strategy(
                bot=bot,
                symbol=symbol,
                collateral_usd=collateral_usd,
                leverage=leverage,
                take_profit_percent=take_profit_percent,
                stop_loss_percent=stop_loss_percent,
                timeframe=timeframe,
                lookback_candles=lookback_candles,
            )
    
    def check_all_signals(self) -> Dict[str, Dict[str, Any]]:
        """
        Check signals for all assets.
        
        Returns:
            Dictionary mapping symbol to signal info
        """
        signals = {}
        
        for symbol, strategy in self.strategies.items():
            try:
                # Calculate EMAs
                strategy.calculate_emas()
                
                # Get signal info
                signal_info = strategy.get_signal_info()
                
                # Detect crossover
                if strategy.ema9 and strategy.ema20:
                    signal = detect_crossover(strategy.ema9, strategy.ema20)
                    signal_info["crossover_signal"] = signal
                    signal_info["has_signal"] = signal is not None
                
                signals[symbol] = signal_info
            except Exception as e:
                signals[symbol] = {
                    "error": str(e),
                    "has_signal": False,
                }
        
        return signals
    
    def execute_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Execute strategy for all assets that have signals.
        
        Returns:
            Dictionary mapping symbol to execution result
        """
        results = {}
        
        for symbol, strategy in self.strategies.items():
            print(f"\n{'='*60}")
            print(f"Checking {symbol}...")
            print(f"{'='*60}")
            
            try:
                result = strategy.execute()
                results[symbol] = result
            except Exception as e:
                results[symbol] = {
                    "success": False,
                    "error": str(e),
                    "strategy": strategy.name,
                }
        
        return results
    
    def execute_single(self, symbol: str) -> Dict[str, Any]:
        """
        Execute strategy for a single asset.
        
        Args:
            symbol: Symbol to execute strategy for
        
        Returns:
            Execution result
        """
        if symbol not in self.strategies:
            return {
                "success": False,
                "error": f"Symbol {symbol} not in strategy list",
            }
        
        return self.strategies[symbol].execute()


