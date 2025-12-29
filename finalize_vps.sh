#!/bin/bash
# finalize_vps.sh

# 1. Update Caddyfile
echo "34.169.229.189.sslip.io {
    reverse_proxy localhost:8000
}" | sudo tee /etc/caddy/Caddyfile

sudo systemctl reload caddy

# 2. Create Systemd Service
echo "[Unit]
Description=Finance Calculator Backend
After=network.target

[Service]
User=blatik
WorkingDirectory=/home/blatik/telegram-game/backend
ExecStart=/home/blatik/telegram-game/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/finance-app.service

sudo systemctl daemon-reload
sudo systemctl enable finance-app
sudo systemctl restart finance-app

echo "✅ Finalization complete. Backend running at https://34.169.229.189.sslip.io"
