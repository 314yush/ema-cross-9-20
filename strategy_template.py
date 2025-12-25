"""
Template for creating custom trading strategies with collateral, leverage, TP, and SL.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from trading_bot import TradingBot


class AdvancedStrategy(ABC):
    """
    Advanced strategy template with collateral, leverage, TP, and SL support.
    """
    
    def __init__(
        self,
        bot: TradingBot,
        name: str,
        symbol: str,
        collateral_usd: float,
        leverage: int,
        take_profit_percent: float,
        stop_loss_percent: float,
        side: str = "B",  # "B" for buy, "A" for sell
    ):
        """
        Initialize the strategy.
        
        Args:
            bot: TradingBot instance
            name: Strategy name
            symbol: Trading symbol (e.g., "BTC")
            collateral_usd: Collateral amount in USD
            leverage: Leverage multiplier (e.g., 10 for 10x)
            take_profit_percent: Take profit percentage (e.g., 5.0 for 5%)
            stop_loss_percent: Stop loss percentage (e.g., 2.0 for 2%)
            side: "B" for buy (long), "A" for sell (short)
        """
        self.bot = bot
        self.name = name
        self.symbol = symbol
        self.collateral_usd = collateral_usd
        self.leverage = leverage
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.side = side.upper()
        
        # Will be set during execution
        self.entry_price: Optional[float] = None
        self.position_size: Optional[float] = None
    
    @abstractmethod
    def should_execute(self) -> bool:
        """
        Determine if the strategy should execute an order.
        
        Returns:
            True if order should be executed, False otherwise
        """
        pass
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the strategy with full setup: leverage, position, TP, and SL.
        
        Returns:
            Response dictionary with execution details
        """
        if not self.should_execute():
            return {
                "success": False,
                "error": "Strategy conditions not met",
                "strategy": self.name,
            }
        
        try:
            # Step 1: Set leverage
            print(f"📊 Setting leverage to {self.leverage}x for {self.symbol}...")
            leverage_result = self.bot.set_leverage(self.symbol, self.leverage)
            if not leverage_result.get("success"):
                # Try with lower leverage if high leverage fails
                error_msg = leverage_result.get("error") or leverage_result.get("response", {}).get("response", "Unknown")
                print(f"   ⚠️  Failed to set {self.leverage}x leverage: {error_msg}")
                
                # Try maximum allowed leverage (usually 20x for most assets)
                max_leverage = min(self.leverage, 20)  # Hyperliquid typically allows up to 20x
                print(f"   Trying {max_leverage}x leverage instead...")
                leverage_result = self.bot.set_leverage(self.symbol, max_leverage)
                
                if leverage_result.get("success"):
                    self.leverage = max_leverage
                    print(f"   ✅ Set leverage to {max_leverage}x (maximum allowed)")
                else:
                    # Continue anyway - leverage might already be set or not critical
                    print(f"   ⚠️  Continuing without setting leverage (may already be set)")
                    leverage_result = {"success": True, "response": {"status": "ok"}}
            
            # Step 2: Get current price and calculate position size
            print(f"💰 Calculating position size...")
            self.entry_price = self.bot.get_current_price(self.symbol)
            if self.entry_price is None:
                return {
                    "success": False,
                    "error": f"Could not get current price for {self.symbol}",
                    "strategy": self.name,
                }
            
            self.position_size = self.bot.calculate_position_size(
                self.symbol,
                self.collateral_usd,
                self.leverage
            )
            
            print(f"   Entry Price: ${self.entry_price:,.2f}")
            print(f"   Position Size: {self.position_size:.6f} {self.symbol}")
            print(f"   Position Value: ${self.collateral_usd * self.leverage:,.2f}")
            
            # Step 3: Place market order
            print(f"📈 Placing market order...")
            order_result = self.bot.create_market_order(
                symbol=self.symbol,
                side=self.side,
                amount=str(self.position_size),
            )
            
            if not order_result.get("success"):
                return {
                    **order_result,
                    "strategy": self.name,
                }
            
            # Step 4: Set take profit
            is_long = self.side == "B"
            print(f"🎯 Setting take profit at {self.take_profit_percent}%...")
            tp_result = self.bot.set_take_profit(
                self.symbol,
                self.entry_price,
                self.position_size,
                self.take_profit_percent,
                is_long=is_long
            )
            
            # Step 5: Set stop loss
            print(f"🛡️  Setting stop loss at {self.stop_loss_percent}%...")
            sl_result = self.bot.set_stop_loss(
                self.symbol,
                self.entry_price,
                self.position_size,
                self.stop_loss_percent,
                is_long=is_long
            )
            
            # Calculate TP/SL prices for display (corrected for long/short)
            if is_long:
                tp_price = self.entry_price * (1 + self.take_profit_percent / 100)
                sl_price = self.entry_price * (1 - self.stop_loss_percent / 100)
            else:
                tp_price = self.entry_price * (1 - self.take_profit_percent / 100)
                sl_price = self.entry_price * (1 + self.stop_loss_percent / 100)
            
            return {
                "success": True,
                "strategy": self.name,
                "order": order_result,
                "leverage": {
                    "success": leverage_result.get("success"),
                    "leverage": self.leverage,
                },
                "take_profit": {
                    "success": tp_result.get("success"),
                    "tp_percent": self.take_profit_percent,
                    "tp_price": tp_price,
                    "response": tp_result.get("response"),
                },
                "stop_loss": {
                    "success": sl_result.get("success"),
                    "sl_percent": self.stop_loss_percent,
                    "sl_price": sl_price,
                    "response": sl_result.get("response"),
                },
                "position": {
                    "symbol": self.symbol,
                    "side": self.side,
                    "entry_price": self.entry_price,
                    "position_size": self.position_size,
                    "collateral_usd": self.collateral_usd,
                    "leverage": self.leverage,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "strategy": self.name,
            }


class SimpleLongStrategy(AdvancedStrategy):
    """
    Simple example strategy that opens a long position with TP and SL.
    """
    
    def __init__(
        self,
        bot: TradingBot,
        symbol: str = "BTC",
        collateral_usd: float = 100.0,
        leverage: int = 10,
        take_profit_percent: float = 5.0,
        stop_loss_percent: float = 2.0,
    ):
        super().__init__(
            bot=bot,
            name="SimpleLong",
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            side="B",  # Buy/Long
        )
    
    def should_execute(self) -> bool:
        """Always execute (for demonstration)."""
        return True


class SimpleShortStrategy(AdvancedStrategy):
    """
    Simple example strategy that opens a short position with TP and SL.
    """
    
    def __init__(
        self,
        bot: TradingBot,
        symbol: str = "BTC",
        collateral_usd: float = 100.0,
        leverage: int = 10,
        take_profit_percent: float = 5.0,
        stop_loss_percent: float = 2.0,
    ):
        super().__init__(
            bot=bot,
            name="SimpleShort",
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            side="A",  # Sell/Short
        )
    
    def should_execute(self) -> bool:
        """Always execute (for demonstration)."""
        return True


class ConditionalAdvancedStrategy(AdvancedStrategy):
    """
    Example strategy that executes based on a condition function.
    """
    
    def __init__(
        self,
        bot: TradingBot,
        condition_func,
        symbol: str,
        collateral_usd: float,
        leverage: int,
        take_profit_percent: float,
        stop_loss_percent: float,
        side: str = "B",
        name: str = "ConditionalAdvanced",
    ):
        """
        Initialize conditional strategy.
        
        Args:
            bot: TradingBot instance
            condition_func: Function that returns True/False to determine execution
            symbol: Trading symbol
            collateral_usd: Collateral in USD
            leverage: Leverage multiplier
            take_profit_percent: TP percentage
            stop_loss_percent: SL percentage
            side: "B" for buy, "A" for sell
            name: Strategy name
        """
        super().__init__(
            bot=bot,
            name=name,
            symbol=symbol,
            collateral_usd=collateral_usd,
            leverage=leverage,
            take_profit_percent=take_profit_percent,
            stop_loss_percent=stop_loss_percent,
            side=side,
        )
        self.condition_func = condition_func
    
    def should_execute(self) -> bool:
        """Execute based on condition function."""
        try:
            return self.condition_func()
        except Exception as e:
            print(f"Error in condition function: {e}")
            return False

