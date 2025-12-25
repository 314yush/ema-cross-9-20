# Quick Start Guide - Cloud Deployment

## 🆓 Free Options (Railway Free Plan Expired)

Since Railway's free plan has expired, here are the best alternatives:

### Option 1: Fly.io (Recommended - Best Free Tier) ⭐

**Why Fly.io:**
- ✅ Generous free tier (3 VMs)
- ✅ Never sleeps (always-on)
- ✅ Easy deployment
- ✅ Built-in health checks

**Quick Setup:**
1. Sign up at [fly.io](https://fly.io) (free)
2. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. Login: `fly auth login`
4. Deploy: `fly launch` (uses `fly.toml` automatically)
5. Set secrets: `fly secrets set PRIVATE_KEY=your_key USE_TESTNET=false ...`
6. Deploy: `fly deploy`

See `ALTERNATIVES.md` for detailed guide.

---

### Option 2: Koyeb (Good Free Alternative)

1. Sign up at [koyeb.com](https://www.koyeb.com)
2. Create App → GitHub → Select repository
3. Configure Docker deployment
4. Add environment variables
5. Deploy

See `ALTERNATIVES.md` for details.

---

## 💰 Paid Options

### Railway Pro ($5/month)
- Original platform, now paid
- Never sleeps
- Easy deployment

### DigitalOcean ($5/month)
- Reliable and simple
- Never sleeps
- See `ALTERNATIVES.md` for setup

---

## Fastest Way: Railway (Paid)

### Step 1: Prepare Your Code
1. Make sure all files are committed to Git
2. Push to GitHub/GitLab/Bitbucket

### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your trading bot repository
4. Railway will automatically detect the Dockerfile

### Step 3: Configure Environment Variables
In Railway dashboard → Your Project → Variables, add:

```
PRIVATE_KEY=your_private_key_here
USE_TESTNET=false
STRATEGY=sol_momentum
SYMBOL=SOL
COLLATERAL_USD=1000.0
LEVERAGE=10
TIMEFRAME=15m
RISK_PER_TRADE_PERCENT=1.5
ATR_STOP_MULTIPLIER=0.5
RISK_REWARD_RATIO=3.0
SLOPE_THRESHOLD=0.10
```

### Step 4: Deploy
Railway will automatically build and deploy. Check the "Logs" tab to see your bot running!

---

## Alternative: Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Set Environment to "Docker"
5. Add environment variables (same as Railway above)
6. Click "Create Web Service"

---

## Test Locally First (Recommended)

Before deploying to cloud, test locally with Docker:

```bash
# 1. Create .env file with your configuration
cp .env.example .env
# Edit .env with your values

# 2. Build and run
docker-compose up --build

# 3. View logs
docker-compose logs -f

# 4. Stop
docker-compose down
```

---

## Environment Variables Explained

- **PRIVATE_KEY**: Your Hyperliquid wallet private key (REQUIRED)
- **USE_TESTNET**: Set to `true` for testing, `false` for real trading
- **STRATEGY**: `sol_momentum` (SOL EMA Momentum) or `ema_9_20` (EMA 9/20)
- **SYMBOL**: Trading symbol (SOL, BTC, ETH, etc.)
- **COLLATERAL_USD**: Amount per trade in USD
- **LEVERAGE**: Leverage multiplier (1-20x typically)
- **TIMEFRAME**: Candle timeframe (15m, 30m, 1h, 4h, 1d)
- **RISK_PER_TRADE_PERCENT**: Risk percentage per trade (1-2% recommended)
- **ATR_STOP_MULTIPLIER**: ATR multiplier for stop loss (0.5 = half ATR)
- **RISK_REWARD_RATIO**: Risk-to-reward ratio (3.0 = 1:3)
- **SLOPE_THRESHOLD**: EMA slope threshold (0.10 = 10% slope)

---

## Preventing Railway Sleep (Keep-Alive)

The bot includes a built-in health check server to prevent Railway from sleeping:

1. **Automatic Health Checks** - Railway can ping `/health` endpoint
2. **External Ping Services** - Use UptimeRobot or similar to ping every 5 minutes
3. **See `KEEP_ALIVE.md`** - Detailed guide on preventing sleep

**Quick Setup:**
- Railway automatically detects health checks
- Or set up [UptimeRobot](https://uptimerobot.com) to ping `https://your-app.railway.app/health` every 5 minutes

## Monitoring Your Bot

### Railway
- Dashboard → Your Project → Logs (real-time)
- Check "Metrics" for resource usage
- Visit `https://your-app.railway.app/health` to see bot status

### Render
- Dashboard → Your Service → Logs
- Check "Metrics" tab
- Visit `https://your-app.onrender.com/health` to see bot status

### Local Docker
```bash
docker-compose logs -f trading-bot

# Test health check
curl http://localhost:8080/health
```

---

## Important Security Notes

1. ✅ **Never commit your `.env` file** - It's already in `.gitignore`
2. ✅ **Use environment variables** - Never hardcode secrets in code
3. ✅ **Start with testnet** - Test with `USE_TESTNET=true` first
4. ✅ **Use minimal collateral** - Start small, scale gradually
5. ✅ **Monitor regularly** - Check logs daily

---

## Troubleshooting

### Bot won't start
- Check all environment variables are set
- Verify PRIVATE_KEY format is correct
- Check logs for specific error messages

### Bot stops running
- Check if you've exceeded free tier limits (Railway/Render)
- Verify instance is running (AWS EC2)
- Check logs for crashes or errors

### No trades executing
- Verify strategy conditions are being met
- Check logs for "No entry signal" messages
- Ensure sufficient capital and correct symbol

---

## Need Help?

1. Check `DEPLOYMENT.md` for detailed platform-specific guides
2. Review logs for error messages
3. Test locally with Docker first
4. Start with testnet (`USE_TESTNET=true`)

---

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Railway | ✅ Yes | $5-20/mo | Easiest, reliable |
| Render | ✅ Yes* | $7/mo | Good free tier |
| AWS EC2 | ✅ Yes | $10-15/mo | Most control |
| DigitalOcean | ❌ No | $5/mo | Simple VPS |

*Render free tier may sleep after inactivity

---

**Ready to deploy? Start with Railway - it's the easiest!** 🚀

