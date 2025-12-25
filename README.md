# Hyperliquid Trading Bot

Simple trading bot for Hyperliquid DEX with EMA 9/20 crossover strategy.

## Features

- ✅ EMA 9/20 Crossover Strategy (15-minute timeframe)
- ✅ Automatic trade execution on crossovers
- ✅ Multi-asset support (ETH, SOL, BTC)
- ✅ Maximum leverage per asset (automatically detected)
- ✅ Automatic TP/SL order placement
- ✅ Test trade script

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file:

```bash
PRIVATE_KEY=your_ethereum_private_key_here
USE_TESTNET=false
```

### 3. Run EMA Strategy

```bash
# Continuous mode (checks every 15 minutes)
python3 run_15m_ema_strategy.py

# Single check (for testing)
python3 run_15m_ema_strategy.py --once
```

### 4. Test Trade

```bash
# Open a simple BTC test trade
python3 test_basic_btc_trade_simple.py
```

## Strategy Configuration

The EMA strategy uses:
- **Timeframe:** 15 minutes
- **Assets:** ETH, SOL, BTC
- **Collateral:** $25 per asset
- **Leverage:** Maximum per asset (ETH: 25x, SOL: 20x, BTC: 40x)
- **Stop Loss:** 30%
- **Take Profit:** 100%

## Files

- `trading_bot.py` - Core bot functionality
- `ema_strategy.py` - EMA 9/20 crossover strategy
- `technical_indicators.py` - EMA calculation utilities
- `strategy_template.py` - Strategy base class
- `run_15m_ema_strategy.py` - EMA strategy runner (checks every 15 min)
- `test_basic_btc_trade_simple.py` - Simple test trade script
- `config.py` - Configuration
- `utils.py` - Utilities

## How It Works

1. **EMA Strategy:** Checks for EMA 9/20 crossovers every 15 minutes
   - BUY signal: EMA 9 crosses above EMA 20
   - SELL signal: EMA 9 crosses below EMA 20

2. **Test Trade:** Opens a simple BTC long position for testing

## Cloud Deployment

Deploy your bot to the cloud for 24/7 operation without running it locally.

### Quick Deploy Options

1. **Railway** (Recommended - Easiest)
   - See `QUICKSTART.md` for step-by-step guide
   - Free tier available
   - Automatic deployments from GitHub

2. **Render**
   - See `DEPLOYMENT.md` for details
   - Free tier available (may sleep)

3. **AWS EC2 / DigitalOcean**
   - See `DEPLOYMENT.md` for detailed instructions
   - More control, requires server management

### Docker Support

The bot includes Docker support for easy deployment:

```bash
# Build and run locally
docker-compose up --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

See `DEPLOYMENT.md` for comprehensive cloud deployment guides.

## Security

⚠️ **Never commit your `.env` file** - It contains your private key!

⚠️ **Start with testnet** - Always test with `USE_TESTNET=true` first!

## License

This project is provided as-is for educational and trading purposes.
