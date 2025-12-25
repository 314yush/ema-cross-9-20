# Fly.io Deployment Guide

Simple guide to deploy and use the EMA 9/20 trading bot on Fly.io.

## What's Deployed

1. **EMA 9/20 Strategy** - Runs automatically, checks for crossovers every 15 minutes
2. **Test Trade Script** - Can be run manually to test trade execution

## Quick Deploy

### 1. Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

### 2. Login

```bash
fly auth login
```

### 3. Deploy

```bash
fly deploy
```

### 4. Set Environment Variables

```bash
fly secrets set \
  PRIVATE_KEY="your_private_key_here" \
  USE_TESTNET="false" \
  SYMBOLS="ETH,SOL,BTC" \
  COLLATERAL_USD="25.0" \
  STOP_LOSS_PERCENT="30.0" \
  TAKE_PROFIT_PERCENT="100.0" \
  TIMEFRAME="15m"
```

### 5. Check Status

```bash
fly status -a ema-cross-9-20
fly logs -a ema-cross-9-20
```

## Using the Bot

### Run EMA 9/20 Strategy (Automatic)

The bot runs automatically via `main.py`. It will:
- Check for EMA 9/20 crossovers every 15 minutes
- Execute trades when crossovers are detected
- Set TP/SL orders automatically

**Monitor:**
```bash
fly logs -a ema-cross-9-20
```

**Check health:**
```bash
curl https://ema-cross-9-20.fly.dev/health
```

### Test Trade Execution

To test if trades work, run the test script:

```bash
fly ssh console -a ema-cross-9-20 -C "python3 test_basic_btc_trade_simple.py"
```

This will:
- Open a small BTC long position ($25, max leverage)
- Set TP at 100% and SL at 30%
- Show you the order ID

**Verify on Hyperliquid dashboard** that the trade appears.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PRIVATE_KEY` | Your Hyperliquid private key | `0x...` |
| `USE_TESTNET` | Use testnet (true/false) | `false` |
| `SYMBOLS` | Symbols to trade (comma-separated) | `ETH,SOL,BTC` |
| `COLLATERAL_USD` | Collateral per trade | `25.0` |
| `STOP_LOSS_PERCENT` | Stop loss % | `30.0` |
| `TAKE_PROFIT_PERCENT` | Take profit % | `100.0` |
| `TIMEFRAME` | Candle timeframe | `15m` |

## Useful Commands

**View logs:**
```bash
fly logs -a ema-cross-9-20
```

**Check status:**
```bash
fly status -a ema-cross-9-20
```

**Restart bot:**
```bash
fly apps restart ema-cross-9-20
```

**SSH into container:**
```bash
fly ssh console -a ema-cross-9-20
```

**Update secrets:**
```bash
fly secrets set VARIABLE_NAME="value" -a ema-cross-9-20
```

**View secrets:**
```bash
fly secrets list -a ema-cross-9-20
```

## Health Check

The bot includes a health check server to prevent Fly.io from sleeping:
- Health: `https://ema-cross-9-20.fly.dev/health`
- Ping: `https://ema-cross-9-20.fly.dev/ping`

## Troubleshooting

**Bot not starting:**
- Check logs: `fly logs -a ema-cross-9-20`
- Verify PRIVATE_KEY is set correctly
- Check all environment variables are set

**Trades not executing:**
- Monitor logs for entry signals
- Verify sufficient collateral
- Check Hyperliquid API status

**Health check failing:**
- Check if app is running: `fly status`
- Verify port 8080 is accessible
- Restart if needed: `fly apps restart`

