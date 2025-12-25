"""
Technical indicators for trading strategies.
Includes EMA calculation and crossover detection.
"""
from typing import List, Dict, Optional, Tuple


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """
    Calculate Exponential Moving Average (EMA).
    
    Args:
        prices: List of closing prices (oldest to newest)
        period: EMA period (e.g., 9 or 20)
    
    Returns:
        List of EMA values (same length as prices, with None for insufficient data)
    """
    if len(prices) < period:
        return [None] * len(prices)
    
    ema_values = []
    multiplier = 2.0 / (period + 1)
    
    # First EMA value is SMA of first 'period' prices
    sma = sum(prices[:period]) / period
    ema_values.extend([None] * (period - 1))  # No EMA for first period-1 values
    ema_values.append(sma)
    
    # Calculate subsequent EMA values
    for i in range(period, len(prices)):
        ema = (prices[i] - ema_values[i - 1]) * multiplier + ema_values[i - 1]
        ema_values.append(ema)
    
    return ema_values


def detect_crossover(ema_fast: List[float], ema_slow: List[float]) -> Optional[str]:
    """
    Detect EMA crossover signal.
    
    Args:
        ema_fast: Fast EMA values (e.g., EMA 9)
        ema_slow: Slow EMA values (e.g., EMA 20)
    
    Returns:
        "BUY" if fast EMA crosses above slow EMA
        "SELL" if fast EMA crosses below slow EMA
        None if no crossover detected
    """
    if len(ema_fast) < 2 or len(ema_slow) < 2:
        return None
    
    # Get current and previous values
    current_fast = ema_fast[-1]
    current_slow = ema_slow[-1]
    prev_fast = ema_fast[-2]
    prev_slow = ema_slow[-2]
    
    # Check for None values
    if None in [current_fast, current_slow, prev_fast, prev_slow]:
        return None
    
    # Bullish crossover: fast EMA crosses above slow EMA
    if prev_fast <= prev_slow and current_fast > current_slow:
        return "BUY"
    
    # Bearish crossover: fast EMA crosses below slow EMA
    if prev_fast >= prev_slow and current_fast < current_slow:
        return "SELL"
    
    return None


def get_current_ema_values(ema_fast: List[float], ema_slow: List[float]) -> Tuple[Optional[float], Optional[float]]:
    """
    Get the most recent EMA values.
    
    Args:
        ema_fast: Fast EMA values
        ema_slow: Slow EMA values
    
    Returns:
        Tuple of (current_fast_ema, current_slow_ema)
    """
    current_fast = ema_fast[-1] if ema_fast else None
    current_slow = ema_slow[-1] if ema_slow else None
    return current_fast, current_slow


def get_ema_trend(ema_fast: List[float], ema_slow: List[float]) -> Optional[str]:
    """
    Get current EMA trend (not crossover, just current relationship).
    
    Args:
        ema_fast: Fast EMA values
        ema_slow: Slow EMA values
    
    Returns:
        "BULLISH" if fast EMA > slow EMA
        "BEARISH" if fast EMA < slow EMA
        None if insufficient data
    """
    if not ema_fast or not ema_slow:
        return None
    
    current_fast = ema_fast[-1]
    current_slow = ema_slow[-1]
    
    if current_fast is None or current_slow is None:
        return None
    
    if current_fast > current_slow:
        return "BULLISH"
    elif current_fast < current_slow:
        return "BEARISH"
    else:
        return "NEUTRAL"


def calculate_rsi(prices: List[float], period: int = 14) -> List[Optional[float]]:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: List of closing prices (oldest to newest)
        period: RSI period (default: 14)
    
    Returns:
        List of RSI values (same length as prices, with None for insufficient data)
    """
    if len(prices) < period + 1:
        return [None] * len(prices)
    
    rsi_values = [None] * period
    
    # Calculate price changes
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Separate gains and losses
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    # Calculate initial average gain and loss
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Calculate first RSI
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    rsi_values.append(rsi)
    
    # Calculate subsequent RSI values using Wilder's smoothing
    for i in range(period + 1, len(prices)):
        gain = gains[i-1]
        loss = losses[i-1]
        
        # Wilder's smoothing: new_avg = (old_avg * (period - 1) + new_value) / period
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        rsi_values.append(rsi)
    
    return rsi_values


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[Optional[float]]:
    """
    Calculate Average True Range (ATR).
    
    Args:
        highs: List of high prices (oldest to newest)
        lows: List of low prices (oldest to newest)
        closes: List of close prices (oldest to newest)
        period: ATR period (default: 14)
    
    Returns:
        List of ATR values (same length as prices, with None for insufficient data)
    """
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return [None] * len(highs)
    
    # Calculate True Range (TR)
    tr_values = []
    for i in range(len(highs)):
        if i == 0:
            tr = highs[i] - lows[i]
        else:
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            tr = max(tr1, tr2, tr3)
        tr_values.append(tr)
    
    # Calculate ATR using Wilder's smoothing
    atr_values = [None] * period
    
    # Initial ATR is SMA of first period TR values
    initial_atr = sum(tr_values[:period]) / period
    atr_values.append(initial_atr)
    
    # Calculate subsequent ATR values using Wilder's smoothing
    current_atr = initial_atr
    for i in range(period + 1, len(tr_values)):
        # Wilder's smoothing: new_ATR = (old_ATR * (period - 1) + new_TR) / period
        current_atr = (current_atr * (period - 1) + tr_values[i]) / period
        atr_values.append(current_atr)
    
    return atr_values


def calculate_volume_ma(volumes: List[float], period: int = 20) -> List[Optional[float]]:
    """
    Calculate Volume Moving Average.
    
    Args:
        volumes: List of volume values (oldest to newest)
        period: Moving average period (default: 20)
    
    Returns:
        List of volume MA values (same length as volumes, with None for insufficient data)
    """
    if len(volumes) < period:
        return [None] * len(volumes)
    
    volume_ma = [None] * (period - 1)
    
    # Calculate SMA for each period
    for i in range(period - 1, len(volumes)):
        ma = sum(volumes[i - period + 1:i + 1]) / period
        volume_ma.append(ma)
    
    return volume_ma


def calculate_ema_slope(ema_values: List[float], lookback: int = 4) -> Optional[float]:
    """
    Calculate the slope of EMA over the last N bars.
    
    Args:
        ema_values: List of EMA values (oldest to newest)
        lookback: Number of bars to look back (default: 4)
    
    Returns:
        Slope value (positive for upward, negative for downward), or None if insufficient data
    """
    if len(ema_values) < lookback + 1:
        return None
    
    # Get current and lookback values
    current = ema_values[-1]
    lookback_value = ema_values[-lookback - 1]
    
    if current is None or lookback_value is None:
        return None
    
    # Calculate slope: (current - lookback) / lookback
    slope = (current - lookback_value) / lookback
    
    return slope

