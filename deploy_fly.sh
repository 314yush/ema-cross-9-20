#!/bin/bash
# Quick deployment script for Fly.io

echo "🚀 Deploying Trading Bot to Fly.io"
echo "===================================="
echo ""

# Check if fly CLI is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    echo "✅ Fly CLI installed. Please run this script again."
    exit 1
fi

# Check if logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    fly auth login
fi

# Launch if fly.toml doesn't exist or app doesn't exist
if [ ! -f "fly.toml" ] || ! fly status &> /dev/null; then
    echo "📦 Initializing Fly.io app..."
    fly launch --no-deploy
fi

# Set required environment variables
echo ""
echo "🔧 Setting environment variables..."
echo "Please enter your configuration:"
echo ""

read -p "PRIVATE_KEY: " PRIVATE_KEY
read -p "USE_TESTNET (true/false) [false]: " USE_TESTNET
USE_TESTNET=${USE_TESTNET:-false}

read -p "STRATEGY (sol_momentum/ema_9_20) [sol_momentum]: " STRATEGY
STRATEGY=${STRATEGY:-sol_momentum}

read -p "SYMBOL [SOL]: " SYMBOL
SYMBOL=${SYMBOL:-SOL}

read -p "COLLATERAL_USD [1000.0]: " COLLATERAL_USD
COLLATERAL_USD=${COLLATERAL_USD:-1000.0}

read -p "LEVERAGE [10]: " LEVERAGE
LEVERAGE=${LEVERAGE:-10}

# Set secrets
fly secrets set \
    PRIVATE_KEY="$PRIVATE_KEY" \
    USE_TESTNET="$USE_TESTNET" \
    STRATEGY="$STRATEGY" \
    SYMBOL="$SYMBOL" \
    COLLATERAL_USD="$COLLATERAL_USD" \
    LEVERAGE="$LEVERAGE" \
    TIMEFRAME="15m" \
    RISK_PER_TRADE_PERCENT="1.5" \
    ATR_STOP_MULTIPLIER="0.5" \
    RISK_REWARD_RATIO="3.0" \
    SLOPE_THRESHOLD="0.10"

echo ""
echo "🚀 Deploying..."
fly deploy

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Useful commands:"
echo "   fly logs          - View logs"
echo "   fly status        - Check status"
echo "   fly open          - Open app in browser"
echo "   fly secrets list  - List environment variables"
echo ""

