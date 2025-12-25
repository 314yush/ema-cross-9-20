# Hyperliquid Trading Bot

Trading bot for Hyperliquid DEX with EMA 9/20 crossover strategy.

## Features

- ✅ EMA 9/20 Crossover Strategy (15-minute timeframe)
- ✅ Automatic trade execution on crossovers
- ✅ Multi-asset support (ETH, SOL, BTC)
- ✅ Maximum leverage per asset (automatically detected)
- ✅ Automatic TP/SL order placement
- ✅ Health check server (prevents Fly.io from sleeping)
- ✅ Test trade script

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file:

```env
PRIVATE_KEY=your_ethereum_private_key_here
USE_TESTNET=false
SYMBOLS=ETH,SOL,BTC
COLLATERAL_USD=25.0
STOP_LOSS_PERCENT=30.0
TAKE_PROFIT_PERCENT=100.0
TIMEFRAME=15m
```

### 3. Run Bot

```bash
python3 main.py
```

### 4. Test Trade

```bash
# Open a simple BTC test trade
python3 test_basic_btc_trade_simple.py
```

## Strategy Configuration

The EMA 9/20 strategy:
- **Timeframe:** 15 minutes (configurable)
- **Assets:** ETH, SOL, BTC (configurable via SYMBOLS env var)
- **Collateral:** $25 per asset (configurable)
- **Leverage:** Maximum per asset (automatically detected)
- **Stop Loss:** 30% (configurable)
- **Take Profit:** 100% (configurable)

**Signals:**
- **BUY:** EMA 9 crosses above EMA 20
- **SELL:** EMA 9 crosses below EMA 20

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PRIVATE_KEY` | Your Hyperliquid private key (required) | - |
| `USE_TESTNET` | Use testnet (true/false) | false |
| `SYMBOLS` | Comma-separated symbols to trade | ETH,SOL,BTC |
| `COLLATERAL_USD` | Collateral per trade in USD | 25.0 |
| `STOP_LOSS_PERCENT` | Stop loss percentage | 30.0 |
| `TAKE_PROFIT_PERCENT` | Take profit percentage | 100.0 |
| `TIMEFRAME` | Candle timeframe (15m, 30m, 1h, 4h, 1d) | 15m |
| `HEALTH_CHECK_PORT` | Port for health check server | 8080 |

## Files

- `main.py` - Main entry point (runs EMA 9/20 strategy)
- `trading_bot.py` - Core bot functionality
- `ema_strategy.py` - EMA 9/20 crossover strategy
- `strategy_template.py` - Strategy base class
- `technical_indicators.py` - EMA calculation utilities
- `health_server.py` - Health check server for Fly.io
- `test_basic_btc_trade_simple.py` - Test trade script
- `config.py` - Configuration
- `Dockerfile` - Docker configuration for Fly.io
- `fly.toml` - Fly.io deployment configuration

## Cloud Deployment (Fly.io)

### Deploy to Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   export FLYCTL_INSTALL="$HOME/.fly"
   export PATH="$FLYCTL_INSTALL/bin:$PATH"
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Deploy:**
   ```bash
   fly deploy
   ```

4. **Set Environment Variables:**
   ```bash
   fly secrets set \
     PRIVATE_KEY="your_key" \
     USE_TESTNET="false" \
     SYMBOLS="ETH,SOL,BTC" \
     COLLATERAL_USD="25.0" \
     STOP_LOSS_PERCENT="30.0" \
     TAKE_PROFIT_PERCENT="100.0" \
     TIMEFRAME="15m"
   ```

5. **Monitor:**
   ```bash
   fly logs -a ema-cross-9-20
   fly status -a ema-cross-9-20
   ```

### What Runs on Fly.io

1. **EMA 9/20 Strategy** - Automatically runs via `main.py`, checks every 15 minutes
2. **Test Trade Script** - Run manually: `fly ssh console -a ema-cross-9-20 -C "python3 test_basic_btc_trade_simple.py"`

### Health Check

Health check server prevents Fly.io from sleeping:
- Health: `https://ema-cross-9-20.fly.dev/health`
- Ping: `https://ema-cross-9-20.fly.dev/ping`

See `FLY_DEPLOY.md` for detailed deployment guide.

## How It Works

1. **Bot starts** and initializes connection to Hyperliquid
2. **Every 15 minutes** (or configured timeframe), bot checks for EMA crossovers
3. **When crossover detected:**
   - Calculates position size based on collateral and leverage
   - Executes market order
   - Sets take-profit and stop-loss orders
4. **Health check server** runs in background to keep bot awake

## Security

⚠️ **Never commit your `.env` file** - It contains your private key!

⚠️ **Start with testnet** - Always test with `USE_TESTNET=true` first!

## License

This project is provided as-is for educational and trading purposes.
