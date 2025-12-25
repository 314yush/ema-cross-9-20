"""
Core trading bot class for Hyperliquid DEX.
Handles wallet authentication and market order execution.
"""
from typing import Optional, Dict, Any
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from config import API_URL, PRIVATE_KEY, USE_TESTNET


class TradingBot:
    """
    Main trading bot class that handles authentication and order execution.
    """
    
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize the trading bot.
        
        Args:
            private_key: Account private key (defaults to config)
        """
        # Use provided key or fall back to config
        self.private_key_str = private_key or PRIVATE_KEY
        if not self.private_key_str:
            raise ValueError("Private key must be provided either as argument or in config")
        
        # Strip whitespace from private key
        self.private_key_str = self.private_key_str.strip()
        
        # Remove 0x prefix if present (Hyperliquid accepts both formats)
        if self.private_key_str.startswith("0x"):
            self.private_key_str = self.private_key_str[2:]
        
        # Validate private key format
        if self.private_key_str == "your_private_key_here" or "your" in self.private_key_str.lower():
            raise ValueError("Please set your actual PRIVATE_KEY in the .env file (currently using placeholder)")
        
        # Initialize Hyperliquid account, info, and exchange
        try:
            api_url = constants.MAINNET_API_URL if not USE_TESTNET else constants.TESTNET_API_URL
            # Create LocalAccount from private key (eth_account format)
            self.account: LocalAccount = eth_account.Account.from_key(self.private_key_str)
            self.info = Info(api_url, skip_ws=True)
            # Create Exchange instance - this handles all signing and order placement
            self.exchange = Exchange(self.account, api_url, account_address=None)
            # Get wallet address
            self.wallet_address = self.account.address
        except Exception as e:
            raise ValueError(f"Failed to initialize Hyperliquid wallet: {e}")
    
    def create_market_order(
        self,
        symbol: str,
        side: str,  # "B" for buy or "A" for sell
        amount: str,
        slippage: Optional[float] = None,
        reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a market order on Hyperliquid.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            side: Order side ("B" for buy, "A" for sell)
            amount: Order amount as string (in base units, e.g., "0.1" for BTC)
            slippage: Slippage tolerance (default: 0.05 = 5%). None uses default.
            reduce_only: Whether this is a reduce-only order (Note: market_open doesn't support this directly)
        
        Returns:
            Response dictionary with status and order details
        """
        try:
            # Convert side to boolean (B = buy = True, A = sell = False)
            is_buy = side.upper() == "B" or side.lower() == "buy" or side.lower() == "bid"
            
            # Convert amount to float for Hyperliquid
            size = float(amount)
            
            # Use Exchange.market_open() method - this handles all signing and formatting
            # Signature: market_open(name, is_buy, sz, px=None, slippage=0.05, cloid=None, builder=None)
            # For market orders, px should be None
            # slippage defaults to 0.05 (5%) if not provided
            response = self.exchange.market_open(
                symbol,  # name (positional)
                is_buy,  # is_buy (positional)
                size,  # sz (positional)
                None,  # px (None for market order)
                slippage if slippage is not None else 0.05,  # slippage (default 0.05)
            )
            
            # Note: reduce_only is not directly supported by market_open
            # To implement reduce_only, you would need to use exchange.order() with specific parameters
            
            # Parse response
            if response.get("status") == "ok":
                # Extract order ID from response
                order_id = None
                statuses = response.get("response", {}).get("data", {}).get("statuses", [])
                if statuses:
                    # Check for filled order first
                    if "filled" in statuses[0]:
                        order_id = statuses[0]["filled"].get("oid")
                    # Otherwise check for resting order
                    elif "resting" in statuses[0]:
                        order_id = statuses[0]["resting"].get("oid")
                
                return {
                    "success": True,
                    "status_code": 200,
                    "response": response,
                    "order_id": order_id,
                }
            else:
                # Extract error message
                error_msg = "Unknown error"
                statuses = response.get("response", {}).get("data", {}).get("statuses", [])
                if statuses and "error" in statuses[0]:
                    error_msg = statuses[0]["error"]
                
                return {
                    "success": False,
                    "status_code": 400,
                    "response": response,
                    "error": error_msg,
                }
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "response": {},
                "error": str(e),
            }
    
    def get_wallet_address(self) -> str:
        """Get the wallet address."""
        return self.wallet_address
    
    def get_max_leverage(self, symbol: str) -> Optional[int]:
        """
        Get the maximum leverage allowed for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
        
        Returns:
            Maximum leverage as integer, or None if not found
        """
        try:
            meta = self.info.meta()
            
            # Find asset in meta
            asset_info = None
            if isinstance(meta, dict) and "universe" in meta:
                for asset in meta["universe"]:
                    if asset.get("name") == symbol:
                        asset_info = asset
                        break
            elif isinstance(meta, list):
                for asset in meta:
                    if isinstance(asset, dict) and asset.get("name") == symbol:
                        asset_info = asset
                        break
            
            if asset_info:
                # Try different possible field names
                max_leverage = (
                    asset_info.get("maxLeverage") or
                    asset_info.get("max_leverage") or
                    asset_info.get("leverage") or
                    asset_info.get("maxLeverage")
                )
                
                if max_leverage:
                    return int(max_leverage)
            
            return None
        except Exception as e:
            print(f"Error getting max leverage for {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get the current mid price for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
        
        Returns:
            Current mid price as float, or None if not found
        """
        try:
            mids = self.info.all_mids()
            price_str = mids.get(symbol)
            if price_str:
                return float(price_str)
            return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_position_size(self, symbol: str) -> Optional[float]:
        """
        Get the current position size for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
        
        Returns:
            Position size in base units, or None if no position
        """
        try:
            user_state = self.info.user_state(self.wallet_address)
            positions = user_state.get("assetPositions", [])
            
            for pos in positions:
                position_data = pos.get("position", {})
                if position_data.get("coin") == symbol:
                    size = float(position_data.get("szi", 0))
                    if size != 0:
                        return abs(size)  # Return absolute value
            return None
        except Exception as e:
            print(f"Error getting position size for {symbol}: {e}")
            return None
    
    def set_leverage(self, symbol: str, leverage: int, is_cross: bool = True) -> Dict[str, Any]:
        """
        Set leverage for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            leverage: Leverage multiplier (e.g., 10 for 10x)
            is_cross: True for cross margin, False for isolated margin
        
        Returns:
            Response dictionary
        """
        try:
            response = self.exchange.update_leverage(leverage, symbol, is_cross)
            if isinstance(response, dict):
                return {
                    "success": response.get("status") == "ok",
                    "response": response,
                }
            else:
                # Some exchanges return string or other format
                return {
                    "success": True,
                    "response": response,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_size_decimals(self, symbol: str) -> int:
        """
        Get the number of decimal places required for position size.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Number of decimal places
        """
        try:
            meta = self.info.meta()
            
            # Find asset in meta
            asset_info = None
            if isinstance(meta, dict) and "universe" in meta:
                for asset in meta["universe"]:
                    if asset.get("name") == symbol:
                        asset_info = asset
                        break
            elif isinstance(meta, list):
                for asset in meta:
                    if isinstance(asset, dict) and asset.get("name") == symbol:
                        asset_info = asset
                        break
            
            if asset_info:
                sz_decimals = asset_info.get("szDecimals")
                if sz_decimals is not None:
                    return int(sz_decimals)
            
            # Default to 5 decimals if not found
            return 5
        except Exception as e:
            print(f"Error getting size decimals for {symbol}: {e}")
            return 5
    
    def calculate_position_size(self, symbol: str, collateral_usd: float, leverage: int) -> float:
        """
        Calculate position size in base units from USD collateral and leverage.
        Rounds to the correct number of decimals for the asset.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            collateral_usd: Collateral amount in USD
            leverage: Leverage multiplier
        
        Returns:
            Position size in base units (e.g., BTC amount), rounded correctly
        """
        current_price = self.get_current_price(symbol)
        if current_price is None:
            raise ValueError(f"Could not get current price for {symbol}")
        
        # Position value = collateral * leverage
        position_value_usd = collateral_usd * leverage
        
        # Position size in base units = position value / price
        position_size = position_value_usd / current_price
        
        # Round to correct number of decimals for this asset
        sz_decimals = self.get_size_decimals(symbol)
        position_size = round(position_size, sz_decimals)
        
        return position_size
    
    def set_take_profit(
        self,
        symbol: str,
        entry_price: float,
        position_size: float,
        tp_percent: float,
        is_long: bool = True
    ) -> Dict[str, Any]:
        """
        Set a take-profit order.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            entry_price: Entry price of the position
            position_size: Position size in base units
            tp_percent: Take profit percentage (e.g., 5.0 for 5%)
            is_long: True for long position, False for short
        
        Returns:
            Response dictionary
        """
        try:
            from hyperliquid.utils.signing import OrderType, TriggerOrderType
            
            # Calculate TP price based on position direction
            if is_long:
                # For long: TP is above entry price
                tp_price = entry_price * (1 + tp_percent / 100)
                is_buy = False  # Sell to close long
            else:
                # For short: TP is below entry price
                tp_price = entry_price * (1 - tp_percent / 100)
                is_buy = True  # Buy to close short
            
            # Create trigger order for take profit
            trigger_order_type = OrderType(
                trigger=TriggerOrderType(
                    triggerPx=str(tp_price),
                    isMarket=True,
                    tpsl="tp"
                )
            )
            
            # Place reduce-only order at TP price
            response = self.exchange.order(
                symbol,
                is_buy,
                position_size,
                tp_price,  # limit_px
                trigger_order_type,
                reduce_only=True
            )
            
            # Check response status
            success = response.get("status") == "ok"
            if not success:
                # Log error details
                statuses = response.get("response", {}).get("data", {}).get("statuses", [])
                if statuses and "error" in statuses[0]:
                    error_msg = statuses[0]["error"]
                    print(f"   ⚠️  TP order error: {error_msg}")
            
            return {
                "success": success,
                "response": response,
                "tp_price": tp_price,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def set_stop_loss(
        self,
        symbol: str,
        entry_price: float,
        position_size: float,
        sl_percent: float,
        is_long: bool = True
    ) -> Dict[str, Any]:
        """
        Set a stop-loss order.
        
        Args:
            symbol: Trading symbol (e.g., "BTC")
            entry_price: Entry price of the position
            position_size: Position size in base units
            sl_percent: Stop loss percentage (e.g., 2.0 for 2%)
            is_long: True for long position, False for short
        
        Returns:
            Response dictionary
        """
        try:
            from hyperliquid.utils.signing import OrderType, TriggerOrderType
            
            # Calculate SL price based on position direction
            if is_long:
                # For long: SL is below entry price
                sl_price = entry_price * (1 - sl_percent / 100)
                is_buy = False  # Sell to close long
            else:
                # For short: SL is above entry price
                sl_price = entry_price * (1 + sl_percent / 100)
                is_buy = True  # Buy to close short
            
            # Create trigger order for stop loss
            trigger_order_type = OrderType(
                trigger=TriggerOrderType(
                    triggerPx=str(sl_price),
                    isMarket=True,
                    tpsl="sl"
                )
            )
            
            # Place reduce-only order at SL price
            response = self.exchange.order(
                symbol,
                is_buy,
                position_size,
                sl_price,  # limit_px
                trigger_order_type,
                reduce_only=True
            )
            
            # Check response status
            success = response.get("status") == "ok"
            if not success:
                # Log error details
                statuses = response.get("response", {}).get("data", {}).get("statuses", [])
                if statuses and "error" in statuses[0]:
                    error_msg = statuses[0]["error"]
                    print(f"   ⚠️  SL order error: {error_msg}")
            
            return {
                "success": success,
                "response": response,
                "sl_price": sl_price,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
