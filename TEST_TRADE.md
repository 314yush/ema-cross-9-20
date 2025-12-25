# Testing Trade Execution on Fly.io

This guide shows you how to test if your bot can execute trades correctly.

## ⚠️ Important Notes

- **Test on TESTNET first** - Set `USE_TESTNET=true` before testing
- **Start with small amounts** - Use minimal collateral for testing
- **Verify on dashboard** - Always check Hyperliquid dashboard after trades

## Method 1: Run Test Script on Fly.io (Recommended)

### Step 1: Copy test script to Fly.io

```bash
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# Copy the test script
fly sftp upload test_trade_fly.py /app/test_trade_fly.py -a ema-cross-9-20
```

### Step 2: Run the test script

```bash
fly ssh console -a ema-cross-9-20 -C "python3 /app/test_trade_fly.py"
```

### Step 3: Check results

The script will:
1. Initialize the bot
2. Get current price
3. Calculate a small test position ($5, no leverage)
4. Execute a BUY order
5. Show the order ID

### Step 4: Verify on Hyperliquid

1. Go to [Hyperliquid Dashboard](https://app.hyperliquid.xyz)
2. Check your positions
3. Verify the test trade appears

## Method 2: Monitor for Natural Entry Signal

The bot will automatically execute trades when entry conditions are met.

### Monitor logs:

```bash
fly logs -a ema-cross-9-20
```

### What to look for:

```
✅ Entry conditions met! Executing trade...
✅ Trade executed successfully!
   Entry Price: $XXX.XX
   Position Size: X.XXXXXX SOL
   Stop Loss: $XXX.XX
   Take Profit: $XXX.XX
```

### Verify trade:

1. Check Hyperliquid dashboard
2. Look for new position
3. Verify TP/SL orders are set

## Method 3: Force Test Trade (Advanced)

If you want to force a test trade without waiting for signals:

### Option A: Temporarily modify strategy

1. SSH into Fly.io:
```bash
fly ssh console -a ema-cross-9-20
```

2. Edit the strategy to always return True for `should_execute()`
3. Run the bot
4. Revert changes after testing

### Option B: Use test script locally

```bash
# Set USE_TESTNET=true first!
fly secrets set USE_TESTNET=true -a ema-cross-9-20

# Run test locally (will use Fly.io secrets if connected)
python3 test_live_trade.py
```

## Method 4: Check Bot Capabilities

Run the basic test script to verify all components work:

```bash
# Locally
python3 test_trade_execution.py

# Or on Fly.io
fly ssh console -a ema-cross-9-20 -C "python3 /app/test_trade_execution.py"
```

This tests:
- ✅ Bot initialization
- ✅ Price fetching
- ✅ Strategy setup
- ✅ Indicator calculation
- ✅ Position sizing
- ✅ API connectivity

## Testing Checklist

Before testing live trades:

- [ ] Set `USE_TESTNET=true` for safe testing
- [ ] Verify `PRIVATE_KEY` is set correctly
- [ ] Check wallet has sufficient balance
- [ ] Run basic functionality test
- [ ] Monitor logs for errors
- [ ] Start with minimal collateral ($5-10)
- [ ] Verify trade appears on dashboard
- [ ] Check TP/SL orders are set correctly

## Troubleshooting

### Trade fails with "Insufficient balance"

- Check wallet balance on Hyperliquid
- Reduce test collateral amount
- Verify you're on testnet if testing

### Trade fails with "Invalid private key"

- Verify `PRIVATE_KEY` secret is set correctly
- Check key format (should be hex, 0x prefix optional)
- Ensure key matches your Hyperliquid wallet

### Trade executes but doesn't appear

- Check Hyperliquid dashboard (may take a few seconds)
- Verify you're looking at the correct wallet
- Check if trade was rejected (view in order history)

### Bot keeps crashing

- Check logs: `fly logs -a ema-cross-9-20`
- Verify all environment variables are set
- Check for API rate limits

## Safe Testing Procedure

1. **Set testnet mode:**
   ```bash
   fly secrets set USE_TESTNET=true -a ema-cross-9-20
   fly apps restart ema-cross-9-20
   ```

2. **Run basic test:**
   ```bash
   python3 test_trade_execution.py
   ```

3. **Execute small test trade:**
   ```bash
   # Copy script to Fly.io
   fly sftp upload test_trade_fly.py /app/ -a ema-cross-9-20
   
   # Run test
   fly ssh console -a ema-cross-9-20 -C "python3 /app/test_trade_fly.py"
   ```

4. **Verify on dashboard:**
   - Check Hyperliquid testnet dashboard
   - Verify position appears
   - Check TP/SL orders

5. **Switch to mainnet (when ready):**
   ```bash
   fly secrets set USE_TESTNET=false -a ema-cross-9-20
   fly apps restart ema-cross-9-20
   ```

## Quick Test Command

Run this to test everything at once:

```bash
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# 1. Test basic functionality
python3 test_trade_execution.py

# 2. Copy test script to Fly.io
fly sftp upload test_trade_fly.py /app/ -a ema-cross-9-20

# 3. Run test trade on Fly.io
fly ssh console -a ema-cross-9-20 -C "python3 /app/test_trade_fly.py"

# 4. Monitor logs
fly logs -a ema-cross-9-20
```

## Next Steps

After successful test:

1. ✅ Monitor bot for 24 hours
2. ✅ Verify trades execute correctly
3. ✅ Check TP/SL orders work
4. ✅ Review performance
5. ✅ Adjust strategy parameters if needed

---

**Remember:** Always test on testnet first! 🧪

