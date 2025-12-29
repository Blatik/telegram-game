#!/bin/bash

# --- Master Setup Script for Financial Calculator Backend ---
# This script automates the installation of all dependencies, 
# clones the repository, and sets up the server environment.

set -e # Exit on error

echo "🚀 Starting VPS Setup..."

# 1. Update system and install base packages
sudo apt update
sudo apt install -y python3-pip python3-venv git curl

# 2. Clone Repository (if not already cloned)
if [ ! -d "telegram-game" ]; then
    echo "📂 Cloning repository..."
    git clone https://github.com/Blatik/telegram-game.git
fi

cd telegram-game/backend

# 3. Setup Virtual Environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Dependencies
echo "📦 Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Install Cloudflare Tunnel (cloudflared)
if ! command -v cloudflared &> /dev/null; then
    echo "🛡️ Installing Cloudflare Tunnel..."
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
fi

echo "✅ Environment Setup Complete!"
echo "--------------------------------------------------"
echo "NEXT STEPS:"
echo "1. Run 'cloudflared tunnel login' to authorize."
echo "2. Run 'uvicorn main:app --host 0.0.0.0 --port 8000' to start the server."
echo "--------------------------------------------------"
