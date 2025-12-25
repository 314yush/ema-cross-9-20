# Cloud Deployment Guide

This guide covers deploying the trading bot to various cloud platforms.

## Prerequisites

1. **Environment Variables**: Create a `.env` file with your configuration:
   ```env
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

2. **Git Repository**: Push your code to GitHub/GitLab/Bitbucket

## Deployment Options

### Option 1: Railway (Recommended - Easiest)

Railway is great for long-running processes and has a free tier.

1. **Sign up**: Go to [railway.app](https://railway.app) and sign up
2. **Create Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your trading bot repository
4. **Configure Environment Variables**:
   - Go to your project → Variables
   - Add all environment variables from your `.env` file
   - **Important**: Set `PRIVATE_KEY` securely
5. **Deploy**: Railway will automatically detect the Dockerfile and deploy
6. **Monitor**: Check logs in the Railway dashboard

**Railway automatically:**
- Detects `railway.json` configuration
- Builds from Dockerfile
- Keeps the service running 24/7
- Provides logs and monitoring

### Option 2: Render

Render offers free tier with some limitations.

1. **Sign up**: Go to [render.com](https://render.com) and sign up
2. **Create Web Service**: 
   - Click "New" → "Web Service"
   - Connect your GitHub repository
3. **Configure**:
   - Build Command: (leave empty, uses Dockerfile)
   - Start Command: (leave empty, uses Dockerfile CMD)
   - Environment: Docker
4. **Set Environment Variables**:
   - Go to Environment section
   - Add all variables from your `.env` file
5. **Deploy**: Click "Create Web Service"
6. **Note**: Free tier may sleep after inactivity. Consider paid plan for 24/7 operation.

### Option 3: AWS EC2

For more control and reliability.

1. **Launch EC2 Instance**:
   - Go to AWS Console → EC2
   - Launch instance (Ubuntu 22.04 LTS recommended)
   - Choose t2.micro (free tier) or t3.small for better performance
   - Configure security group (no special ports needed)

2. **SSH into Instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Docker**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker ubuntu
   ```

4. **Clone Repository**:
   ```bash
   git clone your-repo-url
   cd trading-bot
   ```

5. **Create .env file**:
   ```bash
   nano .env
   # Paste your environment variables
   ```

6. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

7. **View Logs**:
   ```bash
   docker-compose logs -f
   ```

8. **Keep Running**: Use `screen` or `tmux` for persistent sessions, or set up as systemd service

### Option 4: Google Cloud Run

Serverless option (may have timeout limits).

1. **Install gcloud CLI**
2. **Build and Push**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/trading-bot
   ```
3. **Deploy**:
   ```bash
   gcloud run deploy trading-bot \
     --image gcr.io/PROJECT-ID/trading-bot \
     --platform managed \
     --region us-central1 \
     --set-env-vars="PRIVATE_KEY=your_key,USE_TESTNET=false,..."
   ```

### Option 5: DigitalOcean App Platform

1. **Sign up**: [digitalocean.com](https://www.digitalocean.com)
2. **Create App**: Connect GitHub repository
3. **Configure**: Select Dockerfile, set environment variables
4. **Deploy**: DigitalOcean handles the rest

### Option 6: Heroku

1. **Install Heroku CLI**
2. **Login**: `heroku login`
3. **Create App**: `heroku create your-bot-name`
4. **Set Config Vars**:
   ```bash
   heroku config:set PRIVATE_KEY=your_key
   heroku config:set USE_TESTNET=false
   # ... set all other vars
   ```
5. **Deploy**: `git push heroku main`

**Note**: Heroku free tier was discontinued. Paid plans start at $7/month.

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `PRIVATE_KEY` | Your Hyperliquid private key (required) | - |
| `USE_TESTNET` | Use testnet (true/false) | false |
| `STRATEGY` | Strategy to run (sol_momentum, ema_9_20) | sol_momentum |
| `SYMBOL` | Trading symbol | SOL |
| `COLLATERAL_USD` | Collateral per trade in USD | 1000.0 |
| `LEVERAGE` | Leverage multiplier | 10 |
| `TIMEFRAME` | Candle timeframe (15m, 30m, 1h, 4h, 1d) | 15m |
| `RISK_PER_TRADE_PERCENT` | Risk percentage per trade | 1.5 |
| `ATR_STOP_MULTIPLIER` | ATR multiplier for stop loss | 0.5 |
| `RISK_REWARD_RATIO` | Risk-to-reward ratio | 3.0 |
| `SLOPE_THRESHOLD` | EMA slope threshold | 0.10 |

## Preventing Sleep (Keep-Alive)

Railway's free tier can sleep after inactivity. The bot includes a built-in health check server to prevent this.

### Quick Setup

1. **Railway Health Checks** (Recommended):
   - Go to Railway Dashboard → Settings → Health Checks
   - Enable health checks
   - Set path to `/health`
   - Railway will automatically ping and keep your bot awake

2. **External Ping Service** (Backup):
   - Use [UptimeRobot](https://uptimerobot.com) (free)
   - Ping `https://your-app.railway.app/health` every 5 minutes
   - See `KEEP_ALIVE.md` for detailed instructions

The health check server runs automatically on port 8080 (or Railway's assigned port).

## Monitoring & Logs

### Railway
- Dashboard → Your Project → Logs tab
- Real-time logs with search functionality

### Render
- Dashboard → Your Service → Logs tab
- Download logs as needed

### AWS EC2
```bash
docker-compose logs -f trading-bot
```

### Docker (Local)
```bash
docker-compose logs -f
```

## Troubleshooting

### Bot Not Starting
1. Check environment variables are set correctly
2. Verify `PRIVATE_KEY` is correct format
3. Check logs for error messages
4. Ensure `USE_TESTNET` matches your key type

### Bot Stops Running
1. **Railway/Render**: Check if you've exceeded free tier limits
2. **EC2**: Check instance status, ensure it's running
3. Check logs for errors or crashes

### Connection Issues
1. Verify internet connectivity
2. Check Hyperliquid API status
3. Ensure firewall allows outbound connections

## Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use environment variables** - Never hardcode secrets
3. **Rotate keys regularly** - Update `PRIVATE_KEY` periodically
4. **Monitor logs** - Check for suspicious activity
5. **Start with testnet** - Test thoroughly before mainnet
6. **Use minimal collateral** - Start small, scale gradually

## Cost Estimates

- **Railway**: Free tier available, ~$5-20/month for paid
- **Render**: Free tier (may sleep), ~$7/month for always-on
- **AWS EC2**: t2.micro free tier, ~$10-15/month for t3.small
- **DigitalOcean**: ~$5/month for basic droplet
- **Heroku**: ~$7/month minimum

## Recommended Setup

For production use, **Railway** or **AWS EC2** are recommended:
- **Railway**: Easiest setup, good free tier, reliable
- **AWS EC2**: More control, scalable, industry standard

For testing/development:
- **Render**: Good free tier for testing
- **Local Docker**: Best for development

## Support

If you encounter issues:
1. Check logs first
2. Verify environment variables
3. Test locally with Docker first
4. Check platform-specific documentation

