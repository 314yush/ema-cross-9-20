# Keep-Alive Guide - Preventing Railway Sleep

Railway's free tier can sleep after inactivity. This guide explains how to prevent that.

## Built-in Health Check Server

The bot now includes a built-in health check server that runs automatically. This helps prevent Railway from sleeping by:

1. **Responding to health checks** - Railway can ping the `/health` endpoint
2. **Providing status information** - Shows bot status, check count, and last check time
3. **Running in background** - Doesn't interfere with trading operations

## How It Works

The health check server:
- Starts automatically when the bot runs
- Runs on port 8080 (configurable via `HEALTH_CHECK_PORT`)
- Provides two endpoints:
  - `/health` - Full status JSON response
  - `/ping` - Simple "pong" response

### Health Check Endpoints

**GET /health**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-26T12:00:00",
  "bot": "running",
  "checks": 42,
  "last_check": "2025-12-26 12:00:00"
}
```

**GET /ping**
```
pong
```

## Railway Configuration

### Option 1: Railway Health Checks (Recommended)

Railway automatically pings your service if configured:

1. **In Railway Dashboard:**
   - Go to your project → Settings → Health Checks
   - Enable health checks
   - Set path to `/health`
   - Set interval to 30 seconds (or as needed)

2. **Railway will automatically:**
   - Ping `/health` endpoint periodically
   - Keep your service awake
   - Restart if health checks fail

### Option 2: External Ping Services (Free)

Use free external services to ping your bot:

#### UptimeRobot (Recommended)
1. Sign up at [uptimerobot.com](https://uptimerobot.com)
2. Add a new monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: Trading Bot Keep-Alive
   - URL: `https://your-railway-app.railway.app/health`
   - Monitoring Interval: 5 minutes
3. UptimeRobot will ping your bot every 5 minutes

#### Cron-Job.org
1. Sign up at [cron-job.org](https://cron-job.org)
2. Create a new cron job:
   - URL: `https://your-railway-app.railway.app/ping`
   - Schedule: Every 5 minutes (`*/5 * * * *`)
3. Save and activate

#### EasyCron
1. Sign up at [easycron.com](https://www.easycron.com)
2. Create a new cron job:
   - URL: `https://your-railway-app.railway.app/ping`
   - Schedule: Every 5 minutes
3. Free tier allows 1 cron job

### Option 3: Railway Pro Plan

Railway's paid plans ($5+/month) don't sleep:
- No need for keep-alive pings
- Always-on service
- Better reliability

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HEALTH_CHECK_PORT` | Port for health check server | 8080 |

### Railway Port Configuration

Railway automatically assigns a port. The health server will:
1. Use `PORT` environment variable if set (Railway provides this)
2. Fall back to `HEALTH_CHECK_PORT` if `PORT` not set
3. Default to 8080 if neither is set

**Note:** Railway provides a `PORT` environment variable automatically. The health server detects this and uses it.

## Testing Health Checks

### Local Testing
```bash
# Start the bot
python main.py

# In another terminal, test health check
curl http://localhost:8080/health
curl http://localhost:8080/ping
```

### After Deployment
```bash
# Replace with your Railway URL
curl https://your-app.railway.app/health
curl https://your-app.railway.app/ping
```

## Monitoring

### Check if Bot is Awake

Visit your Railway URL in a browser:
- `https://your-app.railway.app/health` - See full status
- `https://your-app.railway.app/ping` - Quick check

### Railway Logs

Check Railway logs to see health check requests:
```
✅ Health check server started on port 8080
   Health endpoint: http://0.0.0.0:8080/health
   Ping endpoint: http://0.0.0.0:8080/ping
```

## Troubleshooting

### Bot Still Sleeping

1. **Check Railway Health Checks:**
   - Ensure health checks are enabled in Railway settings
   - Verify path is set to `/health`

2. **Check External Ping Services:**
   - Verify URL is correct (include `https://`)
   - Check if service is actually pinging (view logs)
   - Ensure ping interval is frequent enough (5 minutes or less)

3. **Check Port Configuration:**
   - Railway should automatically set `PORT` variable
   - Health server should detect and use it
   - Check logs to see which port is being used

### Health Check Not Responding

1. **Check Bot is Running:**
   - View Railway logs
   - Ensure bot started successfully
   - Look for "Health check server started" message

2. **Check Port:**
   - Railway may use a different port
   - Check Railway dashboard → Settings → Networking
   - Verify `PORT` environment variable

3. **Check Firewall:**
   - Railway should handle this automatically
   - If using custom domain, ensure DNS is configured

## Best Practices

1. ✅ **Use Railway Health Checks** - Built-in, most reliable
2. ✅ **Add External Ping Service** - Backup option (UptimeRobot recommended)
3. ✅ **Monitor Regularly** - Check logs weekly
4. ✅ **Start with Testnet** - Test keep-alive before mainnet
5. ✅ **Consider Paid Plan** - If critical, Railway Pro never sleeps

## Free Keep-Alive Services Comparison

| Service | Free Tier | Ping Interval | Best For |
|---------|-----------|---------------|----------|
| UptimeRobot | ✅ 50 monitors | 5 min | Most reliable |
| Cron-Job.org | ✅ Unlimited | Custom | Flexible scheduling |
| EasyCron | ✅ 1 cron job | Custom | Simple setup |
| Railway Health Checks | ✅ Built-in | Configurable | Easiest setup |

## Summary

The bot now includes automatic health check support. To prevent Railway from sleeping:

1. **Enable Railway Health Checks** (easiest)
2. **OR** set up UptimeRobot to ping `/health` every 5 minutes
3. **OR** upgrade to Railway Pro plan

The health check server runs automatically - no additional configuration needed!

