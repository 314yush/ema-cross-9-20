# Free & Low-Cost Cloud Hosting Alternatives

Since Railway's free plan has expired, here are the best alternatives for hosting your trading bot.

## 🆓 Free Tier Options

### Option 1: Fly.io (Recommended - Best Free Tier)

**Why Fly.io:**
- ✅ Generous free tier (3 shared VMs)
- ✅ Never sleeps (always-on)
- ✅ Global edge deployment
- ✅ Easy Docker deployment
- ✅ Built-in health checks

**Setup:**
1. Sign up at [fly.io](https://fly.io) (free)
2. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
3. Login: `fly auth login`
4. Deploy: `fly launch` (uses `fly.toml` automatically)
5. Set secrets: `fly secrets set PRIVATE_KEY=your_key USE_TESTNET=false ...`
6. Deploy: `fly deploy`

**Free Tier Limits:**
- 3 shared-cpu VMs (256MB RAM each)
- 3GB persistent volume
- 160GB outbound data transfer/month

**Cost:** Free for small bots, ~$2-5/month if you need more resources

---

### Option 2: Koyeb (Good Free Tier)

**Why Koyeb:**
- ✅ Free tier available
- ✅ Never sleeps
- ✅ Automatic deployments from GitHub
- ✅ Global edge network

**Setup:**
1. Sign up at [koyeb.com](https://www.koyeb.com) (free)
2. Create App → GitHub → Select repository
3. Configure:
   - Build: Docker
   - Dockerfile: `Dockerfile`
   - Health check: `/health`
4. Add environment variables
5. Deploy

**Free Tier Limits:**
- 1 service
- 512MB RAM
- Shared CPU
- 100GB bandwidth/month

**Cost:** Free tier, $7/month for more resources

---

### Option 3: Render (Free but Sleeps)

**Why Render:**
- ✅ Free tier available
- ⚠️ Sleeps after 15 minutes of inactivity
- ✅ Easy GitHub integration
- ✅ Automatic SSL

**Setup:**
1. Sign up at [render.com](https://render.com) (free)
2. New → Web Service → GitHub repo
3. Configure:
   - Environment: Docker
   - Health check: `/health`
4. Add environment variables
5. Deploy

**Keep-Alive:** Use UptimeRobot to ping `/health` every 5 minutes (see `KEEP_ALIVE.md`)

**Free Tier Limits:**
- Sleeps after 15 min inactivity
- 512MB RAM
- 750 hours/month

**Cost:** Free (with sleep), $7/month for always-on

---

### Option 4: Google Cloud Run (Free Tier)

**Why Cloud Run:**
- ✅ Generous free tier
- ✅ Pay only for usage
- ✅ Auto-scaling
- ⚠️ May have cold starts

**Setup:**
1. Sign up at [cloud.google.com](https://cloud.google.com) (free $300 credit)
2. Install gcloud CLI
3. Build and deploy:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/trading-bot
   gcloud run deploy trading-bot \
     --image gcr.io/PROJECT-ID/trading-bot \
     --platform managed \
     --region us-central1 \
     --set-env-vars="PRIVATE_KEY=your_key,..." \
     --min-instances=1 \
     --max-instances=1
   ```

**Free Tier:**
- 2 million requests/month
- 360,000 GB-seconds compute
- 180,000 vCPU-seconds

**Cost:** Free tier generous, ~$5-10/month for always-on

---

### Option 5: AWS Free Tier (EC2)

**Why AWS EC2:**
- ✅ t2.micro free for 12 months
- ✅ Full control
- ✅ Never sleeps
- ⚠️ Requires server management

**Setup:**
1. Sign up at [aws.amazon.com](https://aws.amazon.com) (free tier)
2. Launch EC2 instance:
   - OS: Ubuntu 22.04 LTS
   - Instance: t2.micro (free tier)
   - Security group: Allow SSH (port 22)
3. SSH and install Docker:
   ```bash
   ssh -i key.pem ubuntu@your-instance-ip
   sudo apt update && sudo apt install docker.io docker-compose -y
   sudo usermod -aG docker ubuntu
   ```
4. Clone repo and deploy:
   ```bash
   git clone https://github.com/314yush/ema-cross-9-20.git
   cd ema-cross-9-20
   # Create .env file
   docker-compose up -d
   ```

**Free Tier:**
- t2.micro: 750 hours/month for 12 months
- 30GB storage

**Cost:** Free for 12 months, then ~$8-10/month

---

## 💰 Low-Cost Paid Options ($5-10/month)

### Option 6: DigitalOcean App Platform ($5/month)

**Why DigitalOcean:**
- ✅ $5/month minimum
- ✅ Never sleeps
- ✅ Easy deployment
- ✅ Good documentation

**Setup:**
1. Sign up at [digitalocean.com](https://www.digitalocean.com)
2. Create App → GitHub → Select repo
3. Configure:
   - Build: Docker
   - Health check: `/health`
4. Add environment variables
5. Deploy

**Cost:** $5/month for basic plan

---

### Option 7: Vultr ($6/month)

**Why Vultr:**
- ✅ $6/month VPS
- ✅ Full control
- ✅ Never sleeps
- ✅ Similar to DigitalOcean

**Setup:** Same as AWS EC2 (VPS approach)

**Cost:** $6/month for basic VPS

---

### Option 8: Oracle Cloud (Always Free)

**Why Oracle Cloud:**
- ✅ Always free tier (no expiration)
- ✅ 2 VMs with 1GB RAM each
- ✅ Never sleeps
- ⚠️ More complex setup

**Setup:**
1. Sign up at [oracle.com/cloud](https://www.oracle.com/cloud)
2. Create Always Free VM instance
3. Follow AWS EC2 setup steps

**Free Tier:**
- 2 VMs (1GB RAM, 50GB storage each)
- Always free (no expiration)

**Cost:** Free forever (if you qualify)

---

## 📊 Comparison Table

| Platform | Free Tier | Sleeps? | Always-On | Easiest | Best For |
|----------|-----------|---------|-----------|---------|----------|
| **Fly.io** | ✅ Yes | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ | Best overall |
| **Koyeb** | ✅ Yes | ❌ No | ✅ Yes | ⭐⭐⭐⭐ | Good alternative |
| **Render** | ✅ Yes | ⚠️ Yes | ⚠️ With ping | ⭐⭐⭐⭐⭐ | Easy but sleeps |
| **Cloud Run** | ✅ Yes | ⚠️ Cold start | ✅ Yes | ⭐⭐⭐ | Google ecosystem |
| **AWS EC2** | ✅ 12mo | ❌ No | ✅ Yes | ⭐⭐ | Full control |
| **DigitalOcean** | ❌ No | ❌ No | ✅ Yes | ⭐⭐⭐⭐ | Reliable paid |
| **Oracle Cloud** | ✅ Forever | ❌ No | ✅ Yes | ⭐⭐ | Long-term free |

## 🎯 Recommendations

### Best Free Option: **Fly.io**
- Never sleeps
- Generous free tier
- Easy deployment
- Built-in health checks

### Best Paid Option: **DigitalOcean** ($5/month)
- Reliable and simple
- Never sleeps
- Good support
- Easy scaling

### Best for Learning: **AWS EC2** (Free 12 months)
- Full control
- Learn server management
- Industry standard

## 🚀 Quick Start: Fly.io (Recommended)

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Launch (creates fly.toml if needed)
fly launch

# 4. Set secrets
fly secrets set PRIVATE_KEY=your_key USE_TESTNET=false STRATEGY=sol_momentum

# 5. Deploy
fly deploy

# 6. Check status
fly status
fly logs
```

## 🔧 Migration from Railway

If you were using Railway:

1. **Export environment variables** from Railway dashboard
2. **Choose new platform** (Fly.io recommended)
3. **Deploy using platform-specific guide**
4. **Set environment variables** in new platform
5. **Test thoroughly** before switching
6. **Update monitoring** (UptimeRobot, etc.)

## 📝 Notes

- **Always test on testnet first** (`USE_TESTNET=true`)
- **Start with minimal collateral** (`COLLATERAL_USD=100`)
- **Monitor logs regularly** for first few days
- **Set up alerts** if platform supports it
- **Keep backups** of your `.env` file (securely)

## 🆘 Need Help?

- Check platform-specific documentation
- Review `DEPLOYMENT.md` for detailed guides
- Test locally with Docker first
- Start with testnet before mainnet

---

**Recommended:** Start with **Fly.io** - it's free, never sleeps, and easiest to deploy! 🚀

